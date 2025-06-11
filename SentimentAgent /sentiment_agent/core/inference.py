# sentiment_agent/core/inference.py

from typing import List
from pyspark.sql import SparkSession, DataFrame
from sentiment_agent.models.registry import get_model
import pandas as pd
from sentiment_agent.utils.logger import get_logger

logger = get_logger(__name__)

def run_inference(
    spark: SparkSession,
    df: DataFrame,
    text_col: str,
    model_type: str,
    model_config: dict
) -> DataFrame:
    """
    Orchestrates model loading and inference.
    Returns a Spark DataFrame with sentiment scores.
    """
    if text_col not in df.columns:
        raise ValueError(f"Column '{text_col}' not found in DataFrame. Available columns: {df.columns}")

    logger.info("Converting input Spark DataFrame to Pandas...")
    pdf = df.select(text_col).toPandas()

    if pdf.empty:
        raise ValueError("Input DataFrame is empty. Please check data source or filters.")

    logger.info(f"Running batch inference on {len(pdf)} rows using model: {model_type}")
    texts = pdf[text_col].astype(str).tolist()
    model = get_model(model_type, model_config)
    model.load()
    scores = model.predict(texts)

    logger.info("Inference complete. Formatting output DataFrame...")
    score_df = pd.DataFrame(scores)
    final_df = pd.concat([pdf, score_df], axis=1)
    return spark.createDataFrame(final_df)
