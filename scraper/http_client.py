"""
HTTP Client with Retry Logic

Provides robust HTTP request handling with retries, timeouts,
rate limiting, and proper error handling.
"""

import time
import logging
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scraper.config import (
    USER_AGENT,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    FETCH_DELAY,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client with retry logic, rate limiting, and error handling.

    Features:
    - Automatic retries with exponential backoff
    - Configurable timeouts
    - Rate limiting between requests
    - Custom user agent
    - Session reuse for connection pooling
    """

    def __init__(
        self,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        fetch_delay: float = FETCH_DELAY,
    ):
        """
        Initialize HTTP client

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            fetch_delay: Delay between requests in seconds (rate limiting)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.fetch_delay = fetch_delay
        self.last_request_time = 0

        # Create session with retry logic
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP codes
            backoff_factor=1,  # Wait 1s, 2s, 4s, 8s between retries
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })

    def _rate_limit(self):
        """
        Enforce rate limiting by waiting if needed.

        Ensures at least fetch_delay seconds between requests.
        """
        if self.fetch_delay > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.fetch_delay:
                wait_time = self.fetch_delay - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                time.sleep(wait_time)

        self.last_request_time = time.time()

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a GET request with retry logic and rate limiting.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments passed to requests.get()

        Returns:
            Response object if successful, None if all retries failed
        """
        self._rate_limit()

        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            logger.debug(f"GET {url}")
            response = self.session.get(url, **kwargs)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes

            logger.debug(f"✓ {response.status_code} {url} ({len(response.content)} bytes)")
            return response

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}")
            return None

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {url}: {e}")
            return None

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout for {url}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None

    def close(self):
        """Close the session and release resources"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self.close()
