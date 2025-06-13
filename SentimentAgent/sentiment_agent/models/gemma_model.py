# sentiment_agent/models/gemma_model.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict
from sentiment_agent.models.base import SentimentModel

class GemmaSentimentModel(SentimentModel):
    """
    Uses Gemma (causal LM) to perform sentiment analysis by prompting.
    """

    def load(self):
        self.model_name = self.config.model_name  # e.g., 'google/gemma-2b'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def _build_prompt(self, text: str) -> str:
        return f"""
        Analyze the sentiment of the following text and respond only with sentiment labels (positive, neutral, negative) with their scores:
        ---
        {text}
        """

    def predict(self, texts: List[str]) -> List[Dict[str, float]]:
        results = []
        for text in texts:
            prompt = self._build_prompt(text)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    do_sample=False,
                    temperature=0.7,
                )
            decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
            parsed = self._parse_response(decoded)
            results.append(parsed)
        return results

    def _parse_response(self, response: str) -> Dict[str, float]:
        """
        Example response expected: "positive: 0.7, neutral: 0.2, negative: 0.1"
        """
        import re
        sentiment_map = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        try:
            for label in sentiment_map.keys():
                match = re.search(f"{label}[:\s]+(\d+\.\d+)", response, re.IGNORECASE)
                if match:
                    sentiment_map[label] = round(float(match.group(1)), 4)
        except Exception:
            print(f"[WARN] Could not parse response: {response}")
        return sentiment_map
