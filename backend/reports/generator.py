"""
Report Generator - Produces JSON and HTML vulnerability reports.
"""

import json
from datetime import datetime, timezone


class ReportGenerator:

    def generate_json(self, scan: dict) -> str:
        return json.dumps(scan, indent=2, default=str)

    def generate_html(self, scan: dict) -> str:
        results = scan.get('results', {}) or {}
        findings = results.get('findings', [])
        summary = results.get('severity_summary', {})
        target = results.get('target_url', scan.get('url', 'Unknown'))
        generated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

        severity_colors = {
            'critical': '#ff2d55', 'high': '#ff6b35',
            'medium': '#ffc107', 'low': '#17a2b8', 'info': '#6c757d'
        }

        findings_html = ''
        for f in findings:
            sev = f.get('severity', 'info')
            color = severity_colors.get(sev, '#6c757d')
            rem = ''.join(f'<li>{r}</li>' for r in f.get('remediation', []))
            refs = ''.join(
                f'<li><a href="{r}" target="_blank">{r}</a></li>'
                for r in f.get('references', [])
            )
            payload_row = f'<tr><th>Payload</th><td><code>{f["payload"]}</code></td></tr>' if f.get('payload') else ''
            param_row = f'<tr><th>Parameter</th><td><code>{f["parameter"]}</code></td></tr>' if f.get('parameter') else ''

            findings_html += f"""
            <div class="finding" style="border-left:4px solid {color}">
              <div class="finding-header">
                <span class="badge" style="background:{color}">{sev.upper()}</span>
                <strong>{f.get('name','')}</strong>
                <span class="tag">{f.get('owasp','')}</span>
                <span class="tag">{f.get('cwe','')}</span>
              </div>
              <table class="details-table">
                <tr><th>URL</th><td><code>{f.get('url','')}</code></td></tr>
                {param_row}
                {payload_row}
                <tr><th>Evidence</th><td><code>{f.get('evidence','')}</code></td></tr>
                <tr><th>CVSS Range</th><td>{f.get('cvss_range','')}</td></tr>
              </table>
              <p>{f.get('description','')}</p>
              <strong>Remediation:</strong><ul>{rem}</ul>
              {'<strong>References:</strong><ul>' + refs + '</ul>' if refs else ''}
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>VulnScan Report – {target}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background:#0d1117; color:#c9d1d9; margin:0; padding:2rem }}
  h1 {{ color:#58a6ff }} h2 {{ color:#8b949e; border-bottom:1px solid #30363d; padding-bottom:.5rem }}
  .summary {{ display:flex; gap:1rem; flex-wrap:wrap; margin:1.5rem 0 }}
  .card {{ background:#161b22; border-radius:8px; padding:1rem 1.5rem; min-width:100px; text-align:center }}
  .card .count {{ font-size:2rem; font-weight:700 }}
  .finding {{ background:#161b22; border-radius:6px; padding:1.2rem; margin:1rem 0 }}
  .finding-header {{ display:flex; align-items:center; gap:.6rem; flex-wrap:wrap; margin-bottom:.8rem }}
  .badge {{ color:#fff; padding:.2rem .6rem; border-radius:4px; font-size:.75rem; font-weight:700; text-transform:uppercase }}
  .tag {{ background:#21262d; border-radius:4px; padding:.2rem .5rem; font-size:.75rem; color:#8b949e }}
  .details-table {{ width:100%; border-collapse:collapse; margin:.5rem 0; font-size:.85rem }}
  .details-table th {{ text-align:left; color:#8b949e; padding:.3rem .5rem; white-space:nowrap; width:100px }}
  .details-table td {{ padding:.3rem .5rem }} code {{ background:#0d1117; border-radius:3px; padding:.1rem .3rem; word-break:break-all }}
  a {{ color:#58a6ff }} ul {{ margin:.3rem 0; padding-left:1.2rem }}
  .meta {{ color:#8b949e; font-size:.85rem }}
</style>
</head>
<body>
<h1>🛡️ VulnScan Security Report</h1>
<p class="meta">Target: <strong>{target}</strong> · Generated: {generated} · Duration: {results.get('duration_seconds',0)}s · URLs crawled: {results.get('urls_crawled',0)}</p>
<h2>Summary</h2>
<div class="summary">
  <div class="card"><div class="count" style="color:#ff2d55">{summary.get('critical',0)}</div>Critical</div>
  <div class="card"><div class="count" style="color:#ff6b35">{summary.get('high',0)}</div>High</div>
  <div class="card"><div class="count" style="color:#ffc107">{summary.get('medium',0)}</div>Medium</div>
  <div class="card"><div class="count" style="color:#17a2b8">{summary.get('low',0)}</div>Low</div>
  <div class="card"><div class="count" style="color:#6c757d">{summary.get('info',0)}</div>Info</div>
  <div class="card"><div class="count" style="color:#58a6ff">{results.get('total_findings',0)}</div>Total</div>
</div>
<h2>Findings</h2>
{findings_html if findings_html else '<p style="color:#8b949e">No vulnerabilities found.</p>'}
</body></html>"""
