# scaling-engine

This repository contains the source code for the **Bitcoin Mining News Bot**, an automated system for fetching, processing, and posting news related to Bitcoin mining.

## Architecture

The bot follows a **Clean 4-File Design** philosophy:

### Core Files

- **`config.py`**: The single source of truth for all configurations
  - API keys and credentials
  - Filter lists (blacklisted sources, terms, etc.)
  - Prompt templates for AI content generation
  - Bot settings and parameters
  - Contains **no logic** - purely configuration data

- **`bot_lib.py`**: The core, stateless engine of the bot
  - All business logic implemented as functions
  - Fetching and filtering articles
  - Generating content with AI
  - Posting to social media platforms
  - Each function is pure and testable

- **`main.py`**: The single entry point for bot execution
  - Orchestrates the entire workflow
  - Calls functions from `bot_lib.py` in a linear sequence
  - Handles high-level error management
  - Simple, readable, and easy to understand

- **`tools.py`**: Command-line interface for bot management
  - Interactive tools for testing and debugging
  - Manual operations and administrative tasks
  - Development utilities

### Automation

- **`.github/workflows/main.yml`**: GitHub Actions workflow
  - Automates bot execution on a schedule
  - Ensures reliable, hands-free operation
  - Handles environment setup and credentials

## Complete Bot Workflow

The **scaling-engine** repository implements a **Bitcoin Mining News Bot** with dual-purpose operation:

### Purpose 1: Continuous Social Media Distribution

**Monitoring Workflow** (every 30 minutes):
- 📰 Fetches Bitcoin mining articles from Event Registry (past 1 hour)
- 🔍 Filters articles based on quality criteria
- 📦 Adds articles to posting queue
- 💾 Stores articles for daily brief aggregation

**Posting Workflow** (every 24 minutes):
- 📋 Retrieves next article from queue
- 🤖 Generates engaging tweet with Gemini AI
- ✅ Checks Twitter rate limiter (60/day target)
- 🐦 Posts to Twitter/X if within limits
- 📊 Records post timestamp

**Why Separate Workflows?**
- Continuous monitoring ensures no news is missed
- Scheduled posting respects Twitter's 100 posts/24hr limit
- Queue management prevents flooding
- Even distribution throughout the day

**Twitter API Rate Limiting**:
- Limit: 100 posts per 24 hours
- Target: 60 posts per day (40% safety buffer)
- Frequency: Every 24 minutes
- Strategy: Queue-based with rate limiter

### Purpose 2: Daily Brief Publication

**Daily Brief Workflow** (once per day at midnight UTC):
- 📚 Aggregates all articles from past 24 hours
- 📝 Generates comprehensive Markdown brief with Gemini AI
- 🔖 Creates GitHub issue with brief content
- 🌐 Triggers website publication when issue is closed

**Complete Workflow Diagram**:

```
┌─────────────────────────────────────────────────────────────┐
│         Monitoring Workflow (Every 30 minutes)              │
│  Event Registry → Filter → Queue → Store for Daily Brief   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ [Article Queue]
                         │
┌────────────────────────┴────────────────────────────────────┐
│         Posting Workflow (Every 24 minutes)                 │
│  Queue → Rate Limiter → Gemini → Twitter                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│       Daily Brief Workflow (Once per day at 00:00 UTC)     │
│  Load Cached Articles → Gemini → GitHub Issue → Website    │
└─────────────────────────────────────────────────────────────┘
```

### APIs Used

| API | Purpose | Credentials Required |
|-----|---------|---------------------|
| **Event Registry** | Fetch Bitcoin mining news articles | `EVENT_REGISTRY_API_KEY` |
| **Gemini (Google AI)** | Generate tweets and daily briefs | `GEMINI_API_KEY` |
| **Twitter** | Post scheduled updates | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` |
| **GitHub** | Create issues for daily briefs | `GITHUB_TOKEN` |
| **Unsplash** | Fetch royalty-free images for tweets | `UNSPLASH_ACCESS_KEY` |

### Design Philosophy

1. **Continuous Operation**: Monitor news sources every 30 minutes
2. **Rate Limit Compliance**: Respect Twitter's 100 posts/day limit (target 60)
3. **Queue-Based Architecture**: Decouple monitoring from posting
4. **Intelligent Scheduling**: Post every 24 minutes for even distribution
5. **Quality Over Quantity**: Filter aggressively, post only worthy content
6. **Verification**: Every step validated before proceeding
7. **Stateless Functions**: Pure functions for testability
8. **Automated Execution**: GitHub Actions for hands-free operation

## Development Philosophy

### 1. Simplicity

- **Functions over classes**: We use simple functions instead of complex object-oriented patterns
- **No inheritance**: Avoids unnecessary complexity and coupling
- **Clear data flow**: Each function has explicit inputs and outputs
- **Readable code**: Code should be easy to understand at first glance

### 2. Verification

- **Verify everything**: Every step is verified before proceeding to the next
- **File operations**: Always check that files exist and contain expected data
- **API responses**: Validate all external API calls
- **Data transformations**: Ensure data is in the expected format at each stage

### 3. Clear Error Handling

- **Specific exceptions**: Use custom exceptions for different failure scenarios
- **Graceful degradation**: Handle failures without halting the entire process
- **Informative messages**: Error messages should clearly explain what went wrong
- **Recovery strategies**: Where possible, implement automatic recovery from failures

## Event Registry Integration

The bot uses the [Event Registry Python SDK](https://github.com/EventRegistry/event-registry-python) to fetch Bitcoin mining news articles from a global news database.

### Setup and Authentication

1. **Install the SDK**:
```bash
pip install eventregistry
```

2. **Get an API Key**:
   - Sign up at [Event Registry](https://eventregistry.org/)
   - Obtain your API key from the dashboard
   - Store it in your `.env` file: `EVENT_REGISTRY_API_KEY=your_key_here`

3. **Initialize the Client**:
```python
from eventregistry import EventRegistry

er = EventRegistry(apiKey=api_key)
```

### Concept-Based Search

Event Registry uses **concept URIs** for semantic search, providing more accurate results than keyword-only searches.

**Concept URIs** are unique identifiers for entities, topics, and categories:
- `http://en.wikipedia.org/wiki/Bitcoin` - Bitcoin concept
- `http://en.wikipedia.org/wiki/Mining` - Mining concept
- `http://en.wikipedia.org/wiki/Cryptocurrency` - Cryptocurrency concept

**Benefits of concept-based search**:
- More accurate results (semantic understanding)
- Language-agnostic (concepts work across languages)
- Reduces false positives from keyword matches

### Query Construction

Use `QueryArticlesIter` for efficient pagination through large result sets:

```python
from eventregistry import EventRegistry, QueryArticlesIter, QueryItems

# Initialize Event Registry
er = EventRegistry(apiKey=api_key)

# Create query with concept URIs
q = QueryArticlesIter(
    conceptUri=QueryItems.AND([
        "http://en.wikipedia.org/wiki/Bitcoin",
        "http://en.wikipedia.org/wiki/Mining"
    ]),
    keywords=QueryItems.OR(["ASIC", "hashrate", "mining pool", "mining rig"]),
    dateStart="2024-01-01",
    dateEnd="2024-01-31",
    lang="eng"
)

# Iterate through results
for article in q.execQuery(er, sortBy="socialScore", maxItems=100):
    print(article)
```

### ReturnInfo Configuration

Control what data is returned using `ReturnInfo` and `ArticleInfoFlags`.

**Note**: `QueryArticlesIter` returns all fields by default and does not support `setRequestedResult()`. Use `QueryArticles` with `RequestArticlesInfo` if you need to control which fields are returned:

```python
from eventregistry import QueryArticles, RequestArticlesInfo, ReturnInfo, ArticleInfoFlags

# Configure detailed article information
returnInfo = ReturnInfo(
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
        originalArticle=True,
        extractedDates=True
    )
)

# Use with QueryArticles (not QueryArticlesIter)
q = QueryArticles(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"
)

q.setRequestedResult(RequestArticlesInfo(
    page=1,
    count=100,
    returnInfo=returnInfo
))
```

### Sorting Options

Event Registry supports multiple sorting strategies:

- **`socialScore`** - Sort by social media engagement (Twitter shares, likes, etc.)
- **`date`** - Sort by publication date (newest first)
- **`rel`** - Sort by relevance to query (default)
- **`sourceImportance`** - Sort by source authority/reputation

```python
# Sort by social engagement for viral content
for article in q.execQuery(er, sortBy="socialScore", maxItems=50):
    process_article(article)

# Sort by date for latest news
for article in q.execQuery(er, sortBy="date", maxItems=50):
    process_article(article)
```

### Filtering Options

**By Language**:
```python
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"  # English only
)
```

**By Source**:
```python
# Include specific sources
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    sourceUri=["bbc.co.uk", "reuters.com"]
)

# Exclude specific sources (in config.py blacklist)
filtered_articles = [a for a in articles if a['source']['uri'] not in BLACKLISTED_SOURCES]
```

**By Date Range**:
```python
from datetime import datetime, timedelta

# Last 7 days
date_end = datetime.now().strftime("%Y-%m-%d")
date_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    dateStart=date_start,
    dateEnd=date_end
)
```

### API Usage Best Practices

1. **Use Concept URIs**: Prefer concept-based search over keyword-only for better accuracy
2. **Combine Concepts and Keywords**: Use concepts for broad topics, keywords for specific terms
3. **Paginate Efficiently**: Use `QueryArticlesIter` instead of manual pagination
4. **Configure ReturnInfo**: Only request data you need to reduce payload size
5. **Implement Rate Limiting**: Respect API quotas and implement exponential backoff
6. **Cache Results**: Store fetched articles to avoid redundant API calls
7. **Handle Errors Gracefully**: Implement retry logic for transient failures

### Troubleshooting

**Problem**: Too many irrelevant results
- **Solution**: Use more specific concept URIs or add `QueryItems.AND` conditions

**Problem**: No results returned
- **Solution**: Check date range, broaden concepts, verify API key validity

**Problem**: Rate limit exceeded
- **Solution**: Reduce request frequency, implement exponential backoff, upgrade API plan

**Problem**: Missing article fields
- **Solution**: Configure `ReturnInfo` to include required fields explicitly

**Example**: Complete Bitcoin mining article fetcher:
```python
def fetch_bitcoin_mining_articles(api_key: str, date_start: str, date_end: str, max_articles: int = 100) -> list:
    """
    Fetch Bitcoin mining related articles from Event Registry.
    
    Uses concept-based search for more accurate results.
    """
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems, ReturnInfo, ArticleInfoFlags
    
    er = EventRegistry(apiKey=api_key)
    
    # Concept-based query with keywords
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR(["ASIC", "hashrate", "mining pool", "difficulty"]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    # Note: QueryArticlesIter returns all fields by default
    # No need to call setRequestedResult()
    
    # Fetch articles sorted by social score
    articles = []
    for article in q.execQuery(er, sortBy="socialScore", maxItems=max_articles):
        articles.append(article)
    
    return articles
```

### Additional Resources

- [Event Registry Documentation](https://eventregistry.org/documentation)
- [Python SDK GitHub](https://github.com/EventRegistry/event-registry-python)
- [API Reference](https://eventregistry.org/documentation/api)

## Unsplash Image Integration

The bot automatically fetches and optimizes royalty-free images from Unsplash to accompany tweets, making the content more engaging and visually appealing.

### Features

- **Automated Image Fetching**: Searches Unsplash API for Bitcoin mining related imagery
- **Image Optimization**: Resizes images to Twitter's recommended specs (1600x900 pixels, 16:9 aspect ratio)
- **Quality Control**: Intelligent cropping to maintain best composition
- **Media Attachments**: Posts up to 2 relevant images per tweet
- **Free Usage**: All images are royalty-free under Unsplash License

### Setup and Authentication

1. **Get an Unsplash API Key**:
   - Sign up at [Unsplash Developers](https://unsplash.com/developers)
   - Create a new application
   - Copy your Access Key
   - Store it in your `.env` file: `UNSPLASH_ACCESS_KEY=your_access_key_here`

2. **Install Dependencies**:
```bash
pip install requests Pillow
```

### Usage

The bot provides four main functions for image handling:

#### 1. Fetch Images from Unsplash

```python
from bot_lib import fetch_unsplash_images

images = fetch_unsplash_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining",
    count=2,
    orientation="landscape"
)

# Returns list of image dictionaries with URLs and metadata
for image in images:
    print(f"Image: {image['url']}")
    print(f"Photographer: {image['photographer']}")
```

#### 2. Download Image

```python
from bot_lib import download_image

path = download_image(
    image_url="https://images.unsplash.com/photo-123...",
    output_path="/tmp/bitcoin_mining.jpg"
)
```

#### 3. Optimize for Twitter

```python
from bot_lib import optimize_image_for_twitter

optimized_path = optimize_image_for_twitter(
    input_path="/tmp/bitcoin_mining.jpg",
    target_size=(1600, 900),  # Twitter recommended specs
    quality=85
)
```

#### 4. Complete Workflow

```python
from bot_lib import fetch_and_prepare_images

# Fetch, download, and optimize in one step
image_paths = fetch_and_prepare_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining hardware",
    output_dir="/tmp/bitcoin_images",
    count=2
)

# Returns list of paths to Twitter-ready images
print(f"Prepared {len(image_paths)} images")
```

### Post Tweet with Images

```python
from bot_lib import post_to_twitter, fetch_and_prepare_images

# Fetch and prepare images
image_paths = fetch_and_prepare_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining",
    count=2
)

# Post to Twitter with images
result = post_to_twitter(
    twitter_api_key=TWITTER_API_KEY,
    twitter_api_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
    content="🚀 Bitcoin Mining Update! #Bitcoin #Mining",
    media_paths=image_paths
)

if result['success']:
    print(f"Posted: {result['url']}")
    print(f"Media IDs: {result['media_ids']}")
```

### Image Optimization Specs

The bot optimizes images according to Twitter's best practices:

- **Aspect Ratio**: 16:9 (1600x900 pixels)
- **File Format**: JPEG (optimal for photos)
- **Quality**: 85% (balanced quality/size)
- **Max File Size**: Under 5MB per image
- **Max Images**: Up to 4 per tweet (default: 2)

### Rate Limits and Best Practices

**Unsplash API Limits** (Free Tier):
- 50 requests per hour
- Recommended: Cache images when possible
- Use specific search queries for better results

**Best Practices**:
1. Use descriptive search queries related to article content
2. Cache images to avoid repeated API calls
3. Always credit photographers (included in metadata)
4. Clean up temporary files after posting
5. Handle API errors gracefully with fallbacks

### Troubleshooting

**Problem**: No images returned
- **Solution**: Try broader search queries, check API key validity

**Problem**: Images look cropped incorrectly
- **Solution**: Adjust `target_size` parameter or use different orientation

**Problem**: File size too large
- **Solution**: Reduce `quality` parameter (try 75-80)

**Problem**: ImportError for PIL/Pillow
- **Solution**: Install Pillow: `pip install Pillow`
- [Concept Search Guide](https://github.com/EventRegistry/event-registry-python/wiki/Concepts)