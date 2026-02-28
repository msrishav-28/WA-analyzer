from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ZeroShotClassifier:
    """
    Classifies messages into predefined 6 types using facebook/bart-large-mnli.
    """
    LABELS = ["solution", "code", "idea", "resource", "question", "reaction"]
    
    def __init__(self):
        try:
            from transformers import pipeline
            logger.info("Loading BART Zero-Shot Classifier (this may take a minute)...")
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            logger.info("Loaded facebook/bart-large-mnli for Zero-Shot Classification")
        except ImportError:
            raise ImportError("Please install transformers and torch.")

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Returns top predicted label and score for each text."""
        out = self.classifier(texts, candidate_labels=self.LABELS, multi_label=False)
        results = []
        for res in out:
            results.append({
                'label': res['labels'][0],
                'score': res['scores'][0]
            })
        return results
