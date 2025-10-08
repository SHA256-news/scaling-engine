# Image Integration Guide

This guide covers the automated image fetching and optimization features for the Bitcoin Mining News Bot.

## Overview

The bot integrates with Unsplash API to automatically fetch free, royalty-free images related to Bitcoin mining. Images are automatically optimized to Twitter's recommended specifications (1600x900 pixels, 16:9 aspect ratio) before posting.

## Features

- ✅ **Automated Image Search**: Search Unsplash for relevant Bitcoin mining imagery
- ✅ **Free & Royalty-Free**: All images from Unsplash are free to use
- ✅ **Twitter Optimization**: Automatic resizing to 1600x900 pixels (16:9 ratio)
- ✅ **Quality Control**: Intelligent cropping maintains best composition
- ✅ **Multiple Images**: Support for up to 4 images per tweet (default: 2)
- ✅ **Clean Workflow**: Automatic cleanup of intermediate files

## Setup

### 1. Get Unsplash API Access

1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Sign up or log in
3. Create a new application
4. Copy your **Access Key**
5. Add to your `.env` file:
   ```
   UNSPLASH_ACCESS_KEY=your_access_key_here
   ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install Pillow requests
```

## Usage

### Quick Start

The simplest way to get Twitter-ready images:

```python
from bot_lib import fetch_and_prepare_images

# Fetch and optimize 2 images
image_paths = fetch_and_prepare_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining",
    count=2
)

# Use with Twitter post
result = post_to_twitter(
    twitter_api_key=TWITTER_API_KEY,
    twitter_api_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
    content="🚀 Bitcoin Mining Update! #Bitcoin #Mining",
    media_paths=image_paths
)
```

### Individual Functions

#### 1. Fetch Images from Unsplash

```python
from bot_lib import fetch_unsplash_images

images = fetch_unsplash_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining",
    count=2,
    orientation="landscape"  # "landscape", "portrait", or "squarish"
)

# Returns list of image dictionaries
for image in images:
    print(f"URL: {image['url']}")
    print(f"Photographer: {image['photographer']}")
    print(f"Size: {image['width']}x{image['height']}")
```

**Parameters:**
- `unsplash_access_key`: Your Unsplash API access key
- `query`: Search query (e.g., "bitcoin mining", "cryptocurrency")
- `count`: Number of images (1-30, default: 2)
- `orientation`: Image orientation (default: "landscape")

**Returns:**
List of dictionaries with image data:
```python
{
    'id': str,              # Unique image ID
    'url': str,             # Full resolution URL
    'download_url': str,    # Download link
    'width': int,           # Original width
    'height': int,          # Original height
    'description': str,     # Image description
    'alt_description': str, # Alt text
    'photographer': str,    # Photographer name
    'photographer_url': str # Profile URL
}
```

#### 2. Download Image

```python
from bot_lib import download_image

path = download_image(
    image_url="https://images.unsplash.com/photo-123...",
    output_path="/tmp/bitcoin_mining.jpg"
)
```

**Parameters:**
- `image_url`: URL of the image to download
- `output_path`: Local path to save the image

**Returns:** Path to downloaded file

#### 3. Optimize for Twitter

```python
from bot_lib import optimize_image_for_twitter

optimized_path = optimize_image_for_twitter(
    input_path="/tmp/bitcoin_mining.jpg",
    output_path="/tmp/bitcoin_mining_optimized.jpg",  # Optional
    target_size=(1600, 900),  # Twitter recommended
    quality=85  # JPEG quality (1-100)
)
```

**Parameters:**
- `input_path`: Path to input image
- `output_path`: Path for optimized image (optional, auto-generated if not provided)
- `target_size`: Target dimensions as (width, height) tuple
- `quality`: JPEG compression quality (1-100, default: 85)

**Returns:** Path to optimized file

**How it works:**
1. Opens the input image
2. Converts to RGB if necessary
3. Crops to maintain 16:9 aspect ratio (centered crop)
4. Resizes to target dimensions (1600x900)
5. Compresses as JPEG with specified quality
6. Saves optimized image

#### 4. Complete Workflow

```python
from bot_lib import fetch_and_prepare_images

image_paths = fetch_and_prepare_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining hardware",
    output_dir="/tmp/bitcoin_images",  # Optional
    count=2
)
```

**Parameters:**
- `unsplash_access_key`: Unsplash API key
- `query`: Search query
- `output_dir`: Directory for images (default: "/tmp/bitcoin_images")
- `count`: Number of images (default: 2)

**Returns:** List of paths to Twitter-ready images

**What it does:**
1. Searches Unsplash for images
2. Downloads each image
3. Optimizes for Twitter specs
4. Cleans up raw downloads
5. Returns list of optimized image paths

## Image Specifications

### Twitter Requirements

The bot optimizes images to Twitter's recommended specifications:

| Specification | Value | Notes |
|--------------|-------|-------|
| **Aspect Ratio** | 16:9 | Most engaging on Twitter |
| **Dimensions** | 1600x900 pixels | Recommended size |
| **Format** | JPEG | Optimal for photos |
| **Quality** | 85% | Balanced quality/size |
| **Max File Size** | 5MB | Twitter limit per image |
| **Max Images** | 4 per tweet | Twitter limit |

### Optimization Process

1. **Aspect Ratio Adjustment**
   - Target: 16:9 (1600:900)
   - Method: Intelligent center cropping
   - Maintains best composition

2. **Resizing**
   - Algorithm: Lanczos resampling
   - Maintains sharp details
   - Prevents pixelation

3. **Compression**
   - Format: JPEG
   - Quality: 85% (configurable)
   - Optimization: Enabled
   - Result: Smaller file size, maintained quality

## Best Practices

### Search Queries

Use specific, relevant queries for better results:

✅ **Good Queries:**
- "bitcoin mining"
- "bitcoin mining hardware"
- "cryptocurrency mining"
- "ASIC miner"
- "mining rig"
- "bitcoin server"

❌ **Avoid Generic Queries:**
- "technology"
- "computer"
- "internet"

### Image Count

- **For news tweets**: 1-2 images (keeps focus on content)
- **For announcements**: 2-4 images (more visual impact)
- **Default**: 2 images (good balance)

### Caching

To respect API limits and improve performance:

```python
import os

def get_cached_or_fetch_images(query, count=2):
    """Get images from cache or fetch new ones."""
    cache_dir = "/tmp/image_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Check if cached images exist
    cache_key = query.replace(" ", "_")
    cache_pattern = f"{cache_dir}/{cache_key}_*.jpg"
    
    cached_images = glob.glob(cache_pattern)
    
    if len(cached_images) >= count:
        print(f"Using {count} cached images")
        return cached_images[:count]
    
    # Fetch new images
    print(f"Fetching {count} new images")
    return fetch_and_prepare_images(
        unsplash_access_key=UNSPLASH_ACCESS_KEY,
        query=query,
        output_dir=cache_dir,
        count=count
    )
```

### Attribution

While not required by Unsplash License, it's good practice to credit photographers:

```python
images_data = fetch_unsplash_images(UNSPLASH_ACCESS_KEY, "bitcoin", count=2)

# Store photographer info
for img in images_data:
    print(f"Photo by {img['photographer']} on Unsplash")
    # Could be added to tweet thread or stored in database
```

## API Limits

### Unsplash API (Free Tier)

| Limit | Value | Notes |
|-------|-------|-------|
| **Requests/Hour** | 50 | Per application |
| **Images/Request** | 30 max | Recommended: 2-5 |
| **Rate Limit Reset** | Hourly | Resets every hour |

**Tips to stay within limits:**
- Cache images when possible
- Use specific queries (fewer retries)
- Batch fetch images for multiple articles
- Implement exponential backoff on errors

## Error Handling

The functions include comprehensive error handling:

```python
try:
    image_paths = fetch_and_prepare_images(
        unsplash_access_key=UNSPLASH_ACCESS_KEY,
        query="bitcoin mining",
        count=2
    )
    
    if not image_paths:
        print("No images found, posting without images")
        # Post tweet without images
    else:
        # Post tweet with images
        pass

except ValueError as e:
    print(f"Invalid parameters: {e}")

except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install Pillow requests")

except Exception as e:
    print(f"Error fetching images: {e}")
    # Fallback: post without images or use default image
```

## Troubleshooting

### Common Issues

**Problem**: `ImportError: No module named 'PIL'`
```bash
# Solution: Install Pillow
pip install Pillow
```

**Problem**: `ImportError: No module named 'requests'`
```bash
# Solution: Install requests
pip install requests
```

**Problem**: No images returned from Unsplash
```
# Solutions:
# 1. Check API key validity
# 2. Try broader search query
# 3. Check rate limit status
# 4. Verify internet connectivity
```

**Problem**: Images look incorrectly cropped
```python
# Solution 1: Use different orientation
images = fetch_unsplash_images(
    query="bitcoin",
    orientation="squarish"  # Instead of landscape
)

# Solution 2: Adjust target size
optimize_image_for_twitter(
    input_path="image.jpg",
    target_size=(1200, 675)  # Different size
)
```

**Problem**: File size too large
```python
# Solution: Reduce quality
optimize_image_for_twitter(
    input_path="image.jpg",
    quality=75  # Lower quality = smaller file
)
```

**Problem**: Rate limit exceeded
```
# Solutions:
# 1. Implement caching
# 2. Reduce request frequency
# 3. Upgrade to paid Unsplash plan
# 4. Use exponential backoff
```

## Examples

### Example 1: Basic Tweet with Images

```python
from bot_lib import fetch_and_prepare_images, post_to_twitter

# Prepare images
images = fetch_and_prepare_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining",
    count=2
)

# Post tweet
if images:
    result = post_to_twitter(
        twitter_api_key=TWITTER_API_KEY,
        twitter_api_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
        content="🚀 Bitcoin Mining Update! #Bitcoin #Mining",
        media_paths=images
    )
    
    print(f"Posted: {result['url']}")
```

### Example 2: Article with Matching Images

```python
from bot_lib import (
    fetch_bitcoin_mining_articles,
    fetch_and_prepare_images,
    post_to_twitter
)

# Fetch article
articles = fetch_bitcoin_mining_articles(
    api_key=EVENT_REGISTRY_API_KEY,
    date_start="2024-01-01",
    date_end="2024-01-31"
)

article = articles[0]

# Fetch matching images
images = fetch_and_prepare_images(
    unsplash_access_key=UNSPLASH_ACCESS_KEY,
    query="bitcoin mining hardware",
    count=2
)

# Create tweet
tweet = f"📰 {article['title'][:200]}... #Bitcoin #Mining"

# Post with images
result = post_to_twitter(
    twitter_api_key=TWITTER_API_KEY,
    twitter_api_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
    content=tweet,
    media_paths=images
)
```

### Example 3: With Error Handling and Fallback

```python
def post_article_with_images(article):
    """Post article with images, fallback to text-only if needed."""
    
    # Try to fetch images
    images = []
    try:
        images = fetch_and_prepare_images(
            unsplash_access_key=UNSPLASH_ACCESS_KEY,
            query="bitcoin mining",
            count=2
        )
    except Exception as e:
        print(f"Could not fetch images: {e}")
        # Continue without images
    
    # Create tweet content
    tweet = f"🚀 {article['title'][:240]}... #Bitcoin"
    
    # Post tweet
    result = post_to_twitter(
        twitter_api_key=TWITTER_API_KEY,
        twitter_api_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
        content=tweet,
        media_paths=images if images else None
    )
    
    return result
```

## Testing

Run the example script to test all functionality:

```bash
python image_example.py
```

This will demonstrate:
1. Fetching images from Unsplash
2. Downloading and optimizing images
3. Complete workflow
4. Article + image integration
5. Error handling

## Additional Resources

- [Unsplash API Documentation](https://unsplash.com/documentation)
- [Unsplash License](https://unsplash.com/license)
- [Twitter Media Best Practices](https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/uploading-media/media-best-practices)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [bot_lib_template.py](bot_lib_template.py) - Full source code

## Support

For issues or questions:
1. Check this guide
2. Review [README.md](README.md)
3. Run [image_example.py](image_example.py)
4. Check function docstrings in code
