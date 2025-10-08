# Twitter API Rate Limiting Strategy

## Overview

Twitter's Free Tier API provides **100 posts per 24 hours**. This document explains how the Bitcoin Mining News Bot respects these limits while maintaining continuous coverage.

## Rate Limit Details

- **Limit**: 100 posts per 24 hours
- **Reset**: Midnight UTC daily
- **Scope**: Includes tweets, retweets, replies
- **Error**: 429 (Too Many Requests) when exceeded

## Posting Strategy

### Conservative Approach (Recommended)

**Target**: 60 posts per day  
**Posting Interval**: Every 24 minutes  
**Coverage**: 24 hours continuous  
**Safety Buffer**: 40 posts unused (40%)

**Advantages**:
- Large safety margin for errors/retries
- Consistent posting rhythm
- Buffer for priority/breaking news
- Handles timezone issues gracefully

### Schedule Example

```
00:00 UTC - Post 1
00:24 UTC - Post 2
00:48 UTC - Post 3
01:12 UTC - Post 4
...
23:36 UTC - Post 60
```

## Implementation

### Two-Workflow Architecture

**1. Monitoring Workflow** (every 30 minutes):
- Check Event Registry for new articles (past 1 hour)
- Filter and add to article queue
- Store for daily brief generation
- **Does NOT post to Twitter**

**2. Posting Workflow** (every 24 minutes):
- Check rate limiter status
- Get next article from queue
- Generate tweet with Gemini
- Post to Twitter (if within limits)
- Record post timestamp

### Queue Management

Articles are:
1. **Collected continuously** (every 30 min)
2. **Queued by priority** (social score)
3. **Posted at intervals** (every 24 min)
4. **Expired after 48 hours** (removed from queue)

### Rate Limiter Logic

```python
# Check if posting is allowed
if not rate_limiter.can_post():
    logger.warning("Rate limit reached")
    return

# Calculate wait time
wait_time = rate_limiter.wait_time_until_next_post()
if wait_time > 0:
    time.sleep(wait_time)

# Post and record
post_to_twitter(tweet)
rate_limiter.record_post()
```

## Error Handling

### 429 Rate Limit Error

```python
try:
    post_to_twitter(tweet)
except TwitterAPIError as e:
    if e.status_code == 429:
        # Extract reset time from headers
        reset_time = e.rate_limit_reset
        wait_seconds = (reset_time - now()).total_seconds()
        
        logger.error(f"Rate limit exceeded. Resets in {wait_seconds/60:.0f} minutes")
        
        # Re-queue article for later
        article_queue.add_articles([article])
```

### Monitoring Health

Daily checks:
- Are we on track? (posts vs expected)
- Is queue healthy? (size, staleness)
- Are we approaching limit? (remaining posts)

## Best Practices

1. **Stay Under Limit**: Target 60-75 posts/day, not 100
2. **Monitor Continuously**: Track posts in rolling 24-hour window
3. **Respect Reset Time**: Don't try to game the midnight reset
4. **Queue Intelligently**: Priority queue by social score/breaking news
5. **Handle Failures Gracefully**: Re-queue failed posts
6. **Log Everything**: Track all posting attempts and rate limit status

## Configuration

In `config.py`:
```python
# Rate Limiting
TWITTER_MAX_POSTS_PER_DAY = 60
TWITTER_POSTING_INTERVAL_MINUTES = 24

# Monitoring
MONITORING_INTERVAL_MINUTES = 30
MONITORING_LOOKBACK_HOURS = 1

# Queue
ARTICLE_QUEUE_FILE = "article_queue.json"
ARTICLE_MAX_AGE_HOURS = 48
```

## Troubleshooting

**Problem**: Hitting rate limits before 100 posts
- **Check**: Are you counting retweets/replies?
- **Solution**: Only count original tweets

**Problem**: Inconsistent posting rhythm
- **Check**: Is GitHub Actions running on schedule?
- **Solution**: Verify cron syntax, check workflow runs

**Problem**: Queue growing too large
- **Check**: Are posts succeeding?
- **Solution**: Check Twitter API status, verify credentials

**Problem**: Missing breaking news
- **Check**: Monitoring frequency too low?
- **Solution**: Increase monitoring to every 15 minutes

---

**Remember**: Twitter's rate limits are strict. Always maintain a safety buffer!
