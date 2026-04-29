import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, interval, switchMap, takeWhile, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface ScanOptions {
  url: string;
  scan_xss?: boolean;
  scan_sqli?: boolean;
  scan_headers?: boolean;
  scan_csrf?: boolean;
  max_depth?: number;
  timeout?: number;
}

export interface Finding {
  id: string;
  type: string;
  subtype: string;
  name: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  owasp: string;
  cwe: string;
  cvss_range: string;
  description: string;
  remediation: string[];
  references: string[];
  url: string;
  parameter?: string;
  payload?: string;
  evidence?: string;
  header?: string;
  cookie_name?: string;
  discovered_at?: string;
}

export interface ScanResult {
  target_url: string;
  duration_seconds: number;
  urls_crawled: number;
  forms_found: number;
  total_findings: number;
  severity_summary: Record<string, number>;
  findings: Finding[];
}

export interface Scan {
  id: string;
  url: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;
  current_task?: string;
  started_at: number;
  completed_at?: number;
  results?: ScanResult;
  error?: string;
}

@Injectable({ providedIn: 'root' })
export class ScanService {
  private readonly api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  startScan(options: ScanOptions): Observable<{ scan_id: string; status: string }> {
    return this.http
      .post<{ scan_id: string; status: string }>(`${this.api}/scan`, options)
      .pipe(catchError(this._handleError));
  }

  getScan(scanId: string): Observable<Scan> {
    return this.http
      .get<Scan>(`${this.api}/scan/${scanId}`)
      .pipe(catchError(this._handleError));
  }

  listScans(statusFilter?: string): Observable<Scan[]> {
    let params = new HttpParams();
    if (statusFilter) {
      params = params.set('status', statusFilter);
    }
    return this.http
      .get<Scan[]>(`${this.api}/scans`, { params })
      .pipe(catchError(this._handleError));
  }

  pollScan(scanId: string): Observable<Scan> {
    return interval(2000).pipe(
      switchMap(() => this.getScan(scanId)),
      takeWhile(
        scan => scan.status === 'pending' || scan.status === 'running',
        true
      )
    );
  }

  getReportUrl(scanId: string): string {
    return `${this.api}/scan/${scanId}/report`;
  }

  private _handleError(err: HttpErrorResponse): Observable<never> {
    const msg = err?.error?.message ?? err?.message ?? 'Error de red desconocido';
    return throwError(() => new Error(msg));
  }
}
