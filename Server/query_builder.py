"""
query_builder.py

Smart query builder for Google Custom Search API.
Handles query optimization, entity prioritization, keyword extraction,
and date filtering for better search accuracy.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


class SmartQueryBuilder:
    """Advanced query construction for better search accuracy"""
    
    # Stop words for different languages
    STOPWORDS = {
        'english': {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'from', 'this', 'that',
            'these', 'those', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'about', 'into', 'through',
            'hai', 'hain', 'ka', 'ki', 'ko', 'ne', 'se', 'par', 'aur', 'ya'  # Roman Urdu
        },
        'urdu': {
            'کا', 'کی', 'کے', 'ہے', 'ہیں', 'تھا', 'تھی', 'تھے', 'ہو', 'ہوں',
            'میں', 'نے', 'سے', 'کو', 'پر', 'اور', 'یا', 'لیکن', 'جو', 'کہ',
            'یہ', 'وہ', 'ان', 'اس', 'جس', 'جب', 'تو', 'بھی', 'گا', 'گی', 'گے'
        }
    }
    
    # Priority entity types for news queries
    PRIORITY_ENTITIES = ['PERSON', 'ORG', 'EVENT', 'GPE', 'NORP', 'LAW', 'FAC']
    
    # Keywords that indicate breaking news
    NEWS_INDICATORS = {
        'english': ['breaking', 'announced', 'reports', 'confirmed', 'alleged', 
                   'claims', 'states', 'says', 'according', 'sources'],
        'urdu': ['خبر', 'اطلاع', 'رپورٹ', 'تصدیق', 'دعویٰ', 'بیان', 'ذرائع']
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove URLs, mentions, hashtags, and special characters"""
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        # Remove mentions and hashtags
        text = re.sub(r'[@#]\S+', '', text)
        # Remove excessive punctuation
        text = re.sub(r'[!?]{2,}', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, language: str, max_keywords: int = 5) -> List[str]:
        """Extract meaningful keywords from text"""
        text = SmartQueryBuilder.clean_text(text)
        stopwords = SmartQueryBuilder.STOPWORDS.get(language.lower(), set())
        
        # Split into words
        words = re.findall(r'\b[\w\u0600-\u06FF]+\b', text.lower())
        
        # Filter keywords
        keywords = []
        for word in words:
            # Skip if stopword or too short
            if word in stopwords or len(word) < 3:
                continue
            # Skip if all digits
            if word.isdigit():
                continue
            keywords.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords[:max_keywords]
    
    @staticmethod
    def prioritize_entities(entities: List, tweet_text: str) -> List[str]:
        """Extract and prioritize entities based on type and importance"""
        prioritized = []
        regular = []
        
        for entity in entities:
            if isinstance(entity, dict):
                entity_text = entity.get('text', '').strip()
                entity_type = entity.get('type', '')
                
                # Clean entity text
                entity_text = re.sub(r'[^\w\s\u0600-\u06FF]', '', entity_text).strip()
                
                if len(entity_text) < 2:
                    continue
                
                # Prioritize certain entity types
                if entity_type in SmartQueryBuilder.PRIORITY_ENTITIES:
                    prioritized.append(entity_text)
                else:
                    regular.append(entity_text)
            elif isinstance(entity, str):
                entity_text = entity.strip()
                if len(entity_text) >= 2:
                    regular.append(entity_text)
        
        # Return prioritized first, then regular (up to 4 total)
        result = prioritized[:3] + regular[:1]
        return result[:4]
    
    @staticmethod
    def detect_news_context(text: str, language: str) -> bool:
        """Check if text contains news-related keywords"""
        indicators = SmartQueryBuilder.NEWS_INDICATORS.get(language.lower(), [])
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indicators)
    
    @staticmethod
    def build_optimized_query(tweet_text: str, entities: List, language: str) -> str:
        """
        Build an optimized search query.
        
        Args:
            tweet_text: The tweet content
            entities: List of extracted entities (from NER)
            language: 'english' or 'urdu'
            
        Returns:
            Optimized search query string
        """
        query_parts = []
        
        # Step 1: Process entities (highest priority)
        if entities:
            prioritized_entities = SmartQueryBuilder.prioritize_entities(entities, tweet_text)
            query_parts.extend(prioritized_entities)
        
        # Step 2: If not enough from entities, extract keywords
        if len(query_parts) < 2:
            keywords = SmartQueryBuilder.extract_keywords(tweet_text, language, max_keywords=5)
            remaining_slots = 5 - len(query_parts)
            query_parts.extend(keywords[:remaining_slots])
        
        # Step 3: Build base query
        if not query_parts:
            # Fallback to first meaningful words
            words = SmartQueryBuilder.clean_text(tweet_text).split()[:6]
            query_parts = [w for w in words if len(w) > 2][:5]
        
        base_query = ' '.join(query_parts[:5])  # Limit to 5 terms for precision
        
        # Step 4: Add contextual hints (subtle, not overwhelming)
        is_news = SmartQueryBuilder.detect_news_context(tweet_text, language)
        
        if language.lower() == 'urdu':
            # Only add Urdu if not already present
            if not re.search(r'[\u0600-\u06FF]', base_query):
                base_query += ' اردو'
        else:
            # For English/Roman Urdu, add minimal context only if it's news-related
            if is_news and 'news' not in base_query.lower():
                base_query += ' news'
        
        return base_query.strip()


class DateFilterCalculator:
    """Smart date range calculation for search queries"""
    
    @staticmethod
    def calculate_date_range(tweet_date: str, window_days: int = 7) -> Optional[Tuple[str, str]]:
        """
        Calculate optimal date range for search.
        
        Args:
            tweet_date: Date string in YYYY-MM-DD format
            window_days: Number of days before/after tweet date (default: 7)
            
        Returns:
            Tuple of (start_date, end_date) in YYYYMMDD format, or None if invalid
        """
        try:
            if not tweet_date:
                return None
            
            tweet_dt = datetime.strptime(tweet_date, "%Y-%m-%d")
            today = datetime.utcnow().date()
            
            # Calculate range
            start_dt = tweet_dt - timedelta(days=window_days)
            end_dt = tweet_dt + timedelta(days=window_days)
            
            # Don't search future dates
            if end_dt.date() > today:
                end_dt = datetime.combine(today, datetime.min.time())
            
            # Don't go too far back (max 2 years)
            min_date = datetime.combine(today - timedelta(days=730), datetime.min.time())
            if start_dt < min_date:
                start_dt = min_date
            
            start_date = start_dt.strftime("%Y%m%d")
            end_date = end_dt.strftime("%Y%m%d")
            
            return (start_date, end_date)
        
        except Exception as e:
            print(f"⚠️ Date calculation error: {e}")
            return None
    
    @staticmethod
    def calculate_days_since(tweet_date: str, buffer_days: int = 7) -> Optional[int]:
        """
        Calculate days from tweet date to today for dateRestrict parameter.
        
        Args:
            tweet_date: Date string in YYYY-MM-DD format
            buffer_days: Additional days to add as buffer (default: 7)
            
        Returns:
            Number of days (capped at 365), or None if invalid
        """
        try:
            if not tweet_date:
                return None
            
            tweet_dt = datetime.strptime(tweet_date, "%Y-%m-%d")
            today = datetime.utcnow().date()
            
            days = (today - tweet_dt.date()).days + buffer_days
            return min(max(days, 1), 365)  # Between 1 and 365 days
        
        except Exception:
            return None


class DomainFilter:
    """Utilities for domain filtering and deduplication"""
    
    @staticmethod
    def normalize_domain(domain: str) -> str:
        """Normalize domain by removing www. prefix"""
        return domain.lower().replace('www.', '').strip()
    
    @staticmethod
    def build_exclusion_string(blocked_domains: set, max_exclusions: int = 15) -> str:
        """
        Build Google search exclusion string for blocked domains.
        
        Args:
            blocked_domains: Set of domain strings to exclude
            max_exclusions: Maximum number of exclusions (to avoid query length issues)
            
        Returns:
            Space-separated string of -site:domain exclusions
        """
        if not blocked_domains:
            return ""
        
        # Limit to prevent query length issues (Google has ~2048 char limit)
        top_blocked = list(blocked_domains)[:max_exclusions]
        return ' '.join(f'-site:{domain}' for domain in top_blocked)
    
    @staticmethod
    def is_duplicate_domain(domain: str, seen_domains: set) -> bool:
        """
        Check if domain is a duplicate (case-insensitive, www-normalized).
        
        Args:
            domain: Domain to check
            seen_domains: Set of already seen domains
            
        Returns:
            True if duplicate, False otherwise
        """
        normalized = DomainFilter.normalize_domain(domain)
        return normalized in seen_domains


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def build_search_query(
    tweet_text: str, 
    entities: List, 
    language: str,
    blocked_domains: set = None,
    max_blocked: int = 15
) -> str:
    """
    Build complete search query with all optimizations.
    
    Args:
        tweet_text: Tweet content
        entities: Extracted entities from NER
        language: 'english' or 'urdu'
        blocked_domains: Set of domains to exclude
        max_blocked: Maximum number of domain exclusions
        
    Returns:
        Complete optimized search query
    """
    # Build base optimized query
    base_query = SmartQueryBuilder.build_optimized_query(tweet_text, entities, language)
    
    # Add domain exclusions if provided
    if blocked_domains:
        exclusions = DomainFilter.build_exclusion_string(blocked_domains, max_blocked)
        return f"{base_query} {exclusions}".strip()
    
    return base_query


def get_date_filter_params(tweet_date: str, use_date_restrict: bool = True) -> dict:
    """
    Get date filter parameters for Google API.
    
    Args:
        tweet_date: Date string in YYYY-MM-DD format
        use_date_restrict: Use dateRestrict param (recommended) vs after:/before:
        
    Returns:
        Dictionary of parameters to add to API request
    """
    params = {}
    
    if not tweet_date:
        return params
    
    if use_date_restrict:
        # Recommended approach
        days = DateFilterCalculator.calculate_days_since(tweet_date)
        if days:
            params['dateRestrict'] = f'd{days}'
    else:
        # Legacy approach (less reliable)
        date_range = DateFilterCalculator.calculate_date_range(tweet_date)
        if date_range:
            start_date, end_date = date_range
            # Note: This would need to be added to the query string, not params
            pass
    
    return params