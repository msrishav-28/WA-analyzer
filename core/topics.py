import numpy as np
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class TopicDiscoverer:
    """
    V6 SOTA Topic Discovery using BERTopic + HDBSCAN + UMAP.
    Extracts dynamic underlying conversational topics without predefined lists.
    """
    def __init__(self):
        try:
            from bertopic import BERTopic
            from hdbscan import HDBSCAN
            from umap import UMAP
            
            logger.info("Initializing BERTopic Engine...")
            # We tune HDBSCAN for short sparse conversational text
            hdbscan_model = HDBSCAN(min_cluster_size=3, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
            # UMAP initialized for clustering short text embeddings
            umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')
            
            # Note: We provide embeddings directly, so no embedding_model initialization inside BERTopic here.
            self.topic_model = BERTopic(
                hdbscan_model=hdbscan_model,
                umap_model=umap_model,
                nr_topics="auto", 
                language="multilingual",
                calculate_probabilities=False
            )
            logger.info("BERTopic Initialized.")
        except ImportError:
            raise ImportError("Please ensure bertopic is installed in the environment.")

    def discover_topics(self, messages: List[str], embeddings: np.ndarray) -> Tuple[List[int], Dict[int, str]]:
        """
        Fits BERTopic on the entire conversation history.
        Args:
            messages: List of raw string texts.
            embeddings: Numpy array of pre-computed embeddings for the messages.
        Returns:
            topics: List of integer topic assignments for each message.
            topic_names: Dictionary mapping topic IDs to human-readable names.
        """
        topics, probs = self.topic_model.fit_transform(messages, embeddings)
        topic_info = self.topic_model.get_topic_info()
        
        # Build dictionary of topic index -> nice topic representation (top 3 words)
        topic_names = {}
        for index, row in topic_info.iterrows():
            topic_id = row['Topic']
            # Join the representation words
            words = row['Representation']
            if isinstance(words, list):
                topic_names[topic_id] = " | ".join(words[:3])
            else:
                topic_names[topic_id] = "Unknown"
        
        return topics, topic_names
