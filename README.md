# Video Semantic Search with Automatic Transcription

A video search system that automatically transcribes uploaded videos and enables semantic search across content. Built as a Proof of Concept with clear architecture for AI applications.

## 🚀 Quick Start

```bash
# 1. Setup Environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Install FFmpeg (required for video processing)
# Mac: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html

# 3. Start Server
python main.py

# 4. Test with sample data (optional)
python scripts/load_all_videos.py

# 5. Test video upload via Postman or API
```

## 🎯 Key Features

- **🎥 Automatic Video Transcription**: Upload videos, get searchable transcripts using OpenAI Whisper
- **🔍 Semantic Search**: Understands meaning, not just keywords
- **⚡ Fast Response**: <10ms search time 
- **📍 Precise Timestamps**: Returns exact video timestamps (±30 seconds)
- **🔄 Background Processing**: Non-blocking video processing with status tracking
- **📊 RESTful API**: Complete API for upload, transcription, and search

## 🏗 System Architecture

### Processing Pipeline
```
Video Upload → Audio Extraction → Whisper Transcription → 
30s Chunking → Embedding Generation → FAISS Index → Search Ready
```

### Two-Tier Data System
1. **Sample Data** (`/data/transcripts/`): 10 pre-loaded demo videos for testing
2. **Upload Data** (In-Memory): User-uploaded videos with automatic transcription

Both integrate seamlessly for unified search experience.

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application with transcription endpoints
├── requirements.txt           # Dependencies (includes Whisper, FFmpeg)
├── src/                      # Core engine modules
│   ├── models.py             # Pydantic data models
│   ├── embedding_manager.py  # Sentence Transformers integration
│   ├── vector_store.py       # FAISS vector storage
│   ├── search_engine.py      # Search orchestration
│   └── transcription_service.py  # Whisper transcription
├── scripts/                  # Utility scripts
│   ├── load_all_videos.py    # Load sample data
│   ├── test_search_only.py   # Search testing
│   └── test_upload.py        # Upload testing
├── data/transcripts/         # Sample video data (10 videos)
├── docs/                     # Complete Documentation
│   ├── testing_guide.md      # Complete testing workflows
│   ├── postman_collection_guide.md  # Postman instructions
│   ├── transcription_architecture.md  # Technical design
│   └── data_storage_architecture.md   # Storage and data flow
├── Video_Search_API_Postman_Collection.json  # Ready-to-import collection
```

## 🔌 API Endpoints

### Core Operations
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | API overview |
| `/health` | GET | Health check |
| `/stats` | GET | System statistics |
| `/search` | POST | Semantic search across all videos |

### Video Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/videos/upload` | POST | Upload video for transcription |
| `/api/videos` | GET | List all indexed videos |
| `/api/videos/{id}` | GET | Get video details + transcript chunks |
| `/api/videos/{id}/status` | GET | Check processing status |
| `/api/videos/{id}/transcript` | GET | Get full transcript text |

## 🎬 Usage Example

### 1. Upload Video
```bash
curl -X POST http://localhost:8000/api/videos/upload \
  -F "file=@my_video.mp4" \
  -F "title=My Video"
```

Response:
```json
{
  "video_id": "video_1734353445_my_video.mp4",
  "status": "processing",
  "message": "Video uploaded successfully. Transcription in progress."
}
```

### 2. Check Processing Status
```bash
curl http://localhost:8000/api/videos/video_1734353445_my_video.mp4/status
```

### 3. Search Content
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning concepts", "top_k": 5}'
```

Response:
```json
{
  "results": [{
    "video_id": "video_1734353445_my_video.mp4",
    "video_title": "My Video",
    "timestamp": 120.0,
    "end_time": 150.0,
    "matched_text": "Machine learning is a subset of artificial intelligence...",
    "relevance_score": 0.892
  }]
}
```

## 🧪 Testing

### Option 1: Postman Collection (Recommended)
1. Import `Video_Search_API_Postman_Collection.json`
2. Follow workflow in `docs/postman_collection_guide.md`
3. Test complete upload → transcription → search pipeline

### Option 2: Python Test Script
```bash
# Automated testing with sample video creation
python test_upload.py
```

### Option 3: Sample Data Testing
```bash
# Load pre-transcribed sample videos
python scripts/load_all_videos.py

# Test search functionality
python scripts/test_search_only.py
```

## 📊 Performance

- **Transcription**: ~30-60 seconds per minute of video (CPU)
- **Search**: <10ms response time
- **Supported Formats**: MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V
- **File Size Limit**: 500MB (configurable)
- **Chunk Size**: 30-second segments

## 🛠 Troubleshooting

**FFmpeg not found**
```bash
# Install ffmpeg on your system
# Mac: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

**Empty search results**
```bash
# Check if videos are indexed
curl http://localhost:8000/stats
# If total_videos is 0, load sample data:
python scripts/load_all_videos.py
```

**Video processing fails**
- Check video format is supported
- Ensure file size is under 500MB
- Verify ffmpeg is installed

## 📋 Technical Implementation

### Technologies Used
- **Backend**: FastAPI with Python 3.8+
- **Transcription**: OpenAI Whisper (base model, 74MB)
- **Audio Processing**: FFmpeg
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2, 384-dim)
- **Vector Search**: FAISS (in-memory)
- **Background Processing**: FastAPI BackgroundTasks

### Current Limitations (PoC)
- **Storage**: In-memory (data lost on restart)
- **Concurrency**: Single server processing
- **Authentication**: None (open API)
- **File Storage**: Temporary only (videos deleted after processing)

For production scaling considerations, see `docs/transcription_architecture.md`.

## 📖 Documentation

- **`docs/testing_guide.md`**: Complete testing workflows 
- **`docs/transcription_architecture.md`**: Technical implementation details
- **`docs/data_storage_architecture.md`**: Storage system and data flow

---

This PoC demonstrates a complete video search system with automatic transcription, suitable for AI applications requiring semantic video content search.