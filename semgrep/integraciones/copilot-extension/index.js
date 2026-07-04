const express = require('express');
const axios = require('axios');
const crypto = require('crypto');

const app = express();

// Necesitamos el body crudo (string) para poder verificar la firma de GitHub
// byte a byte antes de parsearlo como JSON.
app.use(express.text({ type: '*/*' }));

const API_BASE_URL = process.env.WVS_API_URL || 'https://vulnerabilidad-web.sytes.net/backend';
const API_KEY = process.env.WVS_API_KEY || '';
const VERIFY_SIGNATURE = process.env.WVS_COPILOT_VERIFY_SIGNATURE !== 'false';

let cachedKeys = null;
let cachedKeysAt = 0;

async function getGithubPublicKeys() {
    const now = Date.now();
    if (cachedKeys && now - cachedKeysAt < 60 * 60 * 1000) {
        return cachedKeys;
    }
    const res = await axios.get('https://api.github.com/meta/public_keys/copilot_api');
    cachedKeys = res.data.public_keys;
    cachedKeysAt = now;
    return cachedKeys;
}

async function verifySignature(rawBody, keyId, signature) {
    const keys = await getGithubPublicKeys();
    const keyEntry = keys.find(k => k.key_identifier === keyId);
    if (!keyEntry) return false;
    return crypto.verify(
        'sha256',
        Buffer.from(rawBody, 'utf8'),
        { key: keyEntry.key, dsaEncoding: 'ieee-p1363' },
        Buffer.from(signature, 'base64')
    );
}

function sseChunk(res, content, finishReason = null) {
    const chunk = {
        id: `chatcmpl-${Date.now()}`,
        object: 'chat.completion.chunk',
        created: Math.floor(Date.now() / 1000),
        choices: [{ index: 0, delta: { role: 'assistant', content }, finish_reason: finishReason }]
    };
    res.write(`data: ${JSON.stringify(chunk)}\n\n`);
}

function sseEnd(res) {
    res.write('data: [DONE]\n\n');
    res.end();
}

app.get('/', (_req, res) => res.send('WVS Copilot Agent OK'));

app.post('/', async (req, res) => {
    const rawBody = typeof req.body === 'string' ? req.body : '';
    const keyId = req.header('Github-Public-Key-Identifier');
    const signature = req.header('Github-Public-Key-Signature');

    if (VERIFY_SIGNATURE && keyId && signature) {
        try {
            const valid = await verifySignature(rawBody, keyId, signature);
            if (!valid) {
                return res.status(401).send('Firma invalida');
            }
        } catch (err) {
            return res.status(401).send('No se pudo verificar la firma de GitHub');
        }
    }

    let payload;
    try {
        payload = JSON.parse(rawBody);
    } catch (err) {
        return res.status(400).send('JSON invalido');
    }

    const messages = payload.messages || [];
    const lastMessage = messages.length ? messages[messages.length - 1].content : '';
    const urlMatch = (lastMessage || '').match(/https?:\/\/[^\s]+/);

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    if (!urlMatch) {
        sseChunk(res, 'Hola, soy el agente de seguridad. Escribe una URL para escanear, ej: `@wvs-scanner analiza https://ejemplo.com`', 'stop');
        sseEnd(res);
        return;
    }

    const targetUrl = urlMatch[0];

    try {
        sseChunk(res, `Escaneando ${targetUrl}...\n\n`);

        const startRes = await axios.post(`${API_BASE_URL}/api/integrations/scans`, {
            target_url: targetUrl,
            depth: 1
        }, { headers: { 'X-API-Key': API_KEY } });

        const scanId = startRes.data.id;
        let detail = null;

        for (let i = 0; i < 20; i++) {
            await new Promise(r => setTimeout(r, 3000));
            const checkRes = await axios.get(`${API_BASE_URL}/api/integrations/scans/${scanId}`, {
                headers: { 'X-API-Key': API_KEY }
            });
            detail = checkRes.data;
            if (detail.status === 'completed' || detail.status === 'failed') break;
        }

        if (!detail || (detail.status !== 'completed' && detail.status !== 'failed')) {
            sseChunk(res, `El escaneo sigue en curso (ID #${scanId}). Vuelve a preguntar en unos segundos.`, 'stop');
            sseEnd(res);
            return;
        }

        if (detail.status === 'failed') {
            sseChunk(res, `El escaneo fallo: ${detail.error_message}`, 'stop');
            sseEnd(res);
            return;
        }

        const vulns = detail.vulnerabilities || [];
        let md = `### Resultados para ${targetUrl}\n\n`;
        md += `**Riesgo:** ${detail.risk_score}/100 — **${vulns.length}** hallazgo(s)\n\n`;
        if (vulns.length === 0) {
            md += 'No se encontraron vulnerabilidades.\n';
        } else {
            for (const v of vulns) {
                md += `- **[${v.severity.toUpperCase()}] ${v.title}**: ${v.description}\n  - Recomendacion: ${v.remediation}\n`;
            }
        }
        sseChunk(res, md, 'stop');
        sseEnd(res);

    } catch (error) {
        sseChunk(res, `Error al contactar el motor de escaneo: ${error.message}`, 'stop');
        sseEnd(res);
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Agente de Copilot corriendo en el puerto ${PORT}`);
});
