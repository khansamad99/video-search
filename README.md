# Video Semantic Search PoC

A fast semantic search system that finds relevant video timestamps based on user queries. Built to demonstrate sub-second search capability across multiple videos.

## 🚀 Quick Start

```bash
# 1. Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start server
python main.py

# 3. Load sample videos (first time only)
python scripts/load_all_videos.py

# 4. Test search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AWS Lambda?", "top_k": 3}'
```

## 🎯 Key Features

- **Semantic Search**: Understands meaning, not just keywords
- **Fast Response**: <10ms search time (meets <1 second requirement)
- **No Setup Required**: Works out-of-the-box, no external databases
- **RESTful API**: Easy to integrate with any frontend

## 🏗 Architecture

### Current Implementation
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (in-memory)
- **API Framework**: FastAPI
- **Search Process**: Query → Embedding → Vector Similarity → Results

### How It Works
1. Video transcripts are split into 30-second chunks
2. Each chunk is converted to a 384-dimensional embedding
3. User queries are embedded and compared using cosine similarity
4. Returns the most relevant video ID + timestamp

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── src/                 # Core search engine
│   ├── models.py        # Data models
│   ├── embedding_manager.py
│   ├── vector_store.py
│   └── search_engine.py
├── scripts/             # Utility scripts
│   ├── load_all_videos.py
│   └── test_search_only.py
├── data/transcripts/    # Sample video data
└── docs/
    ├── testing_guide.md      # Complete testing guide
    └── production_architecture.md  # Scaling to production
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/stats` | GET | Index statistics |
| `/search` | POST | Search videos |
| `/index` | POST | Index videos |
| `/index` | DELETE | Clear index |

### Example Search Request
```json
POST /search
{
  "query": "How to train a neural network?",
  "top_k": 3
}
```

### Example Response
```json
{
  "results": [{
    "video_id": "video_001",
    "video_title": "Introduction to Machine Learning",
    "timestamp": 60.0,
    "end_time": 90.0,
    "matched_text": "Supervised learning uses labeled data...",
    "relevance_score": 0.856
  }],
  "query": "How to train a neural network?",
  "processing_time_ms": 8.5
}
```

## 🧪 Testing

```bash
# Run comprehensive tests
python scripts/test_search_only.py

# Or test individual queries
curl -X POST http://localhost:8000/search \
  -d '{"query": "What are React hooks?"}'
```

Sample queries to try:
- "What is supervised learning?"
- "How to create a list in Python?"
- "Explain database normalization"
- "What is continuous integration?"

## 📈 Production Considerations

This PoC uses in-memory storage for simplicity. For production:

1. **Video Processing**: Add automatic transcription (Whisper/AWS Transcribe)
2. **Storage**: Use PostgreSQL + pgvector or dedicated vector DB
3. **Scale**: Implement distributed search with Pinecone/Weaviate
4. **Performance**: Add caching layer for repeated queries

See [docs/production_architecture.md](docs/production_architecture.md) for detailed scaling strategy.

## 🛠 Troubleshooting

**Empty search results?**
```bash
# Check if videos are indexed
curl http://localhost:8000/stats
# If total_videos is 0, run: python scripts/load_all_videos.py
```

**Port already in use?**
Change port in `.env` file or use `PORT=8001 python main.py`

## 📊 Performance

- Embedding generation: ~1ms
- Vector search: ~0.5ms  
- Total response: <10ms
- First query: ~200ms (model loading)
- Subsequent queries: <10ms
