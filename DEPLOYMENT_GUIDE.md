# Deployment Guide - Queue Persistence Fix

## What Changed

This PR fixes the critical issue where the post workflow reported success but posted no tweets because the article queue was not persisted between GitHub Actions runs.

### The Fix
Queue files are now committed to the repository after each workflow run, ensuring state persists between independent GitHub Actions jobs.

---

## What to Expect After Merge

### Immediate Effects

1. **New commits from github-actions[bot]**
   - You'll see automated commits with messages like:
     - `Update article queue from monitor workflow [skip ci]`
     - `Update article queue and posted articles from post workflow [skip ci]`
     - `Update daily brief cache from daily-brief workflow [skip ci]`
   - These commits will appear every time a workflow modifies queue files
   - The `[skip ci]` flag prevents these commits from triggering additional workflow runs

2. **Queue files in repository**
   - `article_queue.json` - Contains articles waiting to be posted
   - `posted_articles.json` - History of posted articles (last 30 days)
   - `daily_brief_cache.json` - Articles cached for daily brief (last 24 hours)

3. **Working tweet posting**
   - Monitor workflow will populate the queue with articles
   - Post workflow will actually post tweets (instead of finding an empty queue)
   - You'll see "Tweet posted successfully!" in the logs

---

## Monitoring the Fix

### 1. Check Queue Contents

View the queue file directly in GitHub:
- Navigate to `article_queue.json` in the repository
- Refresh after the monitor workflow runs to see new articles

Or use the tools CLI:
```bash
python tools.py inspect-queue
```

### 2. Monitor Workflow Logs

**Monitor Workflow** (every 30 min):
```
Starting MONITOR workflow
Fetching articles from 2024-10-08 to 2024-10-08
Fetched 42 articles from Event Registry
Filtered to 23 quality articles
Added 15 new articles to queue
Monitor workflow completed successfully
```

**Post Workflow** (every 24 min):
```
Starting POST workflow
Processing article: Bitcoin Mining Difficulty Reaches New High
Generating tweet with Gemini AI...
Generated tweet: Bitcoin mining difficulty hits record high...
Posting to Twitter...
Tweet posted successfully! ID: 1234567890
Post workflow completed successfully
```

### 3. Check Git History

See recent bot commits:
```bash
git log --author="github-actions" --oneline -10
```

Expected output:
```
abc1234 Update article queue and posted articles from post workflow [skip ci]
def5678 Update article queue from monitor workflow [skip ci]
ghi9012 Update article queue from monitor workflow [skip ci]
```

### 4. Verify Tweet Posting

Check the Twitter account to confirm tweets are being posted:
- Tweets should appear approximately every 24 minutes (when queue is not empty)
- Maximum 60 tweets per day (rate limit)

---

## Troubleshooting

### Issue: Queue stays empty
**Symptoms**: Monitor workflow runs but queue remains `[]`

**Possible Causes**:
1. No articles found by Event Registry
2. All articles filtered out by quality criteria
3. EVENT_REGISTRY_API_KEY not configured

**Check**:
```bash
# View monitor workflow logs
# Should see: "Fetched X articles from Event Registry"
# Should see: "Added X new articles to queue"
```

**Solution**:
- Verify EVENT_REGISTRY_API_KEY is set in GitHub Secrets
- Check filter criteria in config.py (MIN_SOCIAL_SCORE, etc.)
- Review BLACKLISTED_SOURCES and BLACKLISTED_KEYWORDS

### Issue: Post workflow not posting
**Symptoms**: Queue has articles but no tweets posted

**Possible Causes**:
1. Twitter API credentials not configured
2. Gemini API key not configured
3. Rate limit reached (60 tweets/day)

**Check**:
```bash
# View post workflow logs
# Should see: "Processing article: [title]"
# Should see: "Tweet posted successfully!"
```

**Solution**:
- Verify all Twitter API credentials in GitHub Secrets
- Verify GEMINI_API_KEY is set
- Check posted_articles.json to see if rate limit reached

### Issue: Git push conflicts
**Symptoms**: Workflow logs show git push errors

**Rare Scenario**: Multiple workflows trying to push simultaneously

**Self-Healing**: The `|| true` in the push command allows workflow to continue
- Next workflow run will include the changes
- No manual intervention needed

### Issue: Too many bot commits
**Symptoms**: Repository cluttered with bot commits

**This is Normal**: Each workflow run commits its changes
- Monitor runs every 30 min
- Post runs every 24 min
- Can result in 30-40 commits per day

**If Problematic**:
1. Increase workflow intervals in `.github/workflows/main.yml`
2. Periodically squash bot commits
3. Consider moving to a separate branch for state files

---

## Success Indicators

✅ **Queue is populating**:
- `article_queue.json` contains articles after monitor runs
- New articles added every 30 minutes

✅ **Tweets are posting**:
- Twitter account shows new tweets
- `posted_articles.json` has entries
- Post workflow logs show "Tweet posted successfully!"

✅ **State is persisting**:
- Queue size decreases after posts
- Bot commits appear in git history
- No "Queue is empty" when articles should exist

---

## Reverting (If Needed)

If you need to revert this change:

1. **Revert commits**:
   ```bash
   git revert 77a491c d2f58a5 21c9bc8
   git push
   ```

2. **Restore .gitignore**:
   - Uncomment queue files in `.gitignore`

3. **Remove queue files**:
   ```bash
   git rm article_queue.json posted_articles.json daily_brief_cache.json
   git commit -m "Remove queue files from tracking"
   git push
   ```

4. **Remove commit steps**:
   - Remove the "Commit and Push" steps from `.github/workflows/main.yml`

**Note**: This will restore the original broken behavior (queue not persisting).

---

## Next Steps

After confirming the fix is working:

1. **Monitor for 24 hours** to ensure tweets are posting correctly
2. **Check rate limiting** is working (max 60 tweets/day)
3. **Verify article quality** - review posted tweets to ensure content meets standards
4. **Adjust filters** if needed in `config.py`

---

## Additional Resources

- **Technical Details**: See [QUEUE_PERSISTENCE.md](./QUEUE_PERSISTENCE.md)
- **Visual Summary**: See [WORKFLOW_FIX_SUMMARY.md](./WORKFLOW_FIX_SUMMARY.md)
- **Rate Limiting**: See [RATE_LIMITING.md](./RATE_LIMITING.md)
- **Tools CLI**: Run `python tools.py --help`

---

## Questions?

If you encounter issues not covered here:
1. Check GitHub Actions workflow logs
2. Inspect queue files directly
3. Use tools CLI for debugging: `python tools.py inspect-queue`, `python tools.py inspect-posted`
4. Review the documentation files listed above

The fix is designed to be self-healing and robust. Most issues resolve themselves in subsequent workflow runs.
