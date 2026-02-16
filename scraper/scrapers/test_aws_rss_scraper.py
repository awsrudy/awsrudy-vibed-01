"""
Tests for AWS RSS Scraper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import feedparser

from scraper.scrapers.aws_rss_scraper import AWSRSSScraper


@pytest.fixture
def source_config():
    """Sample source configuration"""
    return {
        'id': 'aws-news',
        'name': 'AWS News Blog',
        'url': 'https://aws.amazon.com/blogs/aws/',
        'rss': 'https://aws.amazon.com/blogs/aws/feed/',
        'category': 'News',
    }


@pytest.fixture
def mock_rss_response():
    """Mock RSS feed response"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>AWS News Blog</title>
    <link>https://aws.amazon.com/blogs/aws/</link>
    <description>The latest AWS news</description>
    <item>
      <title>Introducing New Lambda Features</title>
      <link>https://aws.amazon.com/blogs/aws/new-lambda-features/</link>
      <pubDate>Wed, 15 Feb 2024 10:00:00 +0000</pubDate>
      <description>Exciting new features for AWS Lambda...</description>
      <content:encoded><![CDATA[<p>AWS Lambda now supports...</p>]]></content:encoded>
      <author>John Doe</author>
    </item>
    <item>
      <title>Amazon S3 Update</title>
      <link>https://aws.amazon.com/blogs/aws/s3-update/</link>
      <pubDate>Tue, 14 Feb 2024 15:30:00 +0000</pubDate>
      <description>New S3 capabilities...</description>
      <content:encoded><![CDATA[<p>Amazon S3 now offers...</p>]]></content:encoded>
    </item>
  </channel>
</rss>"""


def test_aws_rss_scraper_initialization(source_config):
    """Test scraper initialization"""
    scraper = AWSRSSScraper(source_config)

    assert scraper.source_id == 'aws-news'
    assert scraper.source_name == 'AWS News Blog'
    assert scraper.rss_url == 'https://aws.amazon.com/blogs/aws/feed/'

    scraper.close()


def test_aws_rss_scraper_scrape_rss(source_config, mock_rss_response):
    """Test RSS scraping"""
    scraper = AWSRSSScraper(source_config)

    # Mock HTTP response
    mock_response = Mock()
    mock_response.content = mock_rss_response.encode('utf-8')

    with patch.object(scraper.http_client, 'get', return_value=mock_response):
        posts = scraper.scrape_rss()

    assert len(posts) == 2

    # Check first post
    assert posts[0]['title'] == 'Introducing New Lambda Features'
    assert posts[0]['url'] == 'https://aws.amazon.com/blogs/aws/new-lambda-features/'
    assert posts[0]['author'] == 'John Doe'
    assert 'Lambda' in posts[0]['content']

    # Check second post
    assert posts[1]['title'] == 'Amazon S3 Update'
    assert posts[1]['url'] == 'https://aws.amazon.com/blogs/aws/s3-update/'

    scraper.close()


def test_aws_rss_scraper_parse_entry(source_config):
    """Test parsing a single RSS entry"""
    scraper = AWSRSSScraper(source_config)

    # Mock entry - use a dict-like object that feedparser would return
    class MockEntry:
        def __init__(self):
            self.link = 'https://example.com/post'
            self.title = 'Test Post'
            self.published = 'Wed, 15 Feb 2024 10:00:00 +0000'
            self.summary = 'Test summary'
            self.author = 'Test Author'
            self.tags = []
            self.content = []

        def get(self, key, default=''):
            return getattr(self, key, default)

        def __contains__(self, key):
            return hasattr(self, key)

        def __getitem__(self, key):
            return getattr(self, key)

    entry = MockEntry()
    post = scraper._parse_rss_entry(entry)

    assert post is not None
    assert post['title'] == 'Test Post'
    assert post['url'] == 'https://example.com/post'
    assert post['author'] == 'Test Author'

    scraper.close()


def test_aws_rss_scraper_missing_rss_url():
    """Test handling of missing RSS URL"""
    source_config = {
        'id': 'test-blog',
        'name': 'Test Blog',
        'url': 'https://example.com',
        # No 'rss' field
    }

    scraper = AWSRSSScraper(source_config)
    posts = scraper.scrape_rss()

    assert posts == []

    scraper.close()


def test_aws_rss_scraper_invalid_rss(source_config):
    """Test handling of invalid RSS feed"""
    scraper = AWSRSSScraper(source_config)

    # Mock HTTP response with invalid XML
    mock_response = Mock()
    mock_response.content = b"Not valid XML!"

    with patch.object(scraper.http_client, 'get', return_value=mock_response):
        posts = scraper.scrape_rss()

    # Should return empty list, not crash
    assert isinstance(posts, list)

    scraper.close()


def test_aws_rss_scraper_http_failure(source_config):
    """Test handling of HTTP failure"""
    scraper = AWSRSSScraper(source_config)

    # Mock HTTP client returning None (failure)
    with patch.object(scraper.http_client, 'get', return_value=None):
        posts = scraper.scrape_rss()

    assert posts == []

    scraper.close()
