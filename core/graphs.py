import networkx as nx
import numpy as np
from datetime import timedelta
from typing import List, Dict, Tuple

class SocialGraphEngine:
    """
    V6 SOTA Social Graph Engine. Computes dynamic temporal graphing and Network Centralities 
    (Betweenness, Eigenvector) mapping structural conversational flow.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def compute_graph(self, messages: List, engage_win_mins: int = 30) -> Tuple[nx.DiGraph, Dict]:
        """
        Builds the temporal communication graph and extracts centrality stats.
        Requires message objects to have `sender` and `timestamp`.
        """
        engage_win = timedelta(minutes=engage_win_mins)
        n = len(messages)
        
        for i, msg in enumerate(messages):
            j = i + 1
            while j < n and (messages[j].timestamp - msg.timestamp) <= engage_win:
                if messages[j].sender != msg.sender:
                    u, v = messages[j].sender, msg.sender
                    if self.graph.has_edge(u, v):
                        self.graph[u][v]['weight'] += 1
                    else:
                        self.graph.add_edge(u, v, weight=1)
                j += 1

        stats = {}
        if len(self.graph) > 0:
            betweenness = nx.betweenness_centrality(self.graph, weight='weight')
            try: 
                eigenvector = nx.eigenvector_centrality_numpy(self.graph, weight='weight')
            except Exception:
                eigenvector = {node: 0.0 for node in self.graph.nodes()}
            in_degree = dict(self.graph.in_degree(weight='weight'))
            out_degree = dict(self.graph.out_degree(weight='weight'))
            
            for node in self.graph.nodes():
                stats[node] = {
                    'betweenness': float(betweenness.get(node, 0)),
                    'eigenvector': float(eigenvector.get(node, 0)),
                    'in_degree': in_degree.get(node, 0),
                    'out_degree': out_degree.get(node, 0)
                }
        
        return self.graph, stats
