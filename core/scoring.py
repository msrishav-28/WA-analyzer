from typing import Dict
from core.parser import UserStats

class ValueScorer:
    """
    Computes a 9-dimensional weighted value score for each user.
    """
    def __init__(self, weights: Dict[str, float] = None):
        if weights is None:
            self.weights = {
                'replies_triggered': 2.0,
                'conversation_starts': 1.5,
                'questions_asked': 1.0,
                'questions_answered': 3.0,
                'code_snippets': 4.0,
                'links_shared': 2.0,
                'total_words': 0.1,
                'vocab_richness': 2.0,
                'unique_engagers': 1.5
            }
        else:
            self.weights = weights

    def compute_scores(self, user_stats_dict: Dict[str, UserStats]) -> Dict[str, float]:
        scores = {}
        for user, stats in user_stats_dict.items():
            score = 0.0
            score += stats.replies_triggered * self.weights.get('replies_triggered', 0)
            score += stats.conversation_starts * self.weights.get('conversation_starts', 0)
            score += stats.questions_asked * self.weights.get('questions_asked', 0)
            score += stats.questions_answered * self.weights.get('questions_answered', 0)
            score += stats.code_snippets * self.weights.get('code_snippets', 0)
            score += stats.links_shared * self.weights.get('links_shared', 0)
            score += stats.total_words * self.weights.get('total_words', 0)
            score += stats.vocab_richness * self.weights.get('vocab_richness', 0)
            score += len(stats.unique_engagers) * self.weights.get('unique_engagers', 0)
            scores[user] = score
            
        # Optional: Normalize scores (0-100 scale)
        if scores:
            max_score = max(scores.values()) or 1.0
            for user in scores:
                scores[user] = round((scores[user] / max_score) * 100, 2)
                
        return scores
