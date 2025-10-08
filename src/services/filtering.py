"""
filtering.py - Advanced filtering for Bitcoin mining articles

This module provides specialized filtering logic for Bitcoin mining articles,
including keyword-based relevance scoring to ensure articles are truly about
Bitcoin mining and not just tangentially related.
"""

from typing import List, Dict


class BitcoinMiningFilter:
    """
    Filter for Bitcoin mining articles with keyword-based relevance scoring.
    
    This filter checks articles for mining-related keywords to ensure they
    are genuinely about Bitcoin mining operations, hardware, or industry news.
    """
    
    # Mining-related keywords to check for relevance
    MINING_KEYWORDS = [
        'mining', 'miner', 'miners', 'hashrate', 'hash rate',
        'asic', 'mining pool', 'mining rig', 'mining farm',
        'difficulty', 'difficulty adjustment', 'block reward',
        'mining hardware', 'mining operation', 'mining company',
        'proof of work', 'pow', 'mining equipment', 'mining power',
        'terahash', 'petahash', 'exahash', 'th/s', 'ph/s', 'eh/s'
    ]
    
    def __init__(self, min_mining_terms: int = 2):
        """
        Initialize the Bitcoin mining filter.
        
        Args:
            min_mining_terms: Minimum number of mining-related keywords
                            that must appear in the article for it to pass.
                            Lower values are more lenient. Default is 2.
        """
        self.min_mining_terms = min_mining_terms
    
    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles based on mining keyword relevance.
        
        Args:
            articles: List of article dictionaries to filter
            
        Returns:
            Filtered list of articles that contain sufficient mining keywords
        """
        filtered = []
        
        for article in articles:
            if self._is_mining_relevant(article):
                filtered.append(article)
        
        return filtered
    
    def _is_mining_relevant(self, article: Dict) -> bool:
        """
        Check if an article is relevant to Bitcoin mining.
        
        Args:
            article: Article dictionary with 'title' and 'body' fields
            
        Returns:
            True if the article contains at least min_mining_terms keywords
        """
        # Combine title and body for checking
        title = article.get('title', '').lower()
        body = article.get('body', '').lower()
        content = f"{title} {body}"
        
        # Count how many mining keywords appear in the content
        keyword_count = 0
        for keyword in self.MINING_KEYWORDS:
            if keyword in content:
                keyword_count += 1
        
        return keyword_count >= self.min_mining_terms
    
    def get_mining_keyword_count(self, article: Dict) -> int:
        """
        Get the count of mining keywords in an article.
        
        Args:
            article: Article dictionary with 'title' and 'body' fields
            
        Returns:
            Number of mining keywords found in the article
        """
        title = article.get('title', '').lower()
        body = article.get('body', '').lower()
        content = f"{title} {body}"
        
        keyword_count = 0
        for keyword in self.MINING_KEYWORDS:
            if keyword in content:
                keyword_count += 1
        
        return keyword_count
