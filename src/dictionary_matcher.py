"""
Reward360 Transaction Intelligence Engine — Tier 1: Dictionary Matcher

Checks the cleaned transaction string against the curated merchant dictionary.
Tries exact matching first, then falls back to substring matching (longest first).
"""

from typing import Optional, Dict, Any
from src.logger import get_logger
from data.merchant_dictionary import MERCHANT_ALIASES

logger = get_logger(__name__)

class DictionaryMatcher:
    @staticmethod
    def match(cleaned_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to match the cleaned text against the dictionary.
        
        Args:
            cleaned_text: The cleaned, uppercased transaction string.
            
        Returns:
            Dict with match details if successful, None otherwise.
        """
        if not cleaned_text:
            return None
            
        # 1. Exact Match
        if cleaned_text in MERCHANT_ALIASES:
            merchant = MERCHANT_ALIASES[cleaned_text]
            logger.debug(f"Dictionary exact match: '{cleaned_text}' -> {merchant}")
            return {
                "merchant": merchant,
                "method": "Dictionary",
                "match_type": "exact",
                "matched_alias": cleaned_text,
                "match_quality_key": "exact"
            }
            
        # 2. Substring Match (Longest match wins)
        # Sort keys by length descending to catch "AMAZON PRIME" before "AMAZON"
        sorted_aliases = sorted(MERCHANT_ALIASES.keys(), key=len, reverse=True)
        
        # Word boundary search is safer than naive substring
        # e.g., "MCD" shouldn't match inside "AMCDONALDS" (not a real example, but principle holds)
        for alias in sorted_aliases:
            # Simple substring is often sufficient since the text is cleaned
            # and aliases are usually whole words or acronyms
            # We enforce spaces around the alias or matching at string boundaries
            # to avoid matching "HP" inside "TOC[HP]HONE"
            
            # Create a padded version to simulate boundaries
            padded_text = f" {cleaned_text} "
            padded_alias = f" {alias} "
            
            if padded_alias in padded_text or cleaned_text.startswith(f"{alias} ") or cleaned_text.endswith(f" {alias}"):
                merchant = MERCHANT_ALIASES[alias]
                
                # Determine quality based on length of matched alias
                quality_key = "substring_long" if len(alias) >= 6 else "substring_short"
                
                logger.debug(f"Dictionary substring match: '{alias}' in '{cleaned_text}' -> {merchant}")
                return {
                    "merchant": merchant,
                    "method": "Dictionary",
                    "match_type": "substring",
                    "matched_alias": alias,
                    "match_quality_key": quality_key
                }
                
        return None
