"use client";

import React, { useState } from "react";
import { Loader, AlertCircle, CheckCircle, Copy, RefreshCw } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dracula } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Solution {
  title: string;
  severity: string;
  cwe_id: string;
  description: string;
  impact: string;
  vulnerable_code: string;
  secure_code: string;
  solution_steps: string[];
  best_practices: string[];
  verification: string;
  references: string[];
  estimated_fix_time: string;
  source: string;
}

interface AISolutionGeneratorProps {
  vulnerabilityType: string;
  targetStack?: string;
}

export function AISolutionGenerator({
  vulnerabilityType,
  targetStack = "node",
}: AISolutionGeneratorProps) {
  const [loading, setLoading] = useState(false);
  const [solution, setSolution] = useState<Solution | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const generateSolution = async () => {
    setLoading(true);
    setError(null);
    setSolution(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/solutions/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vulnerability_type: vulnerabilityType,
          target_stack: targetStack,
          use_cache: true,
        }),
      });

      const data = await response.json();

      if (!data.success) {
        setError(data.error || "Error generando solución");
      } else {
        setSolution(data);
      }
    } catch (err) {
      setError(`Error conectando con el servidor: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      CRITICAL: "bg-red-500/10 text-red-500 border-red-500/30",
      HIGH: "bg-orange-500/10 text-orange-500 border-orange-500/30",
      MEDIUM: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30",
      LOW: "bg-blue-500/10 text-blue-500 border-blue-500/30",
    };
    return colors[severity] || colors.LOW;
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-[#0f1115] rounded-lg border border-gray-800">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          Generador de Soluciones con IA
        </h2>
        <p className="text-gray-400">
          Powered by Deepseek - Soluciones automáticas para vulnerabilidades
        </p>
      </div>

      {/* Input Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tipo de Vulnerabilidad
          </label>
          <input
            type="text"
            value={vulnerabilityType}
            readOnly
            className="w-full bg-[#161920] border border-gray-700 rounded px-3 py-2 text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Stack Tecnológico
          </label>
          <select
            value={targetStack}
            onChange={(e) => setSolution(null)}
            className="w-full bg-[#161920] border border-gray-700 rounded px-3 py-2 text-white focus:outline-none"
          >
            <option value="node">Node.js</option>
            <option value="python">Python</option>
            <option value="php">PHP</option>
            <option value="java">Java</option>
            <option value="dotnet">.NET</option>
            <option value="nginx">Nginx</option>
            <option value="apache">Apache</option>
            <option value="generic">Genérico</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={generateSolution}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Generando...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                Generar Solución
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-500">Error</p>
            <p className="text-sm text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="text-center">
            <Loader className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-3" />
            <p className="text-gray-400">Generando solución con IA...</p>
          </div>
        </div>
      )}

      {/* Solution Display */}
      {solution && (
        <div className="space-y-6">
          {/* Header */}
          <div className="border-b border-gray-700 pb-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-xl font-bold text-white">{solution.title}</h3>
                <p className="text-sm text-gray-400 mt-1">{solution.cwe_id}</p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(
                  solution.severity
                )}`}
              >
                {solution.severity}
              </span>
            </div>

            <p className="text-gray-300 mb-3">{solution.description}</p>
            <p className="text-sm text-gray-400 mb-2">
              <strong>Impacto:</strong> {solution.impact}
            </p>
            <p className="text-sm text-gray-400">
              <strong>Tiempo estimado:</strong> {solution.estimated_fix_time}
            </p>
          </div>

          {/* Code Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-sm font-semibold text-red-400">Código Vulnerable</h4>
                <button
                  onClick={() => copyToClipboard(solution.vulnerable_code)}
                  className="text-xs bg-red-500/20 hover:bg-red-500/30 text-red-400 px-2 py-1 rounded flex items-center gap-1"
                >
                  <Copy className="w-3 h-3" />
                  {copied ? "Copiado" : "Copiar"}
                </button>
              </div>
              <SyntaxHighlighter
                language="javascript"
                style={dracula}
                className="rounded text-sm"
              >
                {solution.vulnerable_code}
              </SyntaxHighlighter>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-sm font-semibold text-green-400">Código Seguro</h4>
                <button
                  onClick={() => copyToClipboard(solution.secure_code)}
                  className="text-xs bg-green-500/20 hover:bg-green-500/30 text-green-400 px-2 py-1 rounded flex items-center gap-1"
                >
                  <Copy className="w-3 h-3" />
                  {copied ? "Copiado" : "Copiar"}
                </button>
              </div>
              <SyntaxHighlighter
                language="javascript"
                style={dracula}
                className="rounded text-sm"
              >
                {solution.secure_code}
              </SyntaxHighlighter>
            </div>
          </div>

          {/* Solution Steps */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-3">
              Pasos de Remediación
            </h4>
            <ol className="space-y-2">
              {solution.solution_steps.map((step, idx) => (
                <li key={idx} className="flex gap-3 text-gray-300">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center text-blue-400 font-medium text-sm">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Best Practices */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-3">
              Mejores Prácticas
            </h4>
            <ul className="space-y-2">
              {solution.best_practices.map((practice, idx) => (
                <li key={idx} className="flex gap-3 text-gray-300">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                  <span>{practice}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Verification */}
          <div className="bg-[#161920] border border-gray-700 rounded p-4">
            <h4 className="text-sm font-semibold text-white mb-2">Verificación</h4>
            <p className="text-sm text-gray-300">{solution.verification}</p>
          </div>

          {/* References */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-2">Referencias</h4>
            <ul className="space-y-1">
              {solution.references.map((ref, idx) => (
                <li key={idx}>
                  <a
                    href={ref}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm break-all"
                  >
                    {ref}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Source */}
          <div className="text-xs text-gray-500 border-t border-gray-700 pt-3">
            Solución generada con IA Deepseek
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !solution && !error && (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">
            Haz clic en "Generar Solución" para obtener recomendaciones de IA
          </p>
        </div>
      )}
    </div>
  );
}
