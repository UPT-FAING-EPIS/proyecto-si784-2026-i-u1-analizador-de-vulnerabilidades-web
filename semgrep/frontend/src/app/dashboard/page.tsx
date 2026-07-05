"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Shield, Bug, Search, Users, AlertTriangle, TrendingUp,
  CheckCircle, Clock, Activity, RefreshCw, ExternalLink,
  Target, Zap, ChevronRight
} from "lucide-react";
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  ArcElement, Title, Tooltip, Legend, LineElement, PointElement
} from "chart.js";
import { Bar, Doughnut, Line } from "react-chartjs-2";
import { useAuth } from "@/hooks/useAuth";
import { adminApi, scanApi, type DashboardStats, type ScanListItem } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { SeverityBadge, SeverityBar } from "@/components/SeverityBadge";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement,
  Title, Tooltip, Legend, LineElement, PointElement);

const CHART_DEFAULTS = {
  plugins: { legend: { labels: { color: "#94a3b8", font: { size: 12 } } } },
  scales: {
    x: { ticks: { color: "#64748b" }, grid: { color: "rgba(51,65,85,0.3)" } },
    y: { ticks: { color: "#64748b" }, grid: { color: "rgba(51,65,85,0.3)" }, beginAtZero: true },
  },
};

function StatCard({ icon: Icon, label, value, sub, color = "blue" }: {
  icon: React.ElementType; label: string; value: string | number; sub?: string; color?: string;
}) {
  const colors: Record<string, string> = {
    blue: "text-blue-400 bg-blue-500/10",
    red: "text-red-400 bg-red-500/10",
    orange: "text-orange-400 bg-orange-500/10",
    green: "text-green-400 bg-green-500/10",
    purple: "text-purple-400 bg-purple-500/10",
  };
  return (
    <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors[color]}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-sm text-gray-400">{label}</div>
        {sub && <div className="text-xs text-gray-600 mt-0.5">{sub}</div>}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [scans, setScans] = useState<ScanListItem[]>([]);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingScans, setLoadingScans] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [user, authLoading, router]);

  const loadData = useCallback(async () => {
    setLoadingStats(true);
    setLoadingScans(true);
    try {
      const [scanData] = await Promise.allSettled([
        scanApi.list(0, 10),
      ]);
      if (scanData.status === "fulfilled") setScans(scanData.value.scans);
    } finally {
      setLoadingScans(false);
    }

    if (user?.role === "admin") {
      try {
        const data = await adminApi.dashboard();
        setStats(data);
      } catch { /* non-admin */ }
    }
    setLoadingStats(false);
    setLastRefresh(new Date());
  }, [user]);

  useEffect(() => { if (user) loadData(); }, [user, loadData]);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0a0f1e] flex items-center justify-center">
        <div className="text-center">
          <Shield className="w-12 h-12 text-blue-500 mx-auto mb-3 animate-pulse" />
          <p className="text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  // Charts data
  const vuln_by_sev = stats?.vulns_by_severity || [];
  const doughnutData = {
    labels: ["Crítico", "Alto", "Medio", "Bajo"],
    datasets: [{
      data: [
        vuln_by_sev.find(v => v.severity === "critical")?.count || 0,
        vuln_by_sev.find(v => v.severity === "high")?.count || 0,
        vuln_by_sev.find(v => v.severity === "medium")?.count || 0,
        vuln_by_sev.find(v => v.severity === "low")?.count || 0,
      ],
      backgroundColor: ["#dc2626", "#ea580c", "#d97706", "#2563eb"],
      borderWidth: 0,
      hoverOffset: 4,
    }],
  };

  const dailyScans = stats?.daily_scans || [];
  const lineData = {
    labels: dailyScans.map(d => d.date),
    datasets: [{
      label: "Escaneos",
      data: dailyScans.map(d => d.count),
      borderColor: "#3b82f6",
      backgroundColor: "rgba(59,130,246,0.1)",
      fill: true,
      tension: 0.4,
      pointBackgroundColor: "#3b82f6",
    }],
  };

  const statusColor: Record<string, string> = {
    completed: "text-green-400",
    running: "text-yellow-400 animate-pulse",
    pending: "text-gray-400",
    failed: "text-red-400",
  };

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-gray-300">
      <Navbar />

      <main className="pt-14">
        <div className="max-w-[1400px] mx-auto px-6 py-8">

          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-white">
                Bienvenido, <span className="text-blue-400">{user?.username}</span>
              </h1>
              <p className="text-gray-400 text-sm mt-1">
                {new Date().toLocaleDateString("es-ES", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-600">
                Actualizado: {lastRefresh.toLocaleTimeString()}
              </span>
              <button
                onClick={loadData}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white border border-gray-800 px-3 py-1.5 rounded-lg hover:border-gray-600 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Actualizar
              </button>
              <Link
                href="/scanner"
                className="flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 px-4 py-1.5 rounded-lg transition-colors"
              >
                <Search className="w-4 h-4" />
                Nuevo Escaneo
              </Link>
            </div>
          </div>

          {/* Stats - Admin only */}
          {user?.role === "admin" && stats && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <StatCard icon={Users} label="Usuarios totales" value={stats.stats.total_users} color="purple" />
              <StatCard icon={Search} label="Escaneos totales" value={stats.stats.total_scans} color="blue" />
              <StatCard icon={Bug} label="Vulnerabilidades" value={stats.stats.total_vulns} color="orange" />
              <StatCard icon={AlertTriangle} label="Críticas" value={stats.stats.critical_vulns} color="red" />
            </div>
          )}

          {/* Quick action */}
          {!loadingScans && scans.length === 0 && (
            <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/10 border border-blue-500/30 rounded-xl p-8 mb-8 text-center">
              <Target className="w-12 h-12 text-blue-400 mx-auto mb-3" />
              <h2 className="text-xl font-bold text-white mb-2">Comienza tu primer análisis</h2>
              <p className="text-gray-400 mb-5 max-w-md mx-auto">
                Escanea cualquier sitio web en busca de vulnerabilidades OWASP Top 10, problemas SSL, headers inseguros y más.
              </p>
              <Link
                href="/scanner"
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors"
              >
                <Zap className="w-4 h-4" />
                Iniciar Escaneo
              </Link>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">

            {/* Recent scans */}
            <div className="lg:col-span-2 bg-[#131b2e] border border-gray-800/50 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800/50">
                <h2 className="font-semibold text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-400" />
                  Escaneos Recientes
                </h2>
                <Link href="/scanner" className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
                  Ver todos <ChevronRight className="w-3 h-3" />
                </Link>
              </div>
              <div className="divide-y divide-gray-800/50">
                {loadingScans ? (
                  [...Array(4)].map((_, i) => (
                    <div key={i} className="px-5 py-4 animate-pulse">
                      <div className="h-4 bg-gray-800 rounded w-2/3 mb-2" />
                      <div className="h-3 bg-gray-800 rounded w-1/3" />
                    </div>
                  ))
                ) : scans.length > 0 ? scans.map(scan => (
                  <div key={scan.id} className="px-5 py-3.5 hover:bg-white/2 transition-colors flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-white font-medium truncate text-sm">{scan.target_url}</span>
                        <span className={`text-xs ${statusColor[scan.status] || "text-gray-400"}`}>
                          {scan.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span><Clock className="w-3 h-3 inline mr-1" />{new Date(scan.created_at).toLocaleString()}</span>
                        {scan.total_vulns > 0 && (
                          <span className="text-orange-400">{scan.total_vulns} hallazgos</span>
                        )}
                      </div>
                      {scan.total_vulns > 0 && (
                        <div className="mt-1.5">
                          <SeverityBar
                            critical={scan.critical_count}
                            high={scan.high_count}
                            medium={scan.medium_count}
                            low={scan.low_count}
                          />
                        </div>
                      )}
                    </div>
                    <Link
                      href={`/scanner/${scan.id}`}
                      className="ml-3 text-blue-400 hover:text-blue-300 flex-shrink-0"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </Link>
                  </div>
                )) : (
                  <div className="px-5 py-10 text-center text-gray-500">
                    No hay escaneos registrados.
                  </div>
                )}
              </div>
            </div>

            {/* Charts panel */}
            <div className="space-y-6">
              {user?.role === "admin" && stats && (
                <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
                  <h3 className="font-medium text-white mb-4 text-sm">Distribución por Severidad</h3>
                  <div className="h-[180px] flex items-center justify-center">
                    <Doughnut
                      data={doughnutData}
                      options={{
                        plugins: { legend: { position: "bottom", labels: { color: "#94a3b8", padding: 10, font: { size: 11 } } } },
                        cutout: "65%",
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Quick tips */}
              <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
                <h3 className="font-medium text-white mb-3 text-sm">Estado del Sistema</h3>
                <div className="space-y-2">
                  {[
                    { label: "Scanner Engine", ok: true },
                    { label: "DeepSeek AI", ok: !!process.env.NEXT_PUBLIC_AI_ENABLED },
                    { label: "Base de Datos", ok: true },
                    { label: "Reportes PDF", ok: true },
                  ].map(item => (
                    <div key={item.label} className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">{item.label}</span>
                      <span className={`flex items-center gap-1 ${item.ok ? "text-green-400" : "text-gray-600"}`}>
                        <span className={`w-2 h-2 rounded-full ${item.ok ? "bg-green-400" : "bg-gray-700"}`} />
                        {item.ok ? "Online" : "N/A"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Activity chart - admin */}
          {user?.role === "admin" && stats && dailyScans.length > 0 && (
            <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-5">
              <h3 className="font-medium text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                Actividad de Escaneos (últimos 7 días)
              </h3>
              <div className="h-[200px]">
                <Line data={lineData} options={{ ...CHART_DEFAULTS, responsive: true, maintainAspectRatio: false }} />
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
