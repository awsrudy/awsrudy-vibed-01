"""
Utility functions for AWS Blog Scraper

This module provides helper functions for date parsing, text cleaning,
URL normalization, and AWS service detection.
"""

import re
import logging
import math
from datetime import datetime
from typing import Optional, List, Set
from dateutil import parser as dateutil_parser
import pytz
from bs4 import BeautifulSoup

from scraper.config import (
    DATE_FORMATS,
    ALLOWED_HTML_TAGS,
    STRIP_HTML_TAGS,
    AWS_SERVICES,
    CONTENT_MAX_LENGTH,
    SUMMARY_MAX_LENGTH,
)

logger = logging.getLogger(__name__)


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.

    Tries multiple date formats and uses dateutil.parser as fallback.
    Returns timezone-aware datetime in UTC.

    Args:
        date_string: Date string to parse

    Returns:
        Datetime object in UTC, or None if parsing fails
    """
    if not date_string:
        return None

    # Try predefined formats first (faster)
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_string, fmt)
            # If no timezone info, assume UTC
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            # Convert to UTC
            return dt.astimezone(pytz.UTC)
        except (ValueError, TypeError):
            continue

    # Fallback to dateutil parser (handles many formats)
    try:
        dt = dateutil_parser.parse(date_string)
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        return dt.astimezone(pytz.UTC)
    except (ValueError, TypeError, dateutil_parser.ParserError) as e:
        logger.warning(f"Failed to parse date: {date_string} - {e}")
        return None


def clean_html(html_content: str, keep_tags: bool = True) -> str:
    """
    Clean HTML content by removing scripts, styles, and unwanted tags.

    Args:
        html_content: Raw HTML string
        keep_tags: If True, keep allowed HTML tags; if False, extract text only

    Returns:
        Cleaned HTML or plain text
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted tags entirely (scripts, styles, etc.)
    for tag_name in STRIP_HTML_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    if keep_tags:
        # Keep only allowed tags, strip others but preserve text
        for tag in soup.find_all(True):
            if tag.name not in ALLOWED_HTML_TAGS:
                tag.unwrap()

        # Get HTML string
        cleaned = str(soup)
    else:
        # Extract text only
        cleaned = soup.get_text(separator=' ', strip=True)

    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()

    # Truncate if too long
    if len(cleaned) > CONTENT_MAX_LENGTH:
        cleaned = cleaned[:CONTENT_MAX_LENGTH] + "..."
        logger.warning(f"Content truncated to {CONTENT_MAX_LENGTH} characters")

    return cleaned


def extract_summary(content: str, max_length: int = SUMMARY_MAX_LENGTH) -> str:
    """
    Extract a summary/excerpt from content.

    Takes first paragraph or first N characters, whichever is shorter.

    Args:
        content: Full content (HTML or text)
        max_length: Maximum summary length

    Returns:
        Summary string
    """
    if not content:
        return ""

    # If content is HTML, extract first paragraph
    if '<' in content and '>' in content:
        soup = BeautifulSoup(content, 'html.parser')
        first_p = soup.find('p')
        if first_p:
            content = first_p.get_text(strip=True)
        else:
            content = soup.get_text(separator=' ', strip=True)

    # Truncate to max length
    if len(content) > max_length:
        # Try to break at sentence boundary
        truncated = content[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.7:  # If period is reasonably close to end
            return truncated[:last_period + 1]
        else:
            return truncated.rstrip() + "..."

    return content


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing query parameters and fragments.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    if not url:
        return ""

    # Remove fragment (#)
    url = url.split('#')[0]

    # Remove query parameters (?)
    url = url.split('?')[0]

    # Remove trailing slash
    url = url.rstrip('/')

    return url


def extract_aws_services(text: str) -> List[str]:
    """
    Extract AWS service names mentioned in text.

    Uses case-insensitive matching and returns unique services.

    Args:
        text: Text to search for AWS service mentions

    Returns:
        List of AWS service names found (sorted)
    """
    if not text:
        return []

    text_lower = text.lower()
    found_services: Set[str] = set()

    for service in AWS_SERVICES:
        # Match whole word boundaries to avoid false positives
        pattern = r'\b' + re.escape(service.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_services.add(service)

    return sorted(list(found_services))


def generate_slug(title: str) -> str:
    """
    Generate a URL-friendly slug from a title.

    Args:
        title: Post title

    Returns:
        URL-safe slug
    """
    if not title:
        return ""

    # Convert to lowercase
    slug = title.lower()

    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Limit length
    if len(slug) > 100:
        slug = slug[:100].rsplit('-', 1)[0]

    return slug


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid HTTP/HTTPS URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def deduplicate_posts(posts: List[dict]) -> List[dict]:
    """
    Remove duplicate posts based on normalized URL.

    If multiple posts have the same URL, keeps the one with the earliest date.

    Args:
        posts: List of post dictionaries

    Returns:
        Deduplicated list of posts
    """
    if not posts:
        return []

    seen_urls = {}
    unique_posts = []

    for post in posts:
        url = normalize_url(post.get('url', ''))
        if not url:
            # No URL, keep the post
            unique_posts.append(post)
            continue

        if url not in seen_urls:
            seen_urls[url] = post
            unique_posts.append(post)
        else:
            # Duplicate URL found - keep the one with earlier date
            existing_post = seen_urls[url]
            existing_date = existing_post.get('date')
            new_date = post.get('date')

            if new_date and existing_date and new_date < existing_date:
                # New post is older, replace
                unique_posts.remove(existing_post)
                unique_posts.append(post)
                seen_urls[url] = post

    return unique_posts


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate reading time for text.

    Args:
        text: Text content (HTML or plain text)
        words_per_minute: Average reading speed (default: 200 wpm)

    Returns:
        Reading time in minutes (minimum 1)
    """
    if not text:
        return 1

    # Strip HTML tags for word count
    soup = BeautifulSoup(text, 'html.parser')
    plain_text = soup.get_text(separator=' ', strip=True)

    # Count words
    words = len(plain_text.split())

    # Calculate minutes
    minutes = math.ceil(words / words_per_minute)

    return max(1, minutes)  # Minimum 1 minute


def extract_code_blocks(html_content: str) -> list:
    """
    Extract code blocks from HTML content.

    Args:
        html_content: HTML string

    Returns:
        List of code block dictionaries with language and content
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')

    code_blocks = []

    # Find <pre><code> blocks
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            # Try to detect language from class
            language = 'text'
            if code.get('class'):
                for cls in code['class']:
                    if cls.startswith('language-'):
                        language = cls.replace('language-', '')
                        break

            code_blocks.append({
                'language': language,
                'content': code.get_text(),
            })

    return code_blocks


def validate_post(post: dict) -> tuple:
    """
    Validate a post has required fields and quality content.

    Args:
        post: Post dictionary

    Returns:
        Tuple of (is_valid: bool, issues: list)
    """
    issues = []

    # Required fields
    required_fields = ['url', 'title', 'date', 'source']
    for field in required_fields:
        if field not in post or not post[field]:
            issues.append(f"Missing required field: {field}")

    # URL validation
    if 'url' in post and post['url']:
        if not is_valid_url(post['url']):
            issues.append(f"Invalid URL: {post['url']}")

    # Title length (too short or too long)
    if 'title' in post and post['title']:
        title_len = len(post['title'])
        if title_len < 10:
            issues.append(f"Title too short: {title_len} characters")
        elif title_len > 300:
            issues.append(f"Title too long: {title_len} characters")

    # Content validation (should have some content)
    if 'content' in post and post['content']:
        content_len = len(post['content'])
        if content_len < 100:
            issues.append(f"Content too short: {content_len} characters")

    is_valid = len(issues) == 0
    return (is_valid, issues)
