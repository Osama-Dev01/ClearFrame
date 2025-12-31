import re
import hashlib
import json
import pickle
import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from collections import Counter
from dataclasses import dataclass, asdict
import math
import time
from datetime import datetime
import os

# Database imports
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse
from sqlalchemy import text 

from database import engine, get_db, Base
from models import (
    User,
    ApprovalStatus,
    VerificationResult,
    VerificationSource,
    Tweet,
    VerificationStatus
)

@dataclass
class ProcessedTweet:
    """Data class for processed tweet data"""
    tweet_id: int
    tweet_text: str
    status: str
    verdict: str
    votes_in_favor_percentage: float
    confidence: float
    factuality: float
    reason: str
    verification_date: datetime
    tweet_date: datetime
    simhash: int
    tokens: List[str]
    language: str

@dataclass
class MatchResult:
    """Data class for match results"""
    matched_tweet_id: int
    similarity_score: float
    verdict: str
    votes_in_favor_percentage: float
    confidence: float
    factuality: float
    reason: str
    verification_date: datetime
    original_tweet_text: str
    matched_tweet_text: str

class SimHashMatcher:
    """SimHash-based tweet matching system with database integration"""
    
    def __init__(self, hash_bits: int = 64, similarity_threshold: float = 0.85):
        """
        Initialize SimHash matcher.
        
        Args:
            hash_bits: Number of bits in SimHash (64 recommended)
            similarity_threshold: Threshold for similarity matching (0.85 = 85%)
        """
        self.hash_bits = hash_bits
        self.similarity_threshold = similarity_threshold
        
        # Storage for processed tweets
        self.processed_tweets: Dict[int, ProcessedTweet] = {}
        self.simhash_index: Dict[int, Set[int]] = {}  # bucket -> set of tweet_ids
        
        # Configuration
        self.bucket_size = 4  # Use first 4 bits for bucketing (16 buckets)
        self.helper_file = "helper.txt"
        self.backup_file = "helper_backup.pkl"
        
        # Language detection patterns
        self.urdu_regex = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
        self.english_regex = re.compile(r'[A-Za-z]+')
        
        # Stopwords for both languages
        self.stopwords = self._load_stopwords()
        
    def _load_stopwords(self) -> Set[str]:
        """Load comprehensive stopwords for Urdu and English."""
        english_stopwords = {
            'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'with', 'at',
            'by', 'this', 'that', 'are', 'as', 'it', 'was', 'be', 'from', 'or',
            'an', 'but', 'not', 'what', 'all', 'were', 'when', 'we', 'there',
            'been', 'have', 'will', 'would', 'can', 'out', 'up', 'about', 'who',
            'get', 'which', 'go', 'me', 'like', 'know', 'take', 'into', 'just',
            'him', 'your', 'come', 'could', 'now', 'than', 'then', 'its',
            'also', 'how', 'our', 'us', 'some', 'these', 'she', 'they', 'so',
            'had', 'has', 'do', 'my', 'no', 'one', 'very', 'man', 'may', 'more',
            'if', 'time', 'see', 'did', 'only', 'other', 'their', 'them', 'well',
            'because', 'over', 'any', 'where', 'even', 'most', 'after', 'before'
        }
        
        urdu_stopwords = {
            'اور', 'میں', 'ہے', 'کے', 'کی', 'ہیں', 'کو', 'سے', 'پر', 'یہ',
            'وہ', 'تاہم', 'لیکن', 'اگر', 'تو', 'بھی', 'نہیں', 'کیا', 'ہے',
            'ہوں', 'ہیں', 'تھا', 'تھی', 'تھے', 'ہو', 'گا', 'گی', 'گے', 'رہا',
            'رہی', 'رہے', 'دیا', 'دی', 'دئے', 'لیا', 'لی', 'لئے', 'کہا',
            'کہی', 'کہے', 'کر', 'کرو', 'کریں', 'کرتا', 'کرتی', 'کرتے',
            'ہوگی', 'ہوگا', 'ہوں گے', 'ہوگئی', 'ہوگئے', 'ہوتی', 'ہوتا',
            'ہوتے', 'ہوئی', 'ہوا', 'ہوئے', 'کسی', 'کوئی', 'سب', 'اپنے',
            'اپنی', 'اپنا', 'ہمارے', 'ہماری', 'ہمارا', 'تمہارے', 'تمہاری',
            'تمہارا', 'انہوں', 'انہیں', 'انکے', 'انکی', 'انکا', 'اسے',
            'اسکے', 'اسکی', 'اسکا', 'اس', 'ان', 'ایک', 'دو', 'تین', 'چار',
            'پانچ', 'چھ', 'سات', 'آٹھ', 'نو', 'دس', 'کچھ', 'بہت', 'تھوڑا',
            'زیادہ', 'کم', 'آج', 'کل', 'پرسوں', 'اب', 'پہلے', 'بعد', 'سے',
            'تک', 'پر', 'میں', 'کے', 'کا', 'کی', 'کو', 'نے', 'سے', 'تک'
        }
        
        return english_stopwords.union(urdu_stopwords)
    
    def detect_language(self, text: str) -> str:
        """Detect if text contains Urdu, English, or mixed."""
        urdu_chars = len(self.urdu_regex.findall(text))
        english_chars = len(self.english_regex.findall(text))
        
        if urdu_chars > 0 and english_chars > 0:
            return 'mixed'
        elif urdu_chars > 0:
            return 'urdu'
        else:
            return 'english'
    
    def preprocess_text(self, text: str) -> Tuple[List[str], str]:
        """Preprocess text and return tokens with language."""
        # Clean text
        text = text.lower().strip()
        
        # Remove URLs, mentions, hashtags, special characters
        text = re.sub(r'http\S+|@\w+|#\w+|[^\w\s\u0600-\u06FF]', ' ', text)
        text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
        
        # Detect language
        language = self.detect_language(text)
        
        # Extract tokens based on language
        if language == 'english':
            tokens = re.findall(r'\b[a-z]+\b', text)
        elif language == 'urdu':
            tokens = self.urdu_regex.findall(text)
        else:  # mixed
            urdu_tokens = self.urdu_regex.findall(text)
            english_tokens = re.findall(r'\b[a-z]+\b', text)
            tokens = urdu_tokens + english_tokens
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens 
                 if token not in self.stopwords and len(token) > 1]
        
        return tokens, language
    
    def calculate_tf_weight(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate term frequency weights for SimHash."""
        if not tokens:
            return {}
        
        # Count tokens
        token_counts = Counter(tokens)
        
        # Calculate TF with sublinear scaling (log)
        tf_weights = {}
        for token, count in token_counts.items():
            tf = 1 + math.log(count) if count > 0 else 1
            tf_weights[token] = tf
        
        return tf_weights
    
    def calculate_simhash(self, text: str) -> Tuple[int, List[str], str]:
        """Calculate SimHash for a given text."""
        # Preprocess text
        tokens, language = self.preprocess_text(text)
        
        if not tokens:
            return 0, [], language
        
        # Calculate TF weights
        tf_weights = self.calculate_tf_weight(tokens)
        
        # Initialize feature vector
        vector = np.zeros(self.hash_bits, dtype=np.float64)
        
        for token in tokens:
            # Get weight for this token
            weight = tf_weights.get(token, 1.0)
            
            # Create MD5 hash for token
            hash_bytes = hashlib.md5(token.encode('utf-8')).digest()
            
            # Convert to integer
            if self.hash_bits <= 64:
                hash_int = int.from_bytes(hash_bytes[:8], 'big')
            else:
                hash_int = int.from_bytes(hash_bytes[:16], 'big')
            
            # Update feature vector
            for i in range(self.hash_bits):
                # Check if i-th bit is set in hash
                if hash_int & (1 << (i % 64)):
                    vector[i] += weight
                else:
                    vector[i] -= weight
        
        # Generate SimHash from feature vector
        simhash = 0
        for i in range(self.hash_bits):
            if vector[i] > 0:
                simhash |= 1 << i
        
        return simhash, tokens, language
    
    def get_bucket_key(self, simhash: int) -> int:
        """Get bucket key for indexing (using first few bits)."""
        return simhash >> (self.hash_bits - self.bucket_size)
    
    def hamming_distance(self, hash1: int, hash2: int) -> int:
        """Calculate Hamming distance between two SimHashes."""
        return bin(hash1 ^ hash2).count('1')
    
    def similarity_score(self, hash1: int, hash2: int) -> float:
        """Calculate similarity score from 0 to 1."""
        distance = self.hamming_distance(hash1, hash2)
        return 1.0 - (distance / self.hash_bits)
    
    def fetch_tweets_from_db(self, db: Session) -> List[Tuple]:
        """
        Fetch verified tweets from database using the specified query.
        
        Returns:
            List of tuples with tweet data
        """
        try:
            # Execute the SQL query - WRAP WITH text()
            query = text("""
                SELECT 
                    t.tweet_id,
                    t.tweet_text,
                    vr.status,
                    vr.verdict,
                    vr.votes_in_favor_percentage,
                    vr.confidence,
                    vr.factuality,
                    vr.reason,
                    vr.created_at as verification_date,
                    t.submit_date as tweet_date
                FROM 
                    tweets t
                INNER JOIN 
                    verification_results vr ON t.tweet_id = vr.tweet_id
                WHERE 
                    vr.status = 'verified'
                ORDER BY 
                    vr.created_at DESC, 
                    t.tweet_id;
            """)
            
            result = db.execute(query)
            rows = result.fetchall()
            
            print(f"Fetched {len(rows)} verified tweets from database")
            return rows
            
        except SQLAlchemyError as e:
            print(f"Error fetching tweets from database: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def process_and_index_tweets(self, db: Session) -> int:
        """
        Process tweets from database, calculate SimHashes, and build index.
        
        Returns:
            Number of tweets processed
        """
        print("Starting tweet processing and indexing...")
        
        # Clear existing data
        self.processed_tweets.clear()
        self.simhash_index.clear()
        
        # Fetch tweets from database
        tweets_data = self.fetch_tweets_from_db(db)
        
        if not tweets_data:
            print("No tweets found in database")
            return 0
        
        processed_count = 0
        
        for row in tweets_data:
            try:
                # Unpack row data
                (tweet_id, tweet_text, status, verdict, votes_in_favor_percentage,
                 confidence, factuality, reason, verification_date, tweet_date) = row
                
                # Calculate SimHash
                simhash, tokens, language = self.calculate_simhash(tweet_text)
                
                # Create ProcessedTweet object
                processed_tweet = ProcessedTweet(
                    tweet_id=tweet_id,
                    tweet_text=tweet_text,
                    status=status,
                    verdict=verdict,
                    votes_in_favor_percentage=float(votes_in_favor_percentage or 0),
                    confidence=float(confidence or 0),
                    factuality= factuality,
                    reason=reason or "",
                    verification_date=verification_date,
                    tweet_date=tweet_date,
                    simhash=simhash,
                    tokens=tokens,
                    language=language
                )
                
                # Store in memory
                self.processed_tweets[tweet_id] = processed_tweet
                
                # Add to bucket index
                bucket_key = self.get_bucket_key(simhash)
                if bucket_key not in self.simhash_index:
                    self.simhash_index[bucket_key] = set()
                self.simhash_index[bucket_key].add(tweet_id)
                
                processed_count += 1
                
                # Progress indicator
                if processed_count % 100 == 0:
                    print(f"Processed {processed_count} tweets...")
                    
            except Exception as e:
                print(f"Error processing tweet {tweet_id}: {e}")
                continue
        
        print(f"Successfully processed {processed_count} tweets")
        
        # Save to helper file
        self.save_to_helper_file()
        
        return processed_count
    
    def save_to_helper_file(self):
        """Save processed tweets to helper file."""
        try:
            # Prepare data for serialization
            data_to_save = {
                'processed_tweets': {},
                'simhash_index': {},
                'config': {
                    'hash_bits': self.hash_bits,
                    'similarity_threshold': self.similarity_threshold,
                    'bucket_size': self.bucket_size
                }
            }
            
            # Convert ProcessedTweet objects to dictionaries
            for tweet_id, processed_tweet in self.processed_tweets.items():
                data_to_save['processed_tweets'][tweet_id] = asdict(processed_tweet)
                # Convert datetime objects to strings
                data_to_save['processed_tweets'][tweet_id]['verification_date'] = \
                    processed_tweet.verification_date.isoformat() if processed_tweet.verification_date else None
                data_to_save['processed_tweets'][tweet_id]['tweet_date'] = \
                    processed_tweet.tweet_date.isoformat() if processed_tweet.tweet_date else None
            
            # Save simhash index
            data_to_save['simhash_index'] = {k: list(v) for k, v in self.simhash_index.items()}
            
            # Save to JSON file
            with open(self.helper_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
            # Also save backup using pickle for faster loading
            with open(self.backup_file, 'wb') as f:
                pickle.dump(self.processed_tweets, f)
            
            print(f"Saved {len(self.processed_tweets)} processed tweets to {self.helper_file}")
            
        except Exception as e:
            print(f"Error saving to helper file: {e}")
    
    def load_from_helper_file(self) -> bool:
        """Load processed tweets from helper file."""
        try:
            if not os.path.exists(self.helper_file):
                print(f"Helper file {self.helper_file} not found")
                return False
            
            with open(self.helper_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing data
            self.processed_tweets.clear()
            self.simhash_index.clear()
            
            # Load configuration
            config = data.get('config', {})
            self.hash_bits = config.get('hash_bits', 64)
            self.similarity_threshold = config.get('similarity_threshold', 0.85)
            self.bucket_size = config.get('bucket_size', 4)
            
            # Load processed tweets
            for tweet_id_str, tweet_data in data.get('processed_tweets', {}).items():
                try:
                    tweet_id = int(tweet_id_str)
                    
                    # Convert string dates back to datetime objects
                    verification_date_str = tweet_data.get('verification_date')
                    tweet_date_str = tweet_data.get('tweet_date')
                    
                    verification_date = datetime.fromisoformat(verification_date_str) if verification_date_str else None
                    tweet_date = datetime.fromisoformat(tweet_date_str) if tweet_date_str else None
                    
                    # Create ProcessedTweet object
                    processed_tweet = ProcessedTweet(
                        tweet_id=tweet_id,
                        tweet_text=tweet_data['tweet_text'],
                        status=tweet_data['status'],
                        verdict=tweet_data['verdict'],
                        votes_in_favor_percentage=tweet_data['votes_in_favor_percentage'],
                        confidence=tweet_data['confidence'],
                        factuality=tweet_data['factuality'],
                        reason=tweet_data['reason'],
                        verification_date=verification_date,
                        tweet_date=tweet_date,
                        simhash=tweet_data['simhash'],
                        tokens=tweet_data['tokens'],
                        language=tweet_data['language']
                    )
                    
                    self.processed_tweets[tweet_id] = processed_tweet
                    
                except Exception as e:
                    print(f"Error loading tweet {tweet_id_str}: {e}")
                    continue
            
            # Load simhash index
            simhash_index_data = data.get('simhash_index', {})
            for bucket_key_str, tweet_ids in simhash_index_data.items():
                bucket_key = int(bucket_key_str)
                self.simhash_index[bucket_key] = set(tweet_ids)
            
            print(f"Loaded {len(self.processed_tweets)} processed tweets from {self.helper_file}")
            return True
            
        except Exception as e:
            print(f"Error loading from helper file: {e}")
            # Try loading from pickle backup
            return self.load_from_backup()
    
    def load_from_backup(self) -> bool:
        """Load processed tweets from pickle backup."""
        try:
            if not os.path.exists(self.backup_file):
                return False
            
            with open(self.backup_file, 'rb') as f:
                self.processed_tweets = pickle.load(f)
            
            # Rebuild simhash index
            self.simhash_index.clear()
            for tweet_id, processed_tweet in self.processed_tweets.items():
                bucket_key = self.get_bucket_key(processed_tweet.simhash)
                if bucket_key not in self.simhash_index:
                    self.simhash_index[bucket_key] = set()
                self.simhash_index[bucket_key].add(tweet_id)
            
            print(f"Loaded {len(self.processed_tweets)} processed tweets from backup")
            return True
            
        except Exception as e:
            print(f"Error loading from backup: {e}")
            return False
    
    def find_matches(self, new_tweet_text: str, max_results: int = 10) -> List[MatchResult]:
        """
        Find matching tweets for new incoming tweet.
        
        Args:
            new_tweet_text: Text of the new tweet
            max_results: Maximum number of results to return
            
        Returns:
            List of MatchResult objects for tweets with similarity >= threshold
        """
        if not self.processed_tweets:
            print("No processed tweets loaded. Please load from helper file or process database.")
            return []
        
        start_time = time.time()
        
        try:
            # Calculate SimHash for new tweet
            new_simhash, _, _ = self.calculate_simhash(new_tweet_text)
            query_bucket = self.get_bucket_key(new_simhash)
            
            # Get candidate tweets from same and nearby buckets
            candidates = set()
            
            # Check current bucket and nearby buckets (for fuzzy matching)
            for offset in range(-1, 2):  # Check -1, 0, +1 buckets
                bucket_key = query_bucket + offset
                if bucket_key in self.simhash_index:
                    candidates.update(self.simhash_index[bucket_key])
            
            if not candidates:
                print("No candidates found for matching")
                return []
            
            # Calculate similarity for each candidate
            matches = []
            
            for tweet_id in candidates:
                processed_tweet = self.processed_tweets[tweet_id]
                similarity = self.similarity_score(new_simhash, processed_tweet.simhash)
                
                if similarity >= self.similarity_threshold:
                    match_result = MatchResult(
                        matched_tweet_id=processed_tweet.tweet_id,
                        similarity_score=similarity,
                        verdict=processed_tweet.verdict,
                        votes_in_favor_percentage=processed_tweet.votes_in_favor_percentage,
                        confidence=processed_tweet.confidence,
                        factuality=processed_tweet.factuality,
                        reason=processed_tweet.reason,
                        verification_date=processed_tweet.verification_date,
                        original_tweet_text=new_tweet_text,
                        matched_tweet_text=processed_tweet.tweet_text
                    )
                    matches.append(match_result)
            
            # Sort by similarity (highest first)
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"Found {len(matches)} matches in {processing_time:.3f} seconds")
            print(f"Processed {len(candidates)} candidates from {len(set([self.get_bucket_key(self.processed_tweets[tid].simhash) for tid in candidates]))} buckets")
            
            return matches[:max_results]
            
        except Exception as e:
            print(f"Error finding matches: {e}")
            return []
    
    def match_new_tweet(self, new_tweet_text: str) -> Dict:
        """
        Main function to match a new incoming tweet.
        
        Args:
            new_tweet_text: Text of the new tweet
            
        Returns:
            Dictionary with match results and metadata
        """
        result = {
            'query_tweet': new_tweet_text[:200] + ("..." if len(new_tweet_text) > 200 else ""),
            'total_tweets_in_index': len(self.processed_tweets),
            'similarity_threshold': self.similarity_threshold,
            'matches_found': 0,
            'matches': [],
            'best_match': None
        }
        
        # Find matches
        matches = self.find_matches(new_tweet_text)
        
        if matches:
            result['matches_found'] = len(matches)
            result['best_match'] = {
                'tweet_id': matches[0].matched_tweet_id,
                'similarity': matches[0].similarity_score,
                'verdict': matches[0].verdict,
                'votes_in_favor_percentage': matches[0].votes_in_favor_percentage,
                'confidence': matches[0].confidence
            }
            
            # Convert matches to dictionaries for JSON serialization
            for match in matches:
                match_dict = {
                    'matched_tweet_id': match.matched_tweet_id,
                    'similarity_score': round(match.similarity_score, 4),
                    'verdict': match.verdict,
                    'votes_in_favor_percentage': match.votes_in_favor_percentage,
                    'confidence': match.confidence,
                    'factuality': match.factuality,
                    'reason': match.reason[:100] + "..." if len(match.reason) > 100 else match.reason,
                    'verification_date': match.verification_date.isoformat() if match.verification_date else None,
                    'matched_tweet_text': match.matched_tweet_text[:150] + "..." if len(match.matched_tweet_text) > 150 else match.matched_tweet_text,
                    'original_tweet_text': match.original_tweet_text[:150] + "..." if len(match.original_tweet_text) > 150 else match.original_tweet_text
                }
                result['matches'].append(match_dict)
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get statistics about the current index."""
        if not self.processed_tweets:
            return {}
        
        total_tweets = len(self.processed_tweets)
        
        # Language distribution
        languages = {}
        for tweet in self.processed_tweets.values():
            lang = tweet.language
            languages[lang] = languages.get(lang, 0) + 1
        
        # Bucket distribution
        bucket_stats = {}
        for bucket_key, tweet_ids in self.simhash_index.items():
            bucket_stats[bucket_key] = len(tweet_ids)
        
        return {
            'total_tweets': total_tweets,
            'language_distribution': languages,
            'bucket_distribution': bucket_stats,
            'total_buckets': len(self.simhash_index),
            'avg_tweets_per_bucket': total_tweets / len(self.simhash_index) if self.simhash_index else 0,
            'hash_bits': self.hash_bits,
            'similarity_threshold': self.similarity_threshold
        }


# ==================== MAIN APPLICATION CLASS ====================

class TweetMatchingSystem:
    """Main application class for tweet matching system"""
    
    def __init__(self, db_session: Session = None):
        self.matcher = SimHashMatcher(hash_bits=64, similarity_threshold=0.85)
        self.db_session = db_session
        self.initialized = False
    
    def initialize(self, force_reload: bool = True) -> bool:
        """
        Initialize the matching system.
        
        Args:
            force_reload: If True, reload from database even if helper file exists
            
        Returns:
            True if initialization successful, False otherwise
        """
        print("Initializing Tweet Matching System...")
        
        # Try to load from helper file first (unless force_reload is True)
        if not force_reload and self.matcher.load_from_helper_file():
            print("Successfully loaded from helper file")
            self.initialized = True
            return True
        
        # If helper file doesn't exist or force_reload is True, process from database
        if self.db_session:
            print("Processing tweets from database...")
            count = self.matcher.process_and_index_tweets(self.db_session)
            
            if count > 0:
                self.initialized = True
                print(f"Successfully initialized with {count} tweets")
                return True
            else:
                print("Failed to process tweets from database")
                return False
        else:
            print("No database session provided and helper file not found")
            return False
    
    def match_tweet(self, tweet_text: str) -> Dict:
        """
        Match a new incoming tweet against the database.
        
        Args:
            tweet_text: Text of the incoming tweet
            
        Returns:
            Dictionary with match results
        """
        if not self.initialized:
            print("System not initialized. Please call initialize() first.")
            return {'error': 'System not initialized'}
        
        if not tweet_text or not tweet_text.strip():
            return {'error': 'Empty tweet text provided'}
        
        print(f"\nMatching tweet: {tweet_text[:100]}...")
        return self.matcher.match_new_tweet(tweet_text)
    
    def refresh_index(self) -> bool:
        """Refresh the index from database."""
        if not self.db_session:
            print("No database session available for refresh")
            return False
        
        print("Refreshing index from database...")
        count = self.matcher.process_and_index_tweets(self.db_session)
        
        if count > 0:
            print(f"Index refreshed with {count} tweets")
            self.initialized = True
            return True
        else:
            print("Failed to refresh index")
            return False
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        if not self.initialized:
            return {'error': 'System not initialized'}
        
        return self.matcher.get_statistics()


# ==================== USAGE EXAMPLES ====================

def example_usage():
    """Example usage of the Tweet Matching System"""
    
    print("=" * 80)
    print("TWEET MATCHING SYSTEM - SIMHASH IMPLEMENTATION")
    print("=" * 80)
    
    # Create a database session (you would use your actual database connection)
    # db_session = get_db()  # Uncomment when you have database connection
    
    # For demonstration, we'll use None and load from helper file if it exists
    system = TweetMatchingSystem(db_session=None)
    
    # Try to initialize from helper file
    if system.initialize():
        print("System initialized successfully!")
        
        # Get statistics
        stats = system.get_stats()
        print(f"\nSystem Statistics:")
        print(f"  Total tweets in index: {stats.get('total_tweets', 0)}")
        print(f"  Language distribution: {stats.get('language_distribution', {})}")
        print(f"  Similarity threshold: {stats.get('similarity_threshold', 0.85)}")
        
        # Example tweets to match
        test_tweets = [
            "Hello world! This is a test tweet about programming.",
            "ہیلو دنیا! یہ ایک ٹیسٹ ٹویٹ ہے۔",
            "Beautiful weather today in the city.",
            "Python programming is very interesting and useful for data science.",
            "میں آج سکول جا رہا ہوں پڑھائی کے لیے۔",
        ]
        
        # Test matching
        print("\n" + "=" * 80)
        print("TESTING MATCHING FUNCTIONALITY")
        print("=" * 80)
        
        for i, tweet_text in enumerate(test_tweets, 1):
            print(f"\nTest {i}:")
            print(f"Query tweet: {tweet_text[:80]}...")
            
            result = system.match_tweet(tweet_text)
            
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Total matches found: {result['matches_found']}")
                
                if result['matches_found'] > 0:
                    best_match = result['best_match']
                    print(f"  Best match:")
                    print(f"    Tweet ID: {best_match['tweet_id']}")
                    print(f"    Similarity: {best_match['similarity']:.2%}")
                    print(f"    Verdict: {best_match['verdict']}")
                    print(f"    Votes in favor: {best_match['votes_in_favor_percentage']:.1f}%")
                    
                    # Show all matches if more than one
                    if result['matches_found'] > 1:
                        print(f"  All matches:")
                        for match in result['matches'][:3]:  # Show first 3 matches
                            print(f"    - ID {match['matched_tweet_id']}: {match['similarity_score']:.2%} similar")
                else:
                    print("  No matches found above threshold")
        
        print("\n" + "=" * 80)
        print("SYSTEM READY FOR PRODUCTION USE")
        print("=" * 80)
        
    else:
        print("Failed to initialize system")
        print("Please ensure:")
        print("1. Database connection is available, OR")
        print("2. Helper file (helper.txt) exists from previous processing")


def integration_example():
    """
    Example of how to integrate with your existing system.
    This would be in your main application file.
    """
    
    # In your application startup
    def startup_tweet_matcher():
        """Initialize tweet matching system on application startup."""
        try:
            # Get database session from your existing setup
            db = next(get_db())  # Using your existing get_db() generator
            
            # Create and initialize matching system
            system = TweetMatchingSystem(db_session=db)
            
            # Initialize (loads from helper file if exists, otherwise processes DB)
            if system.initialize():
                print("Tweet matching system initialized successfully")
                return system
            else:
                print("Failed to initialize tweet matching system")
                return None
                
        except Exception as e:
            print(f"Error initializing tweet matcher: {e}")
            return None
    
    # When a new tweet arrives in your system
    def process_incoming_tweet(tweet_text: str, matching_system: TweetMatchingSystem):
        """Process an incoming tweet and find matches."""
        try:
            # Find matching tweets
            result = matching_system.match_tweet(tweet_text)
            
            # Process the results
            if result and 'matches_found' in result and result['matches_found'] > 0:
                print(f"Found {result['matches_found']} similar tweets")
                
                # Take action based on matches
                for match in result['matches']:
                    if match['similarity_score'] >= 0.85:  # 85% threshold
                        print(f"High similarity match found:")
                        print(f"  ID: {match['matched_tweet_id']}")
                        print(f"  Similarity: {match['similarity_score']:.2%}")
                        print(f"  Previous verdict: {match['verdict']}")
                        print(f"  Votes in favor: {match['votes_in_favor_percentage']:.1f}%")
                        
                        # You can now use this information in your application:
                        # - Flag potential duplicates
                        # - Pre-populate verification based on similar tweets
                        # - Alert moderators
                        # - etc.
                
                return result
            else:
                print("No similar tweets found above threshold")
                return None
                
        except Exception as e:
            print(f"Error processing incoming tweet: {e}")
            return None
    
    # Scheduled refresh (e.g., daily)
    def refresh_tweet_index(matching_system: TweetMatchingSystem):
        """Refresh the tweet index periodically."""
        print("Refreshing tweet index...")
        if matching_system.refresh_index():
            print("Tweet index refreshed successfully")
            return True
        else:
            print("Failed to refresh tweet index")
            return False


if __name__ == "__main__":
    # Run example usage
    example_usage()
    
    # Show integration example
    print("\n" + "=" * 80)
    print("INTEGRATION GUIDE")
    print("=" * 80)
  