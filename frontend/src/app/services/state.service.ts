import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Scan } from './scan.service';

@Injectable({ providedIn: 'root' })
export class StateService {
  private _currentScan$ = new BehaviorSubject<Scan | null>(null);
  private _history$ = new BehaviorSubject<Scan[]>(this._loadHistory());

  currentScan$ = this._currentScan$.asObservable();
  history$     = this._history$.asObservable();

  setScan(scan: Scan): void {
    this._currentScan$.next(scan);
  }

  getCurrentScan(): Scan | null {
    return this._currentScan$.getValue();
  }

  addToHistory(scan: Scan): void {
    const hist = [scan, ...this._history$.getValue()].slice(0, 30);
    this._history$.next(hist);
    try { localStorage.setItem('vulnscan_history', JSON.stringify(hist)); } catch {}
  }

  clearHistory(): void {
    this._history$.next([]);
    try { localStorage.removeItem('vulnscan_history'); } catch {}
  }

  private _loadHistory(): Scan[] {
    try {
      return JSON.parse(localStorage.getItem('vulnscan_history') ?? '[]');
    } catch { return []; }
  }
}
