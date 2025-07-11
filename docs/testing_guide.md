# Testing Guide 

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

