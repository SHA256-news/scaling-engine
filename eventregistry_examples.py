#!/usr/bin/env python3
"""
Event Registry Examples for Bitcoin Mining News Bot

This file contains practical examples of using the Event Registry API
for fetching Bitcoin mining news articles.

Usage:
    python eventregistry_examples.py
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import Event Registry modules
try:
    from eventregistry import (
        EventRegistry,
        QueryArticles,
        QueryArticlesIter,
        QueryItems,
        ReturnInfo,
        ArticleInfoFlags,
        RequestArticlesInfo
    )
    EVENTREGISTRY_AVAILABLE = True
except ImportError:
    print("Warning: eventregistry module not installed")
    print("Install with: pip install eventregistry")
    EVENTREGISTRY_AVAILABLE = False

# Load environment variables
load_dotenv()
API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")


# =============================================================================
# Example 1: Basic Article Search
# =============================================================================

def example_basic_search(api_key: str) -> List[Dict]:
    """
    Basic article search using concept URI.
    
    This is the simplest way to fetch articles about a specific topic.
    """
    print("\n" + "="*80)
    print("Example 1: Basic Article Search")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    # Initialize Event Registry client
    er = EventRegistry(apiKey=api_key)
    
    # Create a simple query for Bitcoin articles
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang="eng"  # English only
    )
    
    # Fetch up to 10 articles
    articles = []
    for article in q.execQuery(er, maxItems=10):
        articles.append(article)
    
    print(f"Fetched {len(articles)} Bitcoin articles")
    
    # Display first article
    if articles:
        first = articles[0]
        print(f"\nFirst article:")
        print(f"  Title: {first.get('title', 'N/A')}")
        print(f"  URL: {first.get('url', 'N/A')}")
        print(f"  Date: {first.get('date', 'N/A')}")
    
    return articles


# =============================================================================
# Example 2: Concept-Based Search with Multiple Concepts
# =============================================================================

def example_concept_based_search(api_key: str) -> List[Dict]:
    """
    Search using multiple concepts with AND/OR logic.
    
    Demonstrates how to combine concepts for more precise results.
    """
    print("\n" + "="*80)
    print("Example 2: Concept-Based Search")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # Combine Bitcoin AND Mining concepts
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="rel", maxItems=20):
        articles.append(article)
    
    print(f"Fetched {len(articles)} Bitcoin mining articles")
    
    return articles


# =============================================================================
# Example 3: Using QueryArticlesIter for Large Result Sets
# =============================================================================

def example_pagination_iterator(api_key: str) -> List[Dict]:
    """
    Use QueryArticlesIter for efficient pagination through large result sets.
    
    The iterator handles pagination automatically, making it easy to
    process thousands of articles without manual page management.
    """
    print("\n" + "="*80)
    print("Example 3: Pagination with Iterator")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # Query for articles from the last 7 days
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    # Process articles in batches
    articles = []
    batch_size = 25
    processed = 0
    
    for article in q.execQuery(er, sortBy="date", maxItems=100):
        articles.append(article)
        processed += 1
        
        # Print progress every batch
        if processed % batch_size == 0:
            print(f"Processed {processed} articles...")
    
    print(f"Total fetched: {len(articles)} articles")
    
    return articles


# =============================================================================
# Example 4: Configuring ReturnInfo for Different Use Cases
# =============================================================================

def example_return_info_minimal(api_key: str) -> List[Dict]:
    """
    Configure minimal return info for fast filtering.
    
    When you only need basic info to filter articles, request only
    the fields you need to reduce payload size and improve speed.
    """
    print("\n" + "="*80)
    print("Example 4a: Minimal ReturnInfo")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang="eng"
    )
    
    # Request only essential fields
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            url=True,
            date=True,
            source=True
        )
    ))
    
    articles = []
    for article in q.execQuery(er, maxItems=10):
        articles.append(article)
        print(f"  Title: {article.get('title', 'N/A')[:60]}...")
        print(f"  Source: {article.get('source', {}).get('title', 'N/A')}")
    
    return articles


def example_return_info_social_media(api_key: str) -> List[Dict]:
    """
    Configure return info for social media posting.
    
    Request fields needed for creating social media posts:
    title, body, URL, image, and social metrics.
    """
    print("\n" + "="*80)
    print("Example 4b: Social Media ReturnInfo")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        lang="eng"
    )
    
    # Request fields for social media
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            body=True,
            url=True,
            image=True,
            socialScore=True,
            sentiment=True,
            date=True
        )
    ))
    
    articles = []
    for article in q.execQuery(er, sortBy="socialScore", maxItems=10):
        articles.append(article)
        print(f"\n  Title: {article.get('title', 'N/A')}")
        print(f"  Social Score: {article.get('socialScore', 0)}")
        print(f"  Sentiment: {article.get('sentiment', 0)}")
        print(f"  Has Image: {'Yes' if article.get('image') else 'No'}")
    
    return articles


def example_return_info_comprehensive(api_key: str) -> List[Dict]:
    """
    Configure comprehensive return info for detailed analysis.
    
    Request all available fields when you need complete article data.
    """
    print("\n" + "="*80)
    print("Example 4c: Comprehensive ReturnInfo")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang="eng"
    )
    
    # Request all fields
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            body=True,
            url=True,
            date=True,
            time=True,
            authors=True,
            concepts=True,
            categories=True,
            location=True,
            sentiment=True,
            image=True,
            socialScore=True,
            duplicateList=True,
            originalArticle=True
        )
    ))
    
    articles = []
    for article in q.execQuery(er, maxItems=5):
        articles.append(article)
        print(f"\n  Title: {article.get('title', 'N/A')}")
        print(f"  Authors: {len(article.get('authors', []))} author(s)")
        print(f"  Concepts: {len(article.get('concepts', []))} concept(s)")
        print(f"  Categories: {len(article.get('categories', []))} category(ies)")
    
    return articles


# =============================================================================
# Example 5: Filtering by Source, Language, and Sentiment
# =============================================================================

def example_filtering_by_source(api_key: str) -> List[Dict]:
    """
    Filter articles by specific news sources.
    
    Demonstrates how to include or exclude specific sources.
    """
    print("\n" + "="*80)
    print("Example 5a: Filtering by Source")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # Include only specific high-quality sources
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        sourceUri=["reuters.com", "bloomberg.com", "bbc.co.uk"],
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, maxItems=10):
        articles.append(article)
        source = article.get('source', {}).get('title', 'Unknown')
        print(f"  {article.get('title', 'N/A')[:60]}...")
        print(f"    Source: {source}")
    
    return articles


def example_filtering_multiple_languages(api_key: str) -> List[Dict]:
    """
    Fetch articles in multiple languages.
    
    Event Registry supports 100+ languages.
    """
    print("\n" + "="*80)
    print("Example 5b: Multiple Languages")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # English, Spanish, and French
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang=["eng", "spa", "fra"]
    )
    
    articles = []
    for article in q.execQuery(er, maxItems=15):
        articles.append(article)
    
    print(f"Fetched {len(articles)} articles in multiple languages")
    
    return articles


def example_filtering_by_sentiment(api_key: str) -> List[Dict]:
    """
    Filter articles by sentiment (positive/negative).
    
    Demonstrates manual filtering based on sentiment score.
    """
    print("\n" + "="*80)
    print("Example 5c: Filtering by Sentiment")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        lang="eng"
    )
    
    # Request sentiment data
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            url=True,
            sentiment=True
        )
    ))
    
    positive_articles = []
    neutral_articles = []
    negative_articles = []
    
    for article in q.execQuery(er, maxItems=50):
        sentiment = article.get('sentiment', 0)
        
        if sentiment > 0.2:
            positive_articles.append(article)
        elif sentiment < -0.2:
            negative_articles.append(article)
        else:
            neutral_articles.append(article)
    
    print(f"Positive articles: {len(positive_articles)}")
    print(f"Neutral articles: {len(neutral_articles)}")
    print(f"Negative articles: {len(negative_articles)}")
    
    return positive_articles + neutral_articles + negative_articles


# =============================================================================
# Example 6: Sorting Strategies
# =============================================================================

def example_sorting_by_date(api_key: str) -> List[Dict]:
    """
    Sort articles by publication date (newest first).
    
    Best for breaking news and latest developments.
    """
    print("\n" + "="*80)
    print("Example 6a: Sort by Date")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=10):
        articles.append(article)
        print(f"  {article.get('date', 'N/A')}: {article.get('title', 'N/A')[:60]}...")
    
    return articles


def example_sorting_by_social_score(api_key: str) -> List[Dict]:
    """
    Sort by social media engagement (most viral first).
    
    Best for finding trending content for social media posting.
    """
    print("\n" + "="*80)
    print("Example 6b: Sort by Social Score")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        lang="eng"
    )
    
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            socialScore=True,
            url=True
        )
    ))
    
    articles = []
    for article in q.execQuery(er, sortBy="socialScore", maxItems=10):
        articles.append(article)
        score = article.get('socialScore', 0)
        print(f"  Score {score}: {article.get('title', 'N/A')[:60]}...")
    
    return articles


def example_sorting_by_source_importance(api_key: str) -> List[Dict]:
    """
    Sort by source authority/reputation.
    
    Best for credible, authoritative news.
    """
    print("\n" + "="*80)
    print("Example 6c: Sort by Source Importance")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="sourceImportance", maxItems=10):
        articles.append(article)
        source = article.get('source', {}).get('title', 'Unknown')
        print(f"  {source}: {article.get('title', 'N/A')[:60]}...")
    
    return articles


# =============================================================================
# Example 7: Recent Activity Monitoring
# =============================================================================

def example_recent_activity_monitoring(api_key: str) -> List[Dict]:
    """
    Monitor recent Bitcoin mining activity (last 24 hours).
    
    Perfect for real-time news monitoring and alerting.
    """
    print("\n" + "="*80)
    print("Example 7: Recent Activity Monitoring")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # Last 24 hours
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR(["ASIC", "hashrate", "difficulty"]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng",
        isDuplicateFilter="skipDuplicates"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=25):
        articles.append(article)
    
    print(f"Found {len(articles)} articles in the last 24 hours")
    
    if articles:
        print("\nMost recent:")
        for article in articles[:5]:
            print(f"  {article.get('date', 'N/A')} - {article.get('title', 'N/A')[:60]}...")
    
    return articles


# =============================================================================
# Example 8: Getting Trending Concepts
# =============================================================================

def example_trending_concepts(api_key: str) -> List[str]:
    """
    Find trending concepts related to Bitcoin mining.
    
    Helps discover emerging topics and trends.
    """
    print("\n" + "="*80)
    print("Example 8: Trending Concepts")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # Fetch articles and extract concepts
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        lang="eng"
    )
    
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            concepts=True,
            title=True
        )
    ))
    
    # Count concept frequencies
    concept_counts = {}
    
    for article in q.execQuery(er, maxItems=100):
        concepts = article.get('concepts', [])
        for concept in concepts:
            label = concept.get('label', {}).get('eng', '')
            if label:
                concept_counts[label] = concept_counts.get(label, 0) + 1
    
    # Sort by frequency
    trending = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 10 trending concepts:")
    for concept, count in trending[:10]:
        print(f"  {concept}: {count} mentions")
    
    return [c[0] for c in trending]


# =============================================================================
# Example 9: Error Handling and Retry Logic
# =============================================================================

def example_error_handling(api_key: str) -> Optional[List[Dict]]:
    """
    Demonstrate proper error handling and retry logic.
    
    Essential for production deployments.
    """
    print("\n" + "="*80)
    print("Example 9: Error Handling and Retry Logic")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return None
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            er = EventRegistry(apiKey=api_key)
            
            q = QueryArticlesIter(
                conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
                lang="eng"
            )
            
            articles = []
            for article in q.execQuery(er, maxItems=10):
                articles.append(article)
            
            print(f"✓ Successfully fetched {len(articles)} articles")
            return articles
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "invalid api key" in error_msg:
                print("✗ Error: Invalid API key")
                return None
            
            elif "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10
                    print(f"⚠ Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print("✗ Error: Rate limit exceeded after max retries")
                    return None
            
            else:
                print(f"✗ Error: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5)
    
    return None


# =============================================================================
# Example 10: Complete Bitcoin Mining News Fetcher
# =============================================================================

def example_complete_fetcher(api_key: str) -> List[Dict]:
    """
    Complete example: Fetch, filter, and process Bitcoin mining news.
    
    This combines multiple techniques into a production-ready function.
    """
    print("\n" + "="*80)
    print("Example 10: Complete Bitcoin Mining News Fetcher")
    print("="*80)
    
    if not EVENTREGISTRY_AVAILABLE:
        print("Skipping - eventregistry not installed")
        return []
    
    er = EventRegistry(apiKey=api_key)
    
    # Date range: last 7 days
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Build query
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR([
            "ASIC",
            "hashrate",
            "mining pool",
            "mining rig",
            "difficulty"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng",
        isDuplicateFilter="skipDuplicates"
    )
    
    # Configure return info
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            body=True,
            url=True,
            date=True,
            source=True,
            image=True,
            socialScore=True,
            sentiment=True,
            concepts=True
        )
    ))
    
    # Fetch articles
    print("Fetching articles...")
    articles = []
    blacklisted_sources = ["example-spam.com", "low-quality.com"]
    
    for article in q.execQuery(er, sortBy="socialScore", maxItems=100):
        # Filter out blacklisted sources
        source_uri = article.get('source', {}).get('uri', '')
        if source_uri in blacklisted_sources:
            continue
        
        # Filter by quality (require title and URL)
        if not article.get('title') or not article.get('url'):
            continue
        
        # Filter very negative sentiment
        if article.get('sentiment', 0) < -0.5:
            continue
        
        articles.append(article)
    
    print(f"Fetched {len(articles)} high-quality articles")
    
    # Display summary
    if articles:
        print("\nTop 5 articles by social score:")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('title', 'N/A')}")
            print(f"   Source: {article.get('source', {}).get('title', 'Unknown')}")
            print(f"   Date: {article.get('date', 'N/A')}")
            print(f"   Social Score: {article.get('socialScore', 0)}")
            print(f"   Sentiment: {article.get('sentiment', 0):.2f}")
            print(f"   URL: {article.get('url', 'N/A')}")
    
    return articles


# =============================================================================
# Main Function - Run All Examples
# =============================================================================

def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("EVENT REGISTRY API EXAMPLES")
    print("Bitcoin Mining News Bot")
    print("="*80)
    
    # Check API key
    if not API_KEY:
        print("\n✗ Error: EVENT_REGISTRY_API_KEY not found in environment")
        print("Please set your API key in .env file:")
        print("  EVENT_REGISTRY_API_KEY=your_key_here")
        return
    
    if not EVENTREGISTRY_AVAILABLE:
        print("\n✗ Error: eventregistry module not installed")
        print("Install with: pip install eventregistry")
        return
    
    print(f"\n✓ API Key found")
    print(f"✓ Event Registry module loaded")
    
    # Run examples
    examples = [
        ("Basic Search", example_basic_search),
        ("Concept-Based Search", example_concept_based_search),
        ("Pagination Iterator", example_pagination_iterator),
        ("Minimal ReturnInfo", example_return_info_minimal),
        ("Social Media ReturnInfo", example_return_info_social_media),
        ("Comprehensive ReturnInfo", example_return_info_comprehensive),
        ("Filter by Source", example_filtering_by_source),
        ("Multiple Languages", example_filtering_multiple_languages),
        ("Filter by Sentiment", example_filtering_by_sentiment),
        ("Sort by Date", example_sorting_by_date),
        ("Sort by Social Score", example_sorting_by_social_score),
        ("Sort by Source Importance", example_sorting_by_source_importance),
        ("Recent Activity Monitoring", example_recent_activity_monitoring),
        ("Trending Concepts", example_trending_concepts),
        ("Error Handling", example_error_handling),
        ("Complete Fetcher", example_complete_fetcher),
    ]
    
    # Run each example
    for name, func in examples:
        try:
            func(API_KEY)
            time.sleep(1)  # Rate limiting between examples
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
