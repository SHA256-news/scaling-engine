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

Control what data is returned using `ReturnInfo` and `ArticleInfoFlags`:

```python
from eventregistry import ReturnInfo, ArticleInfoFlags

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

# Use in query
q.setRequestedResult(returnInfo)
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
    
    # Configure return information
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            body=True,
            url=True,
            date=True,
            concepts=True,
            socialScore=True
        )
    ))
    
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
- [Concept Search Guide](https://github.com/EventRegistry/event-registry-python/wiki/Concepts)