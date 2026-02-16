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
    Save posts to JSON file

    Args:
        posts: List of post dictionaries
    """
    try:
        output = {
            "posts": posts,
            "last_updated": datetime.now(pytz.UTC).isoformat(),
            "total_posts": len(posts),
            "sources": list(set(post.get('source', 'unknown') for post in posts)),
        }

        with open(POSTS_FILE, 'w') as f:
            if PRETTY_JSON:
                json.dump(output, f, indent=JSON_INDENT, ensure_ascii=False)
            else:
                json.dump(output, f, ensure_ascii=False)

        logger.info(f"Saved {len(posts)} posts to {POSTS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save posts: {e}")
        sys.exit(1)


def main():
    """
    Main scraper execution

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

    # Placeholder: In Wave 2, we'll implement actual scraping here
    logger.info("\nNote: Scraping logic will be implemented in Wave 2")
    logger.info("For now, creating empty posts file...")

    # Create empty posts file
    save_posts([])

    logger.info("\n" + "=" * 60)
    logger.info("Scraper completed successfully")
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
