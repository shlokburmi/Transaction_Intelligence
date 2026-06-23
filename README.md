# Transaction Intelligence Engine

A 4-tier hybrid AI system that takes messy bank card transaction descriptions and outputs the clean merchant name, spending category, and a deterministic confidence score. 

**Core philosophy**: Rule-first, LLM-last. The system uses Dictionary, Regex, and Fuzzy matching to resolve 80%+ of transactions instantly and for free, only falling back to a Large Language Model for the unpredictable long tail.

## Features

- **4-Tier Pipeline**: Dictionary (Exact/Substring) → Regex → RapidFuzz → Groq LLM
- **Deterministic Confidence**: Scores are computed deterministically using configurable weights.
- **Explainability**: Every result includes a human-readable `reason` explaining why it was chosen.
- **Caching**: Results for the same unresolved merchant are cached to minimize LLM calls.
- **Robust Preprocessing**: Original transactions are preserved; clean and normalized variants are passed to specific tiers.
- **Fast**: C-extension fuzzy matching (RapidFuzz) and O(1) dictionary lookups keep average latency in the low milliseconds.

## Supported Usage Modes

There are two ways to run the project.

### Mode 1: Batch Processing (CLI)
Processes a batch of transactions from a CSV file. This mode is the primary production workflow.

```bash
python main.py
```
- Reads from: `data/transactions_input.csv`
- Writes to: `data/transactions_output.csv`
- Writes detailed logs to: `logs/pipeline.log`
- Prints an execution summary to the console.

### Mode 2: Interactive Demo (Streamlit)
Provides a web-based UI for live demonstration and ad-hoc processing.

```bash
streamlit run app.py
```

## Setup & Installation

### 1. Requirements
- Python 3.9+
- A [Groq API Key](https://console.groq.com) (Free tier is fully supported)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and insert your Groq API key:
```bash
cp .env.example .env
```
Open `.env` and set:
`GROQ_API_KEY=your_key_here`

## Configuration

All tunable parameters live in `src/config.py`. You can adjust:
- Confidence weights and bonus scoring rules
- RapidFuzz similarity thresholds (`FUZZY_THRESHOLD`)
- The target LLM model (`GROQ_MODEL`)
- Valid spending categories
- Prompt templates

## Logging and Prompt History

The system uses Python's built-in `logging` module. 
- Console output shows high-level progress and the execution summary.
- The `logs/pipeline.log` file captures `DEBUG` level traces, including the exact prompts sent to the LLM and its raw JSON responses.

## Testing

The engine includes a comprehensive unit test suite covering all modules.
```bash
pytest tests/ -v
```
