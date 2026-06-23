"""
Reward360 Transaction Intelligence Engine — Preprocessor

Normalizes raw transaction strings and produces three versions:
  1. original: untouched
  2. normalized: uppercased, trimmed, multiple spaces collapsed
  3. cleaned: noise stripped (prefixes, trailing IDs, location codes)
"""

import re
from typing import Dict, Any
from src.logger import get_logger
from data.regex_patterns import PROCESSOR_PREFIX_PATTERN, SUFFIX_PATTERN

logger = get_logger(__name__)

class Preprocessor:
    @staticmethod
    def process(raw_text: str) -> Dict[str, str]:
        """
        Process a raw transaction string into 3 standardized forms.
        
        Args:
            raw_text: The raw transaction description from the bank.
            
        Returns:
            Dict containing:
            - "original": The exact input
            - "normalized": Uppercased, trimmed, spaces collapsed
            - "cleaned": Normalized text with prefixes, suffixes, and noise stripped
        """
        # Handle null/empty inputs
        if raw_text is None or not str(raw_text).strip():
            logger.debug("Received empty or null transaction.")
            return {
                "original": str(raw_text) if raw_text is not None else "",
                "normalized": "",
                "cleaned": ""
            }
            
        # Ensure string type
        original = str(raw_text)
        
        # ---------------------------------------------------------
        # Stage 2: Normalize
        # ---------------------------------------------------------
        normalized = original.upper().strip()
        # Collapse multiple whitespace characters into a single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # ---------------------------------------------------------
        # Stage 3: Clean
        # ---------------------------------------------------------
        cleaned = normalized
        
        # 1. Strip known payment processor prefixes (e.g., "SQ *")
        cleaned = PROCESSOR_PREFIX_PATTERN.sub("", cleaned)
        
        # 2. Strip known suffixes (locations, numeric IDs like *2H4XK)
        cleaned = SUFFIX_PATTERN.sub("", cleaned)
        
        # 3. Remove standalone special characters (but keep internal ones like H&M)
        # This replaces things like " - " or " * " with a space
        cleaned = re.sub(r'\s+[-*/#_]+\s+', ' ', cleaned)
        
        # 4. Remove standalone pure numbers, optionally preceded by # or * (e.g., " 0045 ", " #1293 ")
        cleaned = re.sub(r'(?:\s|^)[#*]?\d+(?:\s|$)', ' ', cleaned)
        
        # Final cleanup pass
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # If the aggressive cleaning wiped out everything or left only special chars
        # fall back to the normalized string.
        if not cleaned or not re.search(r'[A-Z0-9]', cleaned):
            logger.debug(f"Cleaning wiped string '{normalized}', falling back to normalized.")
            cleaned = normalized

        logger.debug(f"Preprocessed: '{original}' -> norm:'{normalized}' -> clean:'{cleaned}'")
        
        return {
            "original": original,
            "normalized": normalized,
            "cleaned": cleaned
        }
