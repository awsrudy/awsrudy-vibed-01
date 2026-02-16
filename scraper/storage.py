"""
JSON Storage System

Manages saving, loading, and backing up scraped posts data.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pytz

from scraper.config import POSTS_FILE, DATA_DIR, PRETTY_JSON, JSON_INDENT

logger = logging.getLogger(__name__)


class PostStorage:
    """
    Manages storage of scraped posts in JSON format.

    Features:
    - Save posts to JSON file
    - Load existing posts
    - Create backups before overwriting
    - Generate statistics
    """

    def __init__(self, posts_file: Path = POSTS_FILE):
        """
        Initialize storage

        Args:
            posts_file: Path to posts JSON file
        """
        self.posts_file = posts_file
        self.backup_dir = DATA_DIR / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def save(self, posts: List[Dict], create_backup: bool = True):
        """
        Save posts to JSON file.

        Args:
            posts: List of post dictionaries
            create_backup: Whether to create backup of existing file
        """
        # Create backup if file exists
        if create_backup and self.posts_file.exists():
            self.create_backup()

        # Generate statistics
        stats = self.generate_statistics(posts)

        # Build output structure
        output = {
            "posts": posts,
            "metadata": {
                "last_updated": datetime.now(pytz.UTC).isoformat(),
                "total_posts": len(posts),
                "sources": stats['sources'],
                "date_range": stats['date_range'],
                "top_services": stats['top_services'][:10],  # Top 10 services
            },
            "statistics": stats,
        }

        # Write to file
        try:
            with open(self.posts_file, 'w', encoding='utf-8') as f:
                if PRETTY_JSON:
                    json.dump(output, f, indent=JSON_INDENT, ensure_ascii=False)
                else:
                    json.dump(output, f, ensure_ascii=False)

            logger.info(f"Saved {len(posts)} posts to {self.posts_file}")

        except Exception as e:
            logger.exception(f"Failed to save posts: {e}")
            raise

    def load(self) -> List[Dict]:
        """
        Load posts from JSON file.

        Returns:
            List of post dictionaries, or empty list if file doesn't exist
        """
        if not self.posts_file.exists():
            logger.warning(f"Posts file not found: {self.posts_file}")
            return []

        try:
            with open(self.posts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            posts = data.get('posts', [])
            logger.info(f"Loaded {len(posts)} posts from {self.posts_file}")

            return posts

        except Exception as e:
            logger.exception(f"Failed to load posts: {e}")
            return []

    def create_backup(self) -> Optional[Path]:
        """
        Create a backup of the current posts file.

        Returns:
            Path to backup file, or None if backup failed
        """
        if not self.posts_file.exists():
            logger.warning("No posts file to backup")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"posts_{timestamp}.json"

            shutil.copy2(self.posts_file, backup_file)

            logger.info(f"Created backup: {backup_file}")
            return backup_file

        except Exception as e:
            logger.exception(f"Failed to create backup: {e}")
            return None

    def generate_statistics(self, posts: List[Dict]) -> Dict:
        """
        Generate statistics about posts.

        Args:
            posts: List of post dictionaries

        Returns:
            Dictionary of statistics
        """
        if not posts:
            return {
                'sources': [],
                'posts_per_source': {},
                'date_range': {},
                'top_services': [],
                'posts_with_code': 0,
                'average_reading_time': 0,
            }

        # Sources
        sources = list(set(post.get('source', 'Unknown') for post in posts))

        # Posts per source
        posts_per_source = {}
        for post in posts:
            source = post.get('source', 'Unknown')
            posts_per_source[source] = posts_per_source.get(source, 0) + 1

        # Date range
        dates = [post.get('date') for post in posts if post.get('date')]
        if dates:
            dates = sorted(dates)
            date_range = {
                'earliest': dates[0],
                'latest': dates[-1],
            }
        else:
            date_range = {}

        # AWS services mentioned
        service_count = {}
        for post in posts:
            services = post.get('services', [])
            for service in services:
                service_count[service] = service_count.get(service, 0) + 1

        # Sort by count
        top_services = sorted(
            [{'service': s, 'count': c} for s, c in service_count.items()],
            key=lambda x: x['count'],
            reverse=True
        )

        # Posts with code
        posts_with_code = sum(1 for post in posts if post.get('has_code', False))

        # Average reading time
        reading_times = [post.get('reading_time', 0) for post in posts]
        average_reading_time = sum(reading_times) // len(reading_times) if reading_times else 0

        return {
            'sources': sources,
            'posts_per_source': posts_per_source,
            'date_range': date_range,
            'top_services': top_services,
            'posts_with_code': posts_with_code,
            'average_reading_time': average_reading_time,
        }
