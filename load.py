"""
load.py -- Load step of the HCES 2022-23 pipeline

Pushes cleaned, analysis-ready tables into MySQL using SQLAlchemy.

Usage (from your notebook):
    from load import get_engine, load_table

    engine = get_engine(
        host="localhost",
        port=3306,
        user="root",
        password="your_password_here",
        database="hces_2022_23",
    )

    load_table(household_master, "household_master", engine)
    load_table(merged, "household_category_spend", engine)   # long-format, one row per (household, category)
    load_table(table.reset_index(), "category_share_by_quintile", engine)  # the pivoted summary table

Then query directly from MySQL Workbench, or from Power BI's MySQL connector.
"""

import logging

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def get_engine(host: str, port: int, user: str, password: str, database: str):
    """
    Build a SQLAlchemy engine for a MySQL database.

    NOTE: for a portfolio project, it's fine to put your password directly
    in the notebook. If you ever share this notebook (e.g. on GitHub), 
    remove the password first, or better, load it from an environment
    variable instead:
        import os
        password = os.environ["MYSQL_PASSWORD"]
    """
    from urllib.parse import quote_plus

    # URL-encode the password: special characters like @, :, / etc. in a
    # raw password will otherwise be misread as part of the connection
    # string's structure (e.g. a password containing '@' gets confused
    # with the '@' that separates credentials from the host).
    encoded_password = quote_plus(password)
    connection_string = f"mysql+mysqlconnector://{user}:{encoded_password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    return engine


def load_table(df: pd.DataFrame, table_name: str, engine, if_exists: str = "replace", chunksize: int = 5000) -> None:
    """
    Push a DataFrame into MySQL as a table.

    if_exists: 'replace' (drop and recreate -- use while you're iterating),
    or 'append' (add rows to an existing table -- use once your schema is
    stable and you're adding new data, not rebuilding).

    chunksize batches the insert so large tables (e.g. household-level data
    with 260k+ rows) don't time out or blow up memory in one giant INSERT.
    """
    logger.info(f"Loading {len(df):,} rows into table '{table_name}' (if_exists='{if_exists}')...")
    df.to_sql(table_name, engine, if_exists=if_exists, index=False, chunksize=chunksize)
    logger.info(f"  -> Done: '{table_name}' now has {len(df):,} rows.")


def load_all(household_master: pd.DataFrame, category_merged: pd.DataFrame, category_share: pd.DataFrame, engine) -> None:
    """
    Convenience function: load the three core output tables of this project
    in one call.
        household_master : one row per household (mpce, quintile, weight, etc.)
        category_merged   : long format, one row per (household, category)
        category_share    : the pivoted quintile x category summary table
    """
    load_table(household_master, "household_master", engine)
    load_table(category_merged, "household_category_spend", engine)
    load_table(category_share.reset_index() if hasattr(category_share.index, "names") and category_share.index.names[0] else category_share,
               "category_share_by_quintile", engine)


if __name__ == "__main__":
    print("This module is meant to be imported, e.g.:")
    print("  from load import get_engine, load_table, load_all")
