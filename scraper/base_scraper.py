"""
Base Scraper Abstract Class

Provides common interface and functionality for all blog scrapers.
Individual blog scrapers inherit from this class and implement
the abstract methods.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

from scraper.http_client import HTTPClient
from scraper.utils import (
    parse_date,
    clean_html,
    extract_summary,
    normalize_url,
    extract_aws_services,
    generate_slug,
    is_valid_url,
    calculate_reading_time,
    extract_code_blocks,
)

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for blog scrapers.

    All blog-specific scrapers inherit from this class and implement:
    - scrape_rss(): Parse RSS feed
    - scrape_html(): Parse HTML pages (fallback)

    The base class provides:
    - HTTP client for making requests
    - Common post processing logic
    - Standardized data structure
    """

    def __init__(self, source_config: Dict):
        """
        Initialize scraper with source configuration

        Args:
            source_config: Source configuration from sources.yml
        """
        self.source_config = source_config
        self.source_id = source_config['id']
        self.source_name = source_config['name']
        self.source_url = source_config['url']
        self.rss_url = source_config.get('rss')
        self.category = source_config.get('category', 'General')

        self.http_client = HTTPClient()

        logger.info(f"Initialized scraper for {self.source_name}")

    @abstractmethod
    def scrape_rss(self) -> List[Dict]:
        """
        Scrape posts from RSS feed.

        This method must be implemented by subclasses.

        Returns:
            List of post dictionaries
        """
        pass

    @abstractmethod
    def scrape_html(self) -> List[Dict]:
        """
        Scrape posts from HTML pages (fallback if RSS fails).

        This method must be implemented by subclasses.

        Returns:
            List of post dictionaries
        """
        pass

    def scrape(self) -> List[Dict]:
        """
        Scrape posts using RSS feed (primary) with HTML fallback.

        Returns:
            List of processed post dictionaries
        """
        logger.info(f"Scraping {self.source_name}...")

        posts = []

        # Try RSS first
        if self.rss_url:
            try:
                posts = self.scrape_rss()
                logger.info(f"✓ Scraped {len(posts)} posts from RSS feed")
            except Exception as e:
                logger.warning(f"RSS scraping failed: {e}")

        # Fallback to HTML if RSS failed or no RSS URL
        if not posts:
            try:
                from scraper.config import ENABLE_HTML_FALLBACK
                if ENABLE_HTML_FALLBACK:
                    logger.info("Falling back to HTML scraping...")
                    posts = self.scrape_html()
                    logger.info(f"✓ Scraped {len(posts)} posts from HTML")
                else:
                    logger.warning("HTML fallback disabled in config")
            except Exception as e:
                logger.error(f"HTML scraping failed: {e}")

        # Process all posts
        processed_posts = [self._process_post(post) for post in posts]

        # Filter out invalid posts
        valid_posts = [p for p in processed_posts if p is not None]

        logger.info(f"Processed {len(valid_posts)}/{len(posts)} valid posts from {self.source_name}")

        return valid_posts

    def _process_post(self, post: Dict) -> Optional[Dict]:
        """
        Process and standardize a post.

        Args:
            post: Raw post dictionary from scraper

        Returns:
            Processed post dictionary, or None if invalid
        """
        try:
            # Required fields
            url = post.get('url', '')
            title = post.get('title', '')

            if not url or not is_valid_url(url):
                logger.warning(f"Invalid URL: {url}")
                return None

            if not title:
                logger.warning(f"Missing title for {url}")
                return None

            # Normalize URL
            url = normalize_url(url)

            # Parse date
            date_str = post.get('date', '')
            date = parse_date(date_str)
            if not date:
                logger.warning(f"Invalid date for {url}: {date_str}")
                date = datetime.now()

            # Clean content
            content = post.get('content', '')
            from scraper.config import ENABLE_CONTENT_CLEANING
            if content and ENABLE_CONTENT_CLEANING:
                content = clean_html(content, keep_tags=True)

            # Generate summary
            summary = post.get('summary', '')
            if not summary and content:
                summary = extract_summary(content)

            # Extract AWS services
            from scraper.config import ENABLE_SERVICE_TAGGING
            services = []
            if ENABLE_SERVICE_TAGGING:
                text = f"{title} {summary} {content}"
                services = extract_aws_services(text)

            # Generate slug
            slug = generate_slug(title)

            # Calculate reading time
            reading_time = calculate_reading_time(content)

            # Extract code blocks
            code_blocks = extract_code_blocks(content)

            # Build standardized post object
            processed = {
                'url': url,
                'title': title,
                'date': date.isoformat(),
                'source': self.source_name,
                'source_id': self.source_id,
                'category': self.category,
                'author': post.get('author', 'AWS'),
                'summary': summary,
                'content': content,
                'slug': slug,
                'services': services,
                'tags': post.get('tags', []),
                'image_url': post.get('image_url', ''),
                'reading_time': reading_time,
                'has_code': len(code_blocks) > 0,
            }

            return processed

        except Exception as e:
            logger.exception(f"Failed to process post: {e}")
            return None

    def close(self):
        """Close HTTP client and release resources"""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close resources"""
        self.close()
