"""
Tests for Content Processing
"""

import pytest
from scraper.utils import calculate_reading_time, extract_code_blocks, validate_post


def test_calculate_reading_time():
    """Test reading time calculation"""
    # Short text (~40 words, should be 1 min)
    text = "This is a short text. " * 20
    minutes = calculate_reading_time(text, words_per_minute=200)
    assert minutes == 1  # Minimum 1 minute

    # Long text (~400 words, should be 2 minutes)
    text = "This is a longer text with more words. " * 50
    minutes = calculate_reading_time(text, words_per_minute=200)
    assert minutes == 2

    # HTML content
    html = "<p>Test content " * 100 + "</p>"
    minutes = calculate_reading_time(html)
    assert minutes >= 1


def test_extract_code_blocks():
    """Test code block extraction"""
    html = """
    <p>Some text</p>
    <pre><code class="language-python">print("Hello")</code></pre>
    <p>More text</p>
    <pre><code>console.log("test")</code></pre>
    """

    blocks = extract_code_blocks(html)

    assert len(blocks) == 2
    assert blocks[0]['language'] == 'python'
    assert 'Hello' in blocks[0]['content']
    assert blocks[1]['language'] == 'text'


def test_validate_post_valid():
    """Test validation of valid post"""
    post = {
        'url': 'https://example.com/post',
        'title': 'Test Post Title',
        'date': '2024-02-15T10:00:00Z',
        'source': 'Test Blog',
        'content': 'This is test content. ' * 20,
    }

    is_valid, issues = validate_post(post)

    assert is_valid is True
    assert len(issues) == 0


def test_validate_post_missing_fields():
    """Test validation of post with missing fields"""
    post = {
        'title': 'Test Post',
        # Missing url, date, source
    }

    is_valid, issues = validate_post(post)

    assert is_valid is False
    assert len(issues) >= 3  # Missing url, date, source


def test_validate_post_short_content():
    """Test validation of post with short content"""
    post = {
        'url': 'https://example.com/post',
        'title': 'Test Post Title',
        'date': '2024-02-15T10:00:00Z',
        'source': 'Test Blog',
        'content': 'Too short',
    }

    is_valid, issues = validate_post(post)

    assert is_valid is False
    assert any('Content too short' in issue for issue in issues)
