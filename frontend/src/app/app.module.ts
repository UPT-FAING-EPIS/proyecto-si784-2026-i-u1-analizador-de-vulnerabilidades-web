import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { ScannerComponent } from './components/scanner/scanner.component';
import { ResultsComponent } from './components/results/results.component';
import { HistoryComponent } from './components/history/history.component';
import { ReportComponent } from './components/report/report.component';

import { ScanService } from './services/scan.service';
import { SeverityPipe } from './pipes/severity.pipe';

const routes: Routes = [
  { path: '',         component: ScannerComponent },
  { path: 'results',  component: ResultsComponent },
  { path: 'history',  component: HistoryComponent },
  { path: 'report',   component: ReportComponent  },
  { path: '**',       redirectTo: '' },
];

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    ScannerComponent,
    ResultsComponent,
    HistoryComponent,
    ReportComponent,
    SeverityPipe,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
  ],
  providers: [ScanService],
  bootstrap: [AppComponent],
})
export class AppModule {}
