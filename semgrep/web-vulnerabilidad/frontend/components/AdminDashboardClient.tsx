"use client";

import {
  ArrowLeft,
  LogOut,
  RefreshCw,
  ShieldCheck,
  Users,
  UserCog,
  Activity,
  Bug
} from "lucide-react";
import { signOut } from "next-auth/react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
} from "chart.js";

import { API_URL } from "@/lib/env";

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend);

type DailyRegistration = {
  date: string;
  count: number;
};

type AdminUser = {
  id: number;
  email: string;
  username: string;
  is_admin: boolean;
  created_at: string;
};

type AdminOverview = {
  total_users: number;
  total_admins: number;
  total_scans: number;
  total_vulnerabilities: number;
  daily_registrations: DailyRegistration[];
  recent_users: AdminUser[];
};

const EMPTY_OVERVIEW: AdminOverview = {
  total_users: 0,
  total_admins: 0,
  total_scans: 0,
  total_vulnerabilities: 0,
  daily_registrations: [],
  recent_users: []
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("es-PE", { month: "short", day: "2-digit" }).format(new Date(`${value}T00:00:00`));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("es-PE", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function AdminDashboardClient({
  accessToken,
  username
}: {
  accessToken: string;
  username: string;
}) {
  const [overview, setOverview] = useState<AdminOverview>(EMPTY_OVERVIEW);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadOverview = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/admin/overview`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`
        }
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail ?? `Error HTTP ${response.status}`);
      }
      setOverview((await response.json()) as AdminOverview);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No se pudo cargar el panel administrador.");
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  const registrationsChart = useMemo(() => {
    return {
      labels: overview.daily_registrations.map((item) => formatDate(item.date)),
      datasets: [
        {
          label: "Usuarios registrados",
          data: overview.daily_registrations.map((item) => item.count),
          borderColor: "#2563eb",
          backgroundColor: "#2563eb",
          pointBackgroundColor: "#0f766e",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8,
          showLine: false
        }
      ]
    };
  }, [overview.daily_registrations]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <UserCog size={22} aria-hidden />
          </div>
          <div>
            <h1>Panel administrador</h1>
            <p>{username}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link className="button secondary" href="/dashboard">
            <ArrowLeft size={17} aria-hidden />
            Dashboard
          </Link>
          <button className="button secondary" type="button" onClick={loadOverview} disabled={loading}>
            <RefreshCw size={17} aria-hidden />
            Actualizar
          </button>
          <button className="button danger" type="button" onClick={() => signOut({ callbackUrl: "/login" })}>
            <LogOut size={17} aria-hidden />
            Salir
          </button>
        </div>
      </header>

      <div className="admin-main">
        {error ? <div className="error-box">{error}</div> : null}
        <section className="stats-grid">
          <div className="stat">
            <span>Usuarios</span>
            <strong>{overview.total_users}</strong>
          </div>
          <div className="stat">
            <span>Administradores</span>
            <strong>{overview.total_admins}</strong>
          </div>
          <div className="stat">
            <span>Escaneos</span>
            <strong>{overview.total_scans}</strong>
          </div>
          <div className="stat">
            <span>Hallazgos</span>
            <strong>{overview.total_vulnerabilities}</strong>
          </div>
        </section>

        <section className="admin-grid">
          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Registros diarios</h2>
                <p>Usuarios creados por dia durante los ultimos 14 dias.</p>
              </div>
              <Activity size={20} aria-hidden />
            </div>
            <div className="panel-body">
              <div className="chart-box admin-chart">
                <Line
                  data={registrationsChart}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      y: { beginAtZero: true, ticks: { precision: 0 } }
                    }
                  }}
                />
              </div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Usuarios recientes</h2>
                <p>Ultimas cuentas creadas en el sistema.</p>
              </div>
              <Users size={20} aria-hidden />
            </div>
            <div className="table-wrap">
              <table className="scan-table">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Registro</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.recent_users.map((user) => (
                    <tr key={user.id}>
                      <td>
                        <strong>{user.username}</strong>
                        <p className="muted">{user.email}</p>
                      </td>
                      <td>
                        <span className={`badge ${user.is_admin ? "info" : "low"}`}>
                          {user.is_admin ? "Admin" : "Usuario"}
                        </span>
                      </td>
                      <td>{formatDateTime(user.created_at)}</td>
                    </tr>
                  ))}
                  {overview.recent_users.length === 0 ? (
                    <tr>
                      <td colSpan={3}>No hay usuarios registrados.</td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </section>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Estado del sistema</h2>
              <p>Resumen operativo visible solo para administradores.</p>
            </div>
            <ShieldCheck size={20} aria-hidden />
          </div>
          <div className="panel-body admin-status">
            <div>
              <Bug size={18} aria-hidden />
              <span>API, autenticacion y reportes conectados a la base MySQL remota.</span>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
