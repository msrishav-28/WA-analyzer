import numpy as np
from typing import List, Dict, Tuple
from core.parser import Message

class SemanticInfluenceEngine:
    """
    Calculates Semantic Uniqueness and Idea Influence using MTEB/bge-m3 embeddings.
    """
    def __init__(self):
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            self.cosine_similarity = cosine_similarity
        except ImportError:
            raise ImportError("Please install scikit-learn.")

    def calculate_uniqueness(self, messages: List[Message], embeddings: np.ndarray, window: int = 50) -> Dict[str, float]:
        """
        Calculates uniqueness per user based on message embeddings.
        Uniqueness is 1 - cosine_similarity(msg, mean(previous N msgs)).
        Returns a dictionary of {sender: average_uniqueness}.
        """
        user_scores = {msg.sender: 0.0 for msg in messages}
        user_counts = {msg.sender: 0 for msg in messages}
        
        n = len(messages)
        for i in range(n):
            sender = messages[i].sender
            if i == 0:
                user_scores[sender] += 1.0
            else:
                start_idx = max(0, i - window)
                prev_embs = embeddings[start_idx:i]
                mean_emb = np.mean(prev_embs, axis=0).reshape(1, -1)
                curr_emb = embeddings[i].reshape(1, -1)
                
                sim = self.cosine_similarity(curr_emb, mean_emb)[0][0]
                user_scores[sender] += float(1.0 - sim)
                
            user_counts[sender] += 1
            
        for sender in user_scores:
            if user_counts[sender] > 0:
                user_scores[sender] = float(user_scores[sender] / user_counts[sender])
                
        return user_scores

    def calculate_idea_influence(self, messages: List[Message], embeddings: np.ndarray, reply_window: int = 10) -> Dict[str, float]:
        """
        Calculates how much a user's messages echo through subsequent replies by others.
        Returns a dictionary of {sender: average_influence_score}.
        """
        user_influence = {msg.sender: 0.0 for msg in messages}
        user_counts = {msg.sender: 0 for msg in messages}
        n = len(messages)
        
        for i in range(n):
            sender = messages[i].sender
            root_emb = embeddings[i].reshape(1, -1)
            
            # Look ahead for replies by OTHER users
            echo_score = 0.0
            replies = 0
            for j in range(i + 1, min(i + 1 + reply_window, n)):
                if messages[j].sender != sender:
                    reply_emb = embeddings[j].reshape(1, -1)
                    sim = self.cosine_similarity(root_emb, reply_emb)[0][0]
                    echo_score += float(max(0.0, sim)) # only count positive echo
                    replies += 1
            
            user_influence[sender] += echo_score
            user_counts[sender] += 1
            
        # Average influence per user
        for sender in user_influence:
            if user_counts[sender] > 0:
                user_influence[sender] = float(user_influence[sender] / user_counts[sender])
                
        return user_influence
