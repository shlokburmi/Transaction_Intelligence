"""
Tests for Support Modules (Category Mapper & Confidence Scorer).
"""

from src.category_mapper import CategoryMapper
from src.confidence_scorer import ConfidenceScorer

def test_category_mapper():
    # Exact
    assert CategoryMapper.get_category("Amazon") == "Shopping"
    assert CategoryMapper.get_category("Starbucks") == "Dining"
    
    # Partial match fallback
    assert CategoryMapper.get_category("Amazon Web Services") == "Utilities" # Note: "Amazon Web Services" is mapped to Utilities directly, but "Amazon Prime" would map to "Shopping" via partial match if "Amazon Prime" was passed.
    
    # Not found
    assert CategoryMapper.get_category("Unknown Store") is None
    assert CategoryMapper.get_category("") is None

def test_confidence_scorer():
    # Dictionary exact
    score1 = ConfidenceScorer.calculate("Dictionary", "exact", ["category_from_db", "merchant_name_clean"])
    # 90 + 9 + 3 + 2 = 104 -> capped at 99
    assert score1 == 99
    
    # Dictionary substring short
    score2 = ConfidenceScorer.calculate("Dictionary", "substring_short", ["category_from_db"])
    # 90 + 4 + 3 = 97
    assert score2 == 97
    
    # Fuzzy match
    score3 = ConfidenceScorer.calculate("Fuzzy", "fuzzy_85_89", ["category_from_db"])
    # 70 + 5 + 3 = 78
    assert score3 == 78
    
    # LLM unknown
    score4 = ConfidenceScorer.calculate("LLM", "llm_unknown_merchant", ["category_from_llm"])
    # 55 + 3 + 1 = 59
    assert score4 == 59
    
    # Fallback
    score5 = ConfidenceScorer.calculate("Fallback")
    # 25 + 0 + 0 = 25
    assert score5 == 25

def test_get_location_for_txn():
    from app import get_location_for_txn
    assert get_location_for_txn("THEOBROMA CAFE DELHI") == "Delhi, IN"
    assert get_location_for_txn("KFC ONLINE DELIVERY") == "Online"
    assert get_location_for_txn("UBER *TRIP SFO TO PA 11/04 CA") == "San Francisco, CA"
    assert get_location_for_txn("AMZN Mktp US*2J8A39R Anzn.com/billWA") == "Seattle, WA"
    assert get_location_for_txn("TST* LOCAL COFFEE SHOP NY") == "New York, NY"
    assert get_location_for_txn("SOME RANDOM TX SHOP") == "Dallas, TX"
    assert get_location_for_txn("CHICAGO CHICKEN") == "Chicago, IL"
    assert get_location_for_txn("MCDONALDS MUMBAI") == "Mumbai, IN"
    assert get_location_for_txn("ZEPTO BLR") == "Bangalore, IN"
    assert get_location_for_txn("HYD BIRYANI HOUSE") == "Hyderabad, IN"
    assert get_location_for_txn("CHE CLOTHING") == "Chennai, IN"
    assert get_location_for_txn("RELIANCE FRESH IN") == "Mumbai, IN"
    assert get_location_for_txn("JUST CAFE") == "Online"

