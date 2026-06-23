"""
Tests for the Preprocessor module.
"""

from src.preprocessor import Preprocessor

def test_empty_inputs():
    assert Preprocessor.process("")["cleaned"] == ""
    assert Preprocessor.process(None)["cleaned"] == ""
    assert Preprocessor.process("   ")["cleaned"] == ""

def test_normalization():
    result = Preprocessor.process("  Uber   Eats  ")
    assert result["original"] == "  Uber   Eats  "
    assert result["normalized"] == "UBER EATS"
    
def test_prefix_removal():
    assert Preprocessor.process("SQ *BLUE TOKAI COFFEE")["cleaned"] == "BLUE TOKAI COFFEE"
    assert Preprocessor.process("PAYPAL *EBAY")["cleaned"] == "EBAY"
    assert Preprocessor.process("CRV*UBER")["cleaned"] == "UBER"

def test_suffix_removal():
    assert Preprocessor.process("AMZN MKTP IN*2H4XK")["cleaned"] == "AMZN MKTP"
    assert Preprocessor.process("STARBUCKS #1293 NEW YORK US")["cleaned"] == "STARBUCKS NEW YORK" # NEW YORK might stay, US and ID removed
    assert Preprocessor.process("SBUX 04829 MUMBAI")["cleaned"] == "SBUX MUMBAI"

def test_standalone_number_removal():
    # Store IDs should be removed
    assert Preprocessor.process("MCDONALDS 0045 DELHI")["cleaned"] == "MCDONALDS DELHI"
    # Numbers within words should stay
    assert Preprocessor.process("B2B LOGISTICS")["cleaned"] == "B2B LOGISTICS"

def test_preserve_meaningful_characters():
    assert Preprocessor.process("H&M CLOTHING")["cleaned"] == "H&M CLOTHING"
    assert Preprocessor.process("MARKS & SPENCER")["cleaned"] == "MARKS & SPENCER"
    
def test_pure_noise_fallback():
    # If cleaning removes everything, it should fall back to normalized
    result = Preprocessor.process("***12345***")
    assert result["cleaned"] == "***12345***"
