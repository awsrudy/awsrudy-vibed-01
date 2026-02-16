"""
AWS Blog Scraper - Main Entry Point

This scraper fetches AWS blog posts from multiple sources, processes them,
and stores them in JSON format for the Jekyll site.

Usage:
    python scraper/main.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
import pytz

from scraper.config import (
    POSTS_FILE,
    SOURCES_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    PRETTY_JSON,
    JSON_INDENT,
)
from scraper.utils import parse_date

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


def load_sources() -> list:
    """
    Load blog source configuration from _data/sources.yml

    Returns:
        List of source dictionaries
    """
    try:
        import yaml
        with open(SOURCES_FILE, 'r') as f:
            data = yaml.safe_load(f)
            sources = data.get('sources', [])
            enabled_sources = [s for s in sources if s.get('enabled', True)]
            logger.info(f"Loaded {len(enabled_sources)} enabled sources from {SOURCES_FILE}")
            return enabled_sources
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")
        return []


def save_posts(posts: list):
    """
    Save posts using PostStorage

    Args:
        posts: List of post dictionaries
    """
    from scraper.storage import PostStorage

    storage = PostStorage()
    storage.save(posts, create_backup=True)


def main():
    """
    Main scraper execution with error handling and monitoring

    This is a skeleton implementation for Wave 1.
    Actual scraping logic will be implemented in Wave 2.
    """
    logger.info("=" * 60)
    logger.info("AWS Blog Scraper - Starting")
    logger.info("=" * 60)

    # Load sources
    sources = load_sources()
    if not sources:
        logger.error("No sources configured. Exiting.")
        sys.exit(1)

    logger.info(f"Sources configured: {len(sources)}")
    for source in sources:
        logger.info(f"  - {source['name']} ({source['id']})")

    # Scrape all sources with error tracking
    all_posts = []
    failed_sources = []
    successful_sources = []

    for source in sources:
        try:
            from scraper.scrapers import AWSRSSScraper

            with AWSRSSScraper(source) as scraper:
                posts = scraper.scrape()
                all_posts.extend(posts)

                logger.info(f"✓ {source['name']}: {len(posts)} posts")
                successful_sources.append(source['name'])

        except Exception as e:
            logger.error(f"✗ Failed to scrape {source['name']}: {e}")
            failed_sources.append(source['name'])
            continue

    logger.info(f"\nTotal posts scraped: {len(all_posts)}")
    logger.info(f"Successful sources: {len(successful_sources)}/{len(sources)}")

    # Critical error check: no posts scraped at all
    if len(all_posts) == 0:
        logger.error("CRITICAL: No posts scraped from any source!")
        logger.error("This may indicate a network issue or all sources are down.")
        if failed_sources:
            logger.error(f"Failed sources: {', '.join(failed_sources)}")
        # In production, send notification (email, Slack, etc.)
        sys.exit(1)

    # Warning: some sources failed
    if failed_sources:
        logger.warning(f"WARNING: {len(failed_sources)} source(s) failed: {', '.join(failed_sources)}")
        # In production, send notification

    # Deduplicate posts
    from scraper.config import ENABLE_DEDUPLICATION
    if ENABLE_DEDUPLICATION and all_posts:
        from scraper.utils import deduplicate_posts

        original_count = len(all_posts)
        all_posts = deduplicate_posts(all_posts)
        duplicates = original_count - len(all_posts)

        if duplicates > 0:
            logger.info(f"Removed {duplicates} duplicate posts")

    # Sort posts by date (newest first)
    from scraper.config import SORT_POSTS_BY_DATE
    if SORT_POSTS_BY_DATE and all_posts:
        all_posts = sorted(all_posts, key=lambda p: p['date'], reverse=True)

    # Save posts
    try:
        save_posts(all_posts)
        logger.info("✓ Posts saved successfully")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to save posts: {e}")
        sys.exit(1)

    logger.info("\n" + "=" * 60)
    logger.info("Scraper completed successfully")
    logger.info(f"Summary: {len(all_posts)} posts from {len(successful_sources)} sources")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nScraper interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Scraper failed with error: {e}")
        sys.exit(1)
