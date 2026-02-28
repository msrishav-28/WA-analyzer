from typing import List, Dict

class EmotionAnalyzer:
    """
    V6 SOTA Emotion Engine using RoBERTa sequence classification.
    Produces complex emotions (e.g. 'admiration', 'annoyance', 'joy', 'curiosity') 
    instead of flat VADER polarity.
    """
    def __init__(self):
        try:
            from transformers import pipeline
            print("⏳ Loading RoBERTa Emotion Classifier (this may take a minute)...")
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
            print("✅ Loaded SamLowe/roberta-base-go_emotions")
        except ImportError:
            raise ImportError("Please install transformers and torch.")

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Returns the primary emotion and score for each text."""
        # Pipeline top_k=1 returns a list of lists of dicts
        out = self.classifier(texts)
        results = []
        for res in out:
            top_emotion = res[0]
            results.append({
                'emotion': top_emotion['label'],
                'score': top_emotion['score']
            })
        return results
