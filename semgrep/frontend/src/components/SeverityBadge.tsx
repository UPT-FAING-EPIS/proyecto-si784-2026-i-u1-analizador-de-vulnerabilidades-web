export function SeverityBadge({ severity }: { severity: string }) {
  const config: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    critical: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/30", dot: "bg-red-500" },
    high:     { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/30", dot: "bg-orange-500" },
    medium:   { bg: "bg-yellow-500/10", text: "text-yellow-400", border: "border-yellow-500/30", dot: "bg-yellow-500" },
    low:      { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/30", dot: "bg-blue-500" },
    info:     { bg: "bg-gray-500/10", text: "text-gray-400", border: "border-gray-500/30", dot: "bg-gray-500" },
  };
  const s = severity.toLowerCase();
  const c = config[s] || config.info;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${c.bg} ${c.text} ${c.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {severity.toUpperCase()}
    </span>
  );
}

export function SeverityBar({ critical = 0, high = 0, medium = 0, low = 0 }: {
  critical?: number; high?: number; medium?: number; low?: number;
}) {
  const total = critical + high + medium + low;
  if (total === 0) return <div className="h-1.5 bg-gray-800 rounded-full" />;
  return (
    <div className="flex h-1.5 rounded-full overflow-hidden gap-0.5">
      {critical > 0 && <div className="bg-red-500 rounded-full" style={{ width: `${(critical/total)*100}%` }} />}
      {high > 0 && <div className="bg-orange-500 rounded-full" style={{ width: `${(high/total)*100}%` }} />}
      {medium > 0 && <div className="bg-yellow-500 rounded-full" style={{ width: `${(medium/total)*100}%` }} />}
      {low > 0 && <div className="bg-blue-500 rounded-full" style={{ width: `${(low/total)*100}%` }} />}
    </div>
  );
}
