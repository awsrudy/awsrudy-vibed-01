"""
Tests for Storage System
"""

import pytest
import json
from pathlib import Path
from scraper.storage import PostStorage


@pytest.fixture
def temp_posts_file(tmp_path):
    """Temporary posts file for testing"""
    return tmp_path / "posts.json"


@pytest.fixture
def sample_posts():
    """Sample posts for testing"""
    return [
        {
            'url': 'https://example.com/post1',
            'title': 'Test Post 1',
            'date': '2024-02-15T10:00:00Z',
            'source': 'AWS News Blog',
            'services': ['Lambda', 'S3'],
            'reading_time': 5,
            'has_code': True,
        },
        {
            'url': 'https://example.com/post2',
            'title': 'Test Post 2',
            'date': '2024-02-16T10:00:00Z',
            'source': 'AWS Architecture Blog',
            'services': ['Lambda', 'DynamoDB'],
            'reading_time': 7,
            'has_code': False,
        },
    ]


def test_storage_save(temp_posts_file, sample_posts):
    """Test saving posts"""
    storage = PostStorage(temp_posts_file)
    storage.save(sample_posts, create_backup=False)

    assert temp_posts_file.exists()

    # Load and verify
    with open(temp_posts_file, 'r') as f:
        data = json.load(f)

    assert data['metadata']['total_posts'] == 2
    assert len(data['posts']) == 2


def test_storage_load(temp_posts_file, sample_posts):
    """Test loading posts"""
    storage = PostStorage(temp_posts_file)
    storage.save(sample_posts, create_backup=False)

    loaded_posts = storage.load()

    assert len(loaded_posts) == 2
    assert loaded_posts[0]['title'] == 'Test Post 1'


def test_storage_backup(temp_posts_file, sample_posts):
    """Test backup creation"""
    storage = PostStorage(temp_posts_file)
    storage.save(sample_posts, create_backup=False)

    # Create backup
    backup_file = storage.create_backup()

    assert backup_file is not None
    assert backup_file.exists()
    assert 'posts_' in backup_file.name


def test_storage_statistics(temp_posts_file, sample_posts):
    """Test statistics generation"""
    storage = PostStorage(temp_posts_file)
    stats = storage.generate_statistics(sample_posts)

    assert len(stats['sources']) == 2
    assert stats['posts_per_source']['AWS News Blog'] == 1
    assert stats['posts_with_code'] == 1
    assert stats['average_reading_time'] == 6  # (5 + 7) // 2
    assert len(stats['top_services']) >= 2
