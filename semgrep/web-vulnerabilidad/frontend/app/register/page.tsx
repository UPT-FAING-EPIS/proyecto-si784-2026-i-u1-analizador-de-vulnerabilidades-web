"use client";

import { signIn, useSession } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ShieldPlus } from "lucide-react";

import { API_URL } from "@/lib/env";

export default function RegisterPage() {
  const router = useRouter();
  const { status } = useSession();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/dashboard");
    }
  }, [router, status]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        setError(body.detail ?? "No se pudo crear la cuenta.");
        setLoading(false);
        return;
      }

      const login = await signIn("credentials", {
        email,
        password,
        redirect: false
      });
      setLoading(false);

      if (login?.error) {
        router.replace("/login");
        return;
      }
      router.replace("/dashboard");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "No se pudo crear la cuenta.");
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-visual">
        <ShieldPlus size={54} aria-hidden />
        <h1>Registro de analistas</h1>
        <p>Crea una cuenta para almacenar historial, reportes y resultados vinculados a tus escaneos autorizados.</p>
      </section>
      <section className="auth-panel">
        <form className="auth-form" onSubmit={handleSubmit}>
          <header>
            <h2>Crear cuenta</h2>
            <p>La contrasena se almacena con hash bcrypt en el backend.</p>
          </header>
          {error ? <div className="error-box">{error}</div> : null}
          <div className="field">
            <label htmlFor="username">Nombre</label>
            <input
              id="username"
              type="text"
              autoComplete="name"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              minLength={2}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="email">Correo</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Contrasena</label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </div>
          <button className="button primary" type="submit" disabled={loading}>
            <ShieldPlus size={18} aria-hidden />
            {loading ? "Creando..." : "Crear cuenta"}
          </button>
          <Link className="button secondary" href="/login">
            Ya tengo cuenta
          </Link>
        </form>
      </section>
    </main>
  );
}
