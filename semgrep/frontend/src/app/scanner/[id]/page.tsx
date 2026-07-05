"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, Shield, Bug, AlertTriangle, Clock, Download,
  ChevronDown, ChevronUp, ExternalLink, CheckCircle, XCircle,
  Globe, Server, Code, RefreshCw, FileText, Brain
} from "lucide-react";
import { scanApi, reportApi, type ScanResult, type Vulnerability } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { SeverityBadge } from "@/components/SeverityBadge";

function VulnCard({ vuln }: { vuln: Vulnerability }) {
  const [expanded, setExpanded] = useState(false);
  const ai = vuln.ai_analysis as Record<string, unknown> | null;
  const remediation = ai?.remediation as Record<string, unknown> | null;

  return (
    <div className={`bg-[#131b2e] border rounded-xl overflow-hidden transition-colors ${
      vuln.false_positive ? "opacity-50 border-gray-800/30" : "border-gray-800/50 hover:border-gray-700/50"
    }`}>
      <div
        className="flex items-center justify-between px-5 py-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <SeverityBadge severity={vuln.severity} />
          <div className="min-w-0">
            <div className="text-white font-medium text-sm truncate">{vuln.title}</div>
            <div className="text-gray-500 text-xs mt-0.5 truncate">{vuln.endpoint}</div>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0 ml-3">
          {vuln.cwe_id && (
            <span className="text-xs text-gray-600 border border-gray-800 px-2 py-0.5 rounded hidden sm:block">
              {vuln.cwe_id}
            </span>
          )}
          {vuln.cvss_score && (
            <span className={`text-xs font-bold ${vuln.cvss_score >= 9 ? "text-red-400" : vuln.cvss_score >= 7 ? "text-orange-400" : "text-yellow-400"}`}>
              CVSS {vuln.cvss_score.toFixed(1)}
            </span>
          )}
          {vuln.false_positive && (
            <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">FP</span>
          )}
          {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-800/50 px-5 py-4 space-y-4">
          {/* Description */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Descripción</h4>
            <p className="text-sm text-gray-300">{vuln.description}</p>
          </div>

          {/* Technical details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {vuln.endpoint && (
              <div className="bg-[#0a0f1e] rounded-lg p-3">
                <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1.5">Endpoint</h4>
                <code className="text-xs text-blue-400 break-all">{vuln.endpoint}</code>
              </div>
            )}
            {vuln.payload && (
              <div className="bg-[#0a0f1e] rounded-lg p-3">
                <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1.5">Payload</h4>
                <code className="text-xs text-red-400 break-all">{vuln.payload}</code>
              </div>
            )}
          </div>

          {vuln.evidence && (
            <div className="bg-[#0a0f1e] rounded-lg p-3">
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1.5">Evidencia</h4>
              <pre className="text-xs text-yellow-300 whitespace-pre-wrap break-all">{vuln.evidence}</pre>
            </div>
          )}

          {vuln.risk && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Riesgo</h4>
              <p className="text-sm text-orange-300">{vuln.risk}</p>
            </div>
          )}

          {/* AI Analysis */}
          {ai && (
            <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/10 border border-blue-800/30 rounded-lg p-4">
              <h4 className="text-xs font-semibold text-blue-400 uppercase mb-3 flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5" />
                Análisis IA
              </h4>

              {ai.risk_explanation && (
                <p className="text-sm text-gray-300 mb-3">{ai.risk_explanation as string}</p>
              )}

              {remediation && (
                <>
                  {(remediation.immediate as string[])?.length > 0 && (
                    <div className="mb-3">
                      <h5 className="text-xs font-medium text-gray-400 mb-2">Acciones Inmediatas</h5>
                      <ul className="space-y-1.5">
                        {(remediation.immediate as string[]).map((a, i) => (
                          <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                            <CheckCircle className="w-3.5 h-3.5 text-green-400 flex-shrink-0 mt-0.5" />
                            {a}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(remediation.code_fix as string) && (
                    <div>
                      <h5 className="text-xs font-medium text-gray-400 mb-2">Código Corregido</h5>
                      <pre className="bg-[#0a0f1e] rounded-lg p-3 text-xs text-green-300 whitespace-pre-wrap break-all overflow-x-auto">
                        {remediation.code_fix as string}
                      </pre>
                    </div>
                  )}
                </>
              )}

              {(ai.references as string[])?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-800/50">
                  <h5 className="text-xs font-medium text-gray-500 mb-1.5">Referencias</h5>
                  <div className="space-y-1">
                    {(ai.references as string[]).slice(0, 2).map((ref, i) => (
                      <a key={i} href={ref} target="_blank" rel="noopener noreferrer"
                        className="text-xs text-blue-400 hover:text-blue-300 block truncate">
                        {ref}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Solution */}
          {vuln.solution && !ai && (
            <div className="bg-green-900/10 border border-green-800/30 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-green-400 uppercase mb-1.5">Solución</h4>
              <p className="text-sm text-gray-300">{vuln.solution}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


export default function ScanDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user } = useAuth();
  const router = useRouter();
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [sortBy, setSortBy] = useState("severity");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await scanApi.get(Number(id));
        setScan(data);
        if (data.status === "running" || data.status === "pending") {
          const interval = setInterval(async () => {
            const updated = await scanApi.get(Number(id));
            setScan(updated);
            if (updated.status === "completed" || updated.status === "failed") {
              clearInterval(interval);
            }
          }, 3000);
          return () => clearInterval(interval);
        }
      } catch {
        router.push("/scanner");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0f1e]">
        <Navbar />
        <div className="pt-14 flex items-center justify-center h-[calc(100vh-56px)]">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 text-blue-500 mx-auto mb-3 animate-spin" />
            <p className="text-gray-400">Cargando escaneo...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!scan) return null;

  const SEVERITY_ORDER: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };

  let filteredVulns = [...(scan.vulnerabilities || [])];
  if (filter !== "all") filteredVulns = filteredVulns.filter(v => v.severity === filter);
  if (sortBy === "severity") filteredVulns.sort((a, b) => (SEVERITY_ORDER[a.severity] || 5) - (SEVERITY_ORDER[b.severity] || 5));
  else if (sortBy === "type") filteredVulns.sort((a, b) => a.vuln_type.localeCompare(b.vuln_type));

  const aiReport = scan.result_summary?.ai_report as Record<string, unknown> | undefined;

  const statusDot: Record<string, string> = {
    completed: "bg-green-400",
    running: "bg-yellow-400 animate-pulse",
    pending: "bg-gray-400 animate-pulse",
    failed: "bg-red-400",
  };

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-gray-300">
      <Navbar />
      <main className="pt-14">
        <div className="max-w-[1400px] mx-auto px-6 py-8">

          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <button onClick={() => router.push("/scanner")}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 mb-3 transition-colors">
                <ArrowLeft className="w-4 h-4" />
                Volver al Scanner
              </button>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${statusDot[scan.status] || "bg-gray-400"}`} />
                {scan.target_url}
              </h1>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span>Escaneo #{scan.id}</span>
                <span><Clock className="w-3.5 h-3.5 inline mr-1" />{new Date(scan.created_at).toLocaleString()}</span>
                {scan.scan_duration && <span>{scan.scan_duration}s duración</span>}
              </div>
            </div>
            {scan.status === "completed" && (
              <div className="flex gap-2">
                <button
                  onClick={() => reportApi.html(scan.id)}
                  className="flex items-center gap-2 text-sm text-gray-300 border border-gray-700 px-3 py-1.5 rounded-lg hover:border-gray-500 transition-colors"
                >
                  <FileText className="w-4 h-4" />HTML
                </button>
                <button
                  onClick={() => reportApi.pdf(scan.id)}
                  className="flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />PDF
                </button>
              </div>
            )}
          </div>

          {/* Running state */}
          {(scan.status === "running" || scan.status === "pending") && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-5 mb-6 flex items-center gap-3">
              <RefreshCw className="w-5 h-5 text-yellow-400 animate-spin flex-shrink-0" />
              <div>
                <p className="text-yellow-300 font-medium">Escaneo en progreso...</p>
                <p className="text-yellow-600 text-sm">Los resultados se actualizarán automáticamente.</p>
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
            {[
              { label: "Total", value: scan.total_vulns, color: "text-white" },
              { label: "Críticas", value: scan.critical_count, color: "text-red-400" },
              { label: "Altas", value: scan.high_count, color: "text-orange-400" },
              { label: "Medias", value: scan.medium_count, color: "text-yellow-400" },
              { label: "Bajas", value: scan.low_count, color: "text-blue-400" },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-4 text-center">
                <div className={`text-2xl font-bold ${color}`}>{value}</div>
                <div className="text-xs text-gray-500 mt-0.5">{label}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6">

            {/* Vulnerabilities */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-white">
                  Vulnerabilidades <span className="text-gray-500 font-normal">({filteredVulns.length})</span>
                </h2>
                <div className="flex items-center gap-2">
                  <select value={filter} onChange={e => setFilter(e.target.value)}
                    className="text-sm bg-[#131b2e] border border-gray-700 rounded-lg px-3 py-1.5 text-gray-300 focus:outline-none">
                    <option value="all">Todas</option>
                    <option value="critical">Críticas</option>
                    <option value="high">Altas</option>
                    <option value="medium">Medias</option>
                    <option value="low">Bajas</option>
                  </select>
                  <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                    className="text-sm bg-[#131b2e] border border-gray-700 rounded-lg px-3 py-1.5 text-gray-300 focus:outline-none">
                    <option value="severity">Por severidad</option>
                    <option value="type">Por tipo</option>
                  </select>
                </div>
              </div>

              <div className="space-y-3">
                {filteredVulns.length > 0 ? filteredVulns.map(v => (
                  <VulnCard key={v.id} vuln={v} />
                )) : (
                  <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-10 text-center">
                    <CheckCircle className="w-10 h-10 text-green-500 mx-auto mb-3" />
                    <p className="text-white font-medium">
                      {filter === "all" ? "No se encontraron vulnerabilidades" : `No hay vulnerabilidades ${filter}s`}
                    </p>
                    <p className="text-gray-500 text-sm mt-1">El objetivo parece estar bien configurado.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Side panel */}
            <div className="space-y-4">

              {/* AI Report */}
              {aiReport && (
                <div className="bg-[#131b2e] border border-blue-800/30 rounded-xl p-5">
                  <h3 className="font-medium text-white mb-3 flex items-center gap-2">
                    <Brain className="w-4 h-4 text-blue-400" />
                    Reporte IA
                  </h3>
                  {aiReport.risk_level && (
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-sm text-gray-400">Nivel de riesgo:</span>
                      <span className={`text-sm font-bold ${
                        aiReport.risk_level === "CRÍTICO" ? "text-red-400" :
                        aiReport.risk_level === "ALTO" ? "text-orange-400" :
                        aiReport.risk_level === "MEDIO" ? "text-yellow-400" : "text-blue-400"
                      }`}>{aiReport.risk_level as string}</span>
                    </div>
                  )}
                  {aiReport.risk_score !== undefined && (
                    <div className="mb-3">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Puntuación de riesgo</span>
                        <span>{aiReport.risk_score as number}/100</span>
                      </div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            (aiReport.risk_score as number) >= 75 ? "bg-red-500" :
                            (aiReport.risk_score as number) >= 50 ? "bg-orange-500" :
                            (aiReport.risk_score as number) >= 25 ? "bg-yellow-500" : "bg-blue-500"
                          }`}
                          style={{ width: `${aiReport.risk_score as number}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {aiReport.executive_summary && (
                    <p className="text-sm text-gray-400 leading-relaxed">{(aiReport.executive_summary as string).substring(0, 300)}...</p>
                  )}
                  {(aiReport.immediate_actions as string[])?.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-800/50">
                      <h4 className="text-xs font-medium text-gray-500 mb-2">Acciones urgentes</h4>
                      <ul className="space-y-1">
                        {(aiReport.immediate_actions as string[]).slice(0, 3).map((a, i) => (
                          <li key={i} className="text-xs text-gray-300 flex items-start gap-1.5">
                            <span className="text-red-400 flex-shrink-0">→</span>
                            {a}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Technologies */}
              {scan.technologies && Object.values(scan.technologies).some(v => v.length > 0) && (
                <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
                  <h3 className="font-medium text-white mb-3 flex items-center gap-2">
                    <Server className="w-4 h-4 text-green-400" />
                    Tecnologías detectadas
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(scan.technologies).filter(([, v]) => v.length > 0).map(([cat, items]) => (
                      <div key={cat}>
                        <div className="text-xs text-gray-500 mb-1 capitalize">{cat}</div>
                        <div className="flex flex-wrap gap-1">
                          {items.map(item => (
                            <span key={item} className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded">
                              {item}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Crawled URLs */}
              {scan.crawled_urls && scan.crawled_urls.length > 0 && (
                <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
                  <h3 className="font-medium text-white mb-3 flex items-center gap-2">
                    <Globe className="w-4 h-4 text-purple-400" />
                    URLs descubiertas ({scan.crawled_urls.length})
                  </h3>
                  <div className="space-y-1 max-h-[200px] overflow-y-auto">
                    {scan.crawled_urls.slice(0, 20).map((url, i) => (
                      <div key={i} className="text-xs text-gray-400 truncate hover:text-gray-300">
                        {url}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
