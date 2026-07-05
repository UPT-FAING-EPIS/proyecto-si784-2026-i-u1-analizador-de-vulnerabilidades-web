"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Shield, Search, Sparkles, Brain } from "lucide-react";
import { AISolutionGenerator } from "@/components/AISolutionGenerator";
import { Navbar } from "@/components/Navbar";
import { useAuth } from "@/hooks/useAuth";

const COMMON_VULNS = [
  "SQL Injection",
  "Cross-Site Scripting (XSS)",
  "Cross-Site Request Forgery (CSRF)",
  "Broken Authentication",
  "Sensitive Data Exposure",
  "Security Misconfiguration",
  "Insecure Deserialization",
  "Broken Access Control",
  "Server Side Request Forgery (SSRF)",
  "Remote Code Execution (RCE)",
  "Local File Inclusion (LFI)",
  "Path Traversal"
];

export default function SolutionsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [vulnType, setVulnType] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [user, authLoading, router]);

  const filteredVulns = COMMON_VULNS.filter(v => 
    v.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-gray-300">
      <Navbar />

      <main className="pt-20">
        <div className="max-w-[1400px] mx-auto px-6 py-8">
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Sparkles className="w-8 h-8 text-blue-500" />
                Soluciones con IA
              </h1>
              <p className="text-gray-400 mt-2">
                Genera guías de remediación detalladas y código seguro para cualquier vulnerabilidad.
              </p>
            </div>
          </div>

          {!vulnType ? (
            <div className="space-y-8">
              {/* Search Section */}
              <div className="bg-[#131b2e] border border-gray-800/50 rounded-2xl p-8 text-center max-w-2xl mx-auto shadow-xl shadow-black/20">
                <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Brain className="w-8 h-8 text-blue-500" />
                </div>
                <h2 className="text-xl font-bold text-white mb-4">¿Sobre qué vulnerabilidad necesitas ayuda?</h2>
                
                <div className="relative mb-6">
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Escribe el tipo de vulnerabilidad (ej: SQLi, XSS)..."
                    className="w-full bg-[#0a0f1e] border border-gray-700 rounded-xl px-12 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-all shadow-inner"
                  />
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                </div>

                <div className="flex flex-wrap justify-center gap-2">
                  {filteredVulns.slice(0, 6).map(v => (
                    <button
                      key={v}
                      onClick={() => setVulnType(v)}
                      className="px-4 py-2 bg-gray-800/50 hover:bg-gray-700 text-sm rounded-lg text-gray-300 transition-colors border border-gray-700/50"
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

              {/* Info grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    title: "Análisis Profundo",
                    desc: "La IA analiza la causa raíz y el impacto potencial de la vulnerabilidad.",
                    icon: Shield
                  },
                  {
                    title: "Código Seguro",
                    desc: "Obtén ejemplos de código corregido adaptado a tu stack tecnológico.",
                    icon: Brain
                  },
                  {
                    title: "Mejores Prácticas",
                    desc: "Recomendaciones basadas en estándares OWASP y mejores prácticas de la industria.",
                    icon: Sparkles
                  }
                ].map((item, i) => (
                  <div key={i} className="bg-[#131b2e] border border-gray-800/50 rounded-xl p-6 hover:border-blue-500/30 transition-colors">
                    <item.icon className="w-8 h-8 text-blue-500 mb-4" />
                    <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                    <p className="text-sm text-gray-400 leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div>
              <button 
                onClick={() => setVulnType("")}
                className="mb-6 flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                ← Volver al buscador
              </button>
              <AISolutionGenerator vulnerabilityType={vulnType} />
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
