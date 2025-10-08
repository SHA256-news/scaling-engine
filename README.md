# scaling-engine

Bitcoin Mining Bot - Automated news aggregation and posting system for Bitcoin mining content.

## EventRegistry Integration

This bot uses the [EventRegistry Python SDK](https://github.com/EventRegistry/event-registry-python) to fetch Bitcoin mining news.

### API Setup

1. Get an API key from [NewsAPI.ai Dashboard](https://newsapi.ai/dashboard)
2. Set environment variable:
   ```bash
   export EVENTREGISTRY_API_KEY="your-api-key"
   ```

### Query Configuration

The bot queries EventRegistry for Bitcoin mining news with these parameters:

- **Keywords**: Bitcoin AND mining (both must appear)
- **Language**: English only
- **Date Range**: Last 24 hours (configurable)
- **Data Type**: News articles (not PR or blogs)
- **Deduplication**: Enabled (skip duplicate articles)

### Rate Limits & Costs

- **Free tier**: Limited daily requests
- **Archive queries**: More expensive (disabled by default)
- **Token usage**: Monitored automatically
- **Optimization**: Retrieve only needed fields

### Best Practices

1. **Always use QueryArticlesIter** for pagination
2. **Resolve labels to URIs** before querying (use `getConceptUri()`, etc.)
3. **Check response structure** defensively (never assume keys exist)
4. **Monitor token usage** with `getRemainingAvailableRequests()`
5. **Set allowUseOfArchive=False** for recent data (cheaper)
6. **Use ReturnInfo** to specify exactly what data you need

### Example Usage

```python
from eventregistry import EventRegistry, QueryArticlesIter, QueryItems

er = EventRegistry(
    apiKey=os.getenv('EVENTREGISTRY_API_KEY'),
    allowUseOfArchive=False
)

# Query for Bitcoin mining articles
q = QueryArticlesIter(
    keywords=QueryItems.AND(["bitcoin", "mining"]),
    lang="eng",
    dataType="news"
)

articles = list(q.execQuery(er, maxItems=50))
print(f"Found {len(articles)} articles")
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

## Documentation

See [agent.md](agent.md) for comprehensive implementation guidance.