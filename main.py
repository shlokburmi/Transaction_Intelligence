"""
Reward360 Transaction Intelligence Engine — CLI Entry Point

Usage:
    python main.py
    
Reads from data/transactions_input.csv, processes through the pipeline,
writes to data/transactions_output.csv, and prints a summary.
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.config import INPUT_CSV, OUTPUT_CSV
from src.pipeline import Pipeline
from src.logger import get_logger

logger = get_logger("main")

def main():
    logger.info("Starting Transaction Intelligence Engine")
    
    # 1. Load Data
    try:
        df = pd.read_csv(INPUT_CSV)
        logger.info(f"Loaded {len(df)} transactions from {INPUT_CSV}")
    except FileNotFoundError:
        logger.error(f"Input file not found: {INPUT_CSV}")
        print(f"Error: Could not find input file at {INPUT_CSV}")
        return
        
    # Find the transaction column (assumes 'transaction_description' or first column)
    text_column = "transaction_description"
    if text_column not in df.columns:
        text_column = df.columns[0]
        logger.info(f"Column '{text_column}' selected as input")

    # 2. Process
    pipeline = Pipeline()
    results_df = pipeline.process_batch(df, text_column)
    
    # 3. Output
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)
    logger.info(f"Results saved to {OUTPUT_CSV}")
    
    # 4. Summary
    pipeline.print_summary()

if __name__ == "__main__":
    main()
