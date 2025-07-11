# Testing Guide & Architecture FAQ

## How to Test the System

### Quick Start Testing

1. **Start the API server:**
```bash
cd backend
source venv/bin/activate
python main.py
```

2. **In another terminal, load sample data (first time only):**
```bash
cd backend
source venv/bin/activate
python scripts/load_all_videos.py
```

3. **Test the search functionality:**
```bash
python scripts/test_search_only.py
```

**Note:** The original `test_search.py` tries to reload data each time, which causes errors if data is already indexed. Use `test_search_only.py` for testing searches without reloading data.

### Check Current Status

```bash
# Check if videos are already indexed
curl http://localhost:8000/stats

# If you see "total_videos": 0, run load_all_videos.py
# If you see "total_videos": 10, data is already loaded!
```

### Clear and Reload Data (if needed)

```bash
# Clear all indexed data
curl -X DELETE http://localhost:8000/index

# Reload sample data
python scripts/load_all_videos.py
```

### API Testing Examples

#### Health Check
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "video-search"}
```

#### Get Statistics  
```bash
curl http://localhost:8000/stats
# Response: {"total_videos": 10, "total_chunks": 131, "embedding_dimension": 384}
```

#### Search Videos
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How to train a neural network?", "top_k": 3}'
```

#### Clear Index (if needed)
```bash
curl -X DELETE http://localhost:8000/index
```

#### Load Videos (POST to /index with video JSON data)
See `scripts/load_all_videos.py` for automated loading.

## Architecture Decisions & FAQ

### 1. Do I need to setup a Vector DB?

**No, you don't need any external database setup.** Here's why:

- **FAISS is in-memory**: It stores vectors in RAM, not a database
- **No installation needed**: FAISS comes as a Python package
- **Perfect for PoC**: For ~10 videos, in-memory storage is ideal
- **Fast performance**: No network calls, pure memory access

### 2. Why JSON files instead of a database?

The JSON files serve as **sample data only**, not as a database:

```json
{
  "video_id": "video_001",
  "title": "Introduction to Machine Learning",
  "chunks": [
    {
      "text": "transcript segment",
      "start_time": 0,
      "end_time": 30
    }
  ]
}
```

**Reasons:**
- **Simplicity**: No database setup required for PoC
- **Transparency**: Easy to inspect and modify test data
- **Portability**: Anyone can run without database credentials
- **Focus on algorithm**: Demonstrates semantic search, not data management

### 3. Potential Cross-Questions & Answers

#### Q: "How does this scale to 1000s of videos?"

**Current limitations:**
- In-memory storage limited by RAM
- No persistence between restarts
- Single-instance only

**Production solutions:**
- Use persistent FAISS with `save()`/`load()`
- Switch to distributed solutions (Pinecone, Weaviate, Qdrant)
- Implement caching layer

#### Q: "What happens when the server restarts?"

**Current behavior:**
- All indexed data is lost
- Need to re-index videos

**Production fix:**
```python
# Save index
vector_store.save("index.faiss", "metadata.pkl")

# Load on startup
vector_store.load("index.faiss", "metadata.pkl")
```

#### Q: "How accurate is the semantic search?"

**Accuracy factors:**
- Model quality (all-MiniLM-L6-v2 is good for general text)
- Chunk size (30 seconds balances context vs precision)
- Embedding dimension (384D is efficient)

**Improvements:**
- Larger models (all-mpnet-base-v2)
- Domain-specific fine-tuning
- Hybrid search (semantic + keyword)

#### Q: "Why not use OpenAI embeddings?"

**Trade-offs:**
- **Speed**: Local model ~1ms vs API ~100ms
- **Cost**: Free vs $0.0001 per 1K tokens
- **Privacy**: Local processing vs cloud
- **Quality**: Slightly lower but sufficient for PoC

#### Q: "How do you handle different languages?"

**Current limitation**: English-only model

**Solutions:**
- Multilingual models (paraphrase-multilingual-MiniLM-L12-v2)
- Language detection + model switching
- Translation preprocessing

#### Q: "What about real video files?"

**Current approach**: Pre-transcribed text only

**Extensions needed:**
- Speech-to-text integration (Whisper, Google Speech)
- Timeline alignment
- Speaker diarization

## Performance Benchmarks

With 10 videos (~100 chunks):
- **Indexing**: ~500ms total (one-time)
- **Search**: <10ms per query
- **Memory usage**: ~50MB

## Common Issues & Solutions

### Issue: "Module not found"
```bash
# Make sure you're in the backend directory
cd backend
source venv/bin/activate
```

### Issue: "Port already in use"
```bash
# Change port in .env file
PORT=8001
```

### Issue: "Out of memory"
- Reduce batch size in embedding generation
- Use smaller model
- Implement pagination for large datasets

### Issue: "Error when running test_search.py"
```bash
# This happens when data is already indexed
# Use test_search_only.py instead:
python scripts/test_search_only.py

# Or clear and reload:
curl -X DELETE http://localhost:8000/index
python scripts/load_all_videos.py
```

### Issue: "Empty search results"
```bash
# Check if data is indexed:
curl http://localhost:8000/stats

# If total_videos is 0, load data:
python scripts/load_all_videos.py
```

## Test Coverage Areas

1. **Functional Testing**
   - Semantic similarity (paraphrased queries)
   - Edge cases (empty query, special characters)
   - Performance under load

2. **Integration Testing**
   - API endpoint responses
   - Error handling
   - CORS functionality

3. **Unit Testing**
   - Embedding generation
   - Vector similarity calculation
   - Chunk extraction