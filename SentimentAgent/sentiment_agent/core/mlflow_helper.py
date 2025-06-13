# sentiment_agent/core/mlflow_helper.py

import mlflow
from datetime import datetime
import os
from sentiment_agent.utils.logger import get_logger

logger = get_logger(__name__)


def get_run_name(project: str, model_type: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{project}-{model_type}-{date_str}"


def start_run(project: str, model_type: str):
    run_name = get_run_name(project, model_type)
    logger.info(f"Starting MLflow run: {run_name}")
    return mlflow.start_run(run_name=run_name)


def log_params(params: dict):
    logger.info("Logging parameters to MLflow...")
    for key, val in params.items():
        mlflow.log_param(key, val)


def log_model(model, artifact_path: str, project: str, model_type: str):
    logger.info("Logging model to MLflow...")
    try:
        mlflow.log_artifacts(local_dir=artifact_path)
        mlflow.pyfunc.log_model(
            artifact_path=model_type,
            python_model=model,
            registered_model_name=f"{project}_{model_type}"
        )
        logger.info("Model logged and registered successfully.")
    except Exception as e:
        logger.error("Failed to log model to MLflow", exc_info=True)
        raise


def get_latest_model_uri(project: str, model_type: str) -> str:
    name = f"{project}_{model_type}"
    client = mlflow.tracking.MlflowClient()
    try:
        versions = client.get_latest_versions(name, stages=["Staging", "Production"])
        if not versions:
            raise Exception("No registered versions found.")
        logger.info(f"Latest registered model URI found: {versions[0].source}")
        return versions[0].source
    except Exception as e:
        logger.error(f"Failed to retrieve model from registry: {name}", exc_info=True)
        raise RuntimeError(f"Failed to load registered model '{name}': {e}")
