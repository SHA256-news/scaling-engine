# Queue Persistence Between GitHub Actions Runs

## Problem

Previously, the bot's queue files (`article_queue.json`, `posted_articles.json`, `daily_brief_cache.json`) were listed in `.gitignore`, which meant they were not committed to the repository. This caused a critical issue:

1. **Monitor workflow** runs and fetches articles, saving them to `article_queue.json`
2. **Post workflow** runs in a separate GitHub Actions job with a fresh checkout
3. The queue file is not present (because it wasn't committed), so the post workflow finds an empty queue
4. Result: "Queue is empty, nothing to post" even though articles were just fetched

## Solution

The queue files are now **tracked by Git** and committed after each workflow run. This ensures that state persists between independent GitHub Actions jobs.

### Changes Made

1. **Updated `.gitignore`**: Commented out the queue files so they are now tracked
   ```gitignore
   # These files are now committed to persist state between GitHub Actions runs
   # article_queue.json
   # posted_articles.json
   # daily_brief_cache.json
   ```

2. **Updated GitHub Actions workflows**: Added commit and push steps after each workflow
   - Monitor workflow commits `article_queue.json` and `daily_brief_cache.json`
   - Post workflow commits `article_queue.json` and `posted_articles.json`
   - Daily brief workflow commits `daily_brief_cache.json`

3. **Created initial queue files**: Empty JSON arrays to initialize the state

## How It Works

### Monitor Workflow (every 30 minutes)
```yaml
- name: Run Monitoring Workflow
  env:
    EVENT_REGISTRY_API_KEY: ${{ secrets.EVENT_REGISTRY_API_KEY }}
  run: python main.py --workflow monitor

- name: Commit and Push Queue Changes
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add article_queue.json daily_brief_cache.json || true
    git diff --staged --quiet || git commit -m "Update article queue from monitor workflow [skip ci]"
    git push || true
```

1. Fetches new articles from Event Registry
2. Adds them to `article_queue.json`
3. Commits and pushes the updated queue to the repository
4. Uses `[skip ci]` to avoid triggering additional workflow runs

### Post Workflow (every 24 minutes)
```yaml
- name: Run Posting Workflow
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
    # ... other secrets
  run: python main.py --workflow post

- name: Commit and Push Queue Changes
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add article_queue.json posted_articles.json || true
    git diff --staged --quiet || git commit -m "Update article queue and posted articles from post workflow [skip ci]"
    git push || true
```

1. Checks out the repository (including the latest queue)
2. Reads from `article_queue.json`
3. Posts a tweet and removes the article from the queue
4. Records the post in `posted_articles.json`
5. Commits and pushes both files back to the repository

### Daily Brief Workflow (once per day)
```yaml
- name: Run Daily Brief Workflow
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: python main.py --workflow daily-brief

- name: Commit and Push Cache Changes
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add daily_brief_cache.json || true
    git diff --staged --quiet || git commit -m "Update daily brief cache from daily-brief workflow [skip ci]"
    git push || true
```

1. Processes cached articles from `daily_brief_cache.json`
2. Generates a daily report
3. Clears the cache
4. Commits and pushes the updated cache file

## Benefits

1. **State Persistence**: Queue state is maintained between workflow runs
2. **Reliability**: No more "queue is empty" errors
3. **Visibility**: Queue state is visible in the repository
4. **Debugging**: Easy to inspect queue contents via Git history
5. **Audit Trail**: Full history of what was queued and posted

## Error Handling

The commit and push steps use `|| true` to handle edge cases:
- If there are no changes to commit, the workflow continues successfully
- If there's a push conflict (rare), the workflow continues but may log a warning
- The `[skip ci]` flag prevents infinite workflow loops

## Monitoring

You can inspect the queue at any time:
- View `article_queue.json` in the repository
- Check recent commits from github-actions[bot]
- Use the tools CLI: `python tools.py inspect-queue`

## Alternative Approaches Considered

### Approach 1: GitHub Actions Artifacts (Rejected)
- **Pros**: Keeps queue files out of Git history
- **Cons**: 
  - Artifacts expire after 90 days
  - More complex to implement (upload/download between jobs)
  - Harder to debug and inspect
  - Requires careful coordination between jobs

### Approach 2: External Storage (Rejected)
- **Pros**: Scalable for large queues
- **Cons**:
  - Requires additional infrastructure (S3, database, etc.)
  - Adds complexity and cost
  - Overkill for a simple queue of article metadata

### Approach 3: Git Commits (Selected) ✓
- **Pros**:
  - Simple and reliable
  - No additional infrastructure needed
  - Built-in version control and audit trail
  - Easy to debug and inspect
- **Cons**:
  - Adds commits to repository history (mitigated with `[skip ci]`)
  - Not suitable for very large files (not an issue for small JSON queues)

## Future Improvements

If the queue grows very large or commit frequency becomes problematic, consider:
1. Squashing bot commits periodically
2. Moving to a separate branch for state files
3. Implementing GitHub Actions artifacts with better coordination
4. Using a lightweight external store (Redis, SQLite, etc.)

For now, the Git-based approach is simple, reliable, and appropriate for the bot's needs.
