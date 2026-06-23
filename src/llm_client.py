"""
Reward360 Transaction Intelligence Engine — Tier 4: LLM Client

Wrapper around the Groq API. Handles both merchant extraction (when Tiers 1-3 fail)
and category-only resolution (when merchant is known but not in category DB).
Includes built-in validation for the LLM responses.
"""

import json
import re
import time
from typing import Optional, Dict, Any, Tuple
from groq import Groq, APIError, APITimeoutError, RateLimitError
from src.logger import get_logger
from src.config import (
    GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, 
    LLM_MAX_TOKENS, LLM_MAX_RETRIES, LLM_RETRY_BACKOFF,
    VALID_CATEGORIES, MERCHANT_EXTRACTION_PROMPT, 
    MERCHANT_EXTRACTION_EXAMPLES, CATEGORY_ONLY_PROMPT
)

logger = get_logger(__name__)

class LLMClient:
    def __init__(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. LLM fallback will fail.")
        self.client = Groq(api_key=GROQ_API_KEY)

    def extract_merchant(self, normalized_text: str) -> Optional[Dict[str, Any]]:
        """
        Tier 4 fallback: Ask LLM to extract the merchant from the transaction.
        """
        if not GROQ_API_KEY:
            return None

        system_prompt = f"{MERCHANT_EXTRACTION_PROMPT}\n\n{MERCHANT_EXTRACTION_EXAMPLES}"
        user_prompt = f'Transaction: "{normalized_text}"'
        
        response_data = self._call_llm_with_retry(system_prompt, user_prompt)
        if not response_data:
            return None
            
        # Parse JSON
        parsed_json = self._parse_json_response(response_data)
        if not parsed_json or "merchant" not in parsed_json:
            return None
            
        merchant = parsed_json["merchant"].strip()
        
        # Validation
        validated_merchant = self._validate_merchant(merchant, normalized_text)
        if not validated_merchant:
            return None
            
        # We don't know if the LLM merchant is in our known list yet, the pipeline will decide
        # the quality key later.
        return {
            "merchant": validated_merchant,
            "method": "LLM",
            "match_quality_key": "llm_unknown_merchant" # Pipeline updates this if known
        }

    def get_category_only(self, merchant_name: str) -> Optional[str]:
        """
        Ask LLM to classify a known merchant into a category.
        """
        if not GROQ_API_KEY:
            return None
            
        user_prompt = f'Merchant: "{merchant_name}"'
        
        response_data = self._call_llm_with_retry(CATEGORY_ONLY_PROMPT, user_prompt)
        if not response_data:
            return None
            
        parsed_json = self._parse_json_response(response_data)
        if not parsed_json or "category" not in parsed_json:
            return None
            
        category = parsed_json["category"].strip()
        return self._validate_category(category)

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------
    
    def _call_llm_with_retry(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Calls Groq API with exponential backoff on failure."""
        retries = 0
        while retries <= LLM_MAX_RETRIES:
            try:
                logger.debug(f"LLM Request: {user_prompt}")
                completion = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=LLM_TEMPERATURE,
                    max_tokens=LLM_MAX_TOKENS,
                    response_format={"type": "json_object"}
                )
                
                content = completion.choices[0].message.content
                logger.debug(f"LLM Response: {content}")
                return content
                
            except (RateLimitError, APITimeoutError) as e:
                retries += 1
                if retries > LLM_MAX_RETRIES:
                    logger.error(f"LLM API failed after {LLM_MAX_RETRIES} retries: {e}")
                    return None
                wait_time = LLM_RETRY_BACKOFF * (2 ** (retries - 1))
                logger.warning(f"LLM API rate limit/timeout. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                
            except APIError as e:
                logger.error(f"LLM API generic error: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected LLM error: {e}")
                return None

        return None

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Safely parse JSON, handling potential markdown blocks from the LLM."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            logger.warning(f"Failed to parse JSON from LLM response: {text}")
            return None

    def _validate_merchant(self, merchant: str, raw_input: str) -> Optional[str]:
        """Validates the extracted merchant name."""
        if not merchant or merchant.lower() in ["unknown", "null", "none"]:
            return None
            
        if len(merchant) > 50:
            logger.warning(f"LLM returned merchant name too long (>50): '{merchant}'")
            return None
            
        # Reject if it's a full sentence
        if "." in merchant and len(merchant.split()) > 5:
            logger.warning(f"LLM returned a sentence instead of name: '{merchant}'")
            return None
            
        # Reject if it's exactly the raw input (echo hallucination)
        if merchant.upper() == raw_input.upper():
            logger.warning("LLM echoed the raw input exactly. Rejecting.")
            return None
            
        return merchant.title()

    def _validate_category(self, category: str) -> Optional[str]:
        """Validates the category string."""
        # Simple case-insensitive match
        for valid_cat in VALID_CATEGORIES:
            if category.lower() == valid_cat.lower():
                return valid_cat
                
        logger.warning(f"LLM returned invalid category '{category}', defaulting to Other.")
        return "Other"
