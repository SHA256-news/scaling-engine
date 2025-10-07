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