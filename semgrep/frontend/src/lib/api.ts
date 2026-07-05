/**
 * Cliente API centralizado para VulnScan Pro.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: "admin" | "analyst" | "user";
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface Vulnerability {
  id: number;
  vuln_type: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  description: string;
  endpoint: string;
  payload: string;
  evidence: string;
  risk: string;
  solution: string;
  ai_analysis: Record<string, unknown> | null;
  cwe_id: string | null;
  cvss_score: number | null;
  false_positive: boolean;
}

export interface ScanResult {
  id: number;
  target_url: string;
  status: "pending" | "running" | "completed" | "failed";
  modules: string[];
  total_vulns: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  technologies: Record<string, string[]>;
  crawled_urls: string[];
  scan_duration: number | null;
  result_summary: { ai_report?: Record<string, unknown>; counts?: Record<string, number> };
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  vulnerabilities: Vulnerability[];
}

export interface ScanListItem {
  id: number;
  target_url: string;
  status: string;
  total_vulns: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  scan_duration: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface DashboardStats {
  stats: {
    total_users: number;
    total_scans: number;
    total_vulns: number;
    critical_vulns: number;
  };
  recent_scans: Array<{ id: number; url: string; status: string; total_vulns: number; created_at: string }>;
  recent_activity: Array<{ id: number; action: string; user_id: number; ip: string; success: boolean; created_at: string }>;
  daily_scans: Array<{ date: string; count: number }>;
  vulns_by_severity: Array<{ severity: string; count: number }>;
}

export interface AISolution {
  success?: boolean;
  title?: string;
  severity?: string;
  cwe_id?: string;
  description?: string;
  impact?: string;
  vulnerable_code?: string;
  secure_code?: string;
  solution_steps?: string[];
  best_practices?: string[];
  verification?: string;
  references?: string[];
  estimated_fix_time?: string;
  source?: string;
  error?: string;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (username: string, email: string, password: string) =>
    request<{ access_token: string; username: string; user_id: number; role: string }>(
      "/api/auth/register",
      { method: "POST", body: JSON.stringify({ username, email, password }) }
    ),

  login: async (username: string, password: string) => {
    const body = new URLSearchParams({ username, password });
    const res = await fetch(`${BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Error" }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json() as Promise<{ access_token: string; username: string; user_id: number; role: string }>;
  },

  me: () => request<AuthUser>("/api/auth/me"),

  changePassword: (current_password: string, new_password: string) =>
    request<{ message: string }>("/api/auth/change-password", {
      method: "PUT",
      body: JSON.stringify({ current_password, new_password }),
    }),

  forgotPassword: (email: string) =>
    request<{ message: string; dev_token?: string }>("/api/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  resetPassword: (token: string, new_password: string) =>
    request<{ message: string }>("/api/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, new_password }),
    }),
};

// ── Scans ─────────────────────────────────────────────────────────────────────

export const scanApi = {
  start: (data: {
    url: string; modules: string[]; depth?: number;
    timeout?: number; use_ai?: boolean; stack?: string;
  }) => request<{ id: number; status: string; message: string }>(
    "/api/scans/",
    { method: "POST", body: JSON.stringify(data) }
  ),

  list: (skip = 0, limit = 20) =>
    request<{ total: number; scans: ScanListItem[] }>(`/api/scans/?skip=${skip}&limit=${limit}`),

  get: (id: number) => request<ScanResult>(`/api/scans/${id}`),

  delete: (id: number) =>
    request<{ message: string }>(`/api/scans/${id}`, { method: "DELETE" }),

  markFalsePositive: (scanId: number, vulnId: number) =>
    request<{ false_positive: boolean }>(
      `/api/scans/${scanId}/vulnerabilities/${vulnId}/false-positive`,
      { method: "PATCH" }
    ),
};

// ── Reports ───────────────────────────────────────────────────────────────────

export const reportApi = {
  json: (scanId: number) => request<Record<string, unknown>>(`/api/reports/${scanId}/json`),

  html: (scanId: number) => {
    const token = getToken();
    window.open(`${BASE_URL}/api/reports/${scanId}/html?token=${token}`, "_blank");
  },

  pdf: (scanId: number) => {
    const token = getToken();
    window.open(`${BASE_URL}/api/reports/${scanId}/pdf?token=${token}`, "_blank");
  },
};

// ── Admin ─────────────────────────────────────────────────────────────────────

export const adminApi = {
  dashboard: () => request<DashboardStats>("/api/admin/dashboard"),

  users: (skip = 0, limit = 50) =>
    request<{ total: number; users: Array<{
      id: number; username: string; email: string; role: string;
      is_active: boolean; last_login: string | null; last_login_ip: string | null;
      created_at: string; failed_attempts: number; locked: boolean;
    }> }>(`/api/admin/users?skip=${skip}&limit=${limit}`),

  updateRole: (userId: number, role: string) =>
    request<{ message: string }>(`/api/admin/users/${userId}/role`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    }),

  toggleActive: (userId: number) =>
    request<{ is_active: boolean }>(`/api/admin/users/${userId}/toggle-active`, { method: "PATCH" }),

  unlock: (userId: number) =>
    request<{ message: string }>(`/api/admin/users/${userId}/unlock`, { method: "PATCH" }),

  deleteUser: (userId: number) =>
    request<{ message: string }>(`/api/admin/users/${userId}`, { method: "DELETE" }),

  logs: (skip = 0, limit = 100) =>
    request<{ total: number; logs: Array<{
      id: number; user_id: number; action: string; ip: string;
      success: boolean; details: Record<string, unknown>; created_at: string;
    }> }>(`/api/admin/logs?skip=${skip}&limit=${limit}`),
};

// ── AI ────────────────────────────────────────────────────────────────────────

export const aiApi = {
  generateSolution: (vulnerability_type: string, target_stack = "generic") =>
    request<AISolution>("/api/solutions/generate", {
      method: "POST",
      body: JSON.stringify({ vulnerability_type, target_stack, use_cache: true }),
    }),
};

// ── Modules ───────────────────────────────────────────────────────────────────

export const modulesApi = {
  list: () => request<{ modules: Array<{ id: string; name: string; description: string }> }>("/api/modules"),
};
