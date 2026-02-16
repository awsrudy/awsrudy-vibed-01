"""
Tests for scraper utilities
"""

import pytest
from datetime import datetime
import pytz
from scraper.utils import (
    parse_date,
    clean_html,
    extract_summary,
    normalize_url,
    extract_aws_services,
    generate_slug,
    is_valid_url,
    deduplicate_posts,
)


def test_parse_date():
    """Test date parsing with various formats"""
    # ISO 8601
    dt = parse_date("2024-02-15T10:30:00Z")
    assert dt is not None
    assert dt.year == 2024
    assert dt.month == 2
    assert dt.day == 15

    # RSS format
    dt = parse_date("Wed, 15 Feb 2024 10:30:00 GMT")
    assert dt is not None

    # Invalid date
    dt = parse_date("not a date")
    assert dt is None

    # Empty string
    dt = parse_date("")
    assert dt is None


def test_clean_html():
    """Test HTML cleaning"""
    # Remove script tags
    html = '<p>Hello</p><script>alert("xss")</script><p>World</p>'
    cleaned = clean_html(html, keep_tags=True)
    assert 'script' not in cleaned
    assert 'Hello' in cleaned
    assert 'World' in cleaned

    # Extract text only
    html = '<p>Test <strong>bold</strong> text</p>'
    text = clean_html(html, keep_tags=False)
    assert '<' not in text
    assert 'Test bold text' in text

    # Empty HTML
    assert clean_html("") == ""


def test_extract_summary():
    """Test summary extraction"""
    # Short content
    summary = extract_summary("This is a short post.")
    assert summary == "This is a short post."

    # Long content with HTML
    html = "<p>First paragraph. This is the summary.</p><p>Second paragraph with more details.</p>"
    summary = extract_summary(html, max_length=50)
    assert len(summary) <= 53  # Allow for "..."
    assert 'First' in summary

    # Empty content
    assert extract_summary("") == ""


def test_normalize_url():
    """Test URL normalization"""
    # Remove query string
    url = "https://example.com/post?utm_source=twitter"
    assert normalize_url(url) == "https://example.com/post"

    # Remove fragment
    url = "https://example.com/post#section"
    assert normalize_url(url) == "https://example.com/post"

    # Remove trailing slash
    url = "https://example.com/post/"
    assert normalize_url(url) == "https://example.com/post"

    # Empty URL
    assert normalize_url("") == ""


def test_extract_aws_services():
    """Test AWS service extraction"""
    # Single service
    text = "We use Amazon S3 for storage"
    services = extract_aws_services(text)
    assert "S3" in services

    # Multiple services
    text = "Deploy with Lambda and store in DynamoDB"
    services = extract_aws_services(text)
    assert "Lambda" in services
    assert "DynamoDB" in services

    # No services
    text = "This is about Azure"
    services = extract_aws_services(text)
    assert len(services) == 0

    # Empty text
    services = extract_aws_services("")
    assert services == []


def test_generate_slug():
    """Test slug generation"""
    # Normal title
    slug = generate_slug("How to Use Amazon S3")
    assert slug == "how-to-use-amazon-s3"

    # Special characters
    slug = generate_slug("AWS Lambda: Best Practices!")
    assert slug == "aws-lambda-best-practices"

    # Long title (should truncate)
    long_title = "This is a very long title that should be truncated " * 5
    slug = generate_slug(long_title)
    assert len(slug) <= 100

    # Empty title
    assert generate_slug("") == ""


def test_is_valid_url():
    """Test URL validation"""
    # Valid URLs
    assert is_valid_url("https://example.com")
    assert is_valid_url("http://example.com/path")
    assert is_valid_url("https://example.com:8080/path?query=1")

    # Invalid URLs
    assert not is_valid_url("not a url")
    assert not is_valid_url("")
    assert not is_valid_url("ftp://example.com")


def test_deduplicate_posts():
    """Test post deduplication"""
    posts = [
        {"url": "https://example.com/post1", "date": "2024-01-01", "title": "Post 1"},
        {"url": "https://example.com/post2", "date": "2024-01-02", "title": "Post 2"},
        {"url": "https://example.com/post1?ref=twitter", "date": "2024-01-03", "title": "Post 1 Duplicate"},
    ]

    deduplicated = deduplicate_posts(posts)
    assert len(deduplicated) == 2  # post1 appears twice (different query string)

    # Empty list
    assert deduplicate_posts([]) == []


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
