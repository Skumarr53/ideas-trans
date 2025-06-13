# sentiment_agent/models/registry.py

from sentiment_agent.models.gemma_model import GemmaSentimentModel
from sentiment_agent.models.nli_model import NLISentimentModel

MODEL_REGISTRY = {
    "gemma": GemmaSentimentModel,
    "nli": NLISentimentModel,
}

def get_model(model_type: str, config) -> object:
    """
    Factory function to return the correct model instance based on type.
    """
    model_type = model_type.lower()
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model type '{model_type}'. Available options: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[model_type](config)
