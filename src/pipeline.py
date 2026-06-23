"""
Reward360 Transaction Intelligence Engine — Pipeline Orchestrator

The main engine that ties all tiers together.
Processes a batch of transactions, applies the 4-tier resolution strategy,
handles caching, computes confidence, tracks timing, and generates summaries.
"""

import time
import pandas as pd
from typing import Dict, Any, List

from src.logger import get_logger
from src.preprocessor import Preprocessor
from src.dictionary_matcher import DictionaryMatcher
from src.regex_matcher import RegexMatcher
from src.fuzzy_matcher import FuzzyMatcher
from src.llm_client import LLMClient
from src.category_mapper import CategoryMapper
from src.confidence_scorer import ConfidenceScorer

logger = get_logger(__name__)

class Pipeline:
    def __init__(self):
        self.llm_client = LLMClient()
        # Cache keyed by 'cleaned' text -> Result Dict
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Tracking for summary statistics
        self.stats = {
            "total": 0,
            "Dictionary": 0,
            "Regex": 0,
            "Fuzzy": 0,
            "LLM": 0,
            "Fallback": 0,
            "LLM_Calls_Made": 0,
            "LLM_Calls_Saved": 0,
            "times": {
                "Dictionary": [],
                "Regex": [],
                "Fuzzy": [],
                "LLM": [],
                "Fallback": [],
                "Total": 0.0
            }
        }

    def process_transaction(self, raw_text: str) -> Dict[str, Any]:
        """
        Process a single transaction through the 4-tier pipeline.
        """
        start_time = time.perf_counter()
        self.stats["total"] += 1
        
        # ---------------------------------------------------------
        # Preprocess
        # ---------------------------------------------------------
        text_versions = Preprocessor.process(raw_text)
        cleaned = text_versions["cleaned"]
        normalized = text_versions["normalized"]
        
        # Early exit for empty strings
        if not cleaned:
            return self._finalize_result(
                start_time, raw_text, "Unknown", "Other", "Fallback", 0, 
                "Empty or pure noise transaction"
            )

        # ---------------------------------------------------------
        # Cache Check
        # ---------------------------------------------------------
        if cleaned in self._cache:
            cached_result = self._cache[cleaned]
            self.stats["LLM_Calls_Saved"] += 1
            return self._finalize_result(
                start_time, raw_text, 
                cached_result["merchant"], cached_result["category"], 
                f"{cached_result['method']} (Cached)", cached_result["confidence"],
                f"Cache hit: reused previous resolution (originally via {cached_result['method']})"
            )

        # ---------------------------------------------------------
        # Resolution Tiers
        # ---------------------------------------------------------
        result = None
        
        # Tier 1: Dictionary
        if not result:
            result = DictionaryMatcher.match(cleaned)
            if result:
                reason = f"Matched alias '{result['matched_alias']}' via dictionary {result['match_type']} match"
                result["reason"] = reason

        # Tier 2: Regex
        if not result:
            result = RegexMatcher.match(normalized)
            if result:
                reason = f"Matched {result['pattern_name']} regex pattern"
                result["reason"] = reason

        # Tier 3: Fuzzy
        if not result:
            result = FuzzyMatcher.match(cleaned)
            if result:
                reason = f"Fuzzy matched to '{result['merchant']}' (similarity: {result['similarity_score']}%)"
                result["reason"] = reason

        # Tier 4: LLM
        if not result:
            self.stats["LLM_Calls_Made"] += 1
            result = self.llm_client.extract_merchant(normalized)
            if result:
                reason = f"Tiers 1-3 failed. LLM identified as '{result['merchant']}'"
                result["reason"] = reason

        # Fallback
        if not result:
            return self._finalize_result(
                start_time, raw_text, "Unknown", "Other", "Fallback", 
                ConfidenceScorer.calculate("Fallback"), 
                "All tiers failed to resolve merchant"
            )

        # ---------------------------------------------------------
        # Category Resolution & Confidence Scoring
        # ---------------------------------------------------------
        merchant = result["merchant"]
        method = result["method"]
        reason = result["reason"]
        match_quality_key = result.get("match_quality_key", "")
        
        validation_factors = []
        
        # Look up category
        category = CategoryMapper.get_category(merchant)
        
        if category:
            validation_factors.append("category_from_db")
        elif merchant != "Unknown":
            # Call LLM for category only
            self.stats["LLM_Calls_Made"] += 1
            category_from_llm = self.llm_client.get_category_only(merchant)
            if category_from_llm:
                category = category_from_llm
                validation_factors.append("category_from_llm")
                reason += f". Category '{category}' from LLM."
            else:
                category = "Other"
                reason += ". LLM failed to assign category."
        else:
            category = "Other"
            
        # Add clean name validation bonus if applicable
        if merchant != "Unknown":
            validation_factors.append("merchant_name_clean")
            
        # Update match quality if LLM matched a known merchant
        if method == "LLM":
            if CategoryMapper.get_category(merchant):
                match_quality_key = "llm_known_merchant"
                
        confidence = ConfidenceScorer.calculate(method, match_quality_key, validation_factors)
        
        # Update cache (only cache valid non-fallback results)
        if merchant != "Unknown":
            self._cache[cleaned] = {
                "merchant": merchant,
                "category": category,
                "confidence": confidence,
                "method": method
            }

        return self._finalize_result(
            start_time, raw_text, merchant, category, method, confidence, reason
        )

    def _finalize_result(self, start_time: float, raw_text: str, merchant: str, 
                         category: str, method: str, confidence: int, reason: str) -> Dict[str, Any]:
        """Format the final output row and update statistics."""
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Update stats
        base_method = method.replace(" (Cached)", "")
        if base_method in self.stats:
            self.stats[base_method] += 1
            self.stats["times"][base_method].append(elapsed_ms)
        self.stats["times"]["Total"] += elapsed_ms

        logger.info(f"[{method}] {raw_text[:30]}... -> {merchant} | {category} | {confidence}%")
        
        return {
            "Raw Transaction": raw_text,
            "Clean Merchant": merchant,
            "Category": category,
            "Confidence": confidence,
            "Method Used": method,
            "Reason": reason,
            "Processing Time (ms)": round(elapsed_ms, 1)
        }

    def process_batch(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Process a DataFrame of transactions."""
        logger.info(f"Starting batch processing of {len(df)} transactions")
        
        results = []
        for text in df[text_column]:
            results.append(self.process_transaction(str(text)))
            
        return pd.DataFrame(results)

    def print_summary(self):
        """Print the execution summary to console and log."""
        total = self.stats["total"]
        if total == 0:
            return
            
        def pct(count):
            return (count / total) * 100 if total > 0 else 0
            
        def avg_time(method):
            times = self.stats["times"][method]
            return sum(times) / len(times) if times else 0
            
        summary = f"""
===========================================================
  TRANSACTION INTELLIGENCE ENGINE — Execution Summary
===========================================================

  Transactions Processed :  {total}
  ---------------------------------------------------------
  Dictionary Matches     :  {self.stats['Dictionary']:2d}  ({pct(self.stats['Dictionary']):5.1f}%)
  Regex Matches          :  {self.stats['Regex']:2d}  ({pct(self.stats['Regex']):5.1f}%)
  Fuzzy Matches          :  {self.stats['Fuzzy']:2d}  ({pct(self.stats['Fuzzy']):5.1f}%)
  LLM Matches            :  {self.stats['LLM']:2d}  ({pct(self.stats['LLM']):5.1f}%)
  Unresolved (Fallback)  :  {self.stats['Fallback']:2d}  ({pct(self.stats['Fallback']):5.1f}%)
  ---------------------------------------------------------
  LLM API Calls Made     :  {self.stats['LLM_Calls_Made']}
  LLM Calls Saved        :  {self.stats['LLM_Calls_Saved']}
  ---------------------------------------------------------
  Total Processing Time  :  {self.stats['times']['Total'] / 1000:.2f}s
  Avg Time (Dictionary)  :  {avg_time('Dictionary'):.2f}ms
  Avg Time (Regex)       :  {avg_time('Regex'):.2f}ms
  Avg Time (Fuzzy)       :  {avg_time('Fuzzy'):.2f}ms
  Avg Time (LLM)         :  {avg_time('LLM'):.2f}ms
===========================================================
"""
        print(summary)
        logger.info("Execution summary generated.")
        
        # Log to file line by line
        for line in summary.split("\n"):
            if line.strip():
                logger.debug(line)

    def process_single_transaction(self, raw_text: str) -> Dict[str, Any]:
        """Process a single raw transaction and return the resolved result."""
        return self.process_transaction(raw_text)

    def process_csv(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Process a batch of transactions from a DataFrame and return resolved results."""
        return self.process_batch(df, text_column)

    def get_dashboard_metrics(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Compute metrics for the KPI dashboard from a processed DataFrame or internal stats."""
        if df is None or df.empty:
            total = self.stats["total"]
            return {
                "total": total,
                "Dictionary": self.stats["Dictionary"],
                "Regex": self.stats["Regex"],
                "Fuzzy": self.stats["Fuzzy"],
                "LLM": self.stats["LLM"],
                "Fallback": self.stats["Fallback"],
                "Cache Hits": self.stats["LLM_Calls_Saved"],
                "avg_confidence": 0.0,
                "avg_processing_time": 0.0,
                "LLM_Calls_Made": self.stats["LLM_Calls_Made"],
                "LLM_Calls_Saved": self.stats["LLM_Calls_Saved"]
            }
        
        total = len(df)
        
        # Check cache hits in method name (e.g. "Dictionary (Cached)")
        cache_hits = df["Method Used"].apply(lambda x: "Cached" in str(x)).sum()
        
        # Strip " (Cached)" to find matching methods
        base_methods = df["Method Used"].apply(lambda x: str(x).replace(" (Cached)", ""))
        base_counts = base_methods.value_counts()
        
        dict_count = int(base_counts.get("Dictionary", 0))
        regex_count = int(base_counts.get("Regex", 0))
        fuzzy_count = int(base_counts.get("Fuzzy", 0))
        llm_count = int(base_counts.get("LLM", 0))
        fallback_count = int(base_counts.get("Fallback", 0))
        
        avg_conf = float(df["Confidence"].mean())
        avg_time = float(df["Processing Time (ms)"].mean()) if "Processing Time (ms)" in df.columns else 0.0
        
        return {
            "total": total,
            "Dictionary": dict_count,
            "Regex": regex_count,
            "Fuzzy": fuzzy_count,
            "LLM": llm_count,
            "Fallback": fallback_count,
            "Cache Hits": cache_hits,
            "avg_confidence": avg_conf,
            "avg_processing_time": avg_time,
            "LLM_Calls_Made": self.stats.get("LLM_Calls_Made", llm_count),
            "LLM_Calls_Saved": self.stats.get("LLM_Calls_Saved", cache_hits)
        }

    def get_execution_summary(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Get summary breakdown data for UI charts and footers."""
        metrics = self.get_dashboard_metrics(df)
        
        if df is None or df.empty:
            return {
                "methods": {
                    "Dictionary": self.stats["Dictionary"],
                    "Regex": self.stats["Regex"],
                    "Fuzzy": self.stats["Fuzzy"],
                    "LLM": self.stats["LLM"],
                    "Fallback": self.stats["Fallback"]
                },
                "categories": {},
                "confidences": []
            }
            
        methods_dist = {
            "Dictionary": metrics["Dictionary"],
            "Regex": metrics["Regex"],
            "Fuzzy": metrics["Fuzzy"],
            "LLM": metrics["LLM"],
            "Fallback": metrics["Fallback"]
        }
        
        categories_dist = df["Category"].value_counts().to_dict()
        confidences = df["Confidence"].tolist()
        
        return {
            "methods": methods_dist,
            "categories": categories_dist,
            "confidences": confidences
        }
