"""
extract.py -- Extract step of the HCES 2022-23 pipeline

Loads all 15 HCES level CSV files from a local folder, renames their columns
using hces_column_mapping.py, and returns/saves them as clean DataFrames.

Usage:
    python extract.py --data-dir "C:/path/to/your/CSV_data_HH_Cons_exp_22_23"

This expects hces_column_mapping.py to be in the same folder as this script
(or importable on your PYTHONPATH).
"""

import argparse
import logging
import os
import re
import sys

import pandas as pd

from hces_column_mapping import load_level, COLUMN_NAMES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def find_level_files(data_dir: str) -> dict:
    """
    Scan a folder and match files to HCES levels 1-15 based on filename.
    Handles naming variants like:
        LEVEL - 01(Section 1 and 1_1).csv
        LEVEL_01.csv
        hces22_lvl_01.csv
    Returns: {level_number: full_filepath}
    """
    level_files = {}
    pattern = re.compile(r"level[\s_-]*0?(\d{1,2})", re.IGNORECASE)

    for fname in os.listdir(data_dir):
        if not fname.lower().endswith((".csv", ".txt")):
            continue
        match = pattern.search(fname)
        if not match:
            logger.warning(f"Could not detect level number from filename: {fname} -- skipping")
            continue
        level_num = int(match.group(1))
        if level_num < 1 or level_num > 15:
            logger.warning(f"Detected out-of-range level {level_num} from filename: {fname} -- skipping")
            continue
        if level_num in level_files:
            logger.warning(
                f"Multiple files matched level {level_num}: "
                f"'{level_files[level_num]}' and '{fname}'. Keeping the first one found."
            )
            continue
        level_files[level_num] = os.path.join(data_dir, fname)

    return level_files


def extract_all_levels(data_dir: str) -> dict:
    """
    Load every detected level file into a clean, renamed DataFrame.
    Returns: {level_number: DataFrame}
    Levels that fail to load (missing file, column mismatch, etc.) are
    skipped with a logged warning rather than crashing the whole run.
    """
    level_files = find_level_files(data_dir)

    missing = sorted(set(range(1, 16)) - set(level_files.keys()))
    if missing:
        logger.warning(f"No file detected for levels: {missing}. Check your folder / filenames.")

    dataframes = {}
    for level in sorted(level_files.keys()):
        filepath = level_files[level]
        logger.info(f"Loading Level {level:02d} from {os.path.basename(filepath)} ...")
        try:
            df = load_level(level, filepath)
            dataframes[level] = df
            logger.info(f"  -> Level {level:02d}: {df.shape[0]:,} rows, {df.shape[1]} columns")
        except Exception as e:
            logger.error(f"  -> FAILED to load Level {level:02d}: {e}")

    return dataframes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract step: load HCES level CSVs.")
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Folder containing the 15 extracted HCES level CSV files",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.data_dir):
        logger.error(f"Folder not found: {args.data_dir}")
        sys.exit(1)

    logger.info(f"Scanning {args.data_dir} for HCES level files...")
    dfs = extract_all_levels(args.data_dir)

    logger.info(f"\nExtraction complete: {len(dfs)}/15 levels loaded successfully.")
    for level, df in sorted(dfs.items()):
        logger.info(f"  Level {level:02d}: {df.shape}")
