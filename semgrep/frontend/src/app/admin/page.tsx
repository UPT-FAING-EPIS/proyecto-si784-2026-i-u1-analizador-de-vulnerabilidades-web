"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Users, Shield, Search, BarChart2, RefreshCw,
  Lock, Unlock, Trash2, Edit3, ChevronDown, Activity,
  UserCheck, UserX, AlertCircle
} from "lucide-react";
import { adminApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";

type AdminUser = {
  id: number; username: string; email: string; role: string;
  is_active: boolean; last_login: string | null; last_login_ip: string | null;
  created_at: string; failed_attempts: number; locked: boolean;
};

type AuditLog = {
  id: number; user_id: number; action: string; ip: string;
  success: boolean; details: Record<string, unknown>; created_at: string;
};

const ROLE_COLORS: Record<string, string> = {
  admin: "bg-red-500/20 text-red-400 border-red-500/30",
  analyst: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  user: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};

export default function AdminPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<"users" | "logs">("users");
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) {
      router.push("/dashboard");
    }
  }, [user, authLoading, router]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await adminApi.users();
      setUsers(data.users);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await adminApi.logs();
      setLogs(data.logs);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === "admin") {
      if (tab === "users") loadUsers();
      else loadLogs();
    }
  }, [user, tab]);

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      await adminApi.updateRole(userId, newRole);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error");
    }
  };

  const handleToggleActive = async (userId: number) => {
    try {
      const result = await adminApi.toggleActive(userId);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: result.is_active } : u));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error");
    }
  };

  const handleUnlock = async (userId: number) => {
    try {
      await adminApi.unlock(userId);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, locked: false, failed_attempts: 0 } : u));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error");
    }
  };

  const handleDelete = async (userId: number, username: string) => {
    if (!confirm(`¿Eliminar usuario ${username}? Esta acción no se puede deshacer.`)) return;
    try {
      await adminApi.deleteUser(userId);
      setUsers(prev => prev.filter(u => u.id !== userId));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error");
    }
  };

  if (authLoading || !user) return null;

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-gray-300">
      <Navbar />
      <main className="pt-14">
        <div className="max-w-[1400px] mx-auto px-6 py-8">

          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Shield className="w-6 h-6 text-red-400" />
                Panel de Administración
              </h1>
              <p className="text-gray-500 text-sm mt-1">Gestión de usuarios, roles y logs de auditoría</p>
            </div>
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 px-3 py-1.5 rounded-lg">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-red-400 text-sm font-medium">Zona Administrativa</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            {[
              { icon: Users, label: "Total Usuarios", value: users.length, color: "text-blue-400", bg: "bg-blue-500/10" },
              { icon: UserCheck, label: "Activos", value: users.filter(u => u.is_active).length, color: "text-green-400", bg: "bg-green-500/10" },
              { icon: UserX, label: "Bloqueados", value: users.filter(u => u.locked).length, color: "text-red-400", bg: "bg-red-500/10" },
              { icon: Activity, label: "Admins", value: users.filter(u => u.role === "admin").length, color: "text-purple-400", bg: "bg-purple-500/10" },
            ].map(({ icon: Icon, label, value, color, bg }) => (
              <div key={label} className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-4 flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${bg}`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <div>
                  <div className={`text-xl font-bold ${color}`}>{value}</div>
                  <div className="text-xs text-gray-500">{label}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-5 border-b border-gray-800/50 pb-0">
            {[
              { id: "users", label: "Usuarios", icon: Users },
              { id: "logs", label: "Logs de Auditoría", icon: Activity },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setTab(id as "users" | "logs")}
                className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
                  tab === id
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-gray-500 hover:text-gray-300"
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-5 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Users Tab */}
          {tab === "users" && (
            <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800/50">
                <h2 className="font-medium text-white">Gestión de Usuarios ({users.length})</h2>
                <button onClick={loadUsers} className="text-gray-500 hover:text-gray-300">
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-[#0a0f1e] border-b border-gray-800/50">
                    <tr>
                      {["Usuario", "Email", "Rol", "Estado", "Último Login", "IP", "Acciones"].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/30">
                    {loading ? (
                      [...Array(5)].map((_, i) => (
                        <tr key={i}>
                          {[...Array(7)].map((_, j) => (
                            <td key={j} className="px-4 py-3">
                              <div className="h-4 bg-gray-800 rounded animate-pulse" />
                            </td>
                          ))}
                        </tr>
                      ))
                    ) : users.map(u => (
                      <tr key={u.id} className="hover:bg-white/2 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-medium text-white">{u.username}</div>
                          <div className="text-xs text-gray-600">#{u.id}</div>
                        </td>
                        <td className="px-4 py-3 text-gray-400">{u.email}</td>
                        <td className="px-4 py-3">
                          {u.id === user.id ? (
                            <span className={`text-xs px-2 py-0.5 rounded-full border ${ROLE_COLORS[u.role]}`}>
                              {u.role}
                            </span>
                          ) : (
                            <select
                              value={u.role}
                              onChange={e => handleRoleChange(u.id, e.target.value)}
                              className={`text-xs bg-transparent border rounded-full px-2 py-0.5 focus:outline-none cursor-pointer ${ROLE_COLORS[u.role]}`}
                            >
                              <option value="admin">admin</option>
                              <option value="analyst">analyst</option>
                              <option value="user">user</option>
                            </select>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className={`flex items-center gap-1 text-xs ${u.is_active ? "text-green-400" : "text-red-400"}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? "bg-green-400" : "bg-red-400"}`} />
                              {u.is_active ? "Activo" : "Inactivo"}
                            </span>
                            {u.locked && (
                              <span className="text-xs text-orange-400 bg-orange-500/10 border border-orange-500/30 px-1.5 py-0.5 rounded">
                                Bloqueado
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-500 text-xs">
                          {u.last_login ? new Date(u.last_login).toLocaleString() : "Nunca"}
                        </td>
                        <td className="px-4 py-3 text-gray-600 text-xs">{u.last_login_ip || "—"}</td>
                        <td className="px-4 py-3">
                          {u.id !== user.id && (
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleToggleActive(u.id)}
                                className={`p-1.5 rounded-lg transition-colors ${
                                  u.is_active
                                    ? "text-gray-500 hover:text-red-400 hover:bg-red-500/10"
                                    : "text-gray-500 hover:text-green-400 hover:bg-green-500/10"
                                }`}
                                title={u.is_active ? "Desactivar" : "Activar"}
                              >
                                {u.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                              </button>
                              {u.locked && (
                                <button
                                  onClick={() => handleUnlock(u.id)}
                                  className="p-1.5 rounded-lg text-gray-500 hover:text-green-400 hover:bg-green-500/10 transition-colors"
                                  title="Desbloquear"
                                >
                                  <Unlock className="w-4 h-4" />
                                </button>
                              )}
                              <button
                                onClick={() => handleDelete(u.id, u.username)}
                                className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                                title="Eliminar"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Logs Tab */}
          {tab === "logs" && (
            <div className="bg-[#131b2e] border border-gray-800/50 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800/50">
                <h2 className="font-medium text-white">Logs de Auditoría ({logs.length})</h2>
                <button onClick={loadLogs} className="text-gray-500 hover:text-gray-300">
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              <div className="overflow-y-auto max-h-[600px]">
                <table className="w-full text-sm">
                  <thead className="bg-[#0a0f1e] border-b border-gray-800/50 sticky top-0">
                    <tr>
                      {["Fecha", "Usuario", "Acción", "IP", "Estado", "Detalles"].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/30">
                    {loading ? (
                      [...Array(8)].map((_, i) => (
                        <tr key={i}><td colSpan={6} className="px-4 py-3">
                          <div className="h-3 bg-gray-800 rounded animate-pulse" />
                        </td></tr>
                      ))
                    ) : logs.map(log => (
                      <tr key={log.id} className="hover:bg-white/2">
                        <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-gray-400">{log.user_id || "—"}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                            log.action.includes("login") ? "bg-blue-500/10 text-blue-400" :
                            log.action.includes("register") ? "bg-green-500/10 text-green-400" :
                            "bg-gray-500/10 text-gray-400"
                          }`}>
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-600 text-xs font-mono">{log.ip}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs ${log.success ? "text-green-400" : "text-red-400"}`}>
                            {log.success ? "✓" : "✗"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-600 text-xs">
                          {log.details ? JSON.stringify(log.details).substring(0, 50) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
