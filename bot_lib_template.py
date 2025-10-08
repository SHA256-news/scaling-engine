"""
bot_lib.py - Core Business Logic for Bitcoin Mining News Bot

This module contains all stateless functions for the bot's business logic:
- Fetching news articles from Event Registry
- Filtering content based on quality criteria
- AI content generation
- Social media posting
- Utility functions for data processing

Design Principles:
- All functions are stateless (no global variables)
- Each function does one thing well
- Pure functions where possible
- Clear input parameters and return values
- Comprehensive docstrings

See agent.md for complete architecture guidelines.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


# =============================================================================
# Event Registry Integration Functions
# =============================================================================

def fetch_bitcoin_mining_articles(
    api_key: str,
    date_start: str,
    date_end: str,
    max_articles: int = 100
) -> List[Dict]:
    """
    Fetch Bitcoin mining related articles from Event Registry.
    
    Uses concept-based search for more accurate results. Combines:
    - Concept URIs for "Bitcoin" and "Mining" (semantic understanding)
    - Keywords for specific mining-related terms (ASIC, hashrate, etc.)
    - Date range filtering to get recent articles
    - Social score sorting for high-engagement content
    
    This function demonstrates best practices for Event Registry integration:
    1. Use concept URIs for main topics (Bitcoin, Mining)
    2. Combine with keywords for specific terminology
    3. Configure ReturnInfo to request only needed fields
    4. Sort by socialScore to prioritize viral/trending content
    5. Filter duplicates to avoid repetitive content
    
    Args:
        api_key: Event Registry API key for authentication
        date_start: Start date in YYYY-MM-DD format (e.g., "2024-01-01")
        date_end: End date in YYYY-MM-DD format (e.g., "2024-01-31")
        max_articles: Maximum number of articles to fetch (default: 100)
    
    Returns:
        List of article dictionaries with the following structure:
        [
            {
                'title': str,           # Article title
                'body': str,            # Full article text
                'url': str,             # Article URL
                'date': str,            # Publication date (YYYY-MM-DD)
                'time': str,            # Publication time
                'source': {
                    'uri': str,         # Source identifier
                    'title': str        # Source name
                },
                'image': str,           # Image URL (if available)
                'socialScore': float,   # Social media engagement score
                'sentiment': float,     # Sentiment (-1 to 1, negative to positive)
                'concepts': List[Dict], # Related concepts
                ...
            },
            ...
        ]
    
    Raises:
        ValueError: If date_start or date_end is invalid format
        APIError: If Event Registry API call fails
        RateLimitError: If API rate limit is exceeded
    
    Example:
        >>> articles = fetch_bitcoin_mining_articles(
        ...     api_key="your_key",
        ...     date_start="2024-01-01",
        ...     date_end="2024-01-31",
        ...     max_articles=50
        ... )
        >>> print(f"Fetched {len(articles)} articles")
        Fetched 50 articles
        >>> print(articles[0]['title'])
        'Bitcoin Mining Difficulty Reaches New All-Time High'
    
    Notes:
        - Uses QueryArticlesIter for efficient pagination
        - Automatically skips duplicate articles
        - Filters to English language articles only
        - Social score ranges from 0 (no engagement) to 100+ (viral)
        - Concepts help understand article topics beyond keywords
        
    See Also:
        - eventregistry_guide.md: Complete guide to Event Registry API
        - eventregistry_examples.py: More usage examples
        - fetch_articles_with_retry(): Version with automatic retry logic
    """
    from eventregistry import (
        EventRegistry,
        QueryArticlesIter,
        QueryItems,
        ReturnInfo,
        ArticleInfoFlags
    )
    
    # Validate date format
    try:
        datetime.strptime(date_start, "%Y-%m-%d")
        datetime.strptime(date_end, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}")
    
    # Initialize Event Registry client
    er = EventRegistry(apiKey=api_key)
    
    # Concept URIs for Bitcoin and Mining
    # These provide semantic understanding beyond keyword matching
    bitcoin_concept = "http://en.wikipedia.org/wiki/Bitcoin"
    mining_concept = "http://en.wikipedia.org/wiki/Mining"
    
    # Create query with concept-based search
    # AND condition ensures articles match BOTH Bitcoin AND Mining
    query = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            bitcoin_concept,
            mining_concept
        ]),
        # OR condition for specific mining keywords
        # These catch articles that may not be tagged with concepts
        keywords=QueryItems.OR([
            "ASIC",
            "hashrate",
            "mining pool",
            "mining rig",
            "difficulty adjustment",
            "block reward"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng",  # English only
        isDuplicateFilter="skipDuplicates"  # Skip duplicate articles
    )
    
    # Configure what data to return
    # Only request fields we'll use to minimize payload size
    query.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,           # Article headline
            body=True,            # Full article text
            url=True,             # Article URL
            date=True,            # Publication date
            time=True,            # Publication time
            source=True,          # Source information
            image=True,           # Article image
            socialScore=True,     # Social media engagement
            sentiment=True,       # Sentiment analysis
            concepts=True         # Related concepts
        )
    ))
    
    # Fetch articles sorted by social engagement
    # Higher social score = more viral/trending content
    articles = []
    for article in query.execQuery(er, sortBy="socialScore", maxItems=max_articles):
        articles.append(article)
    
    return articles


def fetch_articles_with_retry(
    api_key: str,
    date_start: str,
    date_end: str,
    max_articles: int = 100,
    max_retries: int = 3
) -> List[Dict]:
    """
    Fetch articles with automatic retry logic for transient failures.
    
    This is a production-ready version of fetch_bitcoin_mining_articles()
    that includes exponential backoff for rate limiting and transient errors.
    
    Args:
        api_key: Event Registry API key
        date_start: Start date (YYYY-MM-DD)
        date_end: End date (YYYY-MM-DD)
        max_articles: Maximum articles to fetch
        max_retries: Maximum number of retry attempts
    
    Returns:
        List of article dictionaries
    
    Raises:
        APIError: If all retry attempts fail
    
    Example:
        >>> articles = fetch_articles_with_retry(
        ...     api_key="your_key",
        ...     date_start="2024-01-01",
        ...     date_end="2024-01-31",
        ...     max_retries=5
        ... )
    """
    for attempt in range(max_retries):
        try:
            return fetch_bitcoin_mining_articles(
                api_key,
                date_start,
                date_end,
                max_articles
            )
        except Exception as e:
            error_msg = str(e).lower()
            
            # Don't retry authentication errors
            if "invalid api key" in error_msg or "authentication" in error_msg:
                raise
            
            # Retry with exponential backoff for rate limits
            if "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # 10, 20, 40 seconds
                    print(f"Rate limit hit, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise
            
            # Retry other transient errors
            elif attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 5  # 5, 10, 20 seconds
                print(f"Error occurred, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
    return []


def get_trending_mining_articles(
    api_key: str,
    days_back: int = 7,
    max_articles: int = 50
) -> List[Dict]:
    """
    Fetch trending Bitcoin mining articles from recent days.
    
    Optimized for finding viral content with high social media engagement.
    
    Args:
        api_key: Event Registry API key
        days_back: Number of days to look back (default: 7)
        max_articles: Maximum articles to fetch (default: 50)
    
    Returns:
        List of trending articles sorted by social score
    
    Example:
        >>> trending = get_trending_mining_articles(api_key, days_back=3)
        >>> for article in trending[:5]:
        ...     print(f"{article['socialScore']}: {article['title']}")
    """
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    return fetch_bitcoin_mining_articles(
        api_key,
        date_start,
        date_end,
        max_articles
    )


# =============================================================================
# Article Filtering Functions
# =============================================================================

def filter_articles(
    articles: List[Dict],
    blacklisted_sources: List[str],
    blacklisted_keywords: List[str],
    min_social_score: float = 0.0,
    min_sentiment: float = -1.0
) -> List[Dict]:
    """
    Filter articles based on quality criteria.
    
    Applies multiple filters to ensure only high-quality, relevant articles
    are processed. This helps reduce spam, low-quality content, and
    off-topic articles.
    
    Filtering criteria:
    1. Blacklisted sources - Remove articles from known spam/low-quality sites
    2. Blacklisted keywords - Skip articles containing spam indicators
    3. Minimum social score - Ensure minimum engagement level
    4. Minimum sentiment - Filter out extremely negative articles
    5. Required fields - Ensure article has title, URL, and body
    
    Args:
        articles: List of article dictionaries to filter
        blacklisted_sources: List of source URIs to exclude (e.g., ["spam-site.com"])
        blacklisted_keywords: List of keywords to exclude (e.g., ["clickbait", "sponsored"])
        min_social_score: Minimum social score threshold (default: 0.0)
        min_sentiment: Minimum sentiment score, -1 to 1 (default: -1.0)
    
    Returns:
        Filtered list of article dictionaries that pass all criteria
    
    Example:
        >>> articles = fetch_bitcoin_mining_articles(api_key, "2024-01-01", "2024-01-31")
        >>> blacklist_sources = ["example-spam.com", "low-quality-news.com"]
        >>> blacklist_keywords = ["clickbait", "sponsored", "promotion"]
        >>> filtered = filter_articles(
        ...     articles,
        ...     blacklist_sources,
        ...     blacklist_keywords,
        ...     min_social_score=5.0,
        ...     min_sentiment=-0.5
        ... )
        >>> print(f"Filtered from {len(articles)} to {len(filtered)} articles")
        Filtered from 100 to 42 articles
    
    Notes:
        - Case-insensitive keyword matching in title and body
        - Source matching uses the 'uri' field from source dict
        - Returns empty list if all articles are filtered out
        - Preserves original article order
    """
    filtered = []
    
    for article in articles:
        # Check required fields
        if not article.get('title') or not article.get('url') or not article.get('body'):
            continue
        
        # Check blacklisted sources
        source_uri = article.get('source', {}).get('uri', '').lower()
        if any(blacklisted.lower() in source_uri for blacklisted in blacklisted_sources):
            continue
        
        # Check blacklisted keywords in title and body
        title = article.get('title', '').lower()
        body = article.get('body', '').lower()
        
        if any(keyword.lower() in title or keyword.lower() in body 
               for keyword in blacklisted_keywords):
            continue
        
        # Check social score threshold
        social_score = article.get('socialScore', 0)
        if social_score < min_social_score:
            continue
        
        # Check sentiment threshold
        sentiment = article.get('sentiment', 0)
        if sentiment < min_sentiment:
            continue
        
        filtered.append(article)
    
    return filtered


def remove_duplicate_articles(articles: List[Dict]) -> List[Dict]:
    """
    Remove duplicate articles based on URL.
    
    Keeps the first occurrence of each unique URL.
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        List with duplicates removed
    
    Example:
        >>> articles = [
        ...     {'url': 'https://example.com/article1', 'title': 'Article 1'},
        ...     {'url': 'https://example.com/article2', 'title': 'Article 2'},
        ...     {'url': 'https://example.com/article1', 'title': 'Article 1 Duplicate'},
        ... ]
        >>> unique = remove_duplicate_articles(articles)
        >>> print(len(unique))
        2
    """
    seen_urls = set()
    unique_articles = []
    
    for article in articles:
        url = article.get('url')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    return unique_articles


# =============================================================================
# Content Generation Functions (Placeholder)
# =============================================================================

def generate_social_media_content(
    article: Dict,
    gemini_api_key: str,
    prompt_template: str,
    max_length: int = 280
) -> str:
    """
    Generate social media content from article using Gemini API.
    
    Creates engaging social media posts based on article content.
    
    Args:
        article: Article dictionary with 'title', 'body', 'url'
        gemini_api_key: Google Gemini API key
        prompt_template: Template for content generation prompt
        max_length: Maximum character length (default: 280 for Twitter)
    
    Returns:
        Generated social media content string
    
    Raises:
        APIError: If Gemini API call fails
        ValueError: If article is missing required fields
    
    Example:
        >>> article = {
        ...     'title': 'Bitcoin Mining Difficulty Increases',
        ...     'body': 'The Bitcoin network difficulty has increased by 5%...',
        ...     'url': 'https://example.com/article'
        ... }
        >>> template = "Create a tweet about: {title}. Include relevant hashtags."
        >>> content = generate_social_media_content(article, api_key, template)
        >>> print(content)
        '🚀 Bitcoin Mining Difficulty Increases by 5%! #Bitcoin #Mining #Crypto'
    
    Notes:
        - Automatically includes article URL if space permits
        - Adds relevant hashtags (#Bitcoin, #Mining)
        - Validates content length before returning
    """
    # TODO: Implement Gemini API integration
    # See agent.md for Gemini API guidelines
    pass


# =============================================================================
# Social Media Posting Functions (Placeholder)
# =============================================================================

def post_to_twitter(
    twitter_api_key: str,
    twitter_api_secret: str,
    access_token: str,
    access_token_secret: str,
    content: str
) -> Dict:
    """
    Post content to Twitter.
    
    Args:
        twitter_api_key: Twitter API key
        twitter_api_secret: Twitter API secret
        access_token: Twitter access token
        access_token_secret: Twitter access token secret
        content: Tweet content (max 280 characters)
    
    Returns:
        Dictionary with post details:
        {
            'success': bool,
            'tweet_id': str,
            'url': str,
            'error': Optional[str]
        }
    
    Raises:
        ValueError: If content exceeds 280 characters
        APIError: If Twitter API call fails
    
    Example:
        >>> result = post_to_twitter(
        ...     api_key, api_secret, token, token_secret,
        ...     "🚀 Bitcoin Mining Update! #Bitcoin #Mining"
        ... )
        >>> if result['success']:
        ...     print(f"Posted: {result['url']}")
    """
    # TODO: Implement Twitter API integration
    pass


# =============================================================================
# Utility Functions
# =============================================================================

def get_date_range(days_back: int = 7) -> tuple[str, str]:
    """
    Get date range for querying articles.
    
    Args:
        days_back: Number of days to look back (default: 7)
    
    Returns:
        Tuple of (date_start, date_end) in YYYY-MM-DD format
    
    Example:
        >>> start, end = get_date_range(7)
        >>> print(f"From {start} to {end}")
        From 2024-01-24 to 2024-01-31
    """
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return date_start, date_end


def save_articles_to_json(articles: List[Dict], filename: str) -> None:
    """
    Save articles to JSON file.
    
    Args:
        articles: List of article dictionaries
        filename: Output filename (e.g., "articles.json")
    
    Example:
        >>> articles = fetch_bitcoin_mining_articles(api_key, "2024-01-01", "2024-01-31")
        >>> save_articles_to_json(articles, "bitcoin_mining_articles.json")
    """
    import json
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)


def load_articles_from_json(filename: str) -> List[Dict]:
    """
    Load articles from JSON file.
    
    Args:
        filename: Input filename (e.g., "articles.json")
    
    Returns:
        List of article dictionaries
    
    Example:
        >>> articles = load_articles_from_json("bitcoin_mining_articles.json")
        >>> print(f"Loaded {len(articles)} articles")
    """
    import json
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_article_summary(articles: List[Dict], max_display: int = 10) -> None:
    """
    Print summary of articles to console.
    
    Args:
        articles: List of article dictionaries
        max_display: Maximum number of articles to display
    
    Example:
        >>> articles = fetch_bitcoin_mining_articles(api_key, "2024-01-01", "2024-01-31")
        >>> print_article_summary(articles, max_display=5)
    """
    print(f"\n{'='*80}")
    print(f"Article Summary: {len(articles)} total articles")
    print(f"{'='*80}\n")
    
    for i, article in enumerate(articles[:max_display], 1):
        title = article.get('title', 'No title')
        source = article.get('source', {}).get('title', 'Unknown')
        date = article.get('date', 'Unknown')
        social_score = article.get('socialScore', 0)
        
        print(f"{i}. {title}")
        print(f"   Source: {source} | Date: {date} | Social Score: {social_score}")
        print(f"   URL: {article.get('url', 'N/A')}\n")
    
    if len(articles) > max_display:
        print(f"... and {len(articles) - max_display} more articles")


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    """
    Example usage of bot_lib functions.
    
    This demonstrates the typical workflow:
    1. Fetch articles from Event Registry
    2. Filter articles based on quality criteria
    3. Generate social media content
    4. Post to social media platforms
    """
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    EVENT_REGISTRY_API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")
    
    # Example configuration
    BLACKLISTED_SOURCES = [
        "example-spam.com",
        "low-quality-news.com"
    ]
    
    BLACKLISTED_KEYWORDS = [
        "clickbait",
        "sponsored",
        "promotion",
        "advertisement"
    ]
    
    # Fetch articles
    print("Fetching Bitcoin mining articles...")
    date_start, date_end = get_date_range(days_back=7)
    
    articles = fetch_bitcoin_mining_articles(
        api_key=EVENT_REGISTRY_API_KEY,
        date_start=date_start,
        date_end=date_end,
        max_articles=100
    )
    
    print(f"Fetched {len(articles)} articles")
    
    # Filter articles
    print("Filtering articles...")
    filtered_articles = filter_articles(
        articles,
        BLACKLISTED_SOURCES,
        BLACKLISTED_KEYWORDS,
        min_social_score=5.0,
        min_sentiment=-0.5
    )
    
    print(f"Filtered to {len(filtered_articles)} articles")
    
    # Print summary
    print_article_summary(filtered_articles, max_display=10)
    
    # Save to file
    save_articles_to_json(filtered_articles, "bitcoin_mining_articles.json")
    print("\n✓ Saved articles to bitcoin_mining_articles.json")
