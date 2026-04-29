import { Component, OnInit } from '@angular/core';
import { StateService } from '../../services/state.service';
import { Scan, Finding } from '../../services/scan.service';

type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';
type FilterKey = 'all' | Severity | 'xss' | 'sqli' | 'misconfiguration' | 'csrf';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss'],
})
export class ResultsComponent implements OnInit {
  scan: Scan | null = null;
  activeFilter: FilterKey = 'all';
  expandedIds = new Set<string>();
  searchTerm = '';

  readonly severities: Severity[] = ['critical', 'high', 'medium', 'low', 'info'];

  readonly severityConfig: Record<Severity, { label: string; color: string; bg: string; icon: string }> = {
    critical: { label: 'Crítico', color: '#ff2d55', bg: 'rgba(255,45,85,.12)',  icon: '🔴' },
    high:     { label: 'Alto',    color: '#ff6b35', bg: 'rgba(255,107,53,.12)', icon: '🟠' },
    medium:   { label: 'Medio',   color: '#f0b429', bg: 'rgba(240,180,41,.1)',  icon: '🟡' },
    low:      { label: 'Bajo',    color: '#3fb950', bg: 'rgba(63,185,80,.1)',   icon: '🟢' },
    info:     { label: 'Info',    color: '#58a6ff', bg: 'rgba(88,166,255,.1)',  icon: '🔵' },
  };

  filters: { key: FilterKey; label: string }[] = [
    { key: 'all',              label: 'Todos' },
    { key: 'critical',         label: 'Crítico' },
    { key: 'high',             label: 'Alto' },
    { key: 'medium',           label: 'Medio' },
    { key: 'low',              label: 'Bajo' },
    { key: 'xss',              label: 'XSS' },
    { key: 'sqli',             label: 'SQLi' },
    { key: 'misconfiguration', label: 'Headers' },
    { key: 'csrf',             label: 'CSRF' },
  ];

  constructor(private state: StateService) {}

  ngOnInit(): void {
    this.state.currentScan$.subscribe(s => { this.scan = s; });
  }

  get findings(): Finding[] {
    const all = this.scan?.results?.findings ?? [];
    return all.filter(f => {
      const matchFilter =
        this.activeFilter === 'all' ||
        f.severity === this.activeFilter ||
        f.type === this.activeFilter;
      const matchSearch =
        !this.searchTerm ||
        f.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        f.url.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        (f.parameter ?? '').toLowerCase().includes(this.searchTerm.toLowerCase());
      return matchFilter && matchSearch;
    });
  }

  setFilter(k: FilterKey): void { this.activeFilter = k; }

  toggle(id: string): void {
    this.expandedIds.has(id) ? this.expandedIds.delete(id) : this.expandedIds.add(id);
  }

  isExpanded(id: string): boolean { return this.expandedIds.has(id); }

  trackById(_index: number, f: Finding): string { return f.id; }

  severityClass(sev: string): string { return `sev-${sev}`; }

  getSeverityCount(sev: Severity): number {
    return this.scan?.results?.severity_summary?.[sev] ?? 0;
  }

  getTotalVulns(): number {
    return this.scan?.results?.total_findings ?? 0;
  }

  getSeverityConfig(sev: string): { label: string; color: string; bg: string; icon: string } {
    return this.severityConfig[sev as Severity] ?? { label: sev, color: '#888', bg: 'transparent', icon: '⚪' };
  }

  countBySeverity(sev: string): number {
    return this.scan?.results?.severity_summary?.[sev] ?? 0;
  }
}
