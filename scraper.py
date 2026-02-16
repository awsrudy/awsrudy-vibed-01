#!/usr/bin/env python3
"""
AWS Blog Scraper
Fetches blog posts from AWS RSS feeds and creates a searchable JSON database
"""

import feedparser
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import re
from urllib.parse import urlparse

# AWS Blog RSS Feeds
AWS_FEEDS = {
    "AWS News Blog": "https://aws.amazon.com/blogs/aws/feed/",
    "Architecture Blog": "https://aws.amazon.com/blogs/architecture/feed/",
    "Big Data Blog": "https://aws.amazon.com/blogs/big-data/feed/",
    "Business Intelligence": "https://aws.amazon.com/blogs/business-intelligence/feed/",
    "Compute Blog": "https://aws.amazon.com/blogs/compute/feed/",
    "Database Blog": "https://aws.amazon.com/blogs/database/feed/",
    "DevOps Blog": "https://aws.amazon.com/blogs/devops/feed/",
    "Machine Learning": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "Mobile Blog": "https://aws.amazon.com/blogs/mobile/feed/",
    "Networking & Content Delivery": "https://aws.amazon.com/blogs/networking-and-content-delivery/feed/",
    "Security Blog": "https://aws.amazon.com/blogs/security/feed/",
    "Serverless Blog": "https://aws.amazon.com/blogs/compute/category/serverless/feed/",
    "Storage Blog": "https://aws.amazon.com/blogs/storage/feed/",
    "Startups Blog": "https://aws.amazon.com/blogs/startups/feed/",
    "Public Sector": "https://aws.amazon.com/blogs/publicsector/feed/",
    "Gaming": "https://aws.amazon.com/blogs/gametech/feed/",
    "IoT": "https://aws.amazon.com/blogs/iot/feed/",
    "Containers": "https://aws.amazon.com/blogs/containers/feed/",
    "Front-End Web & Mobile": "https://aws.amazon.com/blogs/mobile/feed/",
}


def clean_html(text: str) -> str:
    """Remove HTML tags and clean up text"""
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Limit length for descriptions
    if len(text) > 300:
        text = text[:297] + "..."

    return text


def extract_tags(entry: Any, category: str) -> List[str]:
    """Extract tags from blog entry"""
    tags = set()

    # From entry tags
    if hasattr(entry, 'tags'):
        for tag in entry.tags:
            if hasattr(tag, 'term'):
                tags.add(tag.term)

    # From categories
    if hasattr(entry, 'categories'):
        for cat in entry.categories:
            if isinstance(cat, tuple):
                tags.add(cat[0])
            else:
                tags.add(str(cat))

    # Extract AWS service names from title and description
    aws_services = [
        'EC2', 'S3', 'Lambda', 'RDS', 'DynamoDB', 'CloudFormation',
        'CloudWatch', 'IAM', 'VPC', 'ECS', 'EKS', 'Fargate',
        'API Gateway', 'Step Functions', 'SNS', 'SQS', 'Kinesis',
        'Redshift', 'EMR', 'Glue', 'Athena', 'SageMaker',
        'ElastiCache', 'Aurora', 'DocumentDB', 'Neptune',
        'Amplify', 'AppSync', 'Cognito', 'CloudFront',
        'Route 53', 'ELB', 'ALB', 'NLB', 'Direct Connect',
        'Backup', 'Storage Gateway', 'EBS', 'EFS', 'FSx',
        'CodePipeline', 'CodeBuild', 'CodeDeploy', 'CodeCommit',
        'X-Ray', 'GuardDuty', 'Security Hub', 'WAF', 'Shield',
        'KMS', 'Secrets Manager', 'Systems Manager', 'OpsWorks',
        'Lightsail', 'Batch', 'Outposts', 'Local Zones',
        'Wavelength', 'Snow Family', 'Transfer Family',
        'EventBridge', 'App Runner', 'App Mesh', 'Cloud9'
    ]

    title = entry.get('title', '')
    description = entry.get('summary', '')
    content = f"{title} {description}".lower()

    for service in aws_services:
        if service.lower() in content:
            tags.add(service)

    return sorted(list(tags))[:10]  # Limit to 10 most relevant tags


def parse_feed(feed_url: str, category: str) -> List[Dict[str, Any]]:
    """Parse a single RSS feed"""
    print(f"Fetching {category} from {feed_url}")

    try:
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            print(f"Warning: Feed parsing error for {category}: {feed.bozo_exception}")

        posts = []

        for entry in feed.entries[:20]:  # Limit to 20 most recent posts per feed
            # Get publish date
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6]).isoformat()
            else:
                pub_date = datetime.now().isoformat()

            post = {
                "title": entry.get('title', 'Untitled'),
                "link": entry.get('link', ''),
                "description": clean_html(entry.get('summary', entry.get('description', ''))),
                "category": category,
                "publishDate": pub_date,
                "tags": extract_tags(entry, category),
                "author": entry.get('author', 'AWS')
            }

            posts.append(post)

        print(f"  ✓ Fetched {len(posts)} posts from {category}")
        return posts

    except Exception as e:
        print(f"  ✗ Error fetching {category}: {str(e)}")
        return []


def scrape_all_feeds() -> List[Dict[str, Any]]:
    """Scrape all AWS blog feeds"""
    all_posts = []

    for category, feed_url in AWS_FEEDS.items():
        posts = parse_feed(feed_url, category)
        all_posts.extend(posts)

    return all_posts


def remove_duplicates(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate posts based on link"""
    seen_links = set()
    unique_posts = []

    for post in posts:
        if post['link'] not in seen_links:
            seen_links.add(post['link'])
            unique_posts.append(post)

    return unique_posts


def save_to_json(posts: List[Dict[str, Any]], output_file: str):
    """Save posts to JSON file"""
    # Sort by publish date (newest first)
    posts.sort(key=lambda x: x['publishDate'], reverse=True)

    data = {
        "lastUpdated": datetime.now().isoformat(),
        "totalPosts": len(posts),
        "posts": posts
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(posts)} posts to {output_file}")


def main():
    """Main function"""
    print("=" * 60)
    print("AWS Blog Scraper")
    print("=" * 60)

    # Scrape all feeds
    print("\nScraping AWS blog feeds...")
    posts = scrape_all_feeds()

    # Remove duplicates
    print(f"\nRemoving duplicates...")
    posts = remove_duplicates(posts)
    print(f"Total unique posts: {len(posts)}")

    # Save to JSON
    output_file = "data/blogs.json"
    save_to_json(posts, output_file)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    categories = {}
    for post in posts:
        cat = post['category']
        categories[cat] = categories.get(cat, 0) + 1

    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} posts")

    print("\n✓ Scraping completed successfully!")


if __name__ == "__main__":
    main()
