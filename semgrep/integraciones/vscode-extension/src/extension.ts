import * as vscode from 'vscode';
import * as http from 'http';
import * as https from 'https';

const outputChannel = vscode.window.createOutputChannel('Web Vulnerability Scanner');

export function activate(context: vscode.ExtensionContext) {
    let configureCmd = vscode.commands.registerCommand('wvs.configure', async () => {
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Introduce tu API Key del Web Vulnerability Scanner',
            password: true
        });
        if (apiKey) {
            await context.secrets.store('wvs.apiKey', apiKey);
            vscode.window.showInformationMessage('API Key guardada correctamente.');
        }
    });

    let registerCmd = vscode.commands.registerCommand('wvs.registerAndConfigure', async () => {
        const config = vscode.workspace.getConfiguration('wvs');
        const apiUrl = config.get<string>('apiUrl', 'https://vulnerabilidad-web.sytes.net/backend');

        const email = await vscode.window.showInputBox({
            prompt: 'Correo electronico (si ya tienes cuenta, se usa para iniciar sesion)',
            placeHolder: 'tucorreo@ejemplo.com',
            validateInput: (v) => (v.includes('@') ? null : 'Correo invalido')
        });
        if (!email) return;

        const defaultUsername = email.split('@')[0].padEnd(2, '_');
        const username = await vscode.window.showInputBox({
            prompt: 'Nombre de usuario (solo se usa si es tu primer registro)',
            value: defaultUsername
        });
        if (!username) return;

        const password = await vscode.window.showInputBox({
            prompt: 'Contrasena (minimo 8 caracteres)',
            password: true,
            validateInput: (v) => (v.length >= 8 ? null : 'Minimo 8 caracteres')
        });
        if (!password) return;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Configurando tu cuenta de Web Vulnerability Scanner...',
            cancellable: false
        }, async () => {
            try {
                let token: string;
                try {
                    const registerRes = await registerUser(apiUrl, email, username, password);
                    token = registerRes.access_token;
                } catch (err: any) {
                    if (String(err.message).includes('HTTP 409')) {
                        const loginRes = await loginUser(apiUrl, email, password);
                        token = loginRes.access_token;
                    } else {
                        throw err;
                    }
                }

                const apiKeyRes = await createApiKey(apiUrl, token, `vscode-${username}`);
                await context.secrets.store('wvs.apiKey', apiKeyRes.api_key);
                vscode.window.showInformationMessage('Cuenta lista. Ya puedes usar "WVS: Iniciar Escaneo".');
            } catch (error: any) {
                vscode.window.showErrorMessage(`No se pudo configurar la cuenta: ${error.message}`);
            }
        });
    });

    let scanCmd = vscode.commands.registerCommand('wvs.startScan', async () => {
        const apiKey = await context.secrets.get('wvs.apiKey');
        if (!apiKey) {
            vscode.window.showErrorMessage('API Key no configurada. Ejecuta "WVS: Configurar API Key".');
            return;
        }

        const targetUrl = await vscode.window.showInputBox({
            prompt: 'Introduce la URL a escanear (ej. https://ejemplo.com)',
            placeHolder: 'https://ejemplo.com'
        });

        if (!targetUrl) return;

        const config = vscode.workspace.getConfiguration('wvs');
        const apiUrl = config.get<string>('apiUrl', 'https://vulnerabilidad-web.sytes.net/backend');

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Escaneando ${targetUrl}...`,
            cancellable: false
        }, async (progress) => {
            try {
                const scanId = await startScan(apiUrl, apiKey, targetUrl);
                progress.report({ message: 'Escaneo iniciado, analizando...' });

                let completed = false;
                let resultDetail: any = null;
                while (!completed) {
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    resultDetail = await checkStatus(apiUrl, apiKey, scanId);
                    if (resultDetail.status === 'completed' || resultDetail.status === 'failed') {
                        completed = true;
                    }
                }

                if (resultDetail.status === 'failed') {
                    vscode.window.showErrorMessage(`Fallo el escaneo: ${resultDetail.error_message}`);
                    return;
                }

                const vulns: any[] = resultDetail.vulnerabilities || [];
                printReport(targetUrl, resultDetail, vulns);

                if (vulns.length > 0) {
                    vscode.window.showWarningMessage(
                        `Escaneo finalizado: ${vulns.length} vulnerabilidad(es) en ${targetUrl} (riesgo ${resultDetail.risk_score}/100). Ver panel "Web Vulnerability Scanner".`,
                        'Ver reporte'
                    ).then(choice => {
                        if (choice === 'Ver reporte') {
                            outputChannel.show();
                        }
                    });
                } else {
                    vscode.window.showInformationMessage(`Escaneo finalizado: sin vulnerabilidades en ${targetUrl}.`);
                }

            } catch (error: any) {
                vscode.window.showErrorMessage(`Error de conexion con la API: ${error.message}`);
            }
        });
    });

    context.subscriptions.push(configureCmd, registerCmd, scanCmd, outputChannel);
}

function printReport(targetUrl: string, detail: any, vulns: any[]) {
    outputChannel.clear();
    outputChannel.appendLine(`Escaneo #${detail.id} - ${targetUrl}`);
    outputChannel.appendLine(`Puntuacion de riesgo: ${detail.risk_score}/100`);
    outputChannel.appendLine('');

    if (vulns.length === 0) {
        outputChannel.appendLine('No se encontraron vulnerabilidades.');
    } else {
        for (const v of vulns) {
            outputChannel.appendLine(`[${String(v.severity).toUpperCase()}] ${v.title}`);
            outputChannel.appendLine(`  ${v.description}`);
            outputChannel.appendLine(`  Recomendacion: ${v.remediation}`);
            outputChannel.appendLine('');
        }
    }
    outputChannel.show(true);
}

function makeRequest(urlStr: string, options: http.RequestOptions, body?: any): Promise<any> {
    return new Promise((resolve, reject) => {
        const transport = urlStr.startsWith('https:') ? https : http;
        const req = transport.request(urlStr, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });
        req.on('error', reject);
        if (body) {
            req.write(JSON.stringify(body));
        }
        req.end();
    });
}

function makeFormRequest(urlStr: string, fields: Record<string, string>): Promise<any> {
    const bodyStr = Object.entries(fields)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&');
    return new Promise((resolve, reject) => {
        const transport = urlStr.startsWith('https:') ? https : http;
        const req = transport.request(urlStr, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': Buffer.byteLength(bodyStr)
            }
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });
        req.on('error', reject);
        req.write(bodyStr);
        req.end();
    });
}

function registerUser(apiUrl: string, email: string, username: string, password: string): Promise<any> {
    const options = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
    return makeRequest(`${apiUrl}/api/auth/register`, options, { email, username, password });
}

function loginUser(apiUrl: string, email: string, password: string): Promise<any> {
    return makeFormRequest(`${apiUrl}/api/auth/login`, { username: email, password });
}

function createApiKey(apiUrl: string, token: string, name: string): Promise<any> {
    const options = {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    };
    return makeRequest(`${apiUrl}/api/api-keys`, options, { name });
}

function startScan(apiUrl: string, apiKey: string, targetUrl: string): Promise<number> {
    const url = `${apiUrl}/api/integrations/scans`;
    const options = {
        method: 'POST',
        headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        }
    };
    return makeRequest(url, options, { target_url: targetUrl, depth: 1 }).then(res => res.id);
}

function checkStatus(apiUrl: string, apiKey: string, scanId: number): Promise<any> {
    const url = `${apiUrl}/api/integrations/scans/${scanId}`;
    const options = {
        method: 'GET',
        headers: { 'X-API-Key': apiKey }
    };
    return makeRequest(url, options);
}

export function deactivate() {}
