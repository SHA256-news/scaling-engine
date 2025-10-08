"""
main.py - Entry point for Bitcoin Mining News Bot

This file orchestrates the bot workflow with three distinct modes:
1. Monitor: Fetch and queue new articles (every 30 minutes)
2. Post: Generate and post tweets from queue (every 24 minutes)
3. Daily Brief: Generate comprehensive daily report (once per day)

Usage:
    python main.py --workflow monitor
    python main.py --workflow post
    python main.py --workflow daily-brief
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

import config
import bot_lib


# =============================================================================
# Logging Setup
# =============================================================================

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# =============================================================================
# Utility Functions
# =============================================================================

def load_json_file(filepath: str, default=None) -> any:
    """Load data from JSON file."""
    if default is None:
        default = []
    
    if not os.path.exists(filepath):
        return default
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json_file(filepath: str, data: any) -> bool:
    """Save data to JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def get_posted_articles_today() -> List[str]:
    """Get list of article URLs posted today."""
    posted = load_json_file(config.POSTED_ARTICLES_FILE, default=[])
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Filter to only today's posts
    today_posts = [
        p for p in posted 
        if p.get('date', '').startswith(today)
    ]
    
    return [p.get('url') for p in today_posts]


def add_posted_article(url: str, tweet_id: str = None):
    """Record that an article has been posted."""
    posted = load_json_file(config.POSTED_ARTICLES_FILE, default=[])
    
    posted.append({
        'url': url,
        'tweet_id': tweet_id,
        'date': datetime.now().isoformat(),
        'timestamp': datetime.now().timestamp()
    })
    
    # Keep only last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    posted = [
        p for p in posted 
        if datetime.fromisoformat(p['date']) > cutoff
    ]
    
    save_json_file(config.POSTED_ARTICLES_FILE, posted)


# =============================================================================
# Workflow 1: Monitor (Fetch and Queue Articles)
# =============================================================================

def workflow_monitor():
    """
    Monitor Workflow: Fetch new articles and add to queue.
    
    Runs every 30 minutes to:
    - Fetch articles from Event Registry (past 1 hour)
    - Filter based on quality criteria
    - Add new articles to posting queue
    - Cache articles for daily brief
    """
    logger.info("=" * 80)
    logger.info("Starting MONITOR workflow")
    logger.info("=" * 80)
    
    # Check API key
    if not config.EVENT_REGISTRY_API_KEY:
        logger.error("EVENT_REGISTRY_API_KEY not configured")
        return 1
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=config.MONITOR_HOURS_BACK)
    
    date_start = start_date.strftime("%Y-%m-%d")
    date_end = end_date.strftime("%Y-%m-%d")
    
    logger.info(f"Fetching articles from {date_start} to {date_end}")
    
    try:
        # Fetch articles with retry logic
        articles = bot_lib.fetch_articles_with_retry(
            api_key=config.EVENT_REGISTRY_API_KEY,
            date_start=date_start,
            date_end=date_end,
            max_articles=config.MONITOR_MAX_ARTICLES,
            max_retries=3
        )
        
        logger.info(f"Fetched {len(articles)} articles from Event Registry")
        
        if not articles:
            logger.info("No new articles found")
            return 0
        
        # Filter articles
        filtered_articles = bot_lib.filter_articles(
            articles=articles,
            blacklisted_sources=config.BLACKLISTED_SOURCES,
            blacklisted_keywords=config.BLACKLISTED_KEYWORDS,
            min_social_score=config.MIN_SOCIAL_SCORE,
            min_length=config.MIN_ARTICLE_LENGTH
        )
        
        logger.info(f"Filtered to {len(filtered_articles)} quality articles")
        
        if not filtered_articles:
            logger.info("No articles passed filters")
            return 0
        
        # Remove duplicates
        unique_articles = bot_lib.remove_duplicate_articles(filtered_articles)
        logger.info(f"Removed duplicates, {len(unique_articles)} unique articles")
        
        # Load existing queue
        queue = load_json_file(config.QUEUE_FILE, default=[])
        queue_urls = {item['url'] for item in queue}
        
        # Add new articles to queue
        new_count = 0
        for article in unique_articles:
            if article.get('url') not in queue_urls:
                queue.append({
                    'url': article['url'],
                    'title': article['title'],
                    'body': article.get('body', '')[:500],  # First 500 chars
                    'source': article.get('source', {}),
                    'image': article.get('image'),
                    'socialScore': article.get('socialScore', 0),
                    'added_at': datetime.now().isoformat()
                })
                new_count += 1
        
        logger.info(f"Added {new_count} new articles to queue")
        
        # Limit queue size
        if len(queue) > config.MAX_QUEUE_SIZE:
            queue = queue[-config.MAX_QUEUE_SIZE:]
            logger.info(f"Trimmed queue to {config.MAX_QUEUE_SIZE} articles")
        
        # Save queue
        save_json_file(config.QUEUE_FILE, queue)
        
        # Cache articles for daily brief
        cache = load_json_file(config.DAILY_BRIEF_CACHE, default=[])
        cache.extend(unique_articles)
        
        # Keep only last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        cache = [
            a for a in cache 
            if datetime.fromisoformat(a.get('date', datetime.now().isoformat())) > cutoff
        ]
        
        save_json_file(config.DAILY_BRIEF_CACHE, cache)
        logger.info(f"Cached {len(cache)} articles for daily brief")
        
        logger.info("Monitor workflow completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in monitor workflow: {e}", exc_info=True)
        return 1


# =============================================================================
# Workflow 2: Post (Generate and Post Tweets)
# =============================================================================

def workflow_post():
    """
    Post Workflow: Generate and post a tweet from the queue.
    
    Runs every 24 minutes to:
    - Check rate limits (60 tweets/day max)
    - Get next article from queue
    - Generate engaging tweet with Gemini AI
    - Optionally fetch image from Unsplash
    - Post to Twitter
    """
    logger.info("=" * 80)
    logger.info("Starting POST workflow")
    logger.info("=" * 80)
    
    # Check API keys
    required_keys = [
        'GEMINI_API_KEY',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET'
    ]
    
    missing_keys = [key for key in required_keys if not getattr(config, key)]
    if missing_keys:
        logger.error(f"Missing required API keys: {missing_keys}")
        return 1
    
    # Check rate limits
    posted_today = get_posted_articles_today()
    if len(posted_today) >= config.MAX_TWEETS_PER_DAY:
        logger.info(f"Rate limit reached: {len(posted_today)}/{config.MAX_TWEETS_PER_DAY} tweets today")
        return 0
    
    # Load queue
    queue = load_json_file(config.QUEUE_FILE, default=[])
    
    if not queue:
        logger.info("Queue is empty, nothing to post")
        return 0
    
    # Get next article
    article = queue.pop(0)
    logger.info(f"Processing article: {article['title']}")
    
    try:
        # Generate tweet content
        logger.info("Generating tweet with Gemini AI...")
        
        tweet_text = bot_lib.generate_social_media_content(
            gemini_api_key=config.GEMINI_API_KEY,
            article_title=article['title'],
            article_body=article.get('body', ''),
            max_length=config.MAX_TWEET_LENGTH - 25,  # Reserve space for URL
            platform='twitter',
            prompt_template=config.TWEET_GENERATION_PROMPT
        )
        
        if not tweet_text:
            logger.error("Failed to generate tweet content")
            return 1
        
        logger.info(f"Generated tweet: {tweet_text}")
        
        # Optionally fetch image
        image_path = None
        if config.UNSPLASH_ACCESS_KEY and article.get('image'):
            try:
                logger.info("Fetching and preparing image...")
                
                # Create image cache directory
                os.makedirs(config.IMAGE_CACHE_DIR, exist_ok=True)
                
                # Generate image query based on article
                image_query = "bitcoin mining"  # Simple default
                
                # Fetch and prepare images
                image_paths = bot_lib.fetch_and_prepare_images(
                    unsplash_access_key=config.UNSPLASH_ACCESS_KEY,
                    query=image_query,
                    output_dir=config.IMAGE_CACHE_DIR,
                    count=1
                )
                
                if image_paths:
                    image_path = image_paths[0]
                    logger.info(f"Image ready: {image_path}")
                
            except Exception as e:
                logger.warning(f"Could not fetch image: {e}")
                # Continue without image
        
        # Post to Twitter
        logger.info("Posting to Twitter...")
        
        tweet_id = bot_lib.post_to_twitter(
            api_key=config.TWITTER_API_KEY,
            api_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_secret=config.TWITTER_ACCESS_SECRET,
            text=tweet_text,
            url=article['url'],
            image_path=image_path
        )
        
        if tweet_id:
            logger.info(f"Tweet posted successfully! ID: {tweet_id}")
            
            # Record posted article
            add_posted_article(article['url'], tweet_id)
            
            # Save updated queue
            save_json_file(config.QUEUE_FILE, queue)
            
            logger.info("Post workflow completed successfully")
            return 0
        else:
            logger.error("Failed to post tweet")
            # Re-add article to queue
            queue.insert(0, article)
            save_json_file(config.QUEUE_FILE, queue)
            return 1
            
    except Exception as e:
        logger.error(f"Error in post workflow: {e}", exc_info=True)
        # Re-add article to queue
        queue.insert(0, article)
        save_json_file(config.QUEUE_FILE, queue)
        return 1


# =============================================================================
# Workflow 3: Daily Brief (Generate Daily Report)
# =============================================================================

def workflow_daily_brief():
    """
    Daily Brief Workflow: Generate comprehensive daily report.
    
    Runs once per day at midnight UTC to:
    - Aggregate all articles from past 24 hours
    - Generate comprehensive Markdown report with Gemini AI
    - Create GitHub issue with the report
    - Clear the daily cache
    """
    logger.info("=" * 80)
    logger.info("Starting DAILY BRIEF workflow")
    logger.info("=" * 80)
    
    # Check API keys
    if not config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured")
        return 1
    
    if not config.GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN not configured")
        return 1
    
    # Load cached articles
    articles = load_json_file(config.DAILY_BRIEF_CACHE, default=[])
    
    if not articles:
        logger.info("No articles in cache for daily brief")
        return 0
    
    logger.info(f"Generating daily brief from {len(articles)} articles")
    
    try:
        # Format articles for prompt
        articles_text = "\n\n".join([
            f"- **{a['title']}**\n  Source: {a.get('source', {}).get('title', 'Unknown')}\n  URL: {a['url']}"
            for a in articles[:50]  # Limit to top 50 articles
        ])
        
        # Generate brief with Gemini
        logger.info("Generating brief with Gemini AI...")
        
        # Use Gemini API to generate brief
        import google.generativeai as genai
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = config.DAILY_BRIEF_PROMPT.format(articles=articles_text)
        response = model.generate_content(prompt)
        brief_content = response.text
        
        logger.info(f"Generated brief ({len(brief_content)} characters)")
        
        # Create GitHub issue
        logger.info("Creating GitHub issue...")
        
        import requests
        
        today = datetime.now().strftime("%Y-%m-%d")
        issue_title = f"Bitcoin Mining Daily Brief - {today}"
        
        headers = {
            'Authorization': f'token {config.GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'title': issue_title,
            'body': brief_content,
            'labels': ['daily-brief', 'automated']
        }
        
        owner, repo = config.GITHUB_REPO.split('/')
        url = f'https://api.github.com/repos/{owner}/{repo}/issues'
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            issue_data = response.json()
            logger.info(f"GitHub issue created: {issue_data['html_url']}")
            
            # Clear the cache
            save_json_file(config.DAILY_BRIEF_CACHE, [])
            logger.info("Cleared daily brief cache")
            
            logger.info("Daily brief workflow completed successfully")
            return 0
        else:
            logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
            return 1
            
    except Exception as e:
        logger.error(f"Error in daily brief workflow: {e}", exc_info=True)
        return 1


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point for the bot."""
    parser = argparse.ArgumentParser(
        description='Bitcoin Mining News Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflows:
  monitor      Fetch and queue new articles (runs every 30 min)
  post         Generate and post tweets (runs every 24 min)
  daily-brief  Generate daily report (runs once per day)

Examples:
  python main.py --workflow monitor
  python main.py --workflow post
  python main.py --workflow daily-brief
        """
    )
    
    parser.add_argument(
        '--workflow',
        required=True,
        choices=['monitor', 'post', 'daily-brief'],
        help='Which workflow to run'
    )
    
    args = parser.parse_args()
    
    # Route to appropriate workflow
    workflows = {
        'monitor': workflow_monitor,
        'post': workflow_post,
        'daily-brief': workflow_daily_brief
    }
    
    workflow_func = workflows[args.workflow]
    
    try:
        exit_code = workflow_func()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
