"""
Reward360 Transaction Intelligence Engine — Configuration

Single source of truth for all constants, thresholds, weights, file paths,
and prompt templates. Every tunable parameter lives here so that business
logic modules never hardcode values.

Usage:
    from src.config import (
        GROQ_API_KEY, GROQ_MODEL, VALID_CATEGORIES,
        CONFIDENCE_BASE_SCORES, MATCH_QUALITY_WEIGHTS, ...
    )
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Project root is the parent of the src/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

INPUT_CSV = DATA_DIR / "transactions_input.csv"
OUTPUT_CSV = DATA_DIR / "transactions_output.csv"
LOG_FILE = LOGS_DIR / "pipeline.log"

# ---------------------------------------------------------------------------
# Groq LLM Settings
# ---------------------------------------------------------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0        # Deterministic output
LLM_MAX_TOKENS = 150       # Merchant + category JSON is < 50 tokens
LLM_MAX_RETRIES = 2        # Retry twice on failure, then fallback
LLM_RETRY_BACKOFF = 1.0    # Base backoff in seconds (doubles each retry)

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
VALID_CATEGORIES = [
    "Shopping",
    "Dining",
    "Travel",
    "Fuel",
    "Groceries",
    "Utilities",
    "Entertainment",
    "Other",
]

# ---------------------------------------------------------------------------
# RapidFuzz Settings
# ---------------------------------------------------------------------------
FUZZY_THRESHOLD = 85        # Minimum similarity score (0-100) to accept a match
FUZZY_MIN_LENGTH = 4        # Skip fuzzy matching for cleaned text shorter than this

# ---------------------------------------------------------------------------
# Confidence Scoring — Configurable Weights
#
# Confidence = base_score + match_quality + validation_bonus
# Capped at MAX_CONFIDENCE. All values are integers (percentages).
#
# To tune: change values here. confidence_scorer.py reads these dicts
# and never hardcodes any numbers.
# ---------------------------------------------------------------------------

MAX_CONFIDENCE = 99

# Base score awarded by the resolution method alone
CONFIDENCE_BASE_SCORES = {
    "Dictionary":   90,
    "Regex":        82,
    "Fuzzy":        70,
    "LLM":          55,
    "Fallback":     25,
}

# Additional score based on match quality within a method
MATCH_QUALITY_WEIGHTS = {
    # Dictionary
    "exact":            9,      # Full exact match
    "substring_long":   7,      # Matched a long alias (>= 6 chars)
    "substring_short":  4,      # Matched a short alias (< 6 chars)
    # Regex
    "regex_specific":   8,      # Merchant-specific pattern matched
    "regex_structural": 3,      # Generic structural pattern matched
    # Fuzzy
    "fuzzy_95_100":     10,     # Similarity 95-100%
    "fuzzy_90_94":      7,      # Similarity 90-94%
    "fuzzy_85_89":      5,      # Similarity 85-89%
    # LLM
    "llm_known_merchant":   10, # LLM returned a merchant we recognize
    "llm_unknown_merchant": 3,  # LLM returned a merchant not in our dictionary
}

# Bonus for validation factors
VALIDATION_WEIGHTS = {
    "category_from_db":     3,  # Category resolved from our mapping (deterministic)
    "category_from_llm":    1,  # Category resolved by LLM
    "merchant_name_clean":  2,  # Merchant name passes all validation checks
}

# ---------------------------------------------------------------------------
# LLM Prompt Templates
# ---------------------------------------------------------------------------

MERCHANT_EXTRACTION_PROMPT = """You are a financial transaction classifier for an Indian bank.
Given a raw bank card transaction description, extract the clean merchant name.

Rules:
- Respond ONLY in valid JSON: {{"merchant": "..."}}
- Use proper Title Case for the merchant name
- If you cannot confidently identify the merchant, set merchant to "Unknown"
- Do NOT invent or guess merchant names — if unsure, say "Unknown"
- Do NOT include location, store numbers, or transaction IDs in the merchant name"""

MERCHANT_EXTRACTION_EXAMPLES = """Examples:
"AMZN MKTP IN*2H4XK" → {{"merchant": "Amazon"}}
"SQ *BLUE TOKAI COF" → {{"merchant": "Blue Tokai Coffee"}}
"UBER *EATS HELP.UBER.COM" → {{"merchant": "Uber Eats"}}
"SWIGGY ORDER 12345 BLR" → {{"merchant": "Swiggy"}}
"POS 12345678 BANGALORE" → {{"merchant": "Unknown"}}"""

CATEGORY_ONLY_PROMPT = """You are a financial transaction classifier.
Given a merchant name, classify it into exactly one spending category.

Valid categories: Shopping, Dining, Travel, Fuel, Groceries, Utilities, Entertainment, Other

Rules:
- Respond ONLY in valid JSON: {{"category": "..."}}
- Choose the single most appropriate category
- If unsure, use "Other"
"""
