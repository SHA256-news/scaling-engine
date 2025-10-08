"""
tools.py - CLI Utilities for Bitcoin Mining News Bot

This file provides command-line tools for:
- Testing individual functions
- Debugging workflows
- Manual overrides
- Data inspection

Usage:
    python tools.py <command> [options]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

import config
import bot_lib


def cmd_test_fetch(args):
    """Test article fetching from Event Registry."""
    print("\n" + "=" * 80)
    print("Testing Article Fetching")
    print("=" * 80)
    
    if not config.EVENT_REGISTRY_API_KEY:
        print("ERROR: EVENT_REGISTRY_API_KEY not configured")
        return 1
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    date_start = start_date.strftime("%Y-%m-%d")
    date_end = end_date.strftime("%Y-%m-%d")
    
    print(f"\nFetching articles from {date_start} to {date_end}...")
    print(f"Max articles: {args.count}")
    
    try:
        articles = bot_lib.fetch_articles_with_retry(
            api_key=config.EVENT_REGISTRY_API_KEY,
            date_start=date_start,
            date_end=date_end,
            max_articles=args.count
        )
        
        print(f"\n✓ Fetched {len(articles)} articles")
        
        if articles:
            print("\nSample Articles:")
            for i, article in enumerate(articles[:5], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article.get('source', {}).get('title', 'Unknown')}")
                print(f"   Social Score: {article.get('socialScore', 0)}")
                print(f"   URL: {article['url']}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


def cmd_test_filter(args):
    """Test article filtering."""
    print("\n" + "=" * 80)
    print("Testing Article Filtering")
    print("=" * 80)
    
    if not config.EVENT_REGISTRY_API_KEY:
        print("ERROR: EVENT_REGISTRY_API_KEY not configured")
        return 1
    
    # First fetch articles
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    date_start = start_date.strftime("%Y-%m-%d")
    date_end = end_date.strftime("%Y-%m-%d")
    
    print(f"\nFetching articles from {date_start} to {date_end}...")
    
    try:
        articles = bot_lib.fetch_articles_with_retry(
            api_key=config.EVENT_REGISTRY_API_KEY,
            date_start=date_start,
            date_end=date_end,
            max_articles=args.count
        )
        
        print(f"Fetched {len(articles)} articles")
        
        # Apply filters
        print("\nApplying filters...")
        filtered = bot_lib.filter_articles(
            articles=articles,
            blacklisted_sources=config.BLACKLISTED_SOURCES,
            blacklisted_keywords=config.BLACKLISTED_KEYWORDS,
            min_social_score=config.MIN_SOCIAL_SCORE,
            min_length=config.MIN_ARTICLE_LENGTH
        )
        
        print(f"✓ {len(filtered)} articles passed filters")
        print(f"  Filtered out: {len(articles) - len(filtered)} articles")
        
        if filtered:
            print("\nFiltered Articles:")
            for i, article in enumerate(filtered[:5], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article.get('source', {}).get('title', 'Unknown')}")
                print(f"   Social Score: {article.get('socialScore', 0)}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


def cmd_test_generate(args):
    """Test content generation with Gemini."""
    print("\n" + "=" * 80)
    print("Testing Content Generation")
    print("=" * 80)
    
    if not config.GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not configured")
        return 1
    
    # Use provided text or fetch an article
    if args.title and args.body:
        title = args.title
        body = args.body
    else:
        print("\nFetching a sample article...")
        
        if not config.EVENT_REGISTRY_API_KEY:
            print("ERROR: EVENT_REGISTRY_API_KEY not configured")
            return 1
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        articles = bot_lib.fetch_articles_with_retry(
            api_key=config.EVENT_REGISTRY_API_KEY,
            date_start=start_date.strftime("%Y-%m-%d"),
            date_end=end_date.strftime("%Y-%m-%d"),
            max_articles=1
        )
        
        if not articles:
            print("No articles found")
            return 1
        
        article = articles[0]
        title = article['title']
        body = article.get('body', '')[:500]
        
        print(f"\nArticle: {title}")
    
    print("\nGenerating tweet content...")
    
    try:
        tweet = bot_lib.generate_social_media_content(
            gemini_api_key=config.GEMINI_API_KEY,
            article_title=title,
            article_body=body,
            max_length=config.MAX_TWEET_LENGTH - 25,
            platform='twitter',
            prompt_template=config.TWEET_GENERATION_PROMPT
        )
        
        print(f"\n✓ Generated tweet ({len(tweet)} chars):")
        print("-" * 80)
        print(tweet)
        print("-" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


def cmd_inspect_queue(args):
    """Inspect the article queue."""
    print("\n" + "=" * 80)
    print("Article Queue Inspection")
    print("=" * 80)
    
    try:
        with open(config.QUEUE_FILE, 'r') as f:
            queue = json.load(f)
    except FileNotFoundError:
        print("\nQueue file not found (empty queue)")
        return 0
    except Exception as e:
        print(f"\nError reading queue: {e}")
        return 1
    
    print(f"\nQueue size: {len(queue)} articles")
    
    if not queue:
        print("Queue is empty")
        return 0
    
    print("\nQueue contents:")
    for i, article in enumerate(queue[:args.count], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Added: {article.get('added_at', 'Unknown')}")
        print(f"   Social Score: {article.get('socialScore', 0)}")
        print(f"   URL: {article['url']}")
    
    if len(queue) > args.count:
        print(f"\n... and {len(queue) - args.count} more articles")
    
    return 0


def cmd_inspect_posted(args):
    """Inspect posted articles."""
    print("\n" + "=" * 80)
    print("Posted Articles Inspection")
    print("=" * 80)
    
    try:
        with open(config.POSTED_ARTICLES_FILE, 'r') as f:
            posted = json.load(f)
    except FileNotFoundError:
        print("\nNo posted articles file found")
        return 0
    except Exception as e:
        print(f"\nError reading posted articles: {e}")
        return 1
    
    print(f"\nTotal posted: {len(posted)} articles")
    
    # Count by day
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for p in posted if p.get('date', '').startswith(today))
    
    print(f"Posted today: {today_count}/{config.MAX_TWEETS_PER_DAY}")
    
    if not posted:
        return 0
    
    print("\nRecent posts:")
    for i, post in enumerate(sorted(posted, key=lambda x: x.get('date', ''), reverse=True)[:args.count], 1):
        print(f"\n{i}. {post.get('date', 'Unknown date')}")
        print(f"   URL: {post['url']}")
        if post.get('tweet_id'):
            print(f"   Tweet ID: {post['tweet_id']}")
    
    return 0


def cmd_clear_queue(args):
    """Clear the article queue."""
    print("\n" + "=" * 80)
    print("Clear Article Queue")
    print("=" * 80)
    
    if not args.confirm:
        print("\nWARNING: This will delete all queued articles!")
        response = input("Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("Cancelled")
            return 0
    
    try:
        with open(config.QUEUE_FILE, 'w') as f:
            json.dump([], f)
        
        print("\n✓ Queue cleared")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


def cmd_config_check(args):
    """Check configuration."""
    print("\n" + "=" * 80)
    print("Configuration Check")
    print("=" * 80)
    
    print("\nAPI Keys:")
    keys = {
        'EVENT_REGISTRY_API_KEY': config.EVENT_REGISTRY_API_KEY,
        'GEMINI_API_KEY': config.GEMINI_API_KEY,
        'TWITTER_API_KEY': config.TWITTER_API_KEY,
        'TWITTER_API_SECRET': config.TWITTER_API_SECRET,
        'TWITTER_ACCESS_TOKEN': config.TWITTER_ACCESS_TOKEN,
        'TWITTER_ACCESS_SECRET': config.TWITTER_ACCESS_SECRET,
        'UNSPLASH_ACCESS_KEY': config.UNSPLASH_ACCESS_KEY,
        'GITHUB_TOKEN': config.GITHUB_TOKEN
    }
    
    for key, value in keys.items():
        status = "✓ Set" if value else "✗ Not set"
        print(f"  {key}: {status}")
    
    print("\nWorkflow Requirements:")
    workflows = {
        'monitor': ['EVENT_REGISTRY_API_KEY'],
        'post': ['GEMINI_API_KEY', 'TWITTER_API_KEY', 'TWITTER_API_SECRET', 
                 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET'],
        'daily-brief': ['GEMINI_API_KEY', 'GITHUB_TOKEN']
    }
    
    for workflow, required_keys in workflows.items():
        missing = [k for k in required_keys if not getattr(config, k)]
        if missing:
            print(f"  {workflow}: ✗ Missing {missing}")
        else:
            print(f"  {workflow}: ✓ Ready")
    
    print("\nFiles:")
    files = [
        config.QUEUE_FILE,
        config.POSTED_ARTICLES_FILE,
        config.DAILY_BRIEF_CACHE,
        config.LOG_FILE
    ]
    
    import os
    for filepath in files:
        exists = "✓ Exists" if os.path.exists(filepath) else "○ Not created yet"
        print(f"  {filepath}: {exists}")
    
    return 0


def main():
    """Main entry point for tools CLI."""
    parser = argparse.ArgumentParser(
        description='Bitcoin Mining News Bot - CLI Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Test fetch
    parser_fetch = subparsers.add_parser('test-fetch', help='Test article fetching')
    parser_fetch.add_argument('--days', type=int, default=1, help='Days to look back')
    parser_fetch.add_argument('--count', type=int, default=10, help='Max articles to fetch')
    
    # Test filter
    parser_filter = subparsers.add_parser('test-filter', help='Test article filtering')
    parser_filter.add_argument('--days', type=int, default=1, help='Days to look back')
    parser_filter.add_argument('--count', type=int, default=50, help='Max articles to fetch')
    
    # Test generate
    parser_generate = subparsers.add_parser('test-generate', help='Test content generation')
    parser_generate.add_argument('--title', help='Article title')
    parser_generate.add_argument('--body', help='Article body')
    
    # Inspect queue
    parser_queue = subparsers.add_parser('inspect-queue', help='Inspect article queue')
    parser_queue.add_argument('--count', type=int, default=10, help='Number of articles to show')
    
    # Inspect posted
    parser_posted = subparsers.add_parser('inspect-posted', help='Inspect posted articles')
    parser_posted.add_argument('--count', type=int, default=10, help='Number of posts to show')
    
    # Clear queue
    parser_clear = subparsers.add_parser('clear-queue', help='Clear article queue')
    parser_clear.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # Config check
    parser_config = subparsers.add_parser('config-check', help='Check configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    commands = {
        'test-fetch': cmd_test_fetch,
        'test-filter': cmd_test_filter,
        'test-generate': cmd_test_generate,
        'inspect-queue': cmd_inspect_queue,
        'inspect-posted': cmd_inspect_posted,
        'clear-queue': cmd_clear_queue,
        'config-check': cmd_config_check
    }
    
    handler = commands[args.command]
    
    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
