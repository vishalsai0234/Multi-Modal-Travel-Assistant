# 🌍 Multi-Modal Travel Assistant

A LangGraph-powered travel assistant that aggregates city information, weather forecasts, and images into a rich Streamlit UI — with intelligent routing between local knowledge and web search.

---

## 🏗️ Architecture

<img width="225" height="654" alt="graph" src="https://github.com/user-attachments/assets/6843f5a3-fbb3-4fba-a0cf-dc627fc1949f" />

The workflow starts by receiving a user query such as *"Tell me about Tokyo"*.

1. **Extract Node**
   - The input query is processed and the city name is extracted.

2. **Router Node**
   - The system checks whether information about the city already exists in the local vector database.
   - If available, it follows the **Vector Store path**. (ex. Tokyo)
   - Otherwise, it switches to the **Mock Web Search path**. (ex. Snohomish)

3. **Web Search (if needed)**
   - For cities not present in local knowledge, a mock search API generates a summary.

4. **Parallel Fetch Node**
   - Weather information and city images are independent tasks.
   - To reduce latency, both are fetched simultaneously using `ThreadPoolExecutor`.
   - This acts as a parallel fan-out stage.

5. **Merge Node**
   - Information from all sources is combined into a structured output containing:
     - `city_summary`
     - `weather_forecast`
     - `image_urls`

6. **Final Output**
   - The structured result is displayed using:
     - text summary
     - weather visualization
     - image gallery
     - routing explanation

This design demonstrates conditional routing, multi-modal data integration, parallel execution, and memory-based workflow orchestration using LangGraph.

```
The workflow starts by receiving a user query such as *"Tell me about Tokyo"*.

1. **Extract Node**
   - The input query is processed and the city name is extracted.

2. **Router Node**
   - The system checks whether information about the city already exists in the local vector database.
   - If available, it follows the **Vector Store path**. (ex. Tokyo)
   - Otherwise, it switches to the **Mock Web Search path**. (ex. Snohomish)

3. **Web Search (if needed)**
   - For cities not present in local knowledge, a mock search API generates a summary.

4. **Parallel Fetch Node**
   - Weather information and city images are independent tasks.
   - To reduce latency, both are fetched simultaneously using `ThreadPoolExecutor`.
   - This acts as a parallel fan-out stage.

5. **Merge Node**
   - Information from all sources is combined into a structured output containing:
     - `city_summary`
     - `weather_forecast`
     - `image_urls`

6. **Final Output**
   - The structured result is displayed using:
     - text summary
     - weather visualization
     - image gallery
     - routing explanation

This design demonstrates conditional routing, multi-modal data integration, parallel execution, and memory-based workflow orchestration using LangGraph.
```
```
User Input
    ↓
[extract_city] — parses city name from free-text query
    ↓
[router] — queries local TF-IDF index
    ↓
[conditional edge: route_by_source]
   ↙                            ↘
[vector_retrieve]          [web_search]
(city in local store)    (city not found)
   ↘                            ↙
        [parallel_fetch]  ← DISTINCTION 2: Fan-Out
        /              \
  [weather]         [images]   ← run simultaneously via ThreadPoolExecutor
        \              /
        [synthesizer]  ← structured JSON/Pydantic output
              ↓
           [END]
```

![Graph Topology](graph.png)

---

## 🧠 Design Decisions

### Intelligent Routing (The "Switch")
The system uses TF-IDF cosine similarity (with exact name matching as a fast path) to check whether a queried city exists in our local knowledge base. Cities not found locally are routed to a mock web search tool. This happens through LangGraph's `add_conditional_edges`, driven by `state["source"]`.

**Cities in local store:** Paris, Tokyo, New York  
**Other cities** (Kyoto, Dubai, Snohomish, etc.) → Web Search path

### Why TF-IDF instead of ChromaDB?
ChromaDB's default embedding function requires downloading a 90MB ONNX model. TF-IDF provides equivalent routing behavior with zero dependencies. In production, swap `tools/vector_store.py` with a ChromaDB or FAISS implementation — the interface (`query_city → (str, bool)`) stays identical.

---

## ⭐ Distinction Challenges Attempted

### 🏆 Distinction 2: Parallel Fan-Out
Weather and image fetching are independent. `parallel_fetch_node` uses `concurrent.futures.ThreadPoolExecutor` with `max_workers=2` to run both simultaneously:
- Sequential: ~1.4s (0.8s weather + 0.6s images)  
- Parallel: ~0.8s (max of both)

### 🏆 Distinction 3: Human-in-the-Loop & Memory
The graph is compiled with `MemorySaver` checkpointer. Each Streamlit session gets a unique `thread_id`. Follow-up queries like *"What about next week?"* are detected via keyword matching — the app reuses `st.session_state.last_city` so only weather refreshes, not the full city summary.

---

## 📁 Project Structure

```
travel_assistant/
├── app.py                    # Streamlit entry point
├── requirements.txt
├── generate_graph.py         # Run once to produce graph.png
├── graph/
│   ├── state.py              # TypedDict: TravelState
│   ├── nodes.py              # All 5 node functions
│   ├── edges.py              # route_by_source conditional
│   └── builder.py            # Graph assembly + MemorySaver
├── tools/
│   ├── vector_store.py       # TF-IDF semantic search (no downloads)
│   ├── weather.py            # Mock weather API (7-day forecast)
│   ├── images.py             # Mock image retrieval
│   └── web_search.py         # Mock web search
└── data/
    └── cities.json           # Knowledge base: Paris, Tokyo, New York
```

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. (Optional) Generate graph.png for submission
python generate_graph.py
```

No API keys required — all tools use mock implementations.

---

## 📊 Output Schema

The final node produces a structured dict (parseable as JSON):

```json
{
  "city": "Tokyo",
  "data_source": "Local Knowledge Base",
  "city_summary": "...",
  "weather_forecast": [
    {"day": "Wednesday", "date": "May 20", "temp_high": 24, "temp_low": 17,
     "condition": "Sunny", "humidity": 65, "wind_kmh": 12}
  ],
  "image_urls": ["https://..."],
  "error": ""
}
```

The Streamlit UI parses this to render: text summary, image gallery, and an interactive Plotly line+bar chart.

---

## 🧪 Testing Without Streamlit

```python
from graph.builder import build_graph

app = build_graph(use_memory=False)
result = app.invoke({
    "user_query": "Tell me about Kyoto",
    "city": "", "source": "", "city_summary": "",
    "weather_forecast": [], "image_urls": [],
    "error": "", "final_output": None,
})
print(result["final_output"])
```
