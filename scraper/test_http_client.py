"""
Tests for HTTP Client
"""

import pytest
import time
from unittest.mock import Mock, patch
import requests

from scraper.http_client import HTTPClient


def test_http_client_initialization():
    """Test HTTP client initialization"""
    client = HTTPClient(timeout=10, max_retries=2, fetch_delay=0.5)

    assert client.timeout == 10
    assert client.max_retries == 2
    assert client.fetch_delay == 0.5
    assert client.session is not None

    client.close()


def test_http_client_get_success():
    """Test successful GET request"""
    with HTTPClient(fetch_delay=0) as client:
        # Mock response
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"test content"
            mock_get.return_value = mock_response

            response = client.get("https://example.com")

            assert response is not None
            assert response.status_code == 200


def test_http_client_get_failure():
    """Test failed GET request"""
    with HTTPClient(fetch_delay=0) as client:
        # Mock connection error
        with patch.object(client.session, 'get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

            response = client.get("https://example.com")

            assert response is None


def test_http_client_rate_limiting():
    """Test rate limiting between requests"""
    with HTTPClient(fetch_delay=0.1) as client:
        # Mock response
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # First request
            start = time.time()
            client.get("https://example.com")

            # Second request - should wait
            client.get("https://example.com")
            elapsed = time.time() - start

            # Should have waited at least fetch_delay
            assert elapsed >= 0.1


def test_http_client_context_manager():
    """Test context manager closes session"""
    client = HTTPClient()

    with patch.object(client, 'close') as mock_close:
        with client:
            pass

        mock_close.assert_called_once()
