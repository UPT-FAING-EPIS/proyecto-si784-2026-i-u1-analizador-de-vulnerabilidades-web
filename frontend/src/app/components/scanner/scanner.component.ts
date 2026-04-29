import { Component, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ScanService, Scan } from '../../services/scan.service';
import { StateService } from '../../services/state.service';

@Component({
  selector: 'app-scanner',
  templateUrl: './scanner.component.html',
  styleUrls: ['./scanner.component.scss'],
})
export class ScannerComponent implements OnDestroy {
  form: FormGroup;
  scan: Scan | null = null;
  isScanning = false;
  errorMsg = '';
  private sub?: Subscription;

  constructor(
    private fb: FormBuilder,
    private scanService: ScanService,
    private state: StateService,
    private router: Router,
  ) {
    this.form = this.fb.group({
      url:                  ['http://localhost:8080', [Validators.required]],
      scan_xss:             [true],
      scan_sqli:            [true],
      scan_headers:         [true],
      scan_csrf:            [true],
      scan_redirect:        [true],
      scan_info_disclosure: [true],
      max_depth:            [2],
      timeout:              [10],
    });
  }

  get progressPct(): number { return this.scan?.progress ?? 0; }
  get statusText(): string  { return (this.scan as any)?.current_task ?? 'Esperando...'; }

  startScan(): void {
    if (this.form.invalid || this.isScanning) return;
    this.errorMsg = '';
    this.isScanning = true;
    this.scan = null;

    const opts = { ...this.form.value };
    if (!opts.url.startsWith('http')) opts.url = 'http://' + opts.url;

    this.sub = this.scanService.startScan(opts).subscribe({
      next: ({ scan_id }) => {
        this.sub = this.scanService.pollScan(scan_id).subscribe({
          next: (s: Scan) => {
            this.scan = s;
            this.state.setScan(s);
            if (s.status === 'completed' || s.status === 'error') {
              this.isScanning = false;
              if (s.status === 'completed') this.state.addToHistory(s);
              if (s.status === 'error') this.errorMsg = s.error ?? 'Error desconocido.';
            }
          },
          error: () => { this.isScanning = false; this.errorMsg = 'Error de conexión con el backend.'; },
        });
      },
      error: () => {
        this.isScanning = false;
        this.errorMsg = 'No se pudo conectar al backend. ¿Está corriendo Flask en localhost:5000?';
      },
    });
  }

  reset(): void {
    if (this.sub) this.sub.unsubscribe();
    this.isScanning = false;
    this.scan = null;
    this.errorMsg = '';
  }

  viewResults(): void { this.router.navigate(['/results']); }

  get severitySummary() {
    return this.scan?.results?.severity_summary ?? {};
  }

  ngOnDestroy(): void { this.sub?.unsubscribe(); }
}
