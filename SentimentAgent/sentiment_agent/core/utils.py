# sentiment_agent/core/utils.py

import logging
from datetime import datetime
import os
from pyspark.sql import SparkSession

logger = logging.getLogger("sentiment-agent")
logger.setLevel(logging.INFO)


def setup_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


def create_spark_session(app_name: str = "SentimentAnalysisAgent") -> SparkSession:
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.execution.arrow.enabled", "true") \
        .getOrCreate()


def validate_path(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")


def suggest_resolution(error: Exception) -> str:
    message = str(error).lower()
    if "text column" in message:
        return "Ensure the input data has the correct column for text."
    if "snowflake config" in message:
        return "Please review your Snowflake configuration."
    if "csv path" in message:
        return "Make sure the uploaded file path is correct and accessible."
    return "Please check your input or configuration and try again."


def get_timestamped_filename(base: str, ext: str = "csv") -> str:
    return f"{base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
