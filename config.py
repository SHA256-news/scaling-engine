"""
config.py - Configuration for Bitcoin Mining News Bot

This file contains all configuration data for the bot:
- API keys and credentials
- Filter lists (blacklisted sources, keywords, etc.)
- Prompt templates for AI content generation
- Bot settings and parameters

Contains NO logic - purely configuration data.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# API Configuration
# =============================================================================

# Event Registry API (for fetching news articles)
EVENT_REGISTRY_API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")

# Gemini API (for AI content generation)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Twitter API (for posting tweets)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Unsplash API (for fetching images)
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# GitHub API (for creating issues)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "SHA256-news/scaling-engine")

# =============================================================================
# Content Filtering Configuration
# =============================================================================

# Blacklisted news sources (low quality, spam, etc.)
BLACKLISTED_SOURCES = [
    "example-spam-site.com",
    "clickbait-news.com",
    "low-quality-source.com"
]

# Blacklisted keywords (filter out irrelevant content)
BLACKLISTED_KEYWORDS = [
    "sponsored",
    "advertisement",
    "crypto scam",
    "get rich quick"
]

# Minimum social score threshold (0-100+)
MIN_SOCIAL_SCORE = 5

# Minimum article body length (characters)
MIN_ARTICLE_LENGTH = 200

# =============================================================================
# Twitter Configuration
# =============================================================================

# Rate limiting
MAX_TWEETS_PER_DAY = 60
TWEET_INTERVAL_MINUTES = 24

# Tweet character limits
MAX_TWEET_LENGTH = 280
MAX_TWEET_WITH_MEDIA = 280

# =============================================================================
# Article Queue Configuration
# =============================================================================

# Queue storage paths
QUEUE_FILE = "article_queue.json"
POSTED_ARTICLES_FILE = "posted_articles.json"
DAILY_BRIEF_CACHE = "daily_brief_cache.json"

# Queue settings
MAX_QUEUE_SIZE = 100
QUEUE_RETENTION_DAYS = 7

# =============================================================================
# Workflow Configuration
# =============================================================================

# Monitoring workflow settings (runs every 30 minutes)
MONITOR_HOURS_BACK = 1  # Look back 1 hour for new articles
MONITOR_MAX_ARTICLES = 50

# Posting workflow settings (runs every 24 minutes)
POST_RETRY_ATTEMPTS = 3
POST_TIMEOUT_SECONDS = 30

# Daily brief workflow settings (runs once per day)
BRIEF_HOURS_BACK = 24
BRIEF_MAX_ARTICLES = 200

# =============================================================================
# AI Content Generation - Prompt Templates
# =============================================================================

# Tweet generation prompt
TWEET_GENERATION_PROMPT = """
You are a Bitcoin mining news expert. Generate an engaging, informative tweet about this article.

Article Title: {title}
Article Summary: {summary}

Requirements:
- Maximum {max_length} characters
- Include relevant hashtags (#Bitcoin #Mining #BTC)
- Be informative but concise
- Maintain professional tone
- Focus on key insights
- Do NOT include the article URL (it will be added separately)

Generate only the tweet text, nothing else:
"""

# Daily brief generation prompt
DAILY_BRIEF_PROMPT = """
You are a Bitcoin mining analyst. Create a comprehensive daily brief summarizing today's key developments in Bitcoin mining.

Today's Articles:
{articles}

Requirements:
- Use Markdown formatting
- Start with an executive summary (2-3 sentences)
- Organize by themes (hashrate, difficulty, energy, regulation, etc.)
- Include key statistics and quotes
- Maintain professional, analytical tone
- Be comprehensive but concise
- End with market implications

Generate the daily brief:
"""

# Image query generation prompt
IMAGE_QUERY_PROMPT = """
Based on this article title: "{title}"

Generate a 2-3 word search query for finding a relevant image from Unsplash.
Focus on visual concepts like: bitcoin, mining hardware, data center, technology, cryptocurrency

Query:
"""

# =============================================================================
# Logging Configuration
# =============================================================================

# Log file paths
LOG_FILE = "bot.log"
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# =============================================================================
# Image Configuration
# =============================================================================

# Unsplash settings
UNSPLASH_IMAGE_COUNT = 1
UNSPLASH_ORIENTATION = "landscape"

# Twitter image optimization
TWITTER_IMAGE_SIZE = (1600, 900)
TWITTER_IMAGE_QUALITY = 85
TWITTER_MAX_IMAGE_SIZE_MB = 5

# Image storage
IMAGE_CACHE_DIR = "/tmp/bitcoin_mining_images"

# =============================================================================
# Validation
# =============================================================================

def validate_config():
    """
    Validate that required configuration is present.
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required API keys for each workflow
    workflows = {
        'monitor': ['EVENT_REGISTRY_API_KEY'],
        'post': ['GEMINI_API_KEY', 'TWITTER_API_KEY', 'TWITTER_API_SECRET', 
                 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET'],
        'daily-brief': ['GEMINI_API_KEY', 'GITHUB_TOKEN']
    }
    
    # Optional: UNSPLASH_ACCESS_KEY for images
    
    return len(errors) == 0, errors


def get_workflow_config(workflow_name):
    """
    Get configuration specific to a workflow.
    
    Args:
        workflow_name: One of 'monitor', 'post', 'daily-brief'
    
    Returns:
        dict: Configuration for the specified workflow
    """
    configs = {
        'monitor': {
            'hours_back': MONITOR_HOURS_BACK,
            'max_articles': MONITOR_MAX_ARTICLES,
            'queue_file': QUEUE_FILE,
            'cache_file': DAILY_BRIEF_CACHE
        },
        'post': {
            'queue_file': QUEUE_FILE,
            'posted_file': POSTED_ARTICLES_FILE,
            'retry_attempts': POST_RETRY_ATTEMPTS,
            'timeout': POST_TIMEOUT_SECONDS,
            'max_tweets_per_day': MAX_TWEETS_PER_DAY
        },
        'daily-brief': {
            'hours_back': BRIEF_HOURS_BACK,
            'max_articles': BRIEF_MAX_ARTICLES,
            'cache_file': DAILY_BRIEF_CACHE
        }
    }
    
    return configs.get(workflow_name, {})
