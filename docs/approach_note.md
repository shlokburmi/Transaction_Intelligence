# Approach Note: Reward360 Transaction Intelligence

*Date: June 2026*

This document outlines the engineering trade-offs, limitations, and future scalability considerations for the Transaction Intelligence Engine Proof of Concept.

## 1. Core Architecture Decisions

### Why a 4-Tier Pipeline?
Parsing messy bank data is a long-tail problem. The 80/20 rule applies: 80% of transactions come from 20% of merchants.
- **Dictionary & Regex** handle the high-volume head of the curve deterministically and instantly.
- **RapidFuzz (Fuzzy Matching)** handles misspellings and truncated IDs that bypass strict rules, catching another 5-10% of variations without network calls.
- **Groq LLM** acts as the safety net for the unpredictable long tail.

### Why not pure LLM?
Passing 10 million daily transactions to an LLM would cost thousands of dollars and take hours. Our approach reduces LLM calls by >90% while retaining the adaptability of AI.

### Why separate Merchant and Category resolution?
An early iteration considered asking the LLM for both `merchant` and `category` in one prompt. This was rejected because it introduces non-determinism. By separating the steps, we ensure that if the merchant is identified (even by the LLM) and exists in our known `category_mapping`, the category assignment is 100% deterministic and instantaneous.

### Confidence Scoring
Confidence scores are composite rather than monolithic. A dictionary match isn't just "99%". It is evaluated based on whether it was an exact match or a substring match, combined with validation bonuses. Because weights are configurable via `config.py`, the business logic code remains clean.

## 2. Trade-offs Made for the PoC

| Trade-off | Rationale |
|---|---|
| **In-Memory Cache vs. Redis** | A Python dictionary is sufficient for processing 55-500 rows in a single batch. Redis would add infrastructure complexity unnecessary for a 3-day PoC. |
| **Dictionary size** | The dictionary currently contains ~100 aliases. A production system requires tens of thousands. The PoC proves the matching logic, not the exhaustive completeness of the data. |
| **Synchronous Processing** | `pipeline.py` processes rows sequentially. For large files, async LLM calls or batched prompts would drastically improve throughput. |
| **No Database** | Mappings are stored in Python files (`.py`) instead of SQLite. This allows for type hinting and fast iteration without ORM overhead. |

## 3. Known Limitations

1. **New Merchant Cold Start**: When an entirely new merchant appears, it relies on the LLM. If the LLM successfully identifies it, the category must still be guessed by the LLM (Prompt B). This isn't persisted beyond the run.
2. **Aggressive Prefixing**: The Regex prefix stripper assumes `SQ *` means Square. If a valid merchant name starts with exactly that sequence, it could be incorrectly truncated.
3. **Short Aliases**: Extremely short aliases (e.g., `HP`) can cause false positives if they appear as substrings in other words. We mitigate this with boundary checks and match quality penalties.

## 4. Future Production Improvements

If this PoC were taken to production, the following architecture upgrades would be recommended:

1. **The Learning Loop**: The most critical missing feature. When the LLM confidently resolves a merchant that isn't in the database, the system should queue it for human review. Once approved, it is injected into the Dictionary DB, permanently removing the need to ask the LLM about that merchant again.
2. **MCC Code Integration**: Bank transactions often include Visa/Mastercard Merchant Category Codes (MCC). This is a strong signal for category mapping that should be used before asking the LLM.
3. **Batched LLM Prompts**: Instead of firing one API call per unresolved transaction, bundle 20 unresolved transactions into a single LLM prompt to reduce API round-trip latency.
4. **Vector Database / Semantic Search**: For the middle tier, instead of just RapidFuzz, a lightweight local embedding model could perform semantic matching against known merchants.
