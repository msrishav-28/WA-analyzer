import time
from typing import List, Dict, Tuple
from core.parser import WhatsAppParser, Message, UserStats

class V6Pipeline:
    """
    The orchestrator for the V6 WhatsApp Analyzer SAAS Engine.
    Coordinates MTEB Embeddings, RoBERTa Sentiment, BERTopic Clustering, and Temporal Graphs.
    Gracefully falls back if C-compiled libraries are missing on the runtime environment (e.g. Python 3.14).
    """
    def __init__(self, mode: str = 'local', api_key: str = None):
        print("🚀 Initializing V6 SAAS Engine...")
        self.mode = mode
        
        from core.embeddings import EmbeddingEngine
        self.embed_engine = EmbeddingEngine(mode=mode, api_key=api_key)
        
        try:
            from core.topics import TopicDiscoverer
            self.topic_engine = TopicDiscoverer()
            self.has_bertopic = True
        except ImportError:
            print("⚠️ BERTopic/HDBSCAN not fully installed. Gracefully bypassing Topic Discovery Phase.")
            self.has_bertopic = False
            
        try:
            from core.sentiment import EmotionAnalyzer
            self.emotion_engine = EmotionAnalyzer()
            self.has_emotions = True
        except ImportError:
            print("⚠️ Transformers not fully installed. Gracefully bypassing Emotion Phase.")
            self.has_emotions = False
            
        from core.graphs import SocialGraphEngine
        self.graph_engine = SocialGraphEngine()

    def process_chat(self, text: str) -> Dict:
        start_time = time.time()
        
        parser = WhatsAppParser()
        messages = parser.parse(text)
        if not messages:
            return {"error": "No valid messages parsed."}
            
        print(f"✅ Parsed {len(messages)} messages.")
        
        # 1. Base Stats
        user_stats = {}
        msg_texts = []
        for msg in messages:
            if msg.sender not in user_stats:
                user_stats[msg.sender] = UserStats(name=msg.sender)
            user_stats[msg.sender].messages.append(msg)
            msg_texts.append(msg.content)
            
        # 2. Embeddings
        print("🧠 Computing High-Dimensional Embeddings...")
        embeddings = self.embed_engine.encode(msg_texts)
        
        # 3. Graph Architecture
        print("🕸️ Computing Temporal Graph Network & Centralities...")
        graph, centrality_stats = self.graph_engine.compute_graph(messages, engage_win_mins=30)
        
        # 4. Sentiment / Emotions
        emotion_results = []
        if self.has_emotions:
            print("🎭 Running RoBERTa Emotion Classifier...")
            emotion_results = self.emotion_engine.analyze_batch(msg_texts)
            
        # 5. BERTopic Clustering
        topics, topic_names = [], {}
        if self.has_bertopic:
            print("🔍 Discovering Semantic Topics with BERTopic & HDBSCAN...")
            topics, topic_names = self.topic_engine.discover_topics(msg_texts, embeddings)
            
        print(f"🏁 V6 Pipeline Executed in {time.time() - start_time:.2f} seconds.")
        
        return {
            "num_messages": len(messages),
            "num_users": len(user_stats),
            "centrality_stats": centrality_stats,
            "has_emotions": self.has_emotions,
            "has_bertopic": self.has_bertopic,
            "emotion_sample": emotion_results[:5] if emotion_results else [],
            "topic_sample": topic_names
        }
