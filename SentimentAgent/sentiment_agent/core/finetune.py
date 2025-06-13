# sentiment_agent/core/finetune.py

import mlflow
import os
from datetime import datetime
from sentiment_agent.models.registry import get_model
from sentiment_agent.core.mlflow_helper import start_run, log_params, log_model
from sentiment_agent.utils.logger import get_logger

logger = get_logger(__name__)

def run_finetuning(
    csv_path: str,
    model_type: str,
    project: str,
    model_config: dict
) -> str:
    """
    Loads a model, fine-tunes it on labeled CSV data, and logs via MLflow.
    Returns: MLflow run ID or registered model version URI.
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Training CSV not found: {csv_path}")

    logger.info(f"Starting fine-tuning for model: {model_type}, project: {project}")
    model = get_model(model_type, model_config)
    model.load()

    with start_run(project, model_type):
        params = {
            "data_path": csv_path,
            "model_type": model_type,
            "project": project,
            "timestamp": datetime.now().isoformat(),
        }
        log_params(params)

        if hasattr(model, "finetune"):
            try:
                version = model.finetune(csv_path=csv_path, project_name=project)
                log_model(model, artifact_path="model_artifacts", project=project, model_type=model_type)
                logger.info(f"Fine-tuning complete. Model version: {version}")
                return version
            except NotImplementedError as nie:
                logger.warning(str(nie))
                raise
            except Exception as e:
                logger.error("An error occurred during fine-tuning.", exc_info=True)
                raise
        else:
            raise NotImplementedError(f"Model type '{model_type}' does not support fine-tuning.")
