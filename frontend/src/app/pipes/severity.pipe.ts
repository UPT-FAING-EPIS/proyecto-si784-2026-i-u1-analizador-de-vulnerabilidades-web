import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'severity' })
export class SeverityPipe implements PipeTransform {
  transform(value: string): string {
    const map: Record<string, string> = {
      critical: 'CRÍTICO',
      high:     'ALTO',
      medium:   'MEDIO',
      low:      'BAJO',
      info:     'INFO',
    };
    return map[value?.toLowerCase()] ?? value?.toUpperCase() ?? '';
  }
}
