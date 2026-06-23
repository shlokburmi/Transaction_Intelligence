"""
Tests for the Pipeline Orchestrator.
"""

from src.pipeline import Pipeline

def test_pipeline_dictionary_match():
    pipeline = Pipeline()
    result = pipeline.process_transaction("AMZN MKTP IN*2H4XK")
    
    assert result["Clean Merchant"] == "Amazon"
    assert result["Category"] == "Shopping"
    assert result["Method Used"] == "Dictionary"
    assert result["Confidence"] > 90
    assert "Matched alias" in result["Reason"]
    
def test_pipeline_cache_hit():
    pipeline = Pipeline()
    
    # First call
    res1 = pipeline.process_transaction("AMZN MKTP IN*2H4XK")
    assert res1["Method Used"] == "Dictionary"
    
    # Second call with same cleaned string (different noise)
    res2 = pipeline.process_transaction("AMZN MKTP US*8888")
    assert res2["Clean Merchant"] == "Amazon"
    assert "Cached" in res2["Method Used"]
    assert "Cache hit" in res2["Reason"]
    
def test_pipeline_empty_fallback():
    pipeline = Pipeline()
    result = pipeline.process_transaction("***")
    
    assert result["Clean Merchant"] == "Unknown"
    assert result["Category"] == "Other"
    assert result["Method Used"] == "Fallback"
