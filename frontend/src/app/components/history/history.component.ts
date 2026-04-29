import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { StateService } from '../../services/state.service';
import { Scan } from '../../services/scan.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss'],
})
export class HistoryComponent implements OnInit {
  history: Scan[] = [];

  constructor(private state: StateService, private router: Router) {}

  ngOnInit(): void {
    this.state.history$.subscribe(h => (this.history = h));
  }

  load(scan: Scan): void {
    this.state.setScan(scan);
    this.router.navigate(['/results']);
  }

  clear(): void { this.state.clearHistory(); }

  formatDate(ts: number): string {
    return new Date(ts * 1000).toLocaleString('es-PE');
  }

  totalFindings(scan: Scan): number {
    return scan.results?.total_findings ?? 0;
  }

  critical(scan: Scan): number { return scan.results?.severity_summary?.['critical'] ?? 0; }
  high(scan: Scan):     number { return scan.results?.severity_summary?.['high'] ?? 0; }
}
