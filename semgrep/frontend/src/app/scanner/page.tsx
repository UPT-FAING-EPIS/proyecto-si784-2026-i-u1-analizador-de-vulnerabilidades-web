"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Search, Play, RotateCcw, ChevronDown, ChevronUp, Shield,
  AlertTriangle, CheckCircle, Clock, ExternalLink, Trash2,
  Download, RefreshCw, Settings, X, ChevronRight
} from "lucide-react";
import { scanApi, modulesApi, type ScanListItem } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { SeverityBadge, SeverityBar } from "@/components/SeverityBadge";

const DEFAULT_MODULES = [
  "Headers", "SSL", "XSS", "SQLi", "CSRF", "OpenRedirect",
  "LFI", "CommandInjection", "SSRF", "SensitiveFiles", "HttpMethods",
  "ErrorDisclosure", "Crawling",
];

export default function ScannerPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [user, authLoading, router]);

  const [url, setUrl] = useState("");
  const [modules, setModules] = useState<Record<string, boolean>>(
    Object.fromEntries(DEFAULT_MODULES.map(m => [m, true]))
  );
  const [depth, setDepth] = useState(2);
  const [timeout, setTimeout_] = useState(10);
  const [useAI, setUseAI] = useState(true);
  const [stack, setStack] = useState("generic");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [scanning, setScanning] = useState(false);
  const [currentScanId, setCurrentScanId] = useState<number | null>(null);
  const [scans, setScans] = useState<ScanListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadScans = async () => {
    try {
      const data = await scanApi.list(0, 50);
      setScans(data.scans);
    } catch { /* */ }
    setLoading(false);
  };

  useEffect(() => {
    loadScans();
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  const pollScan = (id: number) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const s = await scanApi.get(id);
        if (s.status === "completed" || s.status === "failed") {
          if (pollRef.current) clearInterval(pollRef.current);
          setScanning(false);
          loadScans();
        }
        setScans(prev => prev.map(sc => sc.id === id ? { ...sc, status: s.status, total_vulns: s.total_vulns } : sc));
      } catch { /* */ }
    }, 3000);
  };

  const handleScan = async () => {
    if (!url.trim()) return;
    setScanning(true);
    try {
      const activeModules = Object.entries(modules).filter(([, v]) => v).map(([k]) => k);
      const data = await scanApi.start({
        url: url.trim(), modules: activeModules, depth, timeout: timeout, use_ai: useAI, stack
      });
      setCurrentScanId(data.id);
      const newScan: ScanListItem = {
        id: data.id, target_url: url.trim(), status: "pending",
        total_vulns: 0, critical_count: 0, high_count: 0, medium_count: 0, low_count: 0,
        scan_duration: null, created_at: new Date().toISOString(), completed_at: null,
      };
      setScans(prev => [newScan, ...prev]);
      pollScan(data.id);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error iniciando escaneo");
      setScanning(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("¿Eliminar este escaneo?")) return;
    try {
      await scanApi.delete(id);
      setScans(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error");
    }
  };

  const toggleModule = (mod: string) =>
    setModules(prev => ({ ...prev, [mod]: !prev[mod] }));

  const selectAll = () => setModules(Object.fromEntries(DEFAULT_MODULES.map(m => [m, true])));
  const selectNone = () => setModules(Object.fromEntries(DEFAULT_MODULES.map(m => [m, false])));

  const statusColor: Record<string, string> = {
    completed: "bg-green-400/10 text-green-400 border-green-400/30",
    running: "bg-yellow-400/10 text-yellow-400 border-yellow-400/30",
    pending: "bg-gray-400/10 text-gray-400 border-gray-400/30",
    failed: "bg-red-400/10 text-red-400 border-red-400/30",
  };

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-gray-300">
      <Navbar />

      <main className="pt-14">
        <div className="max-w-[1400px] mx-auto px-6 py-8">

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Search className="w-6 h-6 text-blue-400" />
              Escáner de Vulnerabilidades
            </h1>
            <p className="text-gray-400 text-sm mt-1">OWASP Top 10 · SSL/TLS · Headers · SQL Injection · XSS · SSRF · LFI · y más</p>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1fr_400px] gap-6">

            {/* Scanner Panel */}
            <div className="space-y-4">

              {/* URL Input */}
              <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
                <label className="text-sm font-medium text-gray-300 mb-2 block">Objetivo</label>
                <div className="flex gap-3">
                  <div className="relative flex-1">
                    <div className={`absolute left-3 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full transition-colors ${scanning ? "bg-yellow-400 animate-pulse" : url ? "bg-green-400" : "bg-gray-600"}`} />
                    <input
                      type="text"
                      value={url}
                      onChange={e => setUrl(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && handleScan()}
                      placeholder="https://ejemplo.com"
                      className="w-full bg-[#0a0f1e] border border-gray-700 rounded-lg py-2.5 pl-8 pr-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
                    />
                    {url && (
                      <button onClick={() => setUrl("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400">
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  <button
                    onClick={handleScan}
                    disabled={scanning || !url.trim()}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-lg font-medium transition-colors whitespace-nowrap"
                  >
                    {scanning ? (
                      <><RefreshCw className="w-4 h-4 animate-spin" /> Escaneando...</>
                    ) : (
                      <><Play className="w-4 h-4 fill-current" /> Iniciar Escaneo</>
                    )}
                  </button>
                </div>
              </div>

              {/* Modules */}
              <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm font-medium text-gray-300">Módulos de Análisis</label>
                  <div className="flex gap-2 text-xs">
                    <button onClick={selectAll} className="text-blue-400 hover:text-blue-300">Todos</button>
                    <span className="text-gray-700">|</span>
                    <button onClick={selectNone} className="text-gray-500 hover:text-gray-400">Ninguno</button>
                  </div>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                  {DEFAULT_MODULES.map(mod => (
                    <label key={mod} className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors text-sm ${
                      modules[mod]
                        ? "bg-blue-600/20 border border-blue-500/40 text-blue-300"
                        : "bg-gray-800/40 border border-gray-700/40 text-gray-500 hover:border-gray-600"
                    }`}>
                      <input
                        type="checkbox"
                        checked={modules[mod] || false}
                        onChange={() => toggleModule(mod)}
                        className="hidden"
                      />
                      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${modules[mod] ? "bg-blue-400" : "bg-gray-700"}`} />
                      <span className="truncate">{mod}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Advanced options */}
              <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl overflow-hidden">
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="w-full flex items-center justify-between px-5 py-3.5 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                >
                  <span className="flex items-center gap-2"><Settings className="w-4 h-4" />Opciones Avanzadas</span>
                  {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
                {showAdvanced && (
                  <div className="px-5 pb-5 border-t border-gray-800/50 pt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                      <label className="text-xs text-gray-500 mb-1 block">Profundidad crawl</label>
                      <select value={depth} onChange={e => setDepth(Number(e.target.value))}
                        className="w-full bg-[#0a0f1e] border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none">
                        <option value={1}>1 nivel</option>
                        <option value={2}>2 niveles</option>
                        <option value={3}>3 niveles</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 mb-1 block">Timeout (seg)</label>
                      <select value={timeout} onChange={e => setTimeout_(Number(e.target.value))}
                        className="w-full bg-[#0a0f1e] border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none">
                        <option value={5}>5s</option>
                        <option value={10}>10s</option>
                        <option value={30}>30s</option>
                        <option value={60}>60s</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 mb-1 block">Stack tecnológico</label>
                      <select value={stack} onChange={e => setStack(e.target.value)}
                        className="w-full bg-[#0a0f1e] border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none">
                        <option value="generic">Genérico</option>
                        <option value="python">Python</option>
                        <option value="node">Node.js</option>
                        <option value="php">PHP</option>
                        <option value="java">Java</option>
                        <option value="dotnet">.NET</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 mb-1 block">Análisis IA</label>
                      <label className="flex items-center gap-2 mt-2 cursor-pointer">
                        <div onClick={() => setUseAI(!useAI)}
                          className={`w-10 h-5 rounded-full relative transition-colors ${useAI ? "bg-blue-600" : "bg-gray-700"}`}>
                          <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${useAI ? "translate-x-5" : "translate-x-0.5"}`} />
                        </div>
                        <span className="text-sm text-gray-400">{useAI ? "Activado" : "Desactivado"}</span>
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Scans List */}
            <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-800/50 flex items-center justify-between">
                <h2 className="font-medium text-white text-sm">Escaneos ({scans.length})</h2>
                <button onClick={loadScans} className="text-gray-500 hover:text-gray-300">
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              <div className="overflow-y-auto max-h-[600px] divide-y divide-gray-800/50">
                {loading ? (
                  [...Array(5)].map((_, i) => (
                    <div key={i} className="px-4 py-3 animate-pulse">
                      <div className="h-3 bg-gray-800 rounded w-3/4 mb-2" />
                      <div className="h-2 bg-gray-800 rounded w-1/2" />
                    </div>
                  ))
                ) : scans.length > 0 ? scans.map(scan => (
                  <div
                    key={scan.id}
                    className="px-4 py-3 hover:bg-white/2 cursor-pointer group"
                    onClick={() => router.push(`/scanner/${scan.id}`)}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <span className="text-sm text-white truncate flex-1 mr-2 font-medium">
                        {scan.target_url.replace(/^https?:\/\//, "").substring(0, 35)}
                        {scan.target_url.length > 42 ? "..." : ""}
                      </span>
                      <button
                        onClick={e => handleDelete(scan.id, e)}
                        className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 flex-shrink-0 transition-opacity"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${statusColor[scan.status] || statusColor.pending}`}>
                        {scan.status}
                      </span>
                      {scan.total_vulns > 0 && (
                        <span className="text-xs text-orange-400">{scan.total_vulns} hallazgos</span>
                      )}
                    </div>
                    {scan.total_vulns > 0 && (
                      <SeverityBar
                        critical={scan.critical_count}
                        high={scan.high_count}
                        medium={scan.medium_count}
                        low={scan.low_count}
                      />
                    )}
                    <div className="text-xs text-gray-600 mt-1">
                      {new Date(scan.created_at).toLocaleString()}
                    </div>
                  </div>
                )) : (
                  <div className="px-4 py-10 text-center text-gray-600 text-sm">
                    No hay escaneos. Inicia el primero.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
