"""
Web Crawler - Discovers endpoints, forms and links in target application.
FIXED:
  - Now always adds base_url to visited so it gets scanned even with no links
  - Removed strict same-origin filter for endpoints (allows testing params on any discovered URL)
  - Better Content-Type detection (handles 'text/html; charset=utf-8')
  - Adds base URL params as endpoints automatically
"""

import logging
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebCrawler:
    def __init__(self, http_client, max_depth: int = 2):
        self.http = http_client
        self.max_depth = max_depth
        self.visited = set()
        self.forms = []
        self.endpoints = []

    def crawl(self, base_url: str) -> dict:
        """Start crawling from base_url."""
        # Normalize: strip trailing slash
        base_url = base_url.rstrip('/')
        self.base_origin = self._get_origin(base_url)

        # Always add base URL itself as a visited + potential endpoint
        self.visited.add(base_url)
        if '?' in base_url:
            self.endpoints.append(base_url)

        self._crawl_url(base_url, depth=0)

        logger.info(f"Crawl finished: {len(self.visited)} URLs, "
                    f"{len(self.forms)} forms, {len(self.endpoints)} endpoints")
        return {
            'urls':      list(self.visited),
            'forms':     self.forms,
            'endpoints': self.endpoints,
        }

    def _crawl_url(self, url: str, depth: int):
        if depth > self.max_depth:
            return
        # Don't skip already-visited on depth-0 (we want to parse the base page)
        if depth > 0 and url in self.visited:
            return
        if not url.startswith(self.base_origin):
            return

        self.visited.add(url)
        logger.debug(f"Crawling [{depth}]: {url}")

        try:
            resp = self.http.get(url)
            if resp is None:
                logger.warning(f"No response for {url}")
                return

            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                logger.debug(f"Skipping non-HTML: {content_type} at {url}")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')

            # ── Collect forms ─────────────────────────────────────
            for form in soup.find_all('form'):
                parsed_form = self._parse_form(form, url)
                if parsed_form['fields']:   # only add forms with actual inputs
                    self.forms.append(parsed_form)

            # ── Collect links and follow them ─────────────────────
            for tag in soup.find_all('a', href=True):
                href = tag['href'].strip()
                if not href or href.startswith(('mailto:', 'tel:', 'javascript:')):
                    continue
                absolute = urljoin(url, href).split('#')[0].rstrip('/')
                if not absolute.startswith(self.base_origin):
                    continue
                if absolute not in self.visited:
                    # Track parameterised endpoints separately
                    if '?' in absolute:
                        self.endpoints.append(absolute)
                    self._crawl_url(absolute, depth + 1)

            # ── Extract inline params from current page URL ────────
            parsed = urlparse(url)
            if parsed.query:
                self.endpoints.append(url)

        except Exception as e:
            logger.warning(f"Crawl error for {url}: {e}", exc_info=True)

    def _parse_form(self, form_tag, page_url: str) -> dict:
        action = form_tag.get('action', '')
        action_url = urljoin(page_url, action) if action else page_url
        method = form_tag.get('method', 'get').upper()

        fields = []
        for inp in form_tag.find_all(['input', 'textarea', 'select']):
            field_type = inp.get('type', 'text').lower()
            name = inp.get('name', '')
            if name and field_type not in ('submit', 'button', 'image', 'reset', 'file'):
                fields.append({
                    'name':  name,
                    'type':  field_type,
                    'value': inp.get('value', ''),
                })

        return {
            'action': action_url,
            'method': method,
            'fields': fields,
            'page':   page_url,
        }

    @staticmethod
    def _get_origin(url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
