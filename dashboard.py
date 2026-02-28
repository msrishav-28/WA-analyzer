import gradio as gr
import pandas as pd
import json
import time
from core.pipeline import V6Pipeline

# We initialize the V6 Engine out-of-band for performance
pipeline = None

def init_pipeline(mode, api_key):
    global pipeline
    if pipeline is None:
        pipeline = V6Pipeline(mode=mode, api_key=api_key)
    return "✅ Engine Initialized and Ready."

def analyze_chat(file_obj, mode, api_key):
    global pipeline
    if not file_obj:
        raise gr.Error("Please upload a .txt file")
    
    if pipeline is None:
        init_pipeline(mode, api_key)
        
    with open(file_obj.name, 'r', encoding='utf-8') as f:
        text = f.read()

    results = pipeline.process_chat(text)
    
    if "error" in results:
        raise gr.Error(results["error"])
        
    # Formatting output for the dashboard
    stats = results["centrality_stats"]
    df = pd.DataFrame([
        {
            "Participant": user,
            "Betweenness Centrality": round(data['betweenness'], 3),
            "Eigenvector Centrality": round(data['eigenvector'], 3),
            "Messages Sent": data['out_degree']
        }
        for user, data in stats.items()
    ]).sort_values(by="Betweenness Centrality", ascending=False)
    
    emotions_str = json.dumps(results["emotion_sample"], indent=2) if results["has_emotions"] else "HuggingFace Transformers not active."
    topics_str = json.dumps(results["topic_sample"], indent=2) if results["has_bertopic"] else "BERTopic/HDBSCAN not active (C-compiler missing for Py3.14)."
    
    health_metrics = f"""
    ### 🏥 V6 Network Health
    **Total Participants:** `{results['num_users']}`
    **Total Messages:** `{results['num_messages']}`
    """

    return health_metrics, df, emotions_str, topics_str

custom_css = """
.container { max-width: 1600px; margin: auto; font-family: 'Inter', sans-serif; }
.header-bg { background: linear-gradient(90deg, #1A202C 0%, #2D3748 100%); padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;}
h1, h2, h3 { color: inherit !important; }
"""

with gr.Blocks(title="WhatsApp Analyzer V6 SAAS", css=custom_css) as demo:
    with gr.Column(elem_classes="container"):
        gr.HTML("<div class='header-bg'><h1>WhatsApp Analyzer V6 Enterprise</h1><p>Powered by BGE-M3 Embeddings, RoBERTa Emotions, and TGNN Flow</p></div>")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Engine Configuration")
                engine_mode = gr.Dropdown(choices=["local", "api"], value="local", label="V6 Embedding Mode")
                api_key = gr.Textbox(placeholder="PPLX API Key...", type="password", label="Perplexity API Key")
                file_input = gr.File(label="Upload WhatsApp Export (.txt)")
                analyze_btn = gr.Button("🚀 Launch V6 Analytics Pipeline", variant="primary", size="lg")
                
            with gr.Column(scale=3):
                health_out = gr.Markdown("### ⏳ Awaiting Data...")
                with gr.Tabs():
                    with gr.TabItem("📊 Social Network Leaders"):
                        leaderboard = gr.DataFrame(interactive=False)
                    with gr.TabItem("🎭 Deep Emotion Profiling (RoBERTa)"):
                        emotions_box = gr.Code(language="json")
                    with gr.TabItem("🧠 Semantic Topics (BERTopic)"):
                        topics_box = gr.Code(language="json")

        analyze_btn.click(
            fn=analyze_chat,
            inputs=[file_input, engine_mode, api_key],
            outputs=[health_out, leaderboard, emotions_box, topics_box]
        )

if __name__ == "__main__":
    print("Starting V6 Dashboard...")
    demo.launch()
