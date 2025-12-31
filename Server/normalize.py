import re
from urllib.parse import urlparse

def normalize_tweet(text: str) -> str:
    """
    Enhanced normalization that preserves critical words and handles both Urdu and English.
    
    Improvements:
    - Preserves negation words (no, not, نہیں, نہ)
    - Better URL cleaning without removing adjacent words
    - Preserves sentence structure
    - Handles mixed language content
    """
    if not text:
        return ""
    
    original_text = text
    
    # 1. Normalize whitespace first
    text = " ".join(text.split())
    
    # 2. Remove URLs more carefully (don't remove adjacent words)
    # Match URLs with word boundaries
    text = re.sub(r'\b(?:https?://|www\.)\S+', '', text)
    
    # 3. Remove standalone domain patterns (but keep context)
    text = re.sub(r'\b[a-z0-9-]+\.(com|org|net|pk|in|tv)\b', '', text, flags=re.IGNORECASE)
    
    # 4. Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # 5. Remove mentions and hashtags (but preserve the text content)
    text = re.sub(r'@\w+', '', text)  # Remove @mentions
    text = re.sub(r'#(\w+)', r'\1', text)  # Keep hashtag text, remove #
    
    # 6. Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # 7. Remove standalone punctuation and special characters
    # But preserve punctuation that's part of sentences
    text = re.sub(r'\s+[^\w\s\u0600-\u06FF]+\s+', ' ', text)
    
    # 8. Final cleanup
    text = text.strip()
    
    # 9. Quality check - if we removed too much, return original
    if len(text) < len(original_text) * 0.3:  # If less than 30% remains
        print("⚠️ Warning: Normalization removed too much content, using original")
        return original_text
    
    return text


def validate_normalization(original: str, normalized: str) -> dict:
    """
    Validate that normalization didn't break the tweet.
    Returns: {is_valid: bool, issues: list}
    """
    issues = []
    
    # Check 1: Length
    if len(normalized) < len(original) * 0.3:
        issues.append("Too much content removed")
    
    # Check 2: Negation words preserved (critical for fact-checking)
    negation_words = ['not', 'no', 'نہیں', 'نہ', "don't", "didn't", "won't", "can't"]
    for neg in negation_words:
        if neg in original.lower() and neg not in normalized.lower():
            issues.append(f"Lost negation word: {neg}")
    
    # Check 3: Key entities preserved (basic check)
    # Extract capitalized words or Urdu named entities
    original_caps = set(re.findall(r'\b[A-Z][a-z]+\b', original))
    normalized_caps = set(re.findall(r'\b[A-Z][a-z]+\b', normalized))
    lost_entities = original_caps - normalized_caps
    if len(lost_entities) > 2:
        issues.append(f"Lost multiple entities: {lost_entities}")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }

    # Test cases
    tests = [
        # Urdu test (the problematic one)
        "پاکستان کو اپنے اندرونی معاملات پر دوسروں کے مشوروں کی ضرورت نہیں: دفترِ خارجہ کا افغان طالبان کے ٹی ایل پی سے متعلق بیان پر ردِعمل\nتفصیلات: \nhttps://\nbbc.in/4n2KmkO",
        
        # English test
        "Afghanistan-Pakistan war escalates again! Pakistani Air Force bombing Kabul. Military junta in Pakistan, after its diplomatic victory over military face off against India in May, is taking on its own protege, Taliban.",
        
        # Mixed content
        "Breaking: PM announces new policy. Details at www.example.com #Pakistan @PMOffice"
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}:")
        print(f"Original ({len(test)} chars):")
        print(test[:100] + "..." if len(test) > 100 else test)
        
        normalized = normalize_tweet(test)
        print(f"\nNormalized ({len(normalized)} chars):")
        print(normalized[:100] + "..." if len(normalized) > 100 else normalized)
        
        validation = validate_normalization(test, normalized)
        print(f"\nValidation: {'✓ PASS' if validation['is_valid'] else '✗ FAIL'}")
        if validation['issues']:
            print(f"Issues: {', '.join(validation['issues'])}")