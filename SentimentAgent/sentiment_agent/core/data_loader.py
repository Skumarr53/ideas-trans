# sentiment_agent/core/data_loader.py

from pyspark.sql import SparkSession, DataFrame
import os


def load_from_snowflake(spark: SparkSession, sf_config: dict) -> DataFrame:
    required_keys = ["sfURL", "sfUser", "sfPassword", "sfDatabase", "sfSchema", "sfWarehouse", "dbtable"]
    for k in required_keys:
        if k not in sf_config:
            raise ValueError(f"Missing Snowflake config key: {k}")

    df = spark.read \
        .format("snowflake") \
        .options(**sf_config) \
        .load()

    return df


def load_from_csv(spark: SparkSession, csv_path: str) -> DataFrame:
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV path not found: {csv_path}")

    df = spark.read.option("header", True).csv(csv_path)
    return df


def validate_text_column(df: DataFrame, text_col: str) -> None:
    if text_col not in df.columns:
        raise ValueError(f"Specified text column '{text_col}' not found in input data.")
