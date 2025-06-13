# sentiment_agent/models/base.py

from abc import ABC, abstractmethod
from typing import List, Dict

class SentimentModel(ABC):
    """
    Abstract base class for all sentiment model implementations.
    Any new model (e.g., Gemma, NLI, etc.) must extend this class.
    """

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def load(self):
        """Loads the model and tokenizer."""
        pass

    @abstractmethod
    def predict(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Returns sentiment scores for each text.
        Output format: List of dictionaries with sentiment labels and scores.
        Example: [{"positive": 0.76, "neutral": 0.18, "negative": 0.06}, ...]
        """
        pass

    def finetune(self, csv_path: str, project_name: str = None) -> str:
        """
        Optional: Fine-tunes the model using a labeled dataset.
        Returns MLflow run ID or model version string.
        Override in subclasses if fine-tuning is supported.
        """
        raise NotImplementedError("Fine-tuning not supported for this model.")
