"""
Tests for the Tier 1 Dictionary Matcher.
"""

from src.dictionary_matcher import DictionaryMatcher

def test_exact_match():
    result = DictionaryMatcher.match("AMAZON")
    assert result is not None
    assert result["merchant"] == "Amazon"
    assert result["match_type"] == "exact"
    assert result["match_quality_key"] == "exact"
    
def test_substring_match_long():
    # "STARBUCKS" is 9 chars -> substring_long
    result = DictionaryMatcher.match("STARBUCKS NEW YORK")
    assert result is not None
    assert result["merchant"] == "Starbucks"
    assert result["match_type"] == "substring"
    assert result["match_quality_key"] == "substring_long"
    assert result["matched_alias"] == "STARBUCKS"
    
def test_substring_match_short():
    # "SBUX" is 4 chars -> substring_short
    result = DictionaryMatcher.match("SBUX MUMBAI")
    assert result is not None
    assert result["merchant"] == "Starbucks"
    assert result["match_type"] == "substring"
    assert result["match_quality_key"] == "substring_short"
    assert result["matched_alias"] == "SBUX"

def test_longest_match_wins():
    # "RELIANCE SMART" should win over "RELIANCE" if both were in dictionary
    # Currently only RELIANCE SMART is in the dictionary, but testing the principle
    result = DictionaryMatcher.match("RELIANCE SMART BENGALURU")
    assert result is not None
    assert result["merchant"] == "Reliance Smart"
    
def test_no_match():
    assert DictionaryMatcher.match("UNKNOWN MERCHANT") is None
    assert DictionaryMatcher.match("") is None
    
def test_boundary_matching():
    # Ensure "HP" doesn't match inside a word like "TOUCHPAD"
    # Note: "TOUCHPAD" is a contrived example, but testing the boundary logic
    assert DictionaryMatcher.match("TOUCHPAD") is None
    
    # "HP" at the start with space
    result = DictionaryMatcher.match("HPCL PETROL BUNK")
    assert result is not None
    assert result["merchant"] == "Hindustan Petroleum"
