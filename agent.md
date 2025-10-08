# Bitcoin Mining Bot - Agent Documentation

This document provides comprehensive guidance for implementing and maintaining the Bitcoin Mining Bot, with special focus on EventRegistry API integration.

## EventRegistry Integration

The bot uses the [EventRegistry Python SDK](https://github.com/EventRegistry/event-registry-python) to fetch Bitcoin mining news articles. Following these patterns ensures reliable API usage.

### API Client Initialization

Always initialize the EventRegistry client with proper configuration:

```python
from eventregistry import EventRegistry

# Initialize with API key (required for production use)
er = EventRegistry(
    apiKey=config.EVENTREGISTRY_API_KEY,
    minDelayBetweenRequests=0.5,  # Respect rate limits
    allowUseOfArchive=False,  # False = last 31 days only (cheaper)
    verboseOutput=False  # Set True for debugging
)
```

### Query Construction Best Practices

Use `QueryArticlesIter` for efficient pagination and proper query construction:

```python
from eventregistry import QueryArticlesIter, QueryItems, ReturnInfo, ArticleInfoFlags

# Use QueryArticlesIter for pagination (recommended)
q = QueryArticlesIter(
    keywords=QueryItems.AND(["bitcoin", "mining"]),  # Explicit operators
    conceptUri=er.getConceptUri("Bitcoin"),  # Get URIs first
    lang="eng",
    dateStart="2024-01-01",
    dataType="news"  # Specify content type
)

# Execute with proper return info
for article in q.execQuery(
    er,
    sortBy="date",
    sortByAsc=False,
    returnInfo=ReturnInfo(
        articleInfo=ArticleInfoFlags(
            bodyLen=-1,  # Full article body
            concepts=True,
            categories=True,
            image=True,
            url=True
        )
    ),
    maxItems=100
):
    print(article)
```

### Error Handling

ALWAYS check response structure defensively:

```python
# ALWAYS check response structure
try:
    res = er.execQuery(q)
    
    # Defensive checking
    if "error" in res:
        logger.error(f"API error: {res['error']}")
        return []
    
    articles = res.get("articles", {}).get("results", [])
    if not articles:
        logger.warning("No articles found")
        return []
        
    return articles
    
except Exception as e:
    logger.error(f"EventRegistry query failed: {e}")
    return []
```

### Rate Limiting & Token Management

Monitor API usage to avoid hitting rate limits:

```python
# Check usage after queries
remaining = er.getRemainingAvailableRequests()
daily_total = er.getDailyAvailableRequests()

if remaining < 100:  # Low token warning
    logger.warning(f"Low tokens: {remaining}/{daily_total}")

# Get detailed usage info
usage = er.getUsageInfo()
logger.info(f"Token usage: {usage}")
```

### URI Resolution (CRITICAL)

ALWAYS resolve labels to URIs before using them in queries:

```python
# ALWAYS resolve labels to URIs first
concept_uri = er.getConceptUri("Bitcoin")
if not concept_uri:
    logger.error("Could not resolve concept: Bitcoin")
    # Handle fallback

category_uri = er.getCategoryUri("Business/Cryptocurrency")
source_uri = er.getNewsSourceUri("CoinDesk")
location_uri = er.getLocationUri("United States")

# Use QueryItems for complex queries
keywords = QueryItems.AND(["bitcoin", "mining"])
concepts = QueryItems.OR([concept_uri1, concept_uri2])
```

### ReturnInfo Configuration

Optimize data retrieval to save tokens:

```python
# Optimize what data you retrieve to save tokens
return_info = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        bodyLen=-1,      # -1 = full, 0 = none, N = N chars
        title=True,
        url=True,
        concepts=False,   # Don't retrieve if not needed
        categories=False,
        image=True,
        sentiment=True
    )
)
```

## Error Handling Patterns

### EventRegistry Specific Errors

Define custom exceptions for EventRegistry operations:

```python
# EventRegistry specific errors
class EventRegistryError(Exception):
    """Base exception for EventRegistry issues"""
    pass

class NoArticlesError(EventRegistryError):
    """No articles found matching criteria"""
    pass

class APIQuotaError(EventRegistryError):
    """API quota exceeded"""
    pass

def fetch_articles() -> List[Dict]:
    """Fetch articles with comprehensive error handling."""
    try:
        q = QueryArticlesIter(...)
        articles = list(q.execQuery(er, maxItems=100))
        
        if not articles:
            raise NoArticlesError("Query returned no results")
            
        return articles
        
    except Exception as e:
        # Check for quota issues
        if "limit" in str(e).lower():
            raise APIQuotaError(f"API quota exceeded: {e}")
        
        # Log and re-raise
        logger.error(f"EventRegistry fetch failed: {e}")
        raise EventRegistryError(f"Failed to fetch articles: {e}")
```

## Configuration Best Practices

### EventRegistry Configuration

```python
# config.py - EventRegistry settings
EVENTREGISTRY_CONFIG = {
    'api_key': os.getenv('EVENTREGISTRY_API_KEY'),
    'min_delay': 0.5,  # Seconds between requests
    'allow_archive': False,  # False = cheaper, last 31 days only
    'max_articles_per_run': 100,
    'default_language': 'eng',
    'data_type': 'news'  # 'news', 'pr', or 'blog'
}

# Query parameters
ARTICLE_QUERY_PARAMS = {
    'keywords': QueryItems.AND(['bitcoin', 'mining']),
    'lang': 'eng',
    'dateStart': None,  # Set dynamically
    'dateEnd': None,
    'isDuplicateFilter': 'skipDuplicates',
    'dataType': 'news'
}

# Return info configuration (what data to retrieve)
ARTICLE_RETURN_INFO = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        bodyLen=-1,
        title=True,
        body=True,
        url=True,
        concepts=True,
        categories=True,
        image=True,
        sentiment=True
    )
)
```

## Common EventRegistry Mistakes

### ❌ Wrong: Assuming Response Structure
```python
articles = response['articles']['results']  # Can crash!
```

### ✅ Right: Defensive Checking
```python
articles = response.get('articles', {}).get('results', [])
if not articles:
    logger.warning("No articles returned")
```

### ❌ Wrong: Using Labels Directly
```python
q = QueryArticlesIter(conceptUri="Bitcoin")  # Wrong!
```

### ✅ Right: Resolve to URI First
```python
bitcoin_uri = er.getConceptUri("Bitcoin")
q = QueryArticlesIter(conceptUri=bitcoin_uri)
```

### ❌ Wrong: Not Handling Empty Results
```python
for article in q.execQuery(er):  # Can be empty!
    process(article)
```

### ✅ Right: Check for Results
```python
articles = list(q.execQuery(er, maxItems=100))
if not articles:
    logger.warning("No articles found")
    return

for article in articles:
    process(article)
```

### ❌ Wrong: Ignoring Rate Limits
```python
while True:
    articles = fetch_articles()  # Will hit rate limit!
```

### ✅ Right: Monitor Usage
```python
remaining = er.getRemainingAvailableRequests()
if remaining < 50:
    logger.warning(f"Low tokens: {remaining}")
    time.sleep(60)  # Back off
```
