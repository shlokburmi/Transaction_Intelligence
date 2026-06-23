"""
Tests for the Tier 3 Fuzzy Matcher.
"""

from src.fuzzy_matcher import FuzzyMatcher
from src.config import FUZZY_THRESHOLD

def test_fuzzy_match_typo():
    # Typo for Starbucks
    result = FuzzyMatcher.match("STARBCKS")
    assert result is not None
    assert result["merchant"] == "Starbucks"
    assert result["similarity_score"] >= FUZZY_THRESHOLD
    
    # Typo for BigBasket
    result2 = FuzzyMatcher.match("BIGBASKETT")
    assert result2 is not None
    assert result2["merchant"] == "BigBasket"

def test_below_threshold():
    # completely different words shouldn't match
    result = FuzzyMatcher.match("SHOPPERS STOP")
    # Actually, it might match if we add SHOPPERS STOP to dictionary, 
    # but let's test a word that is definitely not close to anything in the dictionary
    result = FuzzyMatcher.match("RANDOMGARBAGE TEXT")
    assert result is None

def test_too_short():
    # Should skip strings < FUZZY_MIN_LENGTH (default 4)
    # Even if "HP" is in the dictionary (it is mapped to Hindustan Petroleum via alias, but canonical is "Hindustan Petroleum")
    # Actually, CANONICAL_MERCHANTS contains "Hindustan Petroleum", "Amazon", etc.
    # The cleaned string "HP" is length 2, so it returns None immediately.
    assert FuzzyMatcher.match("HP") is None
    
def test_order_insensitive():
    # Since we use token_sort_ratio, the order of words doesn't matter
    # For example, "Coffee Starbucks" should match "Starbucks" with high score
    # We don't have "Coffee Starbucks" in canonical, but we have "Blue Tokai Coffee"
    result = FuzzyMatcher.match("COFFEE BLUE TOKAI")
    assert result is not None
    assert result["merchant"] == "Blue Tokai Coffee"
