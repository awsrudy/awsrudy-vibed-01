"""
Tests for Base Scraper
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from scraper.base_scraper import BaseScraper


class MockScraper(BaseScraper):
    """Mock scraper for testing"""

    def scrape_rss(self):
        return [
            {
                'url': 'https://example.com/post1',
                'title': 'Test Post 1',
                'date': '2024-02-15T10:00:00Z',
                'content': '<p>Test content</p>',
            }
        ]

    def scrape_html(self):
        return [
            {
                'url': 'https://example.com/post2',
                'title': 'Test Post 2',
                'date': '2024-02-16T10:00:00Z',
                'content': '<p>HTML content</p>',
            }
        ]


def test_base_scraper_initialization():
    """Test base scraper initialization"""
    source_config = {
        'id': 'test-blog',
        'name': 'Test Blog',
        'url': 'https://example.com',
        'rss': 'https://example.com/feed',
        'category': 'Testing',
    }

    scraper = MockScraper(source_config)

    assert scraper.source_id == 'test-blog'
    assert scraper.source_name == 'Test Blog'
    assert scraper.source_url == 'https://example.com'
    assert scraper.rss_url == 'https://example.com/feed'
    assert scraper.category == 'Testing'

    scraper.close()


def test_base_scraper_scrape_rss():
    """Test scraping from RSS feed"""
    source_config = {
        'id': 'test-blog',
        'name': 'Test Blog',
        'url': 'https://example.com',
        'rss': 'https://example.com/feed',
    }

    with MockScraper(source_config) as scraper:
        posts = scraper.scrape()

        assert len(posts) == 1
        assert posts[0]['title'] == 'Test Post 1'
        assert posts[0]['source'] == 'Test Blog'
        assert posts[0]['source_id'] == 'test-blog'


def test_base_scraper_process_post():
    """Test post processing"""
    source_config = {
        'id': 'test-blog',
        'name': 'Test Blog',
        'url': 'https://example.com',
    }

    scraper = MockScraper(source_config)

    raw_post = {
        'url': 'https://example.com/post',
        'title': 'Test Post',
        'date': '2024-02-15T10:00:00Z',
        'content': '<p>This is a test post about AWS Lambda.</p>',
        'author': 'John Doe',
    }

    processed = scraper._process_post(raw_post)

    assert processed is not None
    assert processed['url'] == 'https://example.com/post'
    assert processed['title'] == 'Test Post'
    assert processed['source'] == 'Test Blog'
    assert processed['author'] == 'John Doe'
    assert processed['slug'] == 'test-post'
    assert 'Lambda' in processed['services']  # AWS service detection

    scraper.close()


def test_base_scraper_invalid_post():
    """Test handling of invalid posts"""
    source_config = {
        'id': 'test-blog',
        'name': 'Test Blog',
        'url': 'https://example.com',
    }

    scraper = MockScraper(source_config)

    # Missing URL
    raw_post = {
        'title': 'Test Post',
        'date': '2024-02-15T10:00:00Z',
    }

    processed = scraper._process_post(raw_post)

    assert processed is None

    scraper.close()
