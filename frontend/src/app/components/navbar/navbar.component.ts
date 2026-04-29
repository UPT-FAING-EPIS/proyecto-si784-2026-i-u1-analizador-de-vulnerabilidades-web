import { Component } from '@angular/core';
import { StateService } from '../../services/state.service';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent {
  findingsCount$ = this.state.currentScan$.pipe(
    map(s => s?.results?.total_findings ?? 0)
  );

  constructor(private state: StateService) {}
}
