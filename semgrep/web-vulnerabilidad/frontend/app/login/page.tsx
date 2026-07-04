"use client";

import { signIn, useSession } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { LogIn, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { status } = useSession();
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
    const response = await signIn("credentials", {
      email,
      password,
      redirect: false
    });
    setLoading(false);

    if (response?.error) {
      setError("Credenciales invalidas o backend no disponible.");
      return;
    }
    router.replace("/dashboard");
  }

  return (
    <main className="auth-shell">
      <section className="auth-visual">
        <ShieldCheck size={54} aria-hidden />
        <h1>Web Vulnerability Scanner</h1>
        <p>Inicia sesion para lanzar auditorias web, revisar hallazgos OWASP y consultar reportes con contexto automatico.</p>
      </section>
      <section className="auth-panel">
        <form className="auth-form" onSubmit={handleSubmit}>
          <header>
            <h2>Entrar</h2>
            <p>Usa tu cuenta para acceder al panel de escaneos.</p>
          </header>
          {error ? <div className="error-box">{error}</div> : null}
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
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <button className="button primary" type="submit" disabled={loading}>
            <LogIn size={18} aria-hidden />
            {loading ? "Validando..." : "Entrar"}
          </button>
          <Link className="button secondary" href="/register">
            Crear cuenta
          </Link>
        </form>
      </section>
    </main>
  );
}

