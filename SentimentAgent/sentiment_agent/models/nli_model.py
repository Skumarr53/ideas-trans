# sentiment_agent/models/nli_model.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict
from sentiment_agent.models.base import SentimentModel

class NLISentimentModel(SentimentModel):
    """
    Uses NLI approach to classify sentiment based on entailment probabilities.
    """

    def load(self):
        self.model_name = self.config.model_name  # e.g., MoritzLaurer/... model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def predict(self, texts: List[str]) -> List[Dict[str, float]]:
        # Define candidate labels as NLI hypothesis
        candidate_labels = ["positive", "neutral", "negative"]
        result = []

        for premise in texts:
            label_scores = {}
            for label in candidate_labels:
                hypothesis = f"This example is {label}."
                inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, padding=True).to(self.device)
                with torch.no_grad():
                    logits = self.model(**inputs).logits
                    probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0]

                entailment_score = probs[2]  # index 2 = entailment
                label_scores[label] = round(float(entailment_score), 4)

            result.append(label_scores)

        return result