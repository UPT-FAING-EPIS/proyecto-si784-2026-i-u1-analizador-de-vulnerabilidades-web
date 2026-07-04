"use client";

import {
  ArrowLeft,
  Copy,
  KeyRound,
  LogOut,
  Plus,
  RefreshCw,
  Trash2
} from "lucide-react";
import { signOut } from "next-auth/react";
import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { API_URL } from "@/lib/env";

type ApiKey = {
  id: number;
  name: string;
  key_prefix: string;
  scopes: string[];
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
  revoked_at: string | null;
};

type CreatedApiKey = ApiKey & {
  api_key: string;
};

function formatDateTime(value: string | null) {
  if (!value) {
    return "Nunca";
  }
  return new Intl.DateTimeFormat("es-PE", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function ApiKeysClient({
  accessToken,
  username
}: {
  accessToken: string;
  username: string;
}) {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [name, setName] = useState("Integracion externa");
  const [expiresInDays, setExpiresInDays] = useState("90");
  const [createdKey, setCreatedKey] = useState("");
  const [createdKeyId, setCreatedKeyId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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

  const loadKeys = useCallback(async () => {
    setError("");
    try {
      const data = await apiFetch<ApiKey[]>("/api/api-keys");
      setKeys(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No se pudieron cargar las API keys.");
    }
  }, [apiFetch]);

  useEffect(() => {
    loadKeys();
  }, [loadKeys]);

  async function createKey(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setFeedback("");
    setCreatedKey("");
    setCreatedKeyId(null);
    setLoading(true);
    try {
      const payload = {
        name,
        expires_in_days: expiresInDays === "never" ? null : Number(expiresInDays)
      };
      const data = await apiFetch<CreatedApiKey>("/api/api-keys", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setCreatedKey(data.api_key);
      setCreatedKeyId(data.id);
      setFeedback("API key creada. Guardala ahora; no se volvera a mostrar completa.");
      await loadKeys();
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "No se pudo crear la API key.");
    } finally {
      setLoading(false);
    }
  }

  async function revokeKey(apiKeyId: number) {
    setError("");
    setFeedback("");
    try {
      await apiFetch<ApiKey>(`/api/api-keys/${apiKeyId}`, { method: "DELETE" });
      if (createdKeyId === apiKeyId) {
        setCreatedKey("");
        setCreatedKeyId(null);
      }
      setFeedback("API key revocada.");
      await loadKeys();
    } catch (revokeError) {
      setError(revokeError instanceof Error ? revokeError.message : "No se pudo revocar la API key.");
    }
  }

  async function copyCreatedKey() {
    if (!createdKey) {
      return;
    }
    await navigator.clipboard.writeText(createdKey);
    setFeedback("API key copiada.");
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <KeyRound size={22} aria-hidden />
          </div>
          <div>
            <h1>API Key management</h1>
            <p>{username}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link className="button secondary" href="/dashboard">
            <ArrowLeft size={17} aria-hidden />
            Dashboard
          </Link>
          <button className="button secondary" type="button" onClick={loadKeys}>
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
        {feedback ? <div className="success-box">{feedback}</div> : null}

        <section className="admin-grid">
          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Crear API key</h2>
                <p>Usala para que otros sistemas consuman tus servicios.</p>
              </div>
              <Plus size={20} aria-hidden />
            </div>
            <div className="panel-body">
              <form className="scan-form" onSubmit={createKey}>
                <div className="field">
                  <label htmlFor="key-name">Nombre</label>
                  <input
                    id="key-name"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    minLength={2}
                    maxLength={120}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="expires">Expiracion</label>
                  <select id="expires" value={expiresInDays} onChange={(event) => setExpiresInDays(event.target.value)}>
                    <option value="30">30 dias</option>
                    <option value="90">90 dias</option>
                    <option value="180">180 dias</option>
                    <option value="365">365 dias</option>
                    <option value="never">Sin expiracion</option>
                  </select>
                </div>
                <button className="button primary" type="submit" disabled={loading}>
                  <KeyRound size={18} aria-hidden />
                  {loading ? "Generando..." : "Generar API key"}
                </button>
              </form>

              {createdKey ? (
                <div className="key-display">
                  <div>
                    <span>Nueva API key</span>
                    <code>{createdKey}</code>
                  </div>
                  <button className="button secondary" type="button" onClick={copyCreatedKey}>
                    <Copy size={17} aria-hidden />
                    Copiar
                  </button>
                </div>
              ) : null}
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Uso externo</h2>
                <p>Ejemplos para integrar otros sistemas.</p>
              </div>
              <KeyRound size={20} aria-hidden />
            </div>
            <div className="panel-body">
              <div className="endpoint-list">
                <code>{'curl -H "X-API-Key: TU_API_KEY" http://localhost:8000/api/integrations/stats'}</code>
                <code>{'curl -H "Authorization: Bearer TU_API_KEY" http://localhost:8000/api/integrations/scans'}</code>
                <code>{'POST http://localhost:8000/api/integrations/scans'}</code>
              </div>
            </div>
          </section>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>API keys</h2>
              <p>Solo se guarda el hash; las claves completas no se pueden recuperar.</p>
            </div>
            <KeyRound size={20} aria-hidden />
          </div>
          <div className="table-wrap">
            <table className="scan-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Prefijo</th>
                  <th>Estado</th>
                  <th>Creacion</th>
                  <th>Ultimo uso</th>
                  <th>Expira</th>
                  <th>Accion</th>
                </tr>
              </thead>
              <tbody>
                {keys.map((apiKey) => (
                  <tr key={apiKey.id}>
                    <td>{apiKey.name}</td>
                    <td>
                      <code>{apiKey.key_prefix}...</code>
                    </td>
                    <td>
                      <span className={`badge ${apiKey.is_active ? "low" : "failed"}`}>
                        {apiKey.is_active ? "Activa" : "Revocada"}
                      </span>
                    </td>
                    <td>{formatDateTime(apiKey.created_at)}</td>
                    <td>{formatDateTime(apiKey.last_used_at)}</td>
                    <td>{apiKey.expires_at ? formatDateTime(apiKey.expires_at) : "No expira"}</td>
                    <td>
                      <button
                        className="button danger"
                        type="button"
                        disabled={!apiKey.is_active}
                        onClick={() => revokeKey(apiKey.id)}
                        title="Revocar API key"
                      >
                        <Trash2 size={16} aria-hidden />
                      </button>
                    </td>
                  </tr>
                ))}
                {keys.length === 0 ? (
                  <tr>
                    <td colSpan={7}>No hay API keys creadas.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
