"""
Reward360 Transaction Intelligence Engine — Confidence Scorer

Calculates a deterministic confidence score (0-99%) based on the resolution
method, match quality, and validation bonuses.

Weights are imported from config to separate tuning from logic.
"""

from typing import List
from src.config import CONFIDENCE_BASE_SCORES, MATCH_QUALITY_WEIGHTS, VALIDATION_WEIGHTS, MAX_CONFIDENCE
from src.logger import get_logger

logger = get_logger(__name__)

class ConfidenceScorer:
    @staticmethod
    def calculate(method: str, match_quality_key: str = "", validation_factors: List[str] = None) -> int:
        """
        Calculate composite confidence score.
        
        Args:
            method: Base resolution method ("Dictionary", "Regex", "Fuzzy", "LLM", "Fallback")
            match_quality_key: Key for quality adjustment (e.g., "exact", "regex_specific")
            validation_factors: List of validation keys (e.g., ["category_from_db"])
            
        Returns:
            Integer confidence score between 0 and 99.
        """
        if validation_factors is None:
            validation_factors = []
            
        # 1. Base Score
        base = CONFIDENCE_BASE_SCORES.get(method, 0)
        
        # 2. Match Quality Adjustment
        quality = MATCH_QUALITY_WEIGHTS.get(match_quality_key, 0)
        
        # 3. Validation Bonus
        validation = sum(VALIDATION_WEIGHTS.get(f, 0) for f in validation_factors)
        
        # Calculate and cap
        total = base + quality + validation
        final_score = min(MAX_CONFIDENCE, max(0, total))
        
        logger.debug(f"Confidence calculation: method={method}({base}) + "
                     f"quality={match_quality_key}({quality}) + "
                     f"validation={validation_factors}({validation}) = {final_score}%")
                     
        return final_score
