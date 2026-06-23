"""
Reward360 Transaction Intelligence Engine — Tier 3: Fuzzy Matcher

Uses RapidFuzz to find approximate matches against the known canonical merchants.
This catches typos (STARBCKS -> Starbucks) and minor variations, saving LLM calls.
"""

from typing import Optional, Dict, Any
from rapidfuzz import process, fuzz
from src.logger import get_logger
from src.config import FUZZY_THRESHOLD, FUZZY_MIN_LENGTH
from data.merchant_dictionary import CANONICAL_MERCHANTS

logger = get_logger(__name__)

class FuzzyMatcher:
    @staticmethod
    def match(cleaned_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to fuzzy match the cleaned text against known canonical merchants.
        
        Args:
            cleaned_text: The cleaned, uppercased transaction string.
            
        Returns:
            Dict with match details if similarity >= threshold, None otherwise.
        """
        if not cleaned_text or len(cleaned_text) < FUZZY_MIN_LENGTH:
            return None
            
        # extractOne returns a tuple: (best_match_string, similarity_score, index)
        # Using token_sort_ratio because it's order-insensitive ("Amazon Prime" == "Prime Amazon")
        result = process.extractOne(
            cleaned_text.upper(), 
            [m.upper() for m in CANONICAL_MERCHANTS], 
            scorer=fuzz.token_sort_ratio
        )
        
        if result:
            best_match_upper, score, idx = result
            canonical_name = CANONICAL_MERCHANTS[idx]
            
            if score >= FUZZY_THRESHOLD:
                # Determine quality key based on score range
                if score >= 95:
                    quality_key = "fuzzy_95_100"
                elif score >= 90:
                    quality_key = "fuzzy_90_94"
                else:
                    quality_key = "fuzzy_85_89"
                    
                logger.debug(f"Fuzzy match: '{cleaned_text}' -> {canonical_name} (score: {score:.1f})")
                return {
                    "merchant": canonical_name,
                    "method": "Fuzzy",
                    "similarity_score": round(score, 1),
                    "matched_against": canonical_name,
                    "match_quality_key": quality_key
                }
                
        return None
