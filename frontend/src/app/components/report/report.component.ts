import { Component, OnInit } from '@angular/core';
import { StateService } from '../../services/state.service';
import { ScanService, Scan, Finding } from '../../services/scan.service';

@Component({
  selector: 'app-report',
  templateUrl: './report.component.html',
  styleUrls: ['./report.component.scss'],
})
export class ReportComponent implements OnInit {
  scan: Scan | null = null;
  generatedAt = new Date().toLocaleString('es-PE');

  constructor(
    private state: StateService,
    private scanService: ScanService,
  ) {}

  ngOnInit(): void {
    this.state.currentScan$.subscribe(s => { this.scan = s; });
  }

  get findings(): Finding[] { return this.scan?.results?.findings ?? []; }

  get summary() { return this.scan?.results?.severity_summary ?? {}; }

  severityClass(sev: string): string { return `sev-${sev}`; }

  /**
   * Download raw JSON report.
   */
  exportJSON(): void {
    if (!this.scan?.results) return;
    const blob = new Blob(
      [JSON.stringify(this.scan.results, null, 2)],
      { type: 'application/json' }
    );
    this._download(blob, `vulnscan-${Date.now()}.json`);
  }

  /**
   * Build a self-contained HTML report and trigger download.
   */
  exportHTML(): void {
    if (!this.scan) return;
    const html = this._buildHtmlReport();
    const blob = new Blob([html], { type: 'text/html' });
    this._download(blob, `vulnscan-report-${Date.now()}.html`);
  }

  /** Copy JSON to clipboard */
  copyJSON(): void {
    if (!this.scan?.results) return;
    navigator.clipboard.writeText(JSON.stringify(this.scan.results, null, 2));
  }

  private _download(blob: Blob, filename: string): void {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  private _buildHtmlReport(): string {
    const s = this.scan!;
    const r = s.results!;
    const rows = r.findings.map(f => {
      const sevColors: Record<string, string> = {
        critical: '#ff2d55', high: '#ff6b35', medium: '#f0b429', low: '#3fb950', info: '#58a6ff',
      };
      const c = sevColors[f.severity] ?? '#888';
      const rem = f.remediation.map(x => `<li>${x}</li>`).join('');
      return `
        <tr>
          <td><span style="color:${c};font-weight:700;text-transform:uppercase">${f.severity}</span></td>
          <td>${f.name}</td>
          <td style="font-family:monospace;font-size:12px">${f.url}</td>
          <td>${f.parameter ?? f.header ?? '—'}</td>
          <td>${f.owasp}</td>
          <td>${f.cwe}</td>
          <td style="font-size:12px">${f.evidence ?? ''}</td>
        </tr>
        <tr style="background:#1a1f27">
          <td colspan="7" style="padding:12px 16px">
            <strong>Descripción:</strong> ${f.description}<br>
            <strong>Remediación:</strong><ul style="margin:6px 0 0;padding-left:20px">${rem}</ul>
          </td>
        </tr>`;
    }).join('');

    return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>VulnScan – Reporte de Seguridad</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; padding: 32px; }
  h1  { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
  h2  { font-size: 16px; font-weight: 600; color: #8b949e; border-bottom: 1px solid #30363d; padding-bottom: 8px; margin: 24px 0 14px; }
  .meta { font-size: 13px; color: #8b949e; margin-bottom: 24px; }
  .summary { display: flex; gap: 12px; margin-bottom: 28px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 14px 20px; text-align: center; min-width: 90px; }
  .card .n { font-size: 26px; font-weight: 700; }
  .card .l { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: .5px; }
  table { width: 100%; border-collapse: collapse; background: #161b22; border-radius: 8px; overflow: hidden; }
  th { background: #21262d; padding: 10px 14px; text-align: left; font-size: 11px; color: #8b949e; text-transform: uppercase; }
  td { padding: 10px 14px; border-top: 1px solid #21262d; font-size: 13px; vertical-align: top; }
  a  { color: #58a6ff; }
  .footer { margin-top: 32px; font-size: 12px; color: #8b949e; border-top: 1px solid #30363d; padding-top: 16px; }
</style>
</head>
<body>
<h1>🛡️ VulnScan – Reporte de Seguridad Web</h1>
<p class="meta">
  Objetivo: <strong>${s.url}</strong> &nbsp;·&nbsp;
  Generado: <strong>${this.generatedAt}</strong> &nbsp;·&nbsp;
  Duración: <strong>${r.duration_seconds}s</strong> &nbsp;·&nbsp;
  URLs rastreadas: <strong>${r.urls_crawled}</strong>
</p>

<h2>Resumen de Severidad</h2>
<div class="summary">
  <div class="card"><div class="n" style="color:#ff2d55">${r.severity_summary['critical'] ?? 0}</div><div class="l">Crítico</div></div>
  <div class="card"><div class="n" style="color:#ff6b35">${r.severity_summary['high'] ?? 0}</div><div class="l">Alto</div></div>
  <div class="card"><div class="n" style="color:#f0b429">${r.severity_summary['medium'] ?? 0}</div><div class="l">Medio</div></div>
  <div class="card"><div class="n" style="color:#3fb950">${r.severity_summary['low'] ?? 0}</div><div class="l">Bajo</div></div>
  <div class="card"><div class="n" style="color:#58a6ff">${r.severity_summary['info'] ?? 0}</div><div class="l">Info</div></div>
  <div class="card"><div class="n">${r.total_findings}</div><div class="l">Total</div></div>
</div>

<h2>Hallazgos Detallados (${r.total_findings})</h2>
<table>
  <thead>
    <tr>
      <th>Severidad</th><th>Vulnerabilidad</th><th>URL</th>
      <th>Parámetro</th><th>OWASP</th><th>CWE</th><th>Evidencia</th>
    </tr>
  </thead>
  <tbody>${rows}</tbody>
</table>

<div class="footer">
  Generado por VulnScan v1.0.0 – Herramienta educativa de análisis de seguridad web.
  Alineada con OWASP Top 10:2021. Solo para uso en entornos autorizados.
</div>
</body>
</html>`;
  }
}
