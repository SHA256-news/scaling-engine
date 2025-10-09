import os
import json
from datetime import datetime, timedelta
from src.services.news_provider import EventRegistryProvider
from src.app.config import EVENT_REGISTRY_API_KEY

def capture_raw_articles():
    """
    Fetches articles from Event Registry and saves the raw data to a JSON file.
    """
    print("Starting raw article capture...")
    provider = EventRegistryProvider(api_key=EVENT_REGISTRY_API_KEY)
    
    # Fetch articles from the last day
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)
    
    print(f"Fetching articles from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Get the raw data from the provider
    raw_articles_data = provider.fetch_raw_articles(start_date, end_date)
    
    if raw_articles_data:
        print(f"Successfully fetched {len(raw_articles_data)} articles.")
        
        # Define the output file path
        output_filename = "raw_articles.json"
        
        # Save the raw data to a JSON file
        with open(output_filename, 'w') as f:
            json.dump(raw_articles_data, f, indent=4)
        
        print(f"Raw article data saved to {output_filename}")
    else:
        print("No articles were fetched from Event Registry.")

if __name__ == "__main__":
    capture_raw_articles()
