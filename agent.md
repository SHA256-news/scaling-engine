# Bitcoin Mining News Bot - AI Agent Instructions

## Critical File Operation Protocols

### ALWAYS Verify Before Proceeding

1. **File Existence**: Always check if a file exists before attempting to read or modify it
2. **File Content**: After writing to a file, read it back to verify the content was written correctly
3. **Directory Structure**: Ensure parent directories exist before creating files
4. **Path Resolution**: Always use absolute paths or properly resolve relative paths

### File Operation Best Practices

- Use `with` statements for file operations to ensure proper closure
- Check file permissions before attempting read/write operations
- Handle encoding explicitly (UTF-8) for text files
- Implement try-except blocks for all file I/O operations
- Log all file operations for debugging purposes

## The Clean 4-File Design

### Architecture Overview

This bot follows a strict 4-file architecture that separates concerns and maintains simplicity:

```
config.py     → Configuration only (no logic)
bot_lib.py    → Business logic only (stateless functions)
main.py       → Orchestration only (linear workflow)
tools.py      → CLI utilities only (developer tools)
```

### Design Principles

1. **Separation of Concerns**: Each file has a single, well-defined purpose
2. **No Cross-Dependencies**: `config.py` and `bot_lib.py` don't import from each other
3. **Stateless Functions**: All functions in `bot_lib.py` are pure and testable
4. **Linear Execution**: `main.py` executes steps sequentially with clear flow
5. **Configuration as Data**: `config.py` contains only data structures, no logic

## File Responsibilities

### config.py

**Purpose**: Single source of truth for all configuration

**Contains**:
- API keys and credentials (loaded from environment variables)
- Filter lists (blacklisted sources, keywords, domains)
- Prompt templates for AI content generation
- Bot configuration settings (timeouts, retry counts, etc.)
- Social media platform settings

**MUST NOT contain**:
- Functions (except simple getters if absolutely necessary)
- Business logic
- API calls
- Data processing

**Example Structure**:
```python
# API Configuration
EVENT_REGISTRY_API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")

# Filter Configuration
BLACKLISTED_SOURCES = [
    "example-spam-site.com",
    "low-quality-news.com"
]

BLACKLISTED_KEYWORDS = [
    "clickbait",
    "sponsored"
]

# Prompt Templates
CONTENT_GENERATION_PROMPT = """
Generate a tweet about: {article_title}
Focus on: {key_points}
"""
```

### bot_lib.py

**Purpose**: Core business logic as stateless functions

**Contains**:
- Functions for fetching news articles
- Functions for filtering content
- Functions for AI content generation
- Functions for posting to social media
- Utility functions for data processing

**Design Requirements**:
- All functions must be stateless (no global state)
- Each function should do one thing well
- Functions should be pure when possible
- Clear input parameters and return values
- Comprehensive docstrings

**Anti-Patterns to Avoid**:
- ❌ Classes (use functions instead)
- ❌ Global variables (pass data as parameters)
- ❌ Side effects without clear documentation
- ❌ Complex nested logic (break into smaller functions)

**Example Structure**:
```python
def fetch_articles(api_key: str, query: str, from_date: str) -> list:
    """
    Fetch articles from Event Registry.
    
    Args:
        api_key: Event Registry authentication key
        query: Search query string
        from_date: ISO format date string
    
    Returns:
        List of article dictionaries
    
    Raises:
        APIError: If the API request fails
    """
    # Implementation here
    pass

def filter_articles(articles: list, blacklist: list) -> list:
    """
    Filter articles based on blacklist criteria.
    
    Args:
        articles: List of article dictionaries
        blacklist: List of blacklisted sources
    
    Returns:
        Filtered list of articles
    """
    # Implementation here
    pass
```

### main.py

**Purpose**: Orchestrate the bot workflow

**Contains**:
- Single `main()` function or simple linear script
- Clear sequential steps
- High-level error handling
- Logging of workflow progress

**Workflow Pattern**:
```python
def main():
    """Execute the bot workflow."""
    
    # Step 1: Setup
    logger.info("Starting bot execution")
    
    # Step 2: Fetch articles
    articles = bot_lib.fetch_articles(
        config.EVENT_REGISTRY_API_KEY,
        config.SEARCH_QUERY,
        get_date_range()
    )
    logger.info(f"Fetched {len(articles)} articles")
    
    # Step 3: Filter articles
    filtered = bot_lib.filter_articles(
        articles,
        config.BLACKLISTED_SOURCES
    )
    logger.info(f"Filtered to {len(filtered)} articles")
    
    # Step 4: Generate content
    for article in filtered:
        content = bot_lib.generate_content(
            config.GEMINI_API_KEY,
            article,
            config.CONTENT_PROMPT
        )
        
        # Step 5: Post to social media
        bot_lib.post_to_twitter(
            config.TWITTER_API_KEY,
            content
        )
    
    logger.info("Bot execution completed")

if __name__ == "__main__":
    main()
```

### tools.py

**Purpose**: Developer utilities and CLI tools

**Contains**:
- Interactive testing tools
- Debugging utilities
- Manual override functions
- Data inspection tools

**Example Commands**:
```python
# Test article fetching
python tools.py fetch --query "bitcoin mining" --count 10

# Test content generation
python tools.py generate --article-id 12345

# Verify configuration
python tools.py config --check
```

## Error Handling Patterns

### Custom Exceptions

Define specific exceptions for different failure scenarios:

```python
class BotError(Exception):
    """Base exception for bot errors."""
    pass

class APIError(BotError):
    """Raised when an API call fails."""
    pass

class ContentFilterError(BotError):
    """Raised when content filtering fails."""
    pass

class PostingError(BotError):
    """Raised when posting to social media fails."""
    pass
```

### Error Handling Strategy

1. **Catch Specific Exceptions**: Handle different error types appropriately
2. **Log Everything**: Record all errors with context
3. **Graceful Degradation**: Continue processing other items when one fails
4. **Retry Logic**: Implement exponential backoff for transient failures
5. **User Notification**: Alert on critical failures

**Example**:
```python
def process_articles(articles: list) -> list:
    """Process articles with error handling."""
    results = []
    
    for article in articles:
        try:
            content = generate_content(article)
            post_to_social_media(content)
            results.append({'status': 'success', 'article': article})
        
        except APIError as e:
            logger.error(f"API error for article {article['id']}: {e}")
            results.append({'status': 'api_error', 'article': article})
        
        except PostingError as e:
            logger.error(f"Posting error for article {article['id']}: {e}")
            results.append({'status': 'posting_error', 'article': article})
        
        except Exception as e:
            logger.error(f"Unexpected error for article {article['id']}: {e}")
            results.append({'status': 'unknown_error', 'article': article})
    
    return results
```

## Event Registry API Best Practices

### Overview

Event Registry is the primary news source for the bot. It provides access to millions of articles from global news sources with powerful semantic search capabilities.

### API Setup

1. **Authentication**: Store API key in environment variable
   ```python
   EVENT_REGISTRY_API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")
   ```

2. **Client Initialization**: Create client once, reuse across requests
   ```python
   from eventregistry import EventRegistry
   
   er = EventRegistry(apiKey=EVENT_REGISTRY_API_KEY)
   ```

3. **Rate Limiting**: Implement exponential backoff for rate limit handling
   ```python
   import time
   from eventregistry import EventRegistry
   
   def fetch_with_retry(query_func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return query_func()
           except Exception as e:
               if "rate limit" in str(e).lower():
                   wait_time = 2 ** attempt
                   time.sleep(wait_time)
               else:
                   raise
       raise Exception("Max retries exceeded")
   ```

### Query Construction with Concept URIs

**Why Use Concept URIs?**
- More accurate results through semantic understanding
- Language-agnostic matching
- Reduces false positives from keyword-only search
- Better handling of entity variations (e.g., "BTC" vs "Bitcoin")

**Finding Concept URIs**:
```python
from eventregistry import EventRegistry

er = EventRegistry(apiKey=api_key)

# Search for concepts
concepts = er.getConceptUri("Bitcoin")
# Returns: http://en.wikipedia.org/wiki/Bitcoin

mining_concepts = er.getConceptUri("Mining")
# Returns: http://en.wikipedia.org/wiki/Mining
```

**Combining Concepts**:
```python
from eventregistry import QueryItems

# AND condition (articles must match ALL concepts)
bitcoin_mining = QueryItems.AND([
    "http://en.wikipedia.org/wiki/Bitcoin",
    "http://en.wikipedia.org/wiki/Mining"
])

# OR condition (articles can match ANY concept)
crypto_topics = QueryItems.OR([
    "http://en.wikipedia.org/wiki/Bitcoin",
    "http://en.wikipedia.org/wiki/Ethereum",
    "http://en.wikipedia.org/wiki/Cryptocurrency"
])

# Complex combinations
advanced_query = QueryItems.AND([
    bitcoin_mining,
    QueryItems.OR(["ASIC", "hashrate", "mining pool"])
])
```

### Using QueryArticlesIter for Pagination

**Why QueryArticlesIter?**
- Automatic pagination handling
- Memory-efficient iteration
- Simplified code (no manual page tracking)
- Built-in error handling

**Basic Usage**:
```python
from eventregistry import QueryArticlesIter

q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    dateStart="2024-01-01",
    dateEnd="2024-01-31",
    lang="eng"
)

# Iterate through all matching articles
for article in q.execQuery(er, sortBy="socialScore", maxItems=100):
    process_article(article)
```

**Advanced Pagination Control**:
```python
# Process in batches
q = QueryArticlesIter(
    conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
    dateStart="2024-01-01",
    dateEnd="2024-01-31"
)

batch_size = 25
articles_processed = 0

for article in q.execQuery(er, sortBy="date", maxItems=100):
    process_article(article)
    articles_processed += 1
    
    # Process in batches
    if articles_processed % batch_size == 0:
        print(f"Processed {articles_processed} articles")
        time.sleep(1)  # Rate limiting
```

### ReturnInfo Configuration

**Optimize API Usage**: Only request fields you need

```python
from eventregistry import ReturnInfo, ArticleInfoFlags

# Minimal info for filtering
minimal_info = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        url=True,
        date=True,
        source=True
    )
)

# Full info for content generation
full_info = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        body=True,
        url=True,
        date=True,
        time=True,
        authors=True,
        concepts=True,
        categories=True,
        sentiment=True,
        image=True,
        socialScore=True,
        duplicateList=True
    )
)

# Apply to query
q.setRequestedResult(full_info)
```

**Common Configurations**:

```python
# For social media posting
social_media_info = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        body=True,
        url=True,
        image=True,
        socialScore=True,
        sentiment=True
    )
)

# For article filtering
filter_info = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        url=True,
        source=True,
        duplicateList=True
    )
)

# For analytics
analytics_info = ReturnInfo(
    articleInfo=ArticleInfoFlags(
        title=True,
        date=True,
        concepts=True,
        categories=True,
        sentiment=True,
        socialScore=True
    )
)
```

### Sorting Strategies

**Choose sorting based on use case**:

1. **socialScore**: For viral/trending content
   - Use when: Finding popular articles for social media
   - Best for: Engagement-focused content curation
   ```python
   for article in q.execQuery(er, sortBy="socialScore", maxItems=50):
       # Articles with high social media engagement
       post_to_social_media(article)
   ```

2. **date**: For latest news
   - Use when: Time-sensitive updates
   - Best for: Breaking news, recent developments
   ```python
   for article in q.execQuery(er, sortBy="date", maxItems=50):
       # Most recent articles first
       send_newsletter(article)
   ```

3. **rel**: For relevance (default)
   - Use when: Quality over recency
   - Best for: Topic research, content discovery
   ```python
   for article in q.execQuery(er, sortBy="rel", maxItems=50):
       # Most relevant to query
       analyze_content(article)
   ```

4. **sourceImportance**: For authoritative sources
   - Use when: Credibility is paramount
   - Best for: Fact-checking, professional reporting
   ```python
   for article in q.execQuery(er, sortBy="sourceImportance", maxItems=50):
       # From high-authority sources
       archive_article(article)
   ```

### Optimization Tips

1. **Narrow Date Ranges**: Use specific date ranges to reduce result set
   ```python
   from datetime import datetime, timedelta
   
   # Last 24 hours only
   date_end = datetime.now().strftime("%Y-%m-%d")
   date_start = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
   
   q = QueryArticlesIter(
       conceptUri="http://en.wikipedia.org/wiki/Bitcoin",
       dateStart=date_start,
       dateEnd=date_end
   )
   ```

2. **Use Specific Concepts**: More specific = fewer false positives
   ```python
   # Too broad
   q = QueryArticlesIter(conceptUri="http://en.wikipedia.org/wiki/Technology")
   
   # Better
   q = QueryArticlesIter(
       conceptUri=QueryItems.AND([
           "http://en.wikipedia.org/wiki/Bitcoin",
           "http://en.wikipedia.org/wiki/Mining"
       ])
   )
   ```

3. **Limit Fields in ReturnInfo**: Smaller payloads = faster responses
   ```python
   # Only request what you need
   q.setRequestedResult(ReturnInfo(
       articleInfo=ArticleInfoFlags(
           title=True,
           url=True,
           date=True
           # Don't request body, image, etc. if not needed
       )
   ))
   ```

4. **Cache Results**: Avoid redundant API calls
   ```python
   import json
   from datetime import datetime
   
   def fetch_articles_cached(api_key, query_params, cache_file="articles_cache.json"):
       # Check cache age
       try:
           with open(cache_file, 'r') as f:
               cached = json.load(f)
               cache_time = datetime.fromisoformat(cached['timestamp'])
               if (datetime.now() - cache_time).seconds < 3600:  # 1 hour cache
                   return cached['articles']
       except FileNotFoundError:
           pass
       
       # Fetch fresh data
       articles = fetch_articles(api_key, query_params)
       
       # Save to cache
       with open(cache_file, 'w') as f:
           json.dump({
               'timestamp': datetime.now().isoformat(),
               'articles': articles
           }, f)
       
       return articles
   ```

### Error Handling Patterns

**Common Event Registry Errors**:

```python
from eventregistry import EventRegistry

def fetch_articles_safe(api_key: str, query_params: dict) -> list:
    """Fetch articles with comprehensive error handling."""
    try:
        er = EventRegistry(apiKey=api_key)
        
        q = QueryArticlesIter(**query_params)
        articles = []
        
        for article in q.execQuery(er, sortBy="socialScore", maxItems=100):
            articles.append(article)
        
        return articles
    
    except Exception as e:
        error_message = str(e).lower()
        
        # Handle specific errors
        if "invalid api key" in error_message:
            logger.error("Invalid Event Registry API key")
            raise APIError("Authentication failed - check API key")
        
        elif "rate limit" in error_message:
            logger.warning("Rate limit exceeded, implementing backoff")
            time.sleep(60)  # Wait 1 minute
            return fetch_articles_safe(api_key, query_params)
        
        elif "no results" in error_message:
            logger.info("No articles found for query")
            return []
        
        else:
            logger.error(f"Event Registry error: {e}")
            raise APIError(f"Failed to fetch articles: {e}")
```

**Retry Logic with Exponential Backoff**:

```python
def fetch_with_exponential_backoff(fetch_func, max_retries=3):
    """Execute fetch function with exponential backoff on failure."""
    for attempt in range(max_retries):
        try:
            return fetch_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise
            
            wait_time = (2 ** attempt) * 1  # 1, 2, 4 seconds
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
            time.sleep(wait_time)
```

### Common Patterns for Bitcoin Mining News

**Pattern 1: Trending Bitcoin Mining Articles**
```python
def fetch_trending_bitcoin_mining_news(api_key: str, max_articles: int = 50) -> list:
    """Fetch trending Bitcoin mining articles from the last 7 days."""
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
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
    
    q.setRequestedResult(ReturnInfo(
        articleInfo=ArticleInfoFlags(
            title=True,
            body=True,
            url=True,
            socialScore=True,
            image=True,
            sentiment=True
        )
    ))
    
    articles = []
    for article in q.execQuery(er, sortBy="socialScore", maxItems=max_articles):
        articles.append(article)
    
    return articles
```

**Pattern 2: Recent Mining Hardware News**
```python
def fetch_mining_hardware_news(api_key: str, days_back: int = 3) -> list:
    """Fetch recent Bitcoin mining hardware announcements."""
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

**Pattern 3: Regulatory News Affecting Mining**
```python
def fetch_mining_regulatory_news(api_key: str, max_articles: int = 25) -> list:
    """Fetch news about regulations affecting Bitcoin mining."""
    from datetime import datetime, timedelta
    
    er = EventRegistry(apiKey=api_key)
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    
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
            "energy"
        ]),
        dateStart=date_start,
        dateEnd=date_end,
        lang="eng"
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="sourceImportance", maxItems=max_articles):
        articles.append(article)
    
    return articles
```

## Gemini API Implementation Guidelines

### API Setup

1. **Authentication**: Store API key in environment variable
2. **Client Initialization**: Create client once, reuse for multiple requests
3. **Rate Limiting**: Implement rate limiting to avoid quota exhaustion
4. **Error Handling**: Handle API-specific errors gracefully

### Content Generation Best Practices

1. **Clear Prompts**: Write specific, unambiguous prompts
2. **Context Provision**: Provide sufficient context for quality output
3. **Output Validation**: Verify generated content meets requirements
4. **Fallback Mechanisms**: Have backup strategies for API failures

**Example Implementation**:
```python
import google.generativeai as genai

def generate_tweet(api_key: str, article: dict, prompt_template: str) -> str:
    """
    Generate tweet content using Gemini API.
    
    Args:
        api_key: Gemini API key
        article: Article dictionary with title, description
        prompt_template: Template string for prompt
    
    Returns:
        Generated tweet text
    
    Raises:
        APIError: If generation fails
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = prompt_template.format(
            title=article['title'],
            description=article['description']
        )
        
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise APIError("Empty response from Gemini API")
        
        return response.text.strip()
    
    except Exception as e:
        raise APIError(f"Gemini API error: {e}")
```

### Response Validation

Always validate API responses:
- Check for empty responses
- Verify content length constraints
- Ensure appropriate content (no harmful material)
- Validate formatting requirements

## Development Workflow

### 1. Setup Phase

```bash
# Clone repository
git clone <repository-url>
cd scaling-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Development Phase

**Before Making Changes**:
1. Read all relevant code files
2. Understand the current architecture
3. Identify which file(s) need modification
4. Plan minimal changes

**While Making Changes**:
1. Follow the Clean 4-File Design principles
2. Write functions, not classes
3. Keep functions small and focused
4. Add comprehensive docstrings
5. Verify each change immediately

**Testing Changes**:
```bash
# Test individual functions
python tools.py test-function fetch_articles

# Test full workflow
python main.py

# Check logs
tail -f bot.log
```

### 3. Verification Phase

**Must Verify**:
- [ ] All file operations succeed
- [ ] API calls return expected data
- [ ] Generated content meets quality standards
- [ ] Social media posts are successful
- [ ] Error handling works as expected
- [ ] Logs are informative

### 4. Commit Phase

```bash
# Check what changed
git status
git diff

# Stage changes
git add config.py bot_lib.py main.py

# Commit with clear message
git commit -m "Add article filtering by keyword"

# Push changes
git push origin main
```

## Content Quality Rules

### Article Selection Criteria

**Must Include**:
- Relevant to Bitcoin mining
- From reputable sources
- Recent (within configured time window)
- Complete information (title, description, URL)

**Must Exclude**:
- Blacklisted sources
- Blacklisted keywords
- Duplicate articles
- Articles without sufficient content
- Promotional/spam content

### Generated Content Requirements

**Twitter Posts**:
- Under 280 characters
- Include relevant hashtags (#Bitcoin, #Mining)
- Include article link
- Clear and engaging language
- No promotional tone

**Quality Checks**:
- Factually accurate based on source
- Appropriate tone for platform
- No spam indicators
- Proper grammar and spelling
- Relevant to target audience

### Content Validation

```python
def validate_generated_content(content: str, platform: str) -> bool:
    """
    Validate generated content meets quality standards.
    
    Args:
        content: Generated content string
        platform: Target platform ('twitter', 'facebook', etc.)
    
    Returns:
        True if content passes validation
    """
    if platform == 'twitter':
        if len(content) > 280:
            return False
        if not any(tag in content for tag in ['#Bitcoin', '#Mining']):
            return False
    
    # Check for spam indicators
    spam_words = ['click here', 'buy now', 'limited offer']
    if any(word in content.lower() for word in spam_words):
        return False
    
    return True
```

## Testing Strategy

### Unit Testing

Test individual functions in isolation:

```python
import unittest
from bot_lib import filter_articles

class TestArticleFiltering(unittest.TestCase):
    
    def test_filter_blacklisted_source(self):
        """Test that blacklisted sources are filtered out."""
        articles = [
            {'source': 'good-news.com', 'title': 'Article 1'},
            {'source': 'spam-site.com', 'title': 'Article 2'}
        ]
        blacklist = ['spam-site.com']
        
        result = filter_articles(articles, blacklist)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['source'], 'good-news.com')
```

### Integration Testing

Test the complete workflow:

```python
def test_full_workflow():
    """Test complete bot workflow with mock data."""
    # Setup
    test_config = create_test_config()
    
    # Execute
    articles = fetch_articles(test_config)
    filtered = filter_articles(articles, test_config.blacklist)
    content = generate_content(filtered[0], test_config)
    
    # Verify
    assert len(articles) > 0
    assert len(filtered) <= len(articles)
    assert len(content) <= 280
```

### Manual Testing

Use `tools.py` for manual verification:

```bash
# Fetch and display articles
python tools.py fetch --show

# Generate content without posting
python tools.py generate --dry-run

# Test posting with test account
python tools.py post --test-mode
```

## Repository Management

### File Organization

```
scaling-engine/
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions workflow
├── config.py                  # Configuration
├── bot_lib.py                 # Business logic
├── main.py                    # Entry point
├── tools.py                   # CLI utilities
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
└── agent.md                  # This file
```

### Dependencies Management

**requirements.txt** should include:
```
requests>=2.31.0
google-generativeai>=0.3.0
tweepy>=4.14.0
python-dotenv>=1.0.0
```

Update dependencies:
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

### Environment Variables

Required environment variables (in `.env`):
```
EVENT_REGISTRY_API_KEY=your_event_registry_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_SECRET=your_twitter_access_secret_here
```

### Git Workflow

**Branch Strategy**:
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `hotfix/*`: Emergency fixes

**Commit Guidelines**:
- Use clear, descriptive commit messages
- One logical change per commit
- Reference issues in commit messages
- Keep commits atomic and focused

### GitHub Actions

The `.github/workflows/main.yml` file automates bot execution:

```yaml
name: Bitcoin Mining News Bot

on:
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours
  workflow_dispatch:  # Allow manual triggers

jobs:
  run-bot:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run bot
      env:
        EVENT_REGISTRY_API_KEY: ${{ secrets.EVENT_REGISTRY_API_KEY }}
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
        TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
        TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
        TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
      run: |
        python main.py
```

## Final Rules and Reminders

### ALWAYS

✅ **Verify file operations**: Check that files exist and contain expected data
✅ **Use absolute paths**: Or properly resolve relative paths
✅ **Handle errors gracefully**: Catch specific exceptions and log them
✅ **Follow the 4-file design**: Keep concerns separated
✅ **Write stateless functions**: No global state, clear parameters
✅ **Document everything**: Comprehensive docstrings and comments
✅ **Test incrementally**: Verify each change immediately
✅ **Log extensively**: Record all important operations
✅ **Validate API responses**: Never trust external data blindly
✅ **Keep it simple**: Functions over classes, clarity over cleverness

### NEVER

❌ **Don't mix concerns**: Keep configuration, logic, and orchestration separate
❌ **Don't use classes**: Use functions unless absolutely necessary
❌ **Don't use global state**: Pass data as function parameters
❌ **Don't ignore errors**: Always handle exceptions appropriately
❌ **Don't skip verification**: Always check results before proceeding
❌ **Don't commit secrets**: Use environment variables for sensitive data
❌ **Don't make assumptions**: Verify file existence and API responses
❌ **Don't write complex code**: Keep functions small and focused
❌ **Don't forget logging**: Log all important operations
❌ **Don't deviate from architecture**: Respect the 4-file design

### Code Quality Standards

1. **Readability**: Code should be self-documenting
2. **Simplicity**: Choose simple solutions over clever ones
3. **Consistency**: Follow existing patterns in the codebase
4. **Testability**: Write code that's easy to test
5. **Maintainability**: Think about future developers

### When in Doubt

1. Check this document for guidance
2. Look at existing code for patterns
3. Keep changes minimal and focused
4. Ask for clarification rather than guessing
5. Test thoroughly before committing

---

**Remember**: The goal is to create a reliable, maintainable bot that's easy to understand and modify. Simplicity and verification are your best tools.