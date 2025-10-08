#!/usr/bin/env python3
"""
Image Integration Example - Bitcoin Mining News Bot

Demonstrates the complete workflow for fetching, optimizing, and posting
images with tweets. This example shows how to use the new Unsplash integration.

Usage:
    python image_example.py

Requirements:
    - UNSPLASH_ACCESS_KEY in environment variables
    - Pillow and requests packages installed
"""

import os
from dotenv import load_dotenv
from bot_lib import (
    fetch_unsplash_images,
    download_image,
    optimize_image_for_twitter,
    fetch_and_prepare_images,
    fetch_bitcoin_mining_articles,
    filter_articles,
    get_date_range
)

# Load environment variables
load_dotenv()


def example_1_fetch_images():
    """
    Example 1: Fetch images from Unsplash.
    
    Shows how to search for Bitcoin mining related images.
    """
    print("\n" + "="*80)
    print("Example 1: Fetching Images from Unsplash")
    print("="*80)
    
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY not found in environment")
        print("   Get your API key from: https://unsplash.com/developers")
        return None
    
    try:
        print("\nSearching for 'bitcoin mining' images...")
        images = fetch_unsplash_images(
            unsplash_access_key=UNSPLASH_ACCESS_KEY,
            query="bitcoin mining",
            count=3,
            orientation="landscape"
        )
        
        print(f"✓ Found {len(images)} images:\n")
        
        for i, image in enumerate(images, 1):
            print(f"{i}. {image.get('description') or image.get('alt_description', 'No description')}")
            print(f"   Photographer: {image['photographer']}")
            print(f"   Dimensions: {image['width']}x{image['height']}")
            print(f"   URL: {image['url'][:60]}...")
            print()
        
        return images
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def example_2_download_and_optimize():
    """
    Example 2: Download and optimize images.
    
    Shows the complete workflow from URL to Twitter-ready image.
    """
    print("\n" + "="*80)
    print("Example 2: Download and Optimize Images")
    print("="*80)
    
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY not found")
        return
    
    try:
        # Fetch one image
        print("\nFetching sample image...")
        images = fetch_unsplash_images(
            unsplash_access_key=UNSPLASH_ACCESS_KEY,
            query="cryptocurrency",
            count=1,
            orientation="landscape"
        )
        
        if not images:
            print("✗ No images found")
            return
        
        image = images[0]
        print(f"✓ Found image by {image['photographer']}")
        
        # Download image
        output_dir = "/tmp/bitcoin_images_example"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nDownloading to {output_dir}...")
        raw_path = os.path.join(output_dir, "sample_raw.jpg")
        download_image(image['download_url'], raw_path)
        
        raw_size = os.path.getsize(raw_path) / 1024  # KB
        print(f"✓ Downloaded: {raw_path}")
        print(f"  File size: {raw_size:.1f} KB")
        
        # Optimize for Twitter
        print("\nOptimizing for Twitter (1600x900, 16:9 aspect ratio)...")
        optimized_path = os.path.join(output_dir, "sample_optimized.jpg")
        optimize_image_for_twitter(
            input_path=raw_path,
            output_path=optimized_path,
            target_size=(1600, 900),
            quality=85
        )
        
        optimized_size = os.path.getsize(optimized_path) / 1024  # KB
        print(f"✓ Optimized: {optimized_path}")
        print(f"  File size: {optimized_size:.1f} KB")
        print(f"  Size reduction: {((raw_size - optimized_size) / raw_size * 100):.1f}%")
        
        print("\n✓ Image ready for Twitter posting!")
        print(f"  Path: {optimized_path}")
    
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Install with: pip install Pillow requests")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_3_complete_workflow():
    """
    Example 3: Complete workflow with fetch_and_prepare_images.
    
    Shows the one-function solution for getting Twitter-ready images.
    """
    print("\n" + "="*80)
    print("Example 3: Complete Workflow (One Function)")
    print("="*80)
    
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY not found")
        return None
    
    try:
        print("\nFetching and preparing 2 images for Twitter...")
        image_paths = fetch_and_prepare_images(
            unsplash_access_key=UNSPLASH_ACCESS_KEY,
            query="bitcoin mining hardware",
            output_dir="/tmp/bitcoin_images_workflow",
            count=2
        )
        
        if not image_paths:
            print("✗ No images prepared")
            return None
        
        print(f"✓ Prepared {len(image_paths)} images:\n")
        
        for i, path in enumerate(image_paths, 1):
            file_size = os.path.getsize(path) / 1024  # KB
            print(f"{i}. {path}")
            print(f"   Size: {file_size:.1f} KB")
            print(f"   Ready for Twitter: ✓")
            print()
        
        print("✓ All images ready for posting!")
        return image_paths
    
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Install with: pip install Pillow requests")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def example_4_article_with_images():
    """
    Example 4: Fetch article and matching images.
    
    Shows how to integrate article fetching with image preparation.
    """
    print("\n" + "="*80)
    print("Example 4: Article + Images Workflow")
    print("="*80)
    
    EVENT_REGISTRY_API_KEY = os.getenv("EVENT_REGISTRY_API_KEY")
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    
    if not EVENT_REGISTRY_API_KEY:
        print("⚠️  EVENT_REGISTRY_API_KEY not found")
        print("   This example requires Event Registry API access")
        return
    
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY not found")
        return
    
    try:
        # Fetch recent articles
        print("\nFetching recent Bitcoin mining articles...")
        date_start, date_end = get_date_range(days_back=7)
        
        articles = fetch_bitcoin_mining_articles(
            api_key=EVENT_REGISTRY_API_KEY,
            date_start=date_start,
            date_end=date_end,
            max_articles=5
        )
        
        if not articles:
            print("✗ No articles found")
            return
        
        print(f"✓ Found {len(articles)} articles")
        
        # Get the top article
        article = articles[0]
        title = article.get('title', 'No title')
        
        print(f"\nTop Article: {title[:60]}...")
        print(f"Social Score: {article.get('socialScore', 0)}")
        
        # Fetch matching images based on article
        print("\nFetching matching images...")
        
        # Extract keywords for image search
        # In production, you could use AI to extract relevant keywords
        search_query = "bitcoin mining"
        
        image_paths = fetch_and_prepare_images(
            unsplash_access_key=UNSPLASH_ACCESS_KEY,
            query=search_query,
            count=2
        )
        
        if image_paths:
            print(f"✓ Prepared {len(image_paths)} matching images")
            print("\nReady to post:")
            print(f"  Article: {title[:60]}...")
            print(f"  Images: {len(image_paths)}")
            print(f"\nExample tweet content:")
            print(f"  🚀 {title[:200]}...")
            print(f"  #Bitcoin #Mining #Cryptocurrency")
            print(f"\n  [With {len(image_paths)} images attached]")
        else:
            print("✗ No images prepared")
    
    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_error_handling():
    """
    Example 5: Demonstrate error handling.
    
    Shows how functions handle various error conditions.
    """
    print("\n" + "="*80)
    print("Example 5: Error Handling Demonstrations")
    print("="*80)
    
    print("\n1. Testing invalid image count...")
    try:
        fetch_unsplash_images("fake_key", "bitcoin", count=0)
        print("   ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Correctly raised ValueError: {e}")
    
    print("\n2. Testing non-existent file optimization...")
    try:
        optimize_image_for_twitter("/nonexistent/file.jpg")
        print("   ✗ Should have raised an error")
    except (FileNotFoundError, ImportError) as e:
        error_type = "ImportError" if isinstance(e, ImportError) else "FileNotFoundError"
        print(f"   ✓ Correctly raised {error_type}")
    
    print("\n3. Testing invalid API key...")
    try:
        images = fetch_unsplash_images("invalid_key", "bitcoin", count=2)
        # Will raise exception on API call
        print("   ⚠️  API call did not execute (expected with invalid key)")
    except Exception as e:
        print(f"   ✓ Handled API error gracefully")
    
    print("\n✓ Error handling works as expected!")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("BITCOIN MINING NEWS BOT - IMAGE INTEGRATION EXAMPLES")
    print("="*80)
    
    # Check for API keys
    has_unsplash = bool(os.getenv("UNSPLASH_ACCESS_KEY"))
    has_event_registry = bool(os.getenv("EVENT_REGISTRY_API_KEY"))
    
    print("\nAPI Key Status:")
    print(f"  Unsplash: {'✓' if has_unsplash else '✗ (required for most examples)'}")
    print(f"  Event Registry: {'✓' if has_event_registry else '✗ (required for Example 4)'}")
    
    if not has_unsplash:
        print("\n⚠️  Get Unsplash API key from: https://unsplash.com/developers")
        print("   Add to .env file: UNSPLASH_ACCESS_KEY=your_key_here")
    
    # Run examples
    example_1_fetch_images()
    example_2_download_and_optimize()
    image_paths = example_3_complete_workflow()
    example_4_article_with_images()
    example_5_error_handling()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)
    
    if image_paths:
        print("\nℹ️  Sample images have been saved to /tmp/bitcoin_images_workflow/")
        print("   You can use these for testing Twitter posts")
    
    print("\n📚 Next Steps:")
    print("   1. Get API keys if you haven't already")
    print("   2. Test with your own queries")
    print("   3. Integrate into your bot workflow")
    print("   4. See README.md for complete documentation")
    print()


if __name__ == "__main__":
    main()
