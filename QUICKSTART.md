# Quick Start Guide - Event Registry Integration

Get started with Event Registry API integration in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Event Registry API key ([get one here](https://eventregistry.org/))

## Installation

```bash
# Install the Event Registry SDK
pip install eventregistry

# Install other dependencies
pip install python-dotenv
```

## Setup

1. **Create `.env` file** in your project root:

```bash
EVENT_REGISTRY_API_KEY=your_api_key_here
```

2. **Test your API key**:

```python
from eventregistry import EventRegistry

er = EventRegistry(apiKey="your_api_key_here")
print("✓ Connected successfully!")
```

## Your First Query

### Fetch Bitcoin Mining Articles

```python
from eventregistry import EventRegistry, QueryArticlesIter, QueryItems

# Initialize client
er = EventRegistry(apiKey="your_api_key_here")

# Create query
q = QueryArticlesIter(
    conceptUri=QueryItems.AND([
        "http://en.wikipedia.org/wiki/Bitcoin",
        "http://en.wikipedia.org/wiki/Mining"
    ]),
    lang="eng"
)

# Fetch articles
articles = []
for article in q.execQuery(er, sortBy="socialScore", maxItems=10):
    articles.append(article)
    print(f"- {article['title']}")

print(f"\n✓ Fetched {len(articles)} articles")
```

## Common Use Cases

### 1. Latest News (Last 24 Hours)

```python
from datetime import datetime, timedelta

date_end = datetime.now().strftime("%Y-%m-%d")
date_start = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    dateStart=date_start,
    dateEnd=date_end,
    lang="eng"
)

for article in q.execQuery(er, sortBy="date", maxItems=20):
    print(f"{article['date']}: {article['title']}")
```

### 2. Trending Content

```python
from eventregistry import ReturnInfo, ArticleInfoFlags

q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"
)

# Request social metrics
q.setRequestedResult(ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        url=True,
        socialScore=True
    )
))

for article in q.execQuery(er, sortBy="socialScore", maxItems=10):
    score = article.get('socialScore', 0)
    print(f"[{score}] {article['title']}")
```

### 3. Filter by Source

```python
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    sourceUri=["reuters.com", "bloomberg.com", "bbc.co.uk"],
    lang="eng"
)

for article in q.execQuery(er, maxItems=10):
    source = article.get('source', {}).get('title', 'Unknown')
    print(f"[{source}] {article['title']}")
```

## Production-Ready Example

```python
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from eventregistry import (
    EventRegistry,
    QueryArticlesIter,
    QueryItems,
    ReturnInfo,
    ArticleInfoFlags
)

# Load API key
load_dotenv()
API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")

def fetch_bitcoin_news(days_back=7, max_articles=50):
    """Fetch Bitcoin mining news with error handling."""
    
    # Calculate date range
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    # Initialize client
    er = EventRegistry(apiKey=API_KEY)
    
    # Create query
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR(["ASIC", "hashrate", "mining pool"]),
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
            socialScore=True
        )
    ))
    
    # Fetch articles with error handling
    articles = []
    try:
        for article in q.execQuery(er, sortBy="socialScore", maxItems=max_articles):
            articles.append(article)
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []
    
    return articles

# Usage
if __name__ == "__main__":
    print("Fetching Bitcoin mining news...")
    articles = fetch_bitcoin_news(days_back=7, max_articles=25)
    
    print(f"\nFetched {len(articles)} articles\n")
    
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article.get('source', {}).get('title', 'Unknown')}")
        print(f"   Date: {article['date']}")
        print(f"   Score: {article.get('socialScore', 0)}")
        print()
```

## Next Steps

### Learn More
- 📖 **README.md** - Complete integration guide
- 📚 **eventregistry_guide.md** - Comprehensive API reference
- 💻 **eventregistry_examples.py** - 10 working examples
- 🔧 **bot_lib_template.py** - Production template

### Try These
1. Run `python eventregistry_examples.py` to see all examples
2. Explore different sorting strategies (date, socialScore, rel)
3. Filter by sentiment for positive/negative news
4. Combine multiple concepts for specific topics
5. Configure ReturnInfo for optimal performance

### Common Issues

**Problem**: `Invalid API key`  
**Solution**: Check your API key in `.env` file

**Problem**: `Rate limit exceeded`  
**Solution**: Add delays between requests or implement exponential backoff

**Problem**: No results returned  
**Solution**: Broaden your date range or use less specific concepts

**Problem**: Too many irrelevant results  
**Solution**: Use more specific concept URIs or add keyword filters

## Resources

- [Event Registry Homepage](https://eventregistry.org/)
- [API Documentation](https://eventregistry.org/documentation)
- [Python SDK GitHub](https://github.com/EventRegistry/event-registry-python)
- [Get API Key](https://eventregistry.org/register)

## Support

Need help? Check these resources:
1. **DOCUMENTATION_SUMMARY.md** - Overview of all documentation
2. **eventregistry_guide.md** - Detailed API reference
3. **eventregistry_examples.py** - Working code examples
4. GitHub Issues - Report problems or ask questions

---

**Ready to build?** Start with the production example above and customize for your needs!

✨ **Pro Tip**: Always use concept URIs combined with keywords for best results!
