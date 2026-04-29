"""
HTTP Client - Centralized HTTP request handler with session, retry and header management.
"""

import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'VulnScan/1.0 (Security Testing Tool; Educational Use)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


class HTTPClient:
    """
    Wrapper around requests.Session with:
      - Configurable timeout
      - Automatic retry with backoff
      - Custom headers
      - SSL verification toggle (disabled for local test targets)
    """

    def __init__(self, timeout: int = 10, verify_ssl: bool = False):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)

        retry = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=['GET', 'POST'],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get(self, url: str, params: dict = None, headers: dict = None):
        try:
            return self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=True,
            )
        except requests.exceptions.RequestException as e:
            logger.debug(f"GET {url} failed: {e}")
            return None

    def post(self, url: str, data: dict = None, json: dict = None, headers: dict = None):
        try:
            return self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=True,
            )
        except requests.exceptions.RequestException as e:
            logger.debug(f"POST {url} failed: {e}")
            return None

    def set_cookie(self, name: str, value: str, domain: str = None):
        self.session.cookies.set(name, value, domain=domain)

    def set_header(self, name: str, value: str):
        self.session.headers[name] = value

    def set_auth(self, username: str, password: str):
        self.session.auth = (username, password)
