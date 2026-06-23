"""
Reward360 Transaction Intelligence Engine — Tier 2: Regex Matcher

Attempts to extract the merchant name using compiled regex patterns.
Useful for identifying merchants embedded in a noisy string (e.g., UBER *EATS).
Uses the NORMALIZED string, as structural patterns might rely on prefixes/IDs.
"""

from typing import Optional, Dict, Any
from src.logger import get_logger
from data.regex_patterns import MERCHANT_PATTERNS, STRUCTURAL_PATTERNS

logger = get_logger(__name__)

class RegexMatcher:
    @staticmethod
    def match(normalized_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to extract a merchant name using regex patterns.
        
        Args:
            normalized_text: The uppercased, original-length transaction string.
            
        Returns:
            Dict with match details if successful, None otherwise.
        """
        if not normalized_text:
            return None
            
        # 1. Try specific merchant patterns
        for pattern, merchant_name in MERCHANT_PATTERNS:
            match = pattern.search(normalized_text)
            if match:
                logger.debug(f"Regex specific match: '{pattern.pattern}' -> {merchant_name}")
                return {
                    "merchant": merchant_name,
                    "method": "Regex",
                    "pattern_name": "merchant_specific",
                    "match_quality_key": "regex_specific"
                }

        # 2. Try generic structural patterns
        # e.g., PAYTM*MERCHANT NAME -> MERCHANT NAME
        for pattern in STRUCTURAL_PATTERNS:
            match = pattern.search(normalized_text)
            if match and match.groups():
                extracted = match.group(1).strip()
                if extracted:
                    # Title case the extracted name
                    merchant_name = extracted.title()
                    logger.debug(f"Regex structural match: '{pattern.pattern}' -> {merchant_name}")
                    return {
                        "merchant": merchant_name,
                        "method": "Regex",
                        "pattern_name": "structural_prefix",
                        "match_quality_key": "regex_structural"
                    }
                    
        return None
