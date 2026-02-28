import time
import logging
from typing import List, Dict, Tuple
from core.parser import WhatsAppParser, Message, UserStats

class V6Pipeline:
    """
    The orchestrator for the V6 WhatsApp Analyzer SAAS Engine.
    Coordinates MTEB Embeddings, RoBERTa Sentiment, BERTopic Clustering, and Temporal Graphs.
    Gracefully falls back if C-compiled libraries are missing on the runtime environment (e.g. Python 3.14).
    """
    def __init__(self, mode: str = 'local', api_key: str = None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing V6 SAAS Engine...")
        self.mode = mode
        
        from core.embeddings import EmbeddingEngine
        self.embed_engine = EmbeddingEngine(mode=mode, api_key=api_key)
        
        try:
            from core.topics import TopicDiscoverer
            self.topic_engine = TopicDiscoverer()
            self.has_bertopic = True
        except ImportError:
            self.logger.warning("BERTopic/HDBSCAN not fully installed. Gracefully bypassing Topic Discovery Phase.")
            self.has_bertopic = False
            
        try:
            from core.sentiment import EmotionAnalyzer
            self.emotion_engine = EmotionAnalyzer()
            self.has_emotions = True
        except ImportError:
            self.logger.warning("Transformers not fully installed. Gracefully bypassing Emotion Phase.")
            self.has_emotions = False
            
        try:
            from core.classification import ZeroShotClassifier
            self.classifier_engine = ZeroShotClassifier()
            self.has_classification = True
        except ImportError:
            self.logger.warning("Transformers not fully installed. Gracefully bypassing Zero-Shot Classification Phase.")
            self.has_classification = False

        from core.graphs import SocialGraphEngine
        self.graph_engine = SocialGraphEngine()

        from core.scoring import ValueScorer
        self.value_scorer = ValueScorer()

        from core.influence import SemanticInfluenceEngine
        self.influence_engine = SemanticInfluenceEngine()

    def process_chat(self, text: str) -> Dict:
        start_time = time.time()
        
        parser = WhatsAppParser()
        messages = parser.parse(text)
        if not messages:
            return {"error": "No valid messages parsed."}
            
        self.logger.info(f"Parsed {len(messages)} messages.")
        
        # 1. Base Stats
        user_stats = {}
        msg_texts = []
        for msg in messages:
            if msg.sender not in user_stats:
                user_stats[msg.sender] = UserStats(name=msg.sender)
            user_stats[msg.sender].messages.append(msg)
            msg_texts.append(msg.content)
            
        # 2. Embeddings
        self.logger.info("Computing High-Dimensional Embeddings...")
        embeddings = self.embed_engine.encode(msg_texts)
        
        # 3. Graph Architecture
        self.logger.info("Computing Temporal Graph Network & Centralities...")
        graph, centrality_stats = self.graph_engine.compute_graph(messages, engage_win_mins=30)
        
        self.logger.info("Generating Interactive HTML Graph...")
        graph_html = self.graph_engine.generate_html()
        
        # 4. Sentiment / Emotions
        emotion_results = []
        if self.has_emotions:
            self.logger.info("Running RoBERTa Emotion Classifier...")
            emotion_results = self.emotion_engine.analyze_batch(msg_texts)
            
        # 5. BERTopic Clustering
        topics, topic_names = [], {}
        if self.has_bertopic:
            self.logger.info("Discovering Semantic Topics with BERTopic & HDBSCAN...")
            topics, topic_names = self.topic_engine.discover_topics(msg_texts, embeddings)
            
        # 6. Semantic Influence & Uniqueness
        self.logger.info("Calculating Semantic Influence and Uniqueness...")
        uniqueness_scores = self.influence_engine.calculate_uniqueness(messages, embeddings)
        influence_scores = self.influence_engine.calculate_idea_influence(messages, embeddings)
        
        # 7. Zero-Shot Classification
        if self.has_classification:
            self.logger.info("Running Zero-Shot Message Classification...")
            classification_results = self.classifier_engine.analyze_batch(msg_texts)
            for msg, res in zip(messages, classification_results):
                user_stats[msg.sender].msg_types.append(res['label'])
                
        # 8. Compute Overall Value Score
        self.logger.info("Computing 9-Dimensional Value Scores...")
        # (Assuming parse stats are naturally populated in parser; 
        # normally you'd want a parser phase that actually counts snippets/links/etc. 
        # But we compute the score based on whatever is there).
        value_scores = self.value_scorer.compute_scores(user_stats)

        self.logger.info(f"V6 Pipeline Executed in {time.time() - start_time:.2f} seconds.")
        
        return {
            "num_messages": len(messages),
            "num_users": len(user_stats),
            "centrality_stats": centrality_stats,
            "graph_html": graph_html,
            "value_scores": value_scores,
            "uniqueness_scores": uniqueness_scores,
            "influence_scores": influence_scores,
            "has_emotions": self.has_emotions,
            "has_bertopic": self.has_bertopic,
            "has_classification": self.has_classification,
            "emotion_sample": emotion_results[:5] if emotion_results else [],
            "topic_sample": topic_names
        }
