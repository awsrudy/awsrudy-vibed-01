"""
AWS Blog RSS Scraper

Generic scraper for AWS blogs using RSS feeds.
Works for all AWS blogs (News, Architecture, DevOps, Security, Compute, etc.)
as they all use WordPress with similar RSS feed structures.
"""

import logging
import feedparser
from typing import List, Dict
from datetime import datetime

from scraper.base_scraper import BaseScraper
from scraper.config import MAX_POSTS_PER_SOURCE

logger = logging.getLogger(__name__)


class AWSRSSScraper(BaseScraper):
    """
    Generic scraper for AWS blog RSS feeds.

    AWS blogs use WordPress and have similar RSS feed structures:
    - RSS feed at /feed/ endpoint
    - Standard fields: title, link, description, published, content
    - Author information available
    - Categories/tags included
    """

    def scrape_rss(self) -> List[Dict]:
        """
        Scrape posts from AWS blog RSS feed.

        Returns:
            List of raw post dictionaries
        """
        if not self.rss_url:
            logger.warning(f"No RSS URL for {self.source_name}")
            return []

        logger.info(f"Fetching RSS feed: {self.rss_url}")

        # Fetch RSS feed
        response = self.http_client.get(self.rss_url)
        if not response:
            logger.error(f"Failed to fetch RSS feed: {self.rss_url}")
            return []

        # Parse RSS feed
        try:
            feed = feedparser.parse(response.content)

            if feed.bozo:
                # Bozo flag indicates feed parsing issues
                logger.warning(f"RSS feed has parsing issues: {feed.bozo_exception}")

            entries = feed.entries[:MAX_POSTS_PER_SOURCE]  # Limit posts
            logger.info(f"Found {len(entries)} entries in RSS feed")

            posts = []
            for entry in entries:
                post = self._parse_rss_entry(entry)
                if post:
                    posts.append(post)

            return posts

        except Exception as e:
            logger.exception(f"Failed to parse RSS feed: {e}")
            return []

    def _parse_rss_entry(self, entry) -> Dict:
        """
        Parse a single RSS entry into a post dictionary.

        Args:
            entry: Feedparser entry object

        Returns:
            Post dictionary, or None if parsing failed
        """
        try:
            # Required fields
            url = entry.get('link', '')
            title = entry.get('title', '')

            if not url or not title:
                logger.warning(f"Missing required fields in entry: {entry}")
                return None

            # Date - try multiple fields
            date_str = None
            for date_field in ['published', 'updated', 'created']:
                if date_field in entry:
                    date_str = entry[date_field]
                    break

            # Content - try multiple fields
            content = ''
            if 'content' in entry and len(entry.content) > 0:
                content = entry.content[0].value
            elif 'summary' in entry:
                content = entry.summary
            elif 'description' in entry:
                content = entry.description

            # Summary
            summary = entry.get('summary', '')

            # Author
            author = 'AWS'  # Default
            if 'author' in entry:
                author = entry.author
            elif 'author_detail' in entry and 'name' in entry.author_detail:
                author = entry.author_detail.name

            # Tags
            tags = []
            if 'tags' in entry:
                tags = [tag.term for tag in entry.tags]

            # Categories
            categories = []
            if 'categories' in entry:
                categories = [cat[0] for cat in entry.categories]

            # Combine tags and categories
            all_tags = list(set(tags + categories))

            # Image URL (if available in media content)
            image_url = ''
            if 'media_content' in entry and len(entry.media_content) > 0:
                image_url = entry.media_content[0].get('url', '')
            elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
                image_url = entry.media_thumbnail[0].get('url', '')

            post = {
                'url': url,
                'title': title,
                'date': date_str,
                'content': content,
                'summary': summary,
                'author': author,
                'tags': all_tags,
                'image_url': image_url,
            }

            return post

        except Exception as e:
            logger.exception(f"Failed to parse RSS entry: {e}")
            return None

    def scrape_html(self) -> List[Dict]:
        """
        Scrape posts from HTML pages (fallback).

        For AWS blogs, RSS is the primary method. HTML fallback is not implemented
        as RSS feeds are reliable and contain all necessary data.

        Returns:
            Empty list (HTML fallback not implemented)
        """
        logger.info(f"HTML scraping not implemented for {self.source_name} (RSS feed is sufficient)")
        return []
