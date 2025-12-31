#crossverify.py
import re
import time
import requests
from sentence_transformers import util, SentenceTransformer
from bs4 import BeautifulSoup
from transformers import pipeline
from urllib.parse import urlparse
from database import get_db
from models import PlatformAccount, BlockedDomain
import random
from langdetect import detect, LangDetectException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from urllib.parse import urlparse
from query_builder import (
    SmartQueryBuilder,
    DateFilterCalculator,
    DomainFilter,
    build_search_query,
    get_date_filter_params
)

COLAB_API_URL = "https://juanita-divestible-kathrine.ngrok-free.dev"
API_ENDPOINT = f"{COLAB_API_URL}/nli"



# Configurations (API Keys + URL)
GOOGLE_API_KEY = "AIzaSyD88aEmIVhVYuf-ouh3WVGgDVvXWdz0oLw"
GOOGLE_CX = "90bb854388dee4e5b"
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# Cache for blocked domains (loaded from database)
_blocked_domains_cache = None
_cache_timestamp = None
CACHE_DURATION = 3600  # Refresh cache every hour (If any changes are made to data base)

# User-Agents used for scraping articles
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


# Language detection (Urdu, English and Roman Urdu)
def detect_language(text: str) -> str:
    """ Detects if text is Urdu, English, or Roman Urdu.
    Returns: 'urdu' or 'english' (Roman Urdu is handled as English because the
    model used for English is multi-lingual and works on Roman Urdu)"""
    try:
        # Clean URLs, mentions, hashtags before detection
        clean_for_detection = re.sub(r'http\S+|www\.\S+|[@#]\S+', '', text).strip()

        if not clean_for_detection:
            return 'english'

        lang = detect(clean_for_detection)
        print(f"Detected language code: {lang}") # Can be id, so, hi, ms, ur, en

        # Misclassifications for Roman Urdu(works well just misclassified)
        roman_urdu_aliases = ['id', 'so', 'hi', 'ms']

        if lang == 'ur':
            print("Using 'Urdu' pipeline")
            return 'urdu'
        elif lang in roman_urdu_aliases:
            print("Detected Roman Urdu (mapped to English pipeline)")
            return 'english'
        else:
            print("Using 'English' pipeline")
            return 'english'
    # Fallback in-case any error occurs
    except LangDetectException:
        print("Language detection failed, defaulting to English")
        return 'english'


# Model Manager to manage two seperate pipeline (English/Roman Urdu and Urdu)


# Global model manager instance



# Getter for retrieving blocked domains(Social Media Sites)
def get_blocked_domains(db: Session) -> set:
    """Fetch blocked domains from database with caching.
    Returns a set of blocked domain strings."""
    global _blocked_domains_cache, _cache_timestamp
    
    current_time = time.time()
    
    # Return cached data if still valid (to save retieval time)
    if _blocked_domains_cache and _cache_timestamp:
        if current_time - _cache_timestamp < CACHE_DURATION:
            return _blocked_domains_cache
    
    # Fetch from database
    try:
        blocked = db.query(BlockedDomain.domain).all()
        _blocked_domains_cache = {domain[0].lower() for domain in blocked}
        _cache_timestamp = current_time
        print(f"Loaded {len(_blocked_domains_cache)} blocked domains from database")
        return _blocked_domains_cache
    except Exception as e:
        print(f"Could not load blocked domains from database: {e}")
        # Fallback to hardcoded list
        fallback = {
            'facebook.com', 'twitter.com', 'x.com', 'instagram.com',
            't.me', 'telegram.org', 'reddit.com', 'youtube.com',
            'tiktok.com', 'linkedin.com', 'pinterest.com', 'tumblr.com',
            'snapchat.com', 'whatsapp.com', 'medium.com', 'blogspot.com',
            'wordpress.com', 'wix.com', 'quora.com'
        }
        return fallback

# Checks whether the retrieved domain is a blocked domain or not (Social Media Site)
def is_blocked_domain(url: str, db: Session) -> bool:
    """Check if URL is from a blocked domain."""
    try:
        domain = urlparse(url).netloc.lower()
        domain_clean = domain.replace('www.', '')
        
        # Get blocked domains from database
        blocked_domains = get_blocked_domains(db)
        
        # Check against blocked domains
        for blocked in blocked_domains:
            if blocked in domain_clean:
                return True
        return False
    except:
        return False

# English and Roman Urdu Stop Words


# Google Search with filteration and smart query generation (new module)
def google_search_top_10(tweet_text: str, entities: list, language: str = 'english', db: Session = None, tweet_date: str = None, max_results: int = 10):
    print(f"Step 2: Performing Enhanced Google Search...")
    print(f"Language: {language.upper()}")
    
    # Step 1: Build Optimized Query
    blocked_domains = get_blocked_domains(db)
    
    # Use the query builder module
    final_query = build_search_query(
        tweet_text=tweet_text,
        entities=entities,
        language=language,
        blocked_domains=blocked_domains,
        max_blocked=15  # Limit to top 15 to avoid query length issues
    )
    
    print(f"Query: {final_query[:200]}...")
    print(f"Query Length: {len(final_query)} chars")

    # Step 2: Setup Search Parameters
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": final_query,
        "num": max_results
    }
    
    # Add language parameters
    if language.lower() == 'urdu':
        params['lr'] = 'lang_ur'
        params['hl'] = 'ur'
    else:
        params['lr'] = 'lang_en'
        params['hl'] = 'en'
    
    # Add date filter using dateRestrict (more reliable)
    date_params = get_date_filter_params(tweet_date, use_date_restrict=True)
    params.update(date_params)
    
    if 'dateRestrict' in params:
        print(f"Date Filter: {params['dateRestrict']}")
    else:
        print(f"No date filter applied")
    
    # Step 3: Perform Search with Fallback
    articles = []
    seen_domains = set()
    
    def perform_search_request(search_params: dict) -> list:
        """Helper function to perform search and process results"""
        try:
            response = requests.get(GOOGLE_SEARCH_URL, params=search_params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                results = []
                
                for item in items:
                    url = item.get("link", "")
                    domain = DomainFilter.normalize_domain(
                        urlparse(url).netloc
                    )
                    
                    # Skip blocked domains (double-check)
                    if is_blocked_domain(url, db):
                        print(f"Filtered: {domain} (blocked)")
                        continue
                    
                    # Skip duplicate domains
                    if DomainFilter.is_duplicate_domain(domain, seen_domains):
                        print(f"Skipped: {domain} (duplicate)")
                        continue
                    
                    seen_domains.add(domain)
                    
                    results.append({
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("snippet", ""),
                        "domain": domain
                    })
                
                return results
            
            elif response.status_code == 429:
                print("Rate limit exceeded (Google API)")
            else:
                print(f"Search API Error: HTTP {response.status_code}")
            
            return []
            
        except requests.Timeout:
            print("Search request timed out")
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    # Primary search attempt
    articles = perform_search_request(params)
    print(f"Primary search: {len(articles)} articles")
    
    # Step 4: Fallback Strategies
    
    # Fallback 1: Remove date filter if no results
    if not articles and 'dateRestrict' in params:
        print("Fallback 1: Removing date filter...")
        params.pop('dateRestrict')
        articles = perform_search_request(params)
        print(f"Fallback 1: {len(articles)} articles")
    
    # Fallback 2: Simplify query to entities only
    if not articles and entities:
        print("Fallback 2: Using entities only...")
        prioritized = SmartQueryBuilder.prioritize_entities(entities, tweet_text)
        
        if prioritized:
            simple_query = ' '.join(prioritized[:3])
            params['q'] = simple_query
            articles = perform_search_request(params)
            print(f"Fallback 2: {len(articles)} articles")
    
    # Step 5: Final Results
    if articles:
        print(f"Total unique articles retrieved: {len(articles)}")
    else:
        print("No credible results found after all attempts")
    
    return articles[:max_results]













# Checking data base for credibility scoring based on what we discussed 20%
def check_source_in_database(domain: str, db: Session) -> tuple[bool, float]:
    """Check if a source domain or its variant exists in the platform_accounts table."""
    if not db or not domain:
        return False, 0.0

    try:
        # Normalize domain
        domain = domain.strip().lower()

        # Handle raw URLs
        parsed = urlparse(domain)
        netloc = parsed.netloc or domain
        domain_clean = netloc.replace("www.", "").strip()

        # URL matching
        account = (
            db.query(PlatformAccount)
            .filter(
                or_(
                    func.lower(PlatformAccount.url).ilike(f"%{domain_clean}%"),
                    func.lower(PlatformAccount.url).ilike(f"%{netloc}%"),
                    func.lower(PlatformAccount.url).ilike(f"%{domain}%")
                )
            )
            .first()
        )

        if account:
            credibility = account.credibility_score or 0.5
            print(f"Source '{domain_clean}' found in database (Credibility: {credibility:.2f})")
            return True, credibility

        print(f"Source '{domain_clean}' NOT in database")
        return False, 0.0

    except Exception as e:
        print(f"Database check error for '{domain}': {e}")
        return False, 0.0

# Computing a Final confidence score for the confidence bar in the plugin
def compute_final_confidence(top_3_articles: list, db: Session):
    """Calculates final confidence with 80/20 split:
    - 80% from Evidence Quality (Semantic + NLI combined_score)
    - 20% from Database Matching with CREDIBILITY SCORE:
      * Base weight per source: 6.67%
      * Actual boost: 6.67% × credibility_score
      * Example: BBC (0.95 credibility) = 6.67% × 0.95 = 6.34%"""
    
    print(f"Step 4: Computing final confidence score...")
    
    if not top_3_articles:
        return 0.0, []
    
    # Evidence Quality Calculation
    # Weighted average: 50% best, 30% second, 20% third
    """If all three sources are given same weights, it would affect the final calculation
    drastically. Suppose if source 1 has a score of 70% and source 2 and 3 has a score of
    55% it would drastically affect the final score that's why these weights are being used.
    You can change them to your liking"""
    weights = [0.5, 0.3, 0.2]
    weighted_score = sum(
        art["combined_score"] * weights[i] 
        for i, art in enumerate(top_3_articles[:3])
    )
    
    evidence_score = weighted_score * 0.80
    
    print(f"\nEvidence Quality (80% weightage):")
    for i, art in enumerate(top_3_articles, 1):
        print(f"[{i}] Semantic: {art['semantic_percentage']}%, NLI: {art['nli_percentage']}% (weight: {weights[i-1]*100:.0f}%)")
    print(f"Evidence Subtotal: {evidence_score*100:.1f}% (80% weight)")
    
    # Database matching, the 20% as discussed
    db_boost_total = 0.0
    sources_checked = []
    base_weight_per_source = 20.0 / 3.0  # 6.67% base per source
    
    print(f"\nDatabase matching (20%):")
    for idx, art in enumerate(top_3_articles, 1):
        in_db, credibility_score = check_source_in_database(art["domain"], db)
        # Calculate actual boost(score): base_weight × credibility_score
        if in_db:
            actual_boost_percent = base_weight_per_source * credibility_score
            actual_boost_decimal = actual_boost_percent / 100.0
            db_boost_total += actual_boost_decimal
            
            print(f"[{idx}] {art['domain']}: In DB")
            print(f"Credibility Score: {credibility_score:.2f}")
            print(f"Boost(Score): {base_weight_per_source:.2f}% × {credibility_score:.2f} = {actual_boost_percent:.2f}%")
        else:
            credibility_score = 0.0
            print(f"[{idx}] {art['domain']}: Not in DB (+0%)") # 0 as we discussed on meets
        
        sources_checked.append({
            **art,
            "in_database": in_db,
            "credibility_score": credibility_score
        })
    
    print(f"Database Subtotal: {db_boost_total*100:.2f}%")
    
    # Final Calculation of the confidence score 
    final_confidence = evidence_score + db_boost_total
    final_confidence_percent = round(final_confidence * 100, 1)
    
    print(f"\nFinal Breakdown:")
    print(f"Evidence Quality Score: {evidence_score*100:.1f}%")
    print(f"Database Boost Score:   {db_boost_total*100:.2f}%")
    print(f"    ════════════════════════════════════════════")
    print(f"Final Confidence Score: {final_confidence_percent}%")
    
    return final_confidence_percent, sources_checked

# Verdict (True, False or Unverified) Only Three labels being used as we discussed in meets
def determine_verdict(top_3_articles: list, confidence: float):
    """Determine verdict based on confidence and NLI consensus.
    Thresholds:
    - Unanimous (3/3): 50% confidence
    - Majority (2/3): 55% confidence  
    - High confidence: 65% override
    """
    if not top_3_articles:
        return "Unverified"
    
    label_counts = {"SUPPORTS": 0, "CONTRADICTS": 0, "NEUTRAL": 0}
    for art in top_3_articles:
        label = art.get("nli_label", "NEUTRAL")
        label_counts[label] += 1
    
    majority_label = max(label_counts, key=label_counts.get)
    majority_count = label_counts[majority_label]
    
    print(f"\nVerdict Determination:")
    print(f"Confidence Score: {confidence}%")
    print(f"NLI Votes: Supporting articles={label_counts['SUPPORTS']}, "
          f"Contradicting articles={label_counts['CONTRADICTS']}, Neutral Articles={label_counts['NEUTRAL']}")
    
    if majority_label == "NEUTRAL":
        verdict = "Unverified"
        reason = "No clear support or contradiction"
    
    elif majority_count == 3:  # UNANIMOUS
        if majority_label == "SUPPORTS" and confidence >= 50:
            verdict = "True"
            reason = f"Unanimous support (3/3) with {confidence}% confidence"
        elif majority_label == "CONTRADICTS" and confidence >= 50:
            verdict = "False"
            reason = f"Unanimous contradiction (3/3) with {confidence}% confidence"
        else:
            verdict = "Unverified"
            reason = f"Unanimous {majority_label} but confidence too low ({confidence}% < 50%)"
    
    elif majority_count == 2:  # Majority
        if majority_label == "SUPPORTS" and confidence >= 55:
            verdict = "True"
            reason = f"Strong majority support (2/3) with {confidence}% confidence"
        elif majority_label == "CONTRADICTS" and confidence >= 55:
            verdict = "False"
            reason = f"Strong majority contradiction (2/3) with {confidence}% confidence"
        elif confidence >= 65:
            verdict = "True" if majority_label == "SUPPORTS" else "False"
            reason = f"High confidence ({confidence}%) with majority {majority_label}"
        else:
            verdict = "Unverified"
            reason = f"Majority {majority_label} but confidence too low ({confidence}% < 55%)"
    
    else:
        verdict = "Unverified"
        reason = "No consensus among sources"
    
    print(f"Verdict: {verdict}")
    print(f"Reason: {reason}")
    
    return verdict

# Main Pipeline
def cross_verify(text: str, db: Session, author_handle: str = None, tweet_date: str = None):
    start_time = time.time()
    print("\n" + "="*60)
    print("Cross Verifying...")
    print("="*60)

    # Step 0: Detect language
    print("Step 0: Detecting language...")
    language = detect_language(text)
    print(f"Using {language.upper()} pipeline")
    print("-"*60)

    # Step 1: Extract entities (text already normalized by normalize.py)
    print("="*60)
    payload = {
    "text":text,
    "language": language
        }
    
    response = requests.post(f"{COLAB_API_URL}/ner", json=payload)

    # Parse response
    if response.status_code == 200:
        data = response.json()
        #print(" Response received:")
        
        print("Tweet Text:", data.get("original_text"))
        print("Entities:")
        for ent in data.get("entities", []):
            print(f" - {ent}")
    else:
        print(" Request failed:", response.text)

    tweet_text = data.get("original_text", "")
    entities = data.get("entities", [])


    
    print("="*60)
    # Step 2: Google search top 7
    print("="*60)
    articles = google_search_top_10(tweet_text, entities, language, db, tweet_date)
    print("="*60)
    if not articles:
        print("No credible search results found")
        return {
            "claim": text,
            "language": language,
            "confidence_score": 0.0,
            "verdict": "Unverified",
            "sources": [],
            "elapsed_time": round(time.time() - start_time, 2)
        }

    # Step 3: Semantic similarity + NLI
    print("="*60)

    payload = {
    "tweet_text":tweet_text,
    "articles": articles,
    "language" : language
        }
    
    response = requests.post(f"{COLAB_API_URL}/nli", json=payload)

    if response.status_code == 200:
        data = response.json()

    top_3_articles= data.get("top_articles" , [])       



    

    print("="*60)
    if not top_3_articles:
        print("No relevant evidence found")
        return {
            "claim": text,
            "language": language,
            "confidence_score": 0.0,
            "verdict": "Unverified",
            "sources": [],
            "elapsed_time": round(time.time() - start_time, 2)
        }

    # Step 4: Check database and compute confidence
    print("="*60)
    final_confidence, sources_with_db_status = compute_final_confidence(top_3_articles, db)
    print("="*60)
    # Step 5: Determine verdict
    print("="*60)
    verdict = determine_verdict(top_3_articles, final_confidence)
    print("="*60)
    elapsed_time = round(time.time() - start_time, 2)
    
    print("="*60)
    print(f"Cross-Verification Done, Time Taken: ({elapsed_time}s)")
    print(f"Language: {language.upper()}")
    print(f"Verdict: {verdict}")
    print(f"Confidence Score: {final_confidence}%")
    print(f"Sources returned: {len(sources_with_db_status)}")
    print("="*60)

    return {
        "claim": text,
        "language": language,
        "confidence_score": final_confidence,
        "verdict": verdict,
        "sources": sources_with_db_status,
        "elapsed_time": elapsed_time
    }