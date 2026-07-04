"use client";

import {
  Activity,
  BarChart3,
  Clock,
  Download,
  KeyRound,
  LogOut,
  Printer,
  RefreshCw,
  ScanLine,
  ShieldAlert,
  ShieldCheck,
  UserCog
} from "lucide-react";
import { signOut } from "next-auth/react";
import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip
} from "chart.js";

import { API_URL } from "@/lib/env";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

type ScanStatus = "pending" | "running" | "completed" | "failed";

type Scan = {
  id: number;
  target_url: string;
  status: ScanStatus;
  modules: string[];
  depth: number;
  timeout: number;
  progress: number;
  risk_score: number;
  ai_summary: string | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  vulnerability_count: number;
};

type Vulnerability = {
  id: number;
  module: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  description: string;
  evidence: string | null;
  remediation: string;
  url: string;
  parameter: string | null;
};

type ScanDetail = Scan & {
  vulnerabilities: Vulnerability[];
};

type Stats = {
  total_scans: number;
  completed_scans: number;
  running_scans: number;
  total_vulnerabilities: number;
  by_severity: Record<string, number>;
  by_module: Record<string, number>;
};

const MODULES = [
  { id: "xss", label: "XSS" },
  { id: "sqli", label: "SQLi" },
  { id: "headers", label: "Headers" },
  { id: "csrf", label: "CSRF" },
  { id: "open_redirect", label: "Open redirect" },
  { id: "info_disclosure", label: "Info disclosure" }
];

const EMPTY_STATS: Stats = {
  total_scans: 0,
  completed_scans: 0,
  running_scans: 0,
  total_vulnerabilities: 0,
  by_severity: {},
  by_module: {}
};

export function DashboardClient({
  accessToken,
  username,
  isAdmin
}: {
  accessToken: string;
  username: string;
  isAdmin: boolean;
}) {
  const [targetUrl, setTargetUrl] = useState("https://example.com/");
  const [selectedModules, setSelectedModules] = useState(MODULES.map((module) => module.id));
  const [depth, setDepth] = useState(1);
  const [timeout, setTimeoutValue] = useState(10);
  const [scans, setScans] = useState<Scan[]>([]);
  const [stats, setStats] = useState<Stats>(EMPTY_STATS);
  const [selectedScan, setSelectedScan] = useState<ScanDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");

  const apiFetch = useCallback(async <T,>(path: string, init?: RequestInit): Promise<T> => {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
        ...(init?.headers ?? {})
      }
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail ?? `Error HTTP ${response.status}`);
    }
    return (await response.json()) as T;
  }, [accessToken]);

  const loadData = useCallback(async (keepSelection = true, selectedScanId?: number | null) => {
    const [scanList, statData] = await Promise.all([
      apiFetch<Scan[]>("/api/scans"),
      apiFetch<Stats>("/api/stats")
    ]);
    setScans(scanList);
    setStats(statData);

    if (keepSelection && selectedScanId) {
      const updated = scanList.find((scan) => scan.id === selectedScanId);
      if (updated) {
        const detail = await apiFetch<ScanDetail>(`/api/scans/${updated.id}`);
        setSelectedScan(detail);
      }
    } else if (!selectedScanId && scanList.length > 0) {
      const detail = await apiFetch<ScanDetail>(`/api/scans/${scanList[0].id}`);
      setSelectedScan(detail);
    }
  }, [apiFetch]);

  useEffect(() => {
    loadData(false, null).catch((loadError) => setError(loadError.message));
  }, [loadData]);

  useEffect(() => {
    const hasRunning = scans.some((scan) => scan.status === "running" || scan.status === "pending");
    if (!hasRunning) {
      return;
    }
    const timer = window.setInterval(() => {
      loadData(true, selectedScan?.id ?? null).catch((loadError) => setError(loadError.message));
    }, 4000);
    return () => window.clearInterval(timer);
  }, [loadData, scans, selectedScan?.id]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setFeedback("");

    try {
      const created = await apiFetch<Scan>("/api/scans", {
        method: "POST",
        body: JSON.stringify({
          target_url: targetUrl,
          modules: selectedModules,
          depth,
          timeout
        })
      });
      setFeedback(`Escaneo #${created.id} iniciado.`);
      await loadData(false, null);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "No se pudo iniciar el escaneo.");
    } finally {
      setLoading(false);
    }
  }

  async function openScan(scanId: number) {
    setError("");
    const detail = await apiFetch<ScanDetail>(`/api/scans/${scanId}`);
    setSelectedScan(detail);
  }

  function toggleModule(moduleId: string) {
    setSelectedModules((current) =>
      current.includes(moduleId)
        ? current.filter((item) => item !== moduleId)
        : [...current, moduleId]
    );
  }

  function exportToJson(scan: ScanDetail) {
    try {
      const blob = new Blob([JSON.stringify(scan, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `vulnscan-report-${scan.id}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError("No se pudo exportar a JSON.");
    }
  }

  function printReport() {
    window.print();
  }

  const severityChart = useMemo(() => {
    const labels = ["critical", "high", "medium", "low", "info"];
    return {
      labels: ["Critica", "Alta", "Media", "Baja", "Info"],
      datasets: [
        {
          label: "Hallazgos",
          data: labels.map((label) => stats.by_severity[label] ?? 0),
          backgroundColor: ["#b91c1c", "#dc2626", "#b45309", "#0f766e", "#2563eb"],
          borderRadius: 6
        }
      ]
    };
  }, [stats.by_severity]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={22} aria-hidden />
          </div>
          <div>
            <h1>Web Vulnerability Scanner</h1>
            <p>{username}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link className="button secondary" href="/api-keys">
            <KeyRound size={17} aria-hidden />
            API Keys
          </Link>
          {isAdmin ? (
            <Link className="button secondary" href="/admin">
              <UserCog size={17} aria-hidden />
              Admin
            </Link>
          ) : null}
          <button className="button secondary" type="button" onClick={() => loadData(true, selectedScan?.id ?? null)}>
            <RefreshCw size={17} aria-hidden />
            Actualizar
          </button>
          <button className="button danger" type="button" onClick={() => signOut({ callbackUrl: "/login" })}>
            <LogOut size={17} aria-hidden />
            Salir
          </button>
        </div>
      </header>

      <div className="main-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Nuevo escaneo</h2>
              <p>Ejecuta modulos OWASP sobre una URL autorizada.</p>
            </div>
            <ScanLine size={21} aria-hidden />
          </div>
          <div className="panel-body">
            <form className="scan-form" onSubmit={handleSubmit}>
              {error ? <div className="error-box">{error}</div> : null}
              {feedback ? <div className="success-box">{feedback}</div> : null}
              <div className="field">
                <label htmlFor="target">URL objetivo</label>
                <input
                  id="target"
                  type="url"
                  value={targetUrl}
                  onChange={(event) => setTargetUrl(event.target.value)}
                  placeholder="https://dominio.com/"
                  required
                />
              </div>
              <div className="field">
                <label>Modulos</label>
                <div className="modules-grid">
                  {MODULES.map((module) => (
                    <label className="module-toggle" key={module.id}>
                      <input
                        type="checkbox"
                        checked={selectedModules.includes(module.id)}
                        onChange={() => toggleModule(module.id)}
                      />
                      {module.label}
                    </label>
                  ))}
                </div>
              </div>
              <div className="form-row">
                <div className="field">
                  <label htmlFor="depth">Profundidad</label>
                  <select id="depth" value={depth} onChange={(event) => setDepth(Number(event.target.value))}>
                    <option value={0}>0 niveles</option>
                    <option value={1}>1 nivel</option>
                    <option value={2}>2 niveles</option>
                    <option value={3}>3 niveles</option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="timeout">Timeout</label>
                  <select id="timeout" value={timeout} onChange={(event) => setTimeoutValue(Number(event.target.value))}>
                    <option value={5}>5 s</option>
                    <option value={10}>10 s</option>
                    <option value={20}>20 s</option>
                    <option value={30}>30 s</option>
                  </select>
                </div>
              </div>
              <button className="button primary" type="submit" disabled={loading || selectedModules.length === 0}>
                <Activity size={18} aria-hidden />
                {loading ? "Iniciando..." : "Iniciar escaneo"}
              </button>
            </form>
          </div>
        </section>

        <section className="content-stack">
          <div className="stats-grid">
            <div className="stat">
              <span>Escaneos</span>
              <strong>{stats.total_scans}</strong>
            </div>
            <div className="stat">
              <span>Completados</span>
              <strong>{stats.completed_scans}</strong>
            </div>
            <div className="stat">
              <span>En curso</span>
              <strong>{stats.running_scans}</strong>
            </div>
            <div className="stat">
              <span>Hallazgos</span>
              <strong>{stats.total_vulnerabilities}</strong>
            </div>
          </div>

          <div className="dashboard-split">
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>Historial</h2>
                  <p>Ultimos 50 escaneos de tu cuenta.</p>
                </div>
                <Clock size={20} aria-hidden />
              </div>
              <div className="table-wrap">
                <table className="scan-table">
                  <thead>
                    <tr>
                      <th>Objetivo</th>
                      <th>Estado</th>
                      <th>Riesgo</th>
                      <th>Hallazgos</th>
                      <th>Progreso</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scans.map((scan) => (
                      <tr key={scan.id} onClick={() => openScan(scan.id)}>
                        <td className="url-cell">{scan.target_url}</td>
                        <td>
                          <span className={`badge ${scan.status}`}>{scan.status}</span>
                        </td>
                        <td>{scan.risk_score}</td>
                        <td>{scan.vulnerability_count}</td>
                        <td>
                          <div className="progress" aria-label={`${scan.progress}%`}>
                            <span style={{ width: `${scan.progress}%` }} />
                          </div>
                        </td>
                      </tr>
                    ))}
                    {scans.length === 0 ? (
                      <tr>
                        <td colSpan={5}>No hay escaneos registrados.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>Severidad</h2>
                  <p>Distribucion de vulnerabilidades.</p>
                </div>
                <BarChart3 size={20} aria-hidden />
              </div>
              <div className="panel-body">
                <div className="chart-box">
                  <Bar
                    data={severityChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
                    }}
                  />
                </div>
              </div>
            </section>
          </div>

          <section className="panel report-panel">
            <div className="panel-header">
              <div>
                <h2>Reporte</h2>
                <p>{selectedScan ? `Escaneo #${selectedScan.id}` : "Selecciona un escaneo del historial."}</p>
              </div>
              {selectedScan ? (
                <div className="report-actions" style={{ display: "flex", gap: 8 }}>
                  <button
                    className="button secondary sm"
                    type="button"
                    onClick={() => exportToJson(selectedScan)}
                    title="Exportar Reporte a JSON"
                    style={{ padding: "4px 8px", minHeight: "32px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "4px" }}
                  >
                    <Download size={14} aria-hidden />
                    JSON
                  </button>
                  <button
                    className="button secondary sm"
                    type="button"
                    onClick={printReport}
                    title="Imprimir / Exportar a PDF"
                    style={{ padding: "4px 8px", minHeight: "32px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "4px" }}
                  >
                    <Printer size={14} aria-hidden />
                    PDF
                  </button>
                </div>
              ) : null}
              <ShieldAlert size={20} className="report-icon-hide" aria-hidden />
            </div>
            <div className="panel-body">
              {selectedScan ? (
                <div className="content-stack">
                  <div className="print-only-header">
                    <h1>Informe de Vulnerabilidades Web</h1>
                    <div className="print-meta-grid">
                      <div><strong>Objetivo:</strong> {selectedScan.target_url}</div>
                      <div><strong>ID Escaneo:</strong> #{selectedScan.id}</div>
                      <div><strong>Riesgo Promedio:</strong> {selectedScan.risk_score}/100</div>
                      <div><strong>Fecha de Inicio:</strong> {new Date(selectedScan.created_at).toLocaleString("es-PE")}</div>
                      <div><strong>Módulos Seleccionados:</strong> {selectedScan.modules.join(", ")}</div>
                    </div>
                  </div>
                  {selectedScan.error_message ? <div className="error-box">{selectedScan.error_message}</div> : null}
                  {selectedScan.ai_summary ? (
                    <div className="summary-text">
                      <div className="summary-title-print"><strong>Resumen Ejecutivo:</strong></div>
                      {selectedScan.ai_summary}
                    </div>
                  ) : null}
                  <div className="detail-list">
                    {selectedScan.vulnerabilities.map((finding) => (
                      <article className="finding" key={finding.id}>
                        <div style={{ display: "flex", gap: 8, alignItems: "center", justifyContent: "space-between" }}>
                          <h3>{finding.title}</h3>
                          <span className={`badge ${finding.severity}`}>{finding.severity}</span>
                        </div>
                        <p>{finding.description}</p>
                        <p>
                          <strong>Modulo:</strong> {finding.module}
                          {finding.parameter ? ` | Parametro: ${finding.parameter}` : ""}
                        </p>
                        <p>
                          <strong>URL:</strong> {finding.url}
                        </p>
                        {finding.evidence ? <code>{finding.evidence}</code> : null}
                        <p>
                          <strong>Remediacion:</strong> {finding.remediation}
                        </p>
                      </article>
                    ))}
                    {selectedScan.vulnerabilities.length === 0 ? (
                      <p className="muted">No hay hallazgos para este escaneo.</p>
                    ) : null}
                  </div>
                </div>
              ) : (
                <p className="muted">Todavia no se ha seleccionado un reporte.</p>
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
