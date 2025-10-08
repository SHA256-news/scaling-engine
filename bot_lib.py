"""
bot_lib.py - Core Business Logic for Bitcoin Mining News Bot

This module contains all stateless functions for the bot's business logic:
- Fetching news articles from Event Registry
- Filtering content based on quality criteria
- AI content generation
- Image fetching and optimization (Unsplash API integration)
- Social media posting with media attachments
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
from typing import List, Dict, Optional, Tuple
import time
import os
import io


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
    # Note: QueryArticlesIter returns all fields by default, so no need to call setRequestedResult
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
# Image Fetching and Optimization Functions
# =============================================================================

def fetch_unsplash_images(
    unsplash_access_key: str,
    query: str,
    count: int = 2,
    orientation: str = "landscape"
) -> List[Dict]:
    """
    Fetch images from Unsplash API related to a search query.
    
    Retrieves free, royalty-free images from Unsplash based on the query.
    Perfect for Bitcoin mining related imagery.
    
    Args:
        unsplash_access_key: Unsplash API access key
        query: Search query (e.g., "bitcoin mining", "cryptocurrency")
        count: Number of images to fetch (default: 2, max: 30)
        orientation: Image orientation - "landscape", "portrait", or "squarish"
    
    Returns:
        List of image dictionaries with structure:
        [
            {
                'id': str,              # Unique image ID
                'url': str,             # Full resolution image URL
                'download_url': str,    # Download link
                'width': int,           # Original width
                'height': int,          # Original height
                'description': str,     # Image description
                'alt_description': str, # Alt text
                'photographer': str,    # Photographer name
                'photographer_url': str # Photographer profile URL
            },
            ...
        ]
    
    Raises:
        ValueError: If count exceeds 30 or is less than 1
        APIError: If Unsplash API call fails
    
    Example:
        >>> images = fetch_unsplash_images(
        ...     unsplash_key,
        ...     query="bitcoin mining",
        ...     count=2
        ... )
        >>> print(f"Fetched {len(images)} images")
        Fetched 2 images
        >>> print(images[0]['photographer'])
        'John Doe'
    
    Notes:
        - All images are free to use under Unsplash License
        - Always credit photographer when possible
        - API rate limit: 50 requests/hour (free tier)
        - Use specific queries for better results
    """
    import requests
    
    if count < 1 or count > 30:
        raise ValueError("Count must be between 1 and 30")
    
    # Unsplash API endpoint
    url = "https://api.unsplash.com/search/photos"
    
    headers = {
        "Authorization": f"Client-ID {unsplash_access_key}"
    }
    
    params = {
        "query": query,
        "per_page": count,
        "orientation": orientation
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for result in data.get('results', []):
            images.append({
                'id': result.get('id'),
                'url': result.get('urls', {}).get('full'),
                'download_url': result.get('urls', {}).get('raw'),
                'width': result.get('width'),
                'height': result.get('height'),
                'description': result.get('description', ''),
                'alt_description': result.get('alt_description', ''),
                'photographer': result.get('user', {}).get('name', 'Unknown'),
                'photographer_url': result.get('user', {}).get('links', {}).get('html', '')
            })
        
        return images
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Unsplash API error: {e}")


def download_image(image_url: str, output_path: str) -> str:
    """
    Download an image from a URL to local storage.
    
    Args:
        image_url: URL of the image to download
        output_path: Local path where image will be saved
    
    Returns:
        Path to the downloaded image file
    
    Raises:
        IOError: If download or file write fails
    
    Example:
        >>> path = download_image(
        ...     "https://images.unsplash.com/photo-123",
        ...     "/tmp/bitcoin_mining.jpg"
        ... )
        >>> print(f"Downloaded to: {path}")
        Downloaded to: /tmp/bitcoin_mining.jpg
    """
    import requests
    
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path
    
    except requests.exceptions.RequestException as e:
        raise IOError(f"Failed to download image: {e}")


def optimize_image_for_twitter(
    input_path: str,
    output_path: Optional[str] = None,
    target_size: Tuple[int, int] = (1600, 900),
    quality: int = 85
) -> str:
    """
    Optimize an image for Twitter posting.
    
    Resizes and compresses images to Twitter's recommended specifications:
    - Aspect ratio: 16:9 (1600x900 pixels)
    - Maximum file size: 5MB
    - Format: JPEG for photos, PNG for graphics
    
    Args:
        input_path: Path to the input image
        output_path: Path for optimized image (defaults to input_path with _optimized suffix)
        target_size: Target dimensions as (width, height) tuple (default: 1600x900)
        quality: JPEG quality 1-100 (default: 85)
    
    Returns:
        Path to the optimized image file
    
    Raises:
        FileNotFoundError: If input image doesn't exist
        ValueError: If image cannot be processed
    
    Example:
        >>> optimized = optimize_image_for_twitter(
        ...     "/tmp/bitcoin.jpg",
        ...     target_size=(1600, 900),
        ...     quality=85
        ... )
        >>> print(f"Optimized: {optimized}")
        Optimized: /tmp/bitcoin_optimized.jpg
    
    Notes:
        - Maintains aspect ratio by cropping to fit
        - Centers crop for best composition
        - Reduces file size while maintaining quality
        - Twitter supports up to 4 images per tweet
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raise ImportError("Pillow library required: pip install Pillow")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")
    
    # Generate output path if not provided
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_optimized{ext}"
    
    try:
        # Open and process image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Calculate dimensions to fit target aspect ratio
            target_width, target_height = target_size
            target_aspect = target_width / target_height
            current_aspect = img.width / img.height
            
            if current_aspect > target_aspect:
                # Image is wider - crop width
                new_width = int(img.height * target_aspect)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            elif current_aspect < target_aspect:
                # Image is taller - crop height
                new_height = int(img.width / target_aspect)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))
            
            # Resize to target dimensions
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        return output_path
    
    except Exception as e:
        raise ValueError(f"Failed to optimize image: {e}")


def fetch_and_prepare_images(
    unsplash_access_key: str,
    query: str,
    output_dir: str = "/tmp/bitcoin_images",
    count: int = 2
) -> List[str]:
    """
    Fetch images from Unsplash and prepare them for Twitter posting.
    
    Complete workflow:
    1. Search Unsplash for relevant images
    2. Download images to local storage
    3. Optimize images to Twitter specifications
    
    Args:
        unsplash_access_key: Unsplash API access key
        query: Search query for images
        output_dir: Directory to store downloaded images
        count: Number of images to fetch (default: 2)
    
    Returns:
        List of paths to optimized images ready for Twitter posting
    
    Raises:
        Exception: If image fetching or processing fails
    
    Example:
        >>> image_paths = fetch_and_prepare_images(
        ...     unsplash_key,
        ...     query="bitcoin mining hardware",
        ...     count=2
        ... )
        >>> print(f"Prepared {len(image_paths)} images")
        Prepared 2 images
        >>> for path in image_paths:
        ...     print(f"  - {path}")
          - /tmp/bitcoin_images/image_1_optimized.jpg
          - /tmp/bitcoin_images/image_2_optimized.jpg
    
    Notes:
        - Creates output directory if it doesn't exist
        - Automatically cleans up raw downloads
        - Returns empty list if no images found
        - Safe to use in automated workflows
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch images from Unsplash
    images = fetch_unsplash_images(unsplash_access_key, query, count)
    
    if not images:
        return []
    
    optimized_paths = []
    
    for i, image in enumerate(images):
        try:
            # Download image
            raw_path = os.path.join(output_dir, f"image_{i+1}_raw.jpg")
            download_image(image['download_url'], raw_path)
            
            # Optimize for Twitter
            optimized_path = os.path.join(output_dir, f"image_{i+1}_optimized.jpg")
            optimize_image_for_twitter(raw_path, optimized_path)
            
            optimized_paths.append(optimized_path)
            
            # Clean up raw image
            if os.path.exists(raw_path):
                os.remove(raw_path)
        
        except Exception as e:
            print(f"Warning: Failed to process image {i+1}: {e}")
            continue
    
    return optimized_paths


# =============================================================================
# Social Media Posting Functions (Placeholder)
# =============================================================================

def post_to_twitter(
    twitter_api_key: str,
    twitter_api_secret: str,
    access_token: str,
    access_token_secret: str,
    content: str,
    media_paths: Optional[List[str]] = None
) -> Dict:
    """
    Post content to Twitter with optional image attachments.
    
    Args:
        twitter_api_key: Twitter API key
        twitter_api_secret: Twitter API secret
        access_token: Twitter access token
        access_token_secret: Twitter access token secret
        content: Tweet content (max 280 characters)
        media_paths: Optional list of paths to image files (max 4 images)
    
    Returns:
        Dictionary with post details:
        {
            'success': bool,
            'tweet_id': str,
            'url': str,
            'media_ids': List[str],  # IDs of uploaded media
            'error': Optional[str]
        }
    
    Raises:
        ValueError: If content exceeds 280 characters or more than 4 images
        APIError: If Twitter API call fails
    
    Example:
        >>> # Post with text only
        >>> result = post_to_twitter(
        ...     api_key, api_secret, token, token_secret,
        ...     "🚀 Bitcoin Mining Update! #Bitcoin #Mining"
        ... )
        >>> 
        >>> # Post with images
        >>> image_paths = fetch_and_prepare_images(unsplash_key, "bitcoin mining", count=2)
        >>> result = post_to_twitter(
        ...     api_key, api_secret, token, token_secret,
        ...     "🚀 Bitcoin Mining Update! #Bitcoin #Mining",
        ...     media_paths=image_paths
        ... )
        >>> if result['success']:
        ...     print(f"Posted: {result['url']}")
        ...     print(f"Media IDs: {result['media_ids']}")
    
    Notes:
        - Twitter supports up to 4 images per tweet
        - Images must be under 5MB each
        - Supported formats: JPEG, PNG, GIF, WEBP
        - Media is uploaded before tweet is posted
    """
    if media_paths and len(media_paths) > 4:
        raise ValueError("Twitter supports maximum 4 images per tweet")
    
    # TODO: Implement Twitter API integration with media upload
    # Steps:
    # 1. Upload media files using Twitter media upload API
    # 2. Get media IDs from upload response
    # 3. Create tweet with media IDs attached
    # 4. Return success status with tweet and media details
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
    
    # Example: Fetch and prepare images for Bitcoin mining content
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    
    if UNSPLASH_ACCESS_KEY and filtered_articles:
        print("\n" + "="*80)
        print("Fetching and optimizing images...")
        print("="*80)
        
        # Use the first article's title/concepts for image search
        article = filtered_articles[0]
        search_query = "bitcoin mining"  # Could be derived from article content
        
        try:
            image_paths = fetch_and_prepare_images(
                unsplash_access_key=UNSPLASH_ACCESS_KEY,
                query=search_query,
                output_dir="/tmp/bitcoin_images",
                count=2
            )
            
            print(f"\n✓ Prepared {len(image_paths)} images for Twitter posting:")
            for i, path in enumerate(image_paths, 1):
                file_size = os.path.getsize(path) / 1024  # KB
                print(f"   {i}. {path} ({file_size:.1f} KB)")
            
            # Example: Post to Twitter with images
            # result = post_to_twitter(
            #     twitter_api_key=TWITTER_API_KEY,
            #     twitter_api_secret=TWITTER_API_SECRET,
            #     access_token=TWITTER_ACCESS_TOKEN,
            #     access_token_secret=TWITTER_ACCESS_SECRET,
            #     content="🚀 Bitcoin Mining Update! #Bitcoin #Mining",
            #     media_paths=image_paths
            # )
            
        except Exception as e:
            print(f"\n✗ Error fetching/preparing images: {e}")
