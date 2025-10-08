# Event Registry API Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication and Setup](#authentication-and-setup)
3. [Query Types](#query-types)
4. [Concept URIs vs Keywords](#concept-uris-vs-keywords)
5. [Pagination with Iterators](#pagination-with-iterators)
6. [Return Information Configuration](#return-information-configuration)
7. [Sorting and Filtering](#sorting-and-filtering)
8. [Rate Limiting and Optimization](#rate-limiting-and-optimization)
9. [Common Patterns for Bitcoin Mining News](#common-patterns-for-bitcoin-mining-news)
10. [Code Examples](#code-examples)

## Overview

Event Registry is a comprehensive news aggregation and analysis platform that provides access to millions of articles from news sources worldwide. It uses semantic understanding and machine learning to provide accurate, relevant search results.

### Key Features
- **Global Coverage**: Access to news from 100,000+ sources in 100+ languages
- **Semantic Search**: Concept-based queries using Wikipedia URIs
- **Real-time Updates**: News articles indexed within minutes
- **Rich Metadata**: Sentiment analysis, concepts, categories, locations
- **Social Metrics**: Track article engagement on social media
- **Duplicate Detection**: Identify related articles and original sources

### Python SDK
The official Event Registry Python SDK provides a clean, Pythonic interface to the API.

**Installation**:
```bash
pip install eventregistry
```

**GitHub Repository**: https://github.com/EventRegistry/event-registry-python

## Authentication and Setup

### Getting an API Key

1. Visit [Event Registry](https://eventregistry.org/)
2. Sign up for an account
3. Navigate to your dashboard
4. Copy your API key

### Storing Credentials

**Using Environment Variables** (Recommended):
```bash
# In your .env file
EVENT_REGISTRY_API_KEY=your_api_key_here
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EVENT_REGISTRY_API_KEY")
```

**Direct Assignment** (Development Only):
```python
api_key = "your_api_key_here"  # Never commit this!
```

### Initializing the Client

```python
from eventregistry import EventRegistry

# Initialize client
er = EventRegistry(apiKey=api_key)

# Verify connection
try:
    er.getConceptUri("Bitcoin")
    print("Successfully connected to Event Registry")
except Exception as e:
    print(f"Connection failed: {e}")
```

### API Quotas and Limits

Different subscription tiers have different limits:

| Plan | Daily Requests | Articles/Request | Concepts | Monitoring |
|------|----------------|------------------|----------|------------|
| Free | 500 | 100 | ✓ | ✗ |
| Basic | 5,000 | 1,000 | ✓ | ✓ |
| Pro | 50,000 | 10,000 | ✓ | ✓ |
| Enterprise | Custom | Custom | ✓ | ✓ |

**Check Your Quota**:
```python
# Get remaining quota
remaining = er.getRemainingAvailableRequests()
print(f"Remaining requests today: {remaining}")
```

## Query Types

Event Registry supports multiple query types for different use cases.

### 1. Article Queries

Search for news articles based on various criteria.

```python
from eventregistry import QueryArticles, RequestArticlesInfo

q = QueryArticles(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"
)

# Execute query
res = er.execQuery(q)
```

### 2. Event Queries

Search for news events (clusters of related articles).

```python
from eventregistry import QueryEvents

q = QueryEvents(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"
)

res = er.execQuery(q)
```

### 3. Concept Queries

Find concepts (entities, topics) in Event Registry.

```python
# Search for a concept
concepts = er.getConceptUri("Bitcoin mining")

# Get concept info
concept_info = er.getConceptInfo("http://en.wikipedia.org/wiki/Bitcoin")
```

### 4. Source Queries

Search for news sources.

```python
# Find sources
sources = er.getSourceUri("Reuters")

# Get source info
source_info = er.getSourceInfo("bbc.co.uk")
```

## Concept URIs vs Keywords

### What are Concept URIs?

Concept URIs are unique identifiers for entities, topics, and categories. They're based on Wikipedia URLs and provide semantic understanding.

**Example Concept URIs**:
- `http://en.wikipedia.org/wiki/Bitcoin` - Cryptocurrency Bitcoin
- `http://en.wikipedia.org/wiki/Mining` - Mining activity
- `http://en.wikipedia.org/wiki/Elon_Musk` - Person: Elon Musk
- `http://en.wikipedia.org/wiki/China` - Country: China

### Finding Concept URIs

```python
# Search for a concept
results = er.getConceptUri("Bitcoin")
print(results)  # http://en.wikipedia.org/wiki/Bitcoin

# Multiple results
results = er.getConceptUri("Mining")
# Returns list if multiple matches found

# Get concept details
info = er.getConceptInfo("http://en.wikipedia.org/wiki/Bitcoin")
print(info['label'])  # Bitcoin
print(info['type'])   # wiki
```

### Concept URIs vs Keywords

| Feature | Concept URIs | Keywords |
|---------|-------------|----------|
| Accuracy | High | Medium |
| Language Support | Multi-language | Single language |
| Semantic Understanding | Yes | No |
| False Positives | Low | Higher |
| Complexity | Requires lookup | Simple |
| Best For | Entities, topics | Specific terms |

### When to Use What

**Use Concept URIs for**:
- Named entities (people, organizations, locations)
- Broad topics (Bitcoin, Mining, Technology)
- Multi-language searches
- Reducing false positives

**Use Keywords for**:
- Specific technical terms (ASIC, hashrate)
- Industry jargon
- New/emerging terms not in Wikipedia
- Exact phrase matching

**Best Practice: Combine Both**:
```python
from eventregistry import QueryArticlesIter, QueryItems

q = QueryArticlesIter(
    # Use concepts for main topics
    conceptUri=QueryItems.AND([
        "http://en.wikipedia.org/wiki/Bitcoin",
        "http://en.wikipedia.org/wiki/Mining"
    ]),
    # Use keywords for specific terms
    keywords=QueryItems.OR([
        "ASIC",
        "hashrate",
        "mining pool",
        "difficulty adjustment"
    ]),
    lang="eng"
)
```

### Combining Concepts

```python
from eventregistry import QueryItems

# AND - Articles must match ALL concepts
bitcoin_mining = QueryItems.AND([
    "http://en.wikipedia.org/wiki/Bitcoin",
    "http://en.wikipedia.org/wiki/Mining"
])

# OR - Articles can match ANY concept
crypto_news = QueryItems.OR([
    "http://en.wikipedia.org/wiki/Bitcoin",
    "http://en.wikipedia.org/wiki/Ethereum",
    "http://en.wikipedia.org/wiki/Litecoin"
])

# Complex combinations
advanced = QueryItems.AND([
    QueryItems.OR([
        "http://en.wikipedia.org/wiki/Bitcoin",
        "http://en.wikipedia.org/wiki/Cryptocurrency"
    ]),
    "http://en.wikipedia.org/wiki/Mining"
])
```

## Pagination with Iterators

### Why Use Iterators?

Event Registry provides iterator classes that handle pagination automatically:

**Benefits**:
- Automatic page management
- Memory efficient (lazy loading)
- Simplified code
- Built-in error handling
- Progress tracking

### QueryArticlesIter

```python
from eventregistry import QueryArticlesIter

q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    dateStart="2024-01-01",
    dateEnd="2024-01-31",
    lang="eng"
)

# Iterate through all results
for article in q.execQuery(er, sortBy="date", maxItems=1000):
    print(article['title'])
    # Process article
```

### Controlling Pagination

```python
# Limit total items
for article in q.execQuery(er, maxItems=100):
    process(article)

# Process in batches
batch = []
for i, article in enumerate(q.execQuery(er, maxItems=1000)):
    batch.append(article)
    
    if len(batch) == 50:
        process_batch(batch)
        batch = []

# Process remaining items
if batch:
    process_batch(batch)
```

### Manual Pagination (Advanced)

If you need more control:

```python
from eventregistry import QueryArticles, RequestArticlesInfo

page = 1
page_size = 100

while True:
    q = QueryArticles(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        lang="eng"
    )
    
    q.setRequestedResult(
        RequestArticlesInfo(
            page=page,
            count=page_size,
            sortBy="date"
        )
    )
    
    res = er.execQuery(q)
    articles = res['articles']['results']
    
    if not articles:
        break
    
    for article in articles:
        process(article)
    
    page += 1
```

### Progress Tracking

```python
total_processed = 0
target = 500

for article in q.execQuery(er, maxItems=target):
    process(article)
    total_processed += 1
    
    if total_processed % 100 == 0:
        print(f"Progress: {total_processed}/{target}")
```

## Return Information Configuration

Control exactly what data is returned to optimize API usage and response times.

### ArticleInfoFlags

```python
from eventregistry import ReturnInfo, ArticleInfoFlags

# Configure what fields to return
returnInfo = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        # Basic info
        title=True,
        body=True,
        url=True,
        
        # Dates and times
        date=True,
        time=True,
        
        # Metadata
        authors=True,
        concepts=True,
        categories=True,
        location=True,
        
        # Analysis
        sentiment=True,
        sentiment=True,
        
        # Media
        image=True,
        videos=True,
        
        # Metrics
        socialScore=True,
        
        # Duplicates
        duplicateList=True,
        originalArticle=True,
        
        # Advanced
        extractedDates=True,
        links=True
    )
)
```

### Common Configurations

**Minimal (Filtering Only)**:
```python
minimal = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        url=True,
        date=True,
        source=True
    )
)
```

**Social Media Posting**:
```python
social_media = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        body=True,
        url=True,
        image=True,
        socialScore=True,
        sentiment=True
    )
)
```

**Content Analysis**:
```python
analysis = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        body=True,
        concepts=True,
        categories=True,
        sentiment=True,
        authors=True,
        date=True
    )
)
```

**Comprehensive**:
```python
comprehensive = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        # Include everything
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
        videos=True,
        socialScore=True,
        duplicateList=True,
        originalArticle=True,
        extractedDates=True,
        links=True
    )
)
```

### Applying ReturnInfo

```python
from eventregistry import QueryArticlesIter

q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"
)

# Set return info
q.setRequestedResult(social_media)

# Execute query
for article in q.execQuery(er, maxItems=100):
    print(article)
```

## Sorting and Filtering

### Sorting Options

Event Registry supports multiple sorting strategies:

#### 1. Sort by Relevance (rel)

Default sorting based on relevance to query.

```python
for article in q.execQuery(er, sortBy="rel", maxItems=50):
    # Most relevant articles first
    pass
```

**Use When**:
- Quality over recency matters
- Researching a topic
- Finding definitive articles

#### 2. Sort by Date (date)

Sort by publication date, newest first.

```python
for article in q.execQuery(er, sortBy="date", maxItems=50):
    # Most recent articles first
    pass
```

**Use When**:
- Breaking news monitoring
- Latest developments
- Time-sensitive content

#### 3. Sort by Social Score (socialScore)

Sort by social media engagement (shares, likes, comments).

```python
for article in q.execQuery(er, sortBy="socialScore", maxItems=50):
    # Viral/trending articles first
    pass
```

**Use When**:
- Finding trending content
- Social media posting
- Engagement-focused curation

#### 4. Sort by Source Importance (sourceImportance)

Sort by source authority/reputation.

```python
for article in q.execQuery(er, sortBy="sourceImportance", maxItems=50):
    # Articles from authoritative sources first
    pass
```

**Use When**:
- Credibility is crucial
- Professional reporting
- Fact-checking

### Filtering Options

#### By Language

```python
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang="eng"  # English only
)

# Multiple languages
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    lang=["eng", "spa", "fra"]  # English, Spanish, French
)
```

#### By Date Range

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

#### By Source

```python
# Include specific sources
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    sourceUri=["bbc.co.uk", "reuters.com", "bloomberg.com"]
)

# Exclude sources (manual filtering)
excluded_sources = ["example-spam.com", "low-quality.com"]

for article in q.execQuery(er):
    if article['source']['uri'] not in excluded_sources:
        process(article)
```

#### By Location

```python
# Articles from specific countries
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    sourceLocationUri=[
        "http://en.wikipedia.org/wiki/United_States",
        "http://en.wikipedia.org/wiki/United_Kingdom"
    ]
)
```

#### By Category

```python
# Technology news only
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    categoryUri="http://www.dmoz.org/Computers/Internet"
)
```

### Complex Filtering

```python
from datetime import datetime, timedelta

# Combine multiple filters
date_end = datetime.now().strftime("%Y-%m-%d")
date_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

q = QueryArticlesIter(
    conceptUri=QueryItems.AND([
        "http://en.wikipedia.org/wiki/Bitcoin",
        "http://en.wikipedia.org/wiki/Mining"
    ]),
    keywords=QueryItems.OR(["ASIC", "hashrate", "mining pool"]),
    dateStart=date_start,
    dateEnd=date_end,
    lang="eng",
    sourceUri=["reuters.com", "bloomberg.com", "coindesk.com"],
    isDuplicateFilter="skipDuplicates"
)
```

## Rate Limiting and Optimization

### Understanding Rate Limits

Event Registry enforces rate limits to ensure fair usage:

- **Request-based**: Limited number of API calls per day
- **Results-based**: Limited number of articles per request
- **Concurrent requests**: Limited simultaneous connections

### Checking Quota

```python
# Check remaining requests
remaining = er.getRemainingAvailableRequests()
print(f"Remaining requests: {remaining}")

# Check before making request
if remaining < 10:
    print("Low on quota, consider waiting")
```

### Implementing Exponential Backoff

```python
import time

def fetch_with_backoff(query_func, max_retries=5):
    """Execute query with exponential backoff on rate limit."""
    for attempt in range(max_retries):
        try:
            return query_func()
        except Exception as e:
            if "rate limit" in str(e).lower():
                if attempt == max_retries - 1:
                    raise
                
                wait_time = (2 ** attempt) * 10  # 10, 20, 40, 80, 160 seconds
                print(f"Rate limit hit, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
    
    raise Exception("Max retries exceeded")

# Usage
def my_query():
    q = QueryArticlesIter(conceptUri="http://en.wikipedia.org/wiki/Bitcoin")
    return list(q.execQuery(er, maxItems=100))

articles = fetch_with_backoff(my_query)
```

### Caching Results

```python
import json
import os
from datetime import datetime, timedelta

class ArticleCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, query_params):
        """Generate cache key from query parameters."""
        import hashlib
        key_str = json.dumps(query_params, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query_params, max_age_hours=24):
        """Retrieve from cache if fresh enough."""
        cache_key = self.get_cache_key(query_params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        # Check age
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age = datetime.now() - mtime
        
        if age > timedelta(hours=max_age_hours):
            return None
        
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    def set(self, query_params, data):
        """Store in cache."""
        cache_key = self.get_cache_key(query_params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)

# Usage
cache = ArticleCache()
query_params = {
    'conceptUri': 'http://en.wikipedia.org/wiki/Bitcoin',
    'dateStart': '2024-01-01',
    'dateEnd': '2024-01-31'
}

# Try cache first
articles = cache.get(query_params, max_age_hours=6)

if articles is None:
    # Fetch from API
    q = QueryArticlesIter(**query_params)
    articles = list(q.execQuery(er, maxItems=100))
    
    # Store in cache
    cache.set(query_params, articles)
```

### Optimization Best Practices

1. **Request Only What You Need**:
```python
# Bad - requesting everything
returnInfo = ReturnInfo(articleInfo=ArticleInfoFlags(**{k: True for k in dir(ArticleInfoFlags)}))

# Good - only needed fields
returnInfo = ReturnInfo(articleInfo=ArticleInfoFlags(title=True, url=True, date=True))
```

2. **Use Narrow Date Ranges**:
```python
# Bad - too broad
q = QueryArticlesIter(conceptUri="...", dateStart="2020-01-01")

# Good - specific range
q = QueryArticlesIter(conceptUri="...", dateStart="2024-01-15", dateEnd="2024-01-16")
```

3. **Use Specific Concepts**:
```python
# Bad - too general
q = QueryArticlesIter(conceptUri="http://en.wikipedia.org/wiki/Technology")

# Good - specific
q = QueryArticlesIter(
    conceptUri=QueryItems.AND([
        "http://en.wikipedia.org/wiki/Bitcoin",
        "http://en.wikipedia.org/wiki/Mining"
    ])
)
```

4. **Batch Processing**:
```python
# Process in batches to implement delays
batch_size = 50
processed = 0

for article in q.execQuery(er, maxItems=500):
    process(article)
    processed += 1
    
    if processed % batch_size == 0:
        time.sleep(5)  # 5-second delay between batches
```

5. **Monitor Quota Usage**:
```python
import logging

def fetch_articles_monitored(er, query):
    """Fetch articles with quota monitoring."""
    before = er.getRemainingAvailableRequests()
    
    articles = list(query.execQuery(er, maxItems=100))
    
    after = er.getRemainingAvailableRequests()
    used = before - after
    
    logging.info(f"Fetched {len(articles)} articles, used {used} quota")
    logging.info(f"Remaining quota: {after}")
    
    return articles
```

## Common Patterns for Bitcoin Mining News

### Pattern 1: Daily News Digest

```python
def fetch_daily_bitcoin_mining_digest(api_key: str) -> list:
    """Fetch Bitcoin mining news from the last 24 hours."""
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    # Last 24 hours
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng",
        isDuplicateFilter="skipDuplicates"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=50):
        articles.append(article)
    
    return articles
```

### Pattern 2: Trending Mining Articles

```python
def fetch_trending_mining_articles(api_key: str, days_back: int = 7) -> list:
    """Fetch trending Bitcoin mining articles with high social engagement."""
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems, ReturnInfo, ArticleInfoFlags
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
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
    
    # Request social metrics
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
    for article in q.execQuery(er, sortBy="socialScore", maxItems=25):
        # Filter for high engagement
        if article.get('socialScore', 0) > 10:
            articles.append(article)
    
    return articles
```

### Pattern 3: Mining Hardware Announcements

```python
def fetch_mining_hardware_news(api_key: str, days_back: int = 14) -> list:
    """Fetch news about new Bitcoin mining hardware."""
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
        keywords=QueryItems.OR([
            "ASIC miner",
            "Antminer",
            "Whatsminer",
            "mining hardware",
            "mining equipment",
            "new miner",
            "hashrate"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=30):
        articles.append(article)
    
    return articles
```

### Pattern 4: Mining Profitability Analysis

```python
def fetch_mining_profitability_news(api_key: str, days_back: int = 7) -> list:
    """Fetch articles discussing Bitcoin mining profitability."""
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR([
            "profitability",
            "earnings",
            "revenue",
            "electricity cost",
            "mining economics",
            "break-even"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="rel", maxItems=25):
        articles.append(article)
    
    return articles
```

### Pattern 5: Regulatory News

```python
def fetch_mining_regulatory_news(api_key: str, days_back: int = 30) -> list:
    """Fetch news about regulations affecting Bitcoin mining."""
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR([
            "regulation",
            "ban",
            "legal",
            "government",
            "policy",
            "law",
            "compliance"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    articles = []
    # Sort by source importance for credible regulatory news
    for article in q.execQuery(er, sortBy="sourceImportance", maxItems=25):
        articles.append(article)
    
    return articles
```

### Pattern 6: Environmental Impact Stories

```python
def fetch_mining_environmental_news(api_key: str, days_back: int = 30) -> list:
    """Fetch news about environmental impact of Bitcoin mining."""
    from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    q = QueryArticlesIter(
        conceptUri=QueryItems.AND([
            "http://en.wikipedia.org/wiki/Bitcoin",
            "http://en.wikipedia.org/wiki/Mining"
        ]),
        keywords=QueryItems.OR([
            "energy consumption",
            "renewable energy",
            "carbon footprint",
            "sustainability",
            "environmental",
            "green energy",
            "clean energy"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="rel", maxItems=30):
        articles.append(article)
    
    return articles
```

## Code Examples

### Complete Example: Bitcoin Mining News Aggregator

```python
#!/usr/bin/env python3
"""
Bitcoin Mining News Aggregator
Fetches, filters, and processes Bitcoin mining news from Event Registry
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
from eventregistry import (
    EventRegistry,
    QueryArticlesIter,
    QueryItems,
    ReturnInfo,
    ArticleInfoFlags
)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")

class BitcoinMiningNewsAggregator:
    """Aggregates Bitcoin mining news from Event Registry."""
    
    def __init__(self, api_key: str):
        """Initialize the aggregator with API key."""
        self.er = EventRegistry(apiKey=api_key)
        
        # Bitcoin and Mining concept URIs
        self.bitcoin_uri = "http://en.wikipedia.org/wiki/Bitcoin"
        self.mining_uri = "http://en.wikipedia.org/wiki/Mining"
        
        # Blacklisted sources
        self.blacklisted_sources = [
            "example-spam.com",
            "low-quality-news.com"
        ]
    
    def fetch_articles(
        self,
        days_back: int = 7,
        max_articles: int = 100,
        sort_by: str = "socialScore"
    ) -> List[Dict]:
        """
        Fetch Bitcoin mining articles.
        
        Args:
            days_back: Number of days to look back
            max_articles: Maximum number of articles to fetch
            sort_by: Sorting strategy (socialScore, date, rel, sourceImportance)
        
        Returns:
            List of article dictionaries
        """
        # Calculate date range
        date_end = datetime.now().strftime("%Y-%m-%d")
        date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Create query
        q = QueryArticlesIter(
            conceptUri=QueryItems.AND([
                self.bitcoin_uri,
                self.mining_uri
            ]),
            keywords=QueryItems.OR([
                "ASIC",
                "hashrate",
                "mining pool",
                "mining rig",
                "difficulty adjustment"
            ]),
            dateStart=date_start,
            dateEnd=date_end,
            lang="eng",
            isDuplicateFilter="skipDuplicates"
        )
        
        # Configure return information
        q.setRequestedResult(ReturnInfo(
            articleInfo=ArticleInfoFlags(
                title=True,
                body=True,
                url=True,
                date=True,
                time=True,
                source=True,
                authors=True,
                concepts=True,
                sentiment=True,
                image=True,
                socialScore=True
            )
        ))
        
        # Fetch articles
        articles = []
        for article in q.execQuery(self.er, sortBy=sort_by, maxItems=max_articles):
            articles.append(article)
        
        return articles
    
    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles based on quality criteria.
        
        Args:
            articles: List of articles to filter
        
        Returns:
            Filtered list of articles
        """
        filtered = []
        
        for article in articles:
            # Skip blacklisted sources
            source_uri = article.get('source', {}).get('uri', '')
            if source_uri in self.blacklisted_sources:
                continue
            
            # Require minimum quality
            if not article.get('title') or not article.get('url'):
                continue
            
            # Skip articles with very negative sentiment for spam
            sentiment = article.get('sentiment', 0)
            if sentiment < -0.5:
                continue
            
            filtered.append(article)
        
        return filtered
    
    def save_articles(self, articles: List[Dict], filename: str = "articles.json"):
        """Save articles to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(articles)} articles to {filename}")
    
    def print_summary(self, articles: List[Dict]):
        """Print summary of fetched articles."""
        print(f"\n{'='*80}")
        print(f"Fetched {len(articles)} Bitcoin Mining Articles")
        print(f"{'='*80}\n")
        
        for i, article in enumerate(articles[:10], 1):  # Show first 10
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('title', 'Unknown')
            date = article.get('date', 'Unknown')
            social_score = article.get('socialScore', 0)
            
            print(f"{i}. {title}")
            print(f"   Source: {source} | Date: {date} | Social Score: {social_score}")
            print(f"   URL: {article.get('url', 'N/A')}\n")

def main():
    """Main execution function."""
    # Check API key
    if not API_KEY:
        print("Error: EVENT_REGISTRY_API_KEY not found in environment")
        return
    
    # Initialize aggregator
    aggregator = BitcoinMiningNewsAggregator(API_KEY)
    
    # Fetch articles
    print("Fetching Bitcoin mining articles...")
    articles = aggregator.fetch_articles(
        days_back=7,
        max_articles=100,
        sort_by="socialScore"
    )
    
    print(f"Fetched {len(articles)} articles")
    
    # Filter articles
    print("Filtering articles...")
    filtered_articles = aggregator.filter_articles(articles)
    print(f"Filtered to {len(filtered_articles)} articles")
    
    # Print summary
    aggregator.print_summary(filtered_articles)
    
    # Save to file
    aggregator.save_articles(filtered_articles, "bitcoin_mining_articles.json")

if __name__ == "__main__":
    main()
```

### Error Handling Example

```python
import time
import logging
from eventregistry import EventRegistry, QueryArticlesIter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_articles_with_error_handling(api_key: str, max_retries: int = 3) -> list:
    """Fetch articles with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            er = EventRegistry(apiKey=api_key)
            
            q = QueryArticlesIter(
                conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
                lang="eng"
            )
            
            articles = []
            for article in q.execQuery(er, maxItems=100):
                articles.append(article)
            
            logger.info(f"Successfully fetched {len(articles)} articles")
            return articles
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "invalid api key" in error_msg:
                logger.error("Invalid API key - check your credentials")
                raise
            
            elif "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10
                    logger.warning(f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error("Rate limit exceeded after max retries")
                    raise
            
            elif "no results" in error_msg:
                logger.info("No articles found for query")
                return []
            
            else:
                logger.error(f"Unexpected error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)
    
    return []
```

## Additional Resources

### Official Documentation
- [Event Registry Homepage](https://eventregistry.org/)
- [API Documentation](https://eventregistry.org/documentation)
- [Python SDK GitHub](https://github.com/EventRegistry/event-registry-python)
- [API Reference](https://eventregistry.org/documentation/api)

### Community Resources
- [SDK Wiki](https://github.com/EventRegistry/event-registry-python/wiki)
- [Concept Search Guide](https://github.com/EventRegistry/event-registry-python/wiki/Concepts)
- [Examples Repository](https://github.com/EventRegistry/event-registry-python/tree/master/examples)

### Support
- GitHub Issues: https://github.com/EventRegistry/event-registry-python/issues
- Email: info@eventregistry.org
- API Status: Check dashboard for service status

### Tips for Success

1. **Start Small**: Test with small date ranges and limited results
2. **Read Responses**: Examine the structure of returned articles
3. **Use Logging**: Track API usage and debug issues
4. **Cache Aggressively**: Avoid redundant API calls
5. **Monitor Quota**: Keep track of daily request limits
6. **Handle Errors**: Implement robust error handling and retries
7. **Optimize Queries**: Use specific concepts and narrow date ranges
8. **Test Thoroughly**: Verify results match expectations

---

*Last Updated: January 2024*
