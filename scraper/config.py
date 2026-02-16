"""
Configuration for AWS Blog Scraper

This module contains all configuration constants for the scraper,
including paths, timeouts, and source information.
"""

import os
from pathlib import Path
from typing import Dict, List

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent
SCRAPER_DIR = PROJECT_ROOT / "scraper"
DATA_DIR = PROJECT_ROOT / "_data"
POSTS_FILE = DATA_DIR / "posts.json"
SOURCES_FILE = DATA_DIR / "sources.yml"

# HTTP Configuration
USER_AGENT = "Mozilla/5.0 (compatible; AWSBlogScraper/1.0; +https://github.com/awsrudy/awsrudy-vibed-01)"
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Scraping Configuration
MAX_POSTS_PER_SOURCE = 100  # Limit posts per source to avoid overwhelming the site
FETCH_DELAY = 1.0  # Delay between requests (seconds) - be respectful
CONTENT_MAX_LENGTH = 50000  # Max characters for post content
SUMMARY_MAX_LENGTH = 500  # Max characters for summary/excerpt

# Date Configuration
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with timezone
    "%Y-%m-%d %H:%M:%S",    # Standard datetime
    "%Y-%m-%d",             # Date only
    "%a, %d %b %Y %H:%M:%S %Z",  # RSS format
    "%a, %d %b %Y %H:%M:%S %z",  # RSS format with timezone
]

# Content Cleaning
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'a', 'img',
    'code', 'pre',
    'blockquote',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]

STRIP_HTML_TAGS = [
    'script', 'style', 'iframe', 'object', 'embed',
    'form', 'input', 'button', 'select', 'textarea',
]

# AWS Services List (for tagging)
AWS_SERVICES = [
    # Compute
    "EC2", "Lambda", "Elastic Beanstalk", "Lightsail", "Batch", "Fargate",
    "ECS", "EKS", "App Runner",

    # Storage
    "S3", "EBS", "EFS", "FSx", "Glacier", "Storage Gateway", "Backup",

    # Database
    "RDS", "DynamoDB", "ElastiCache", "Neptune", "DocumentDB", "Redshift",
    "Aurora", "MemoryDB", "Keyspaces",

    # Networking
    "VPC", "CloudFront", "Route 53", "API Gateway", "Direct Connect",
    "Global Accelerator", "App Mesh", "Cloud Map",

    # Security
    "IAM", "Cognito", "Secrets Manager", "KMS", "WAF", "Shield",
    "GuardDuty", "Inspector", "Macie", "Security Hub", "Certificate Manager",

    # Developer Tools
    "CodeCommit", "CodeBuild", "CodeDeploy", "CodePipeline", "Cloud9",
    "CodeArtifact", "CodeStar", "X-Ray",

    # Management
    "CloudWatch", "CloudFormation", "CloudTrail", "Config", "Systems Manager",
    "OpsWorks", "Control Tower", "Organizations", "Service Catalog",

    # Analytics
    "Athena", "EMR", "Kinesis", "QuickSight", "Glue", "Data Pipeline",
    "Lake Formation", "MSK",

    # Machine Learning
    "SageMaker", "Rekognition", "Comprehend", "Translate", "Polly",
    "Transcribe", "Lex", "Personalize", "Forecast", "Textract",

    # Integration
    "SQS", "SNS", "Step Functions", "EventBridge", "AppFlow", "MQ",

    # Containers
    "ECR", "ECS", "EKS", "Fargate", "App Runner", "Copilot",
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Feature Flags
ENABLE_HTML_FALLBACK = True  # If RSS fails, try HTML parsing
ENABLE_DEDUPLICATION = True  # Remove duplicate posts across sources
ENABLE_CONTENT_CLEANING = True  # Clean HTML content
ENABLE_SERVICE_TAGGING = True  # Extract AWS service mentions

# Output Configuration
PRETTY_JSON = True  # Format JSON with indentation
JSON_INDENT = 2
SORT_POSTS_BY_DATE = True  # Sort posts by date (newest first)
INCLUDE_METADATA = True  # Include scraper metadata (last_updated, source, etc.)
