"""
Tests for the Tier 2 Regex Matcher.
"""

from src.regex_matcher import RegexMatcher

def test_merchant_specific_pattern():
    # Uber without capture group
    result1 = RegexMatcher.match("UBER TRIP MUMBAI")
    assert result1 is not None
    assert result1["merchant"] == "Uber"
    assert result1["match_quality_key"] == "regex_specific"
    
    # Uber with capture group
    result2 = RegexMatcher.match("UBER *EATS HELP.UBER.COM")
    assert result2 is not None
    assert result2["merchant"] == "Uber Eats"

    # IRCTC
    result3 = RegexMatcher.match("IRCTC RAIL CONNECT")
    assert result3 is not None
    assert result3["merchant"] == "IRCTC"
    
def test_structural_pattern():
    # PAYTM prefix
    result = RegexMatcher.match("PAYTM*LOCAL KIRANA STORE")
    assert result is not None
    assert result["merchant"] == "Local Kirana Store"
    assert result["match_quality_key"] == "regex_structural"

def test_no_match():
    assert RegexMatcher.match("UNKNOWN STORE BANGALORE") is None
    assert RegexMatcher.match("") is None
