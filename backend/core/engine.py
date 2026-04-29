"""
Core Engine - FIXED:
  - self.findings reset on each run (was accumulating across scans)
  - Better logging of scanner errors
  - scan_redirect and scan_info_disclosure default to True
"""

import logging
import time
from crawler.spider import WebCrawler
from scanners.xss_scanner import XSSScanner
from scanners.sqli_scanner import SQLiScanner
from scanners.header_scanner import HeaderScanner
from scanners.csrf_scanner import CSRFScanner
from scanners.redirect_scanner import RedirectScanner
from scanners.info_disclosure_scanner import InfoDisclosureScanner
from rules.engine import RuleEngine
from utils.http_client import HTTPClient

logger = logging.getLogger(__name__)


class ScanEngine:
    def __init__(self, options: dict = None):
        self.options = options or {}
        self.http = HTTPClient(timeout=self.options.get('timeout', 10))
        self.rule_engine = RuleEngine()

    def run(self, url: str, progress_callback=None) -> dict:
        """Execute full scan pipeline. Fresh state per call."""
        # CRITICAL FIX: reset state on every run
        findings = []
        scanned_urls = []
        start_time = time.time()
        logger.info(f"Starting scan: {url}")

        def progress(pct, msg):
            logger.info(f"[{pct}%] {msg}")
            if progress_callback:
                progress_callback(pct, msg)

        # ── Phase 1: Crawl ──────────────────────────────────────
        progress(5, "Inicializando crawler...")
        try:
            crawler = WebCrawler(
                http_client=self.http,
                max_depth=self.options.get('max_depth', 2)
            )
            crawl_result = crawler.crawl(url)
        except Exception as e:
            logger.error(f"Crawler failed: {e}", exc_info=True)
            crawl_result = {'urls': [url], 'forms': [], 'endpoints': []}

        scanned_urls = crawl_result['urls']
        forms = crawl_result['forms']
        endpoints = crawl_result['endpoints']

        progress(25, f"Crawler completo. {len(scanned_urls)} URLs, {len(forms)} formularios.")

        # ── Phase 2: Scanners ────────────────────────────────────
        scanners = []
        if self.options.get('scan_headers', True):
            scanners.append(('Análisis de Headers', HeaderScanner(self.http)))
        if self.options.get('scan_xss', True):
            scanners.append(('XSS', XSSScanner(self.http)))
        if self.options.get('scan_sqli', True):
            scanners.append(('SQL Injection', SQLiScanner(self.http)))
        if self.options.get('scan_csrf', True):
            scanners.append(('CSRF', CSRFScanner(self.http)))
        if self.options.get('scan_redirect', True):
            scanners.append(('Open Redirect', RedirectScanner(self.http)))
        if self.options.get('scan_info_disclosure', True):
            scanners.append(('Info Disclosure', InfoDisclosureScanner(self.http)))

        total = len(scanners)
        for i, (name, scanner) in enumerate(scanners):
            pct = 25 + int((i / total) * 65)
            progress(pct, f"Ejecutando escáner {name}...")
            try:
                raw_findings = scanner.scan(
                    base_url=url,
                    urls=scanned_urls,
                    forms=forms,
                    endpoints=endpoints,
                )
                logger.info(f"{name}: {len(raw_findings)} hallazgos crudos")
                for raw in raw_findings:
                    classified = self.rule_engine.evaluate(raw)
                    if classified:
                        findings.append(classified)
            except Exception as e:
                logger.error(f"Scanner '{name}' error: {e}", exc_info=True)

        progress(92, "Agregando resultados...")
        duration = round(time.time() - start_time, 2)
        result = self._build_result(url, duration, crawl_result, findings)
        progress(100, f"Escaneo completo. {result['total_findings']} hallazgos.")
        return result

    @staticmethod
    def _build_result(url, duration, crawl_result, findings) -> dict:
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get('severity', 'info'), 5)
        )
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for f in sorted_findings:
            sev = f.get('severity', 'info')
            counts[sev] = counts.get(sev, 0) + 1

        return {
            'target_url': url,
            'duration_seconds': duration,
            'urls_crawled': len(crawl_result['urls']),
            'forms_found': len(crawl_result['forms']),
            'total_findings': len(sorted_findings),
            'severity_summary': counts,
            'findings': sorted_findings,
        }
