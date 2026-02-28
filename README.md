# WhatsApp Analyzer 

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Gradio](https://img.shields.io/badge/gradio-000000?style=for-the-badge&logo=gradio&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-F9AB00?style=for-the-badge&logo=huggingface&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-005B9F?style=for-the-badge)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

An advanced, offline-first tool for analyzing WhatsApp chat exports through the lens of semantic contribution, social graph topology, and deep emotional profiling.

Unlike superficial analytics tools that plot simple message counts or word clouds, the WhatsApp Analyzer is designed for highly technical, developer-centric communities where the actual *quality* and *influence* of a contribution matter more than sheer volume.

## Core Features

- **Value / Contribution Scoring**: A 9-dimensional weighted score assessing individual contribution quality.
- **Deep Emotional Profiling**: 28-dimensional emotion extraction using `roberta-base-go_emotions`.
- **Semantic Uniqueness & Idea Influence**: Measures the originality of messages and how deeply conversational framing echoes across subsequent replies.
- **Dynamic Topic Discovery**: Data-driven, density-based topic clustering utilizing BERTopic (UMAP + HDBSCAN).
- **Zero-Shot Message Classification**: Automatically tags messages into categories (e.g., solution, code, idea, resource) utilizing `facebook/bart-large-mnli`.
- **Interactive Social Graphs**: PyVis-powered NetworkX topological analysis, calculating Betweenness and Eigenvector centralities to detect community bridges and true influencers.

## Embedding Architecture

The V6 Engine operates on a dual-embedding strategy, allowing seamless switching depending on the environment:

- **Local Mode**: Uses `BAAI/bge-m3` via `sentence-transformers` for offline, high-quality, privacy-preserving dense vectors.
- **API Mode**: Integrates the `pplx-embed-v1` Perplexity API for environments where local compute is constrained.

## Installation and Execution

Configure the environment, install the ML dependencies, and launch the asynchronous Gradio dashboard. No data is ever uploaded or retained unless explicit API modes are engaged. Ensure `python3-dev` and a C-compiler exist on your system before attempting a full install of BERTopic/HDBSCAN.

```bash
pip install -r requirements.txt
python dashboard.py
```

## Security and Privacy

Designed originally for sensitive internal corporate communications, by default, the pipeline operates locally. The Python `logging` module replaces legacy arbitrary console printing to allow seamless integration with modern 2026/2027 observability platforms (Vector, Datadog) while maintaining strict local persistence.
