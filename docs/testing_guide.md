# Complete Testing Guide

This guide covers all testing scenarios for the Video Semantic Search system, including both manual transcript indexing and automatic video transcription workflows.

## 🚀 Quick Setup

### Prerequisites
```bash
# 1. Install system dependencies
# Mac: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html

# 2. Setup Python environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Start the API server
python main.py
```

### Verify Installation
```bash
# Check API health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "video-search"}

# Check system status
curl http://localhost:8000/stats
# Expected: {"total_videos": 0, "total_chunks": 0, "embedding_dimension": 384}
```

## 🧪 Testing Methods Overview

We provide **3 comprehensive testing approaches**:

### 1. 🎯 Postman Collection (Recommended for Full Testing)
- **File**: `Video_Search_API_Postman_Collection.json`
- **Coverage**: All endpoints including video upload
- **Best for**: Complete workflow testing, client integration testing
- **Time**: 15-30 minutes for full test suite

### 2. 🐍 Python Scripts (Automated Testing)
- **Files**: `test_upload.py`, `scripts/test_search_only.py`
- **Coverage**: Automated end-to-end testing
- **Best for**: CI/CD, development validation
- **Time**: 5-10 minutes per test

### 3. 🔧 Manual API Testing (Development)
- **Tool**: cURL commands
- **Coverage**: Individual endpoint testing
- **Best for**: Debugging, development
- **Time**: Variable

---

## 🎯 Method 1: Postman Collection Testing (Recommended)

### Setup Postman
1. **Download and Install**: [Postman Desktop App](https://www.postman.com/downloads/)
2. **Import Collection**: 
   - Open Postman
   - Click **Import** 
   - Select `Video_Search_API_Postman_Collection.json`
   - Collection appears as "Video Semantic Search API"

### Environment Configuration
The collection uses these variables (already configured):
- `baseUrl`: `http://localhost:8000`
- `video_id`: Placeholder for video IDs (updated during testing)

### Complete Testing Workflow

#### Phase 1: Basic System Testing
**Folder: "Basic Endpoints"**

1. **Health Check** 
   - Tests: API availability
   - Expected: `{"status": "healthy"}`

2. **Root Endpoint**
   - Tests: API overview and endpoint listing
   - Expected: Complete endpoint documentation

3. **Get Statistics**
   - Tests: Current system state
   - Expected: Video/chunk counts, embedding dimensions

#### Phase 2: Video Upload and Transcription
**Folder: "Video Upload & Transcription"**

4. **Upload Video for Transcription**
   - **Action**: Select a video file (MP4, AVI, MOV, etc.)
   - **Parameters**: 
     - `file`: Choose video file (max 500MB)
     - `title`: Optional custom title
   - **Expected Response**:
     ```json
     {
       "video_id": "video_1734353445_sample.mp4",
       "status": "processing",
       "message": "Video uploaded successfully. Transcription in progress.",
       "title": "My Test Video",
       "file_size_mb": 25.3
     }
     ```
   - **Action**: Copy the `video_id` for next step

5. **Check Video Processing Status**
   - **Setup**: Replace `{{video_id}}` in URL with actual video ID
   - **Action**: Run request multiple times until completion
   - **Processing Response**:
     ```json
     {
       "status": "processing",
       "progress": 45,
       "message": "Extracting audio from video..."
     }
     ```
   - **Completed Response**:
     ```json
     {
       "status": "completed",
       "progress": 100,
       "message": "Video processed successfully",
       "chunks_created": 15,
       "duration": 450.5
     }
     ```

#### Phase 3: Video Data Viewing
**Folder: "Video Data Viewing"**

6. **List All Videos**
   - **Tests**: Overview of all indexed videos
   - **Expected**: Array of videos with metadata

7. **Get Video Details**
   - **Tests**: Complete transcript with timestamps
   - **Expected**: Full video data including all chunks

8. **Get Video Transcript**
   - **Tests**: Plain text transcript extraction
   - **Expected**: Clean transcript text with word count

#### Phase 4: Search Operations
**Folder: "Search Operations"**

9. **Search Videos**
   - **Test Queries**:
     - `"machine learning basics"`
     - `"introduction to the topic"`
     - `"python programming tutorial"`
   - **Expected**: Relevant results with timestamps and scores

10. **Search with Different Query**
    - **Tests**: Search relevance and scoring
    - **Expected**: Different results based on semantic similarity

#### Phase 5: Manual Index Management
**Folder: "Index Management"**

11. **Index Video Transcripts**
    - **Tests**: Manual transcript loading
    - **Use Case**: Pre-transcribed content indexing

12. **Clear Index**
    - **Tests**: Data cleanup functionality
    - **Expected**: Complete index reset

### Testing Best Practices with Postman

#### Test Timing
- **Video Processing**: 1-minute video ≈ 30-60 seconds
- **Status Checks**: Poll every 5-10 seconds
- **Search Testing**: After video shows "completed" status

#### Sample Test Videos
Use these types of videos for comprehensive testing:
- **Short videos** (1-3 minutes): Quick validation
- **Different formats**: MP4, AVI, MOV for compatibility
- **Various content**: Technical talks, tutorials, conversations
- **Multiple languages**: Test Whisper's language detection

#### Common Test Scenarios
1. **Happy Path**: Upload → Process → Search → Find results
2. **Error Handling**: Invalid file types, oversized files
3. **Concurrent Processing**: Multiple video uploads
4. **Search Relevance**: Exact matches vs semantic similarity
5. **Edge Cases**: Empty queries, special characters

---

## 🐍 Method 2: Python Script Testing

### Automated End-to-End Testing

#### Option A: Complete Upload Testing
```bash
# Automated test with video creation
python test_upload.py
```

**What it does:**
1. Creates a 5-second test video using ffmpeg
2. Uploads video to API
3. Monitors processing status
4. Tests search functionality
5. Verifies results and cleanup

**Expected Output:**
```
Video Upload Test Script
=======================
1. Checking API health...
Health check: {'status': 'healthy', 'service': 'video-search'}

2. Uploading video...
Upload successful: {'video_id': 'video_1734...', 'status': 'processing'}

3. Checking processing status...
Attempt 1: processing - 10% - Extracting audio from video...
Attempt 15: completed - 100% - Video processed successfully!
Chunks created: 3
Video duration: 5.0 seconds

4. Testing search...
Search results: 1 matches found
First result:
  Video: Test Video for Transcription
  Timestamp: 0.0s - 5.0s
  Score: 0.756

5. Getting statistics...
Total videos indexed: 1
Total chunks: 3
```

#### Option B: Search-Only Testing (Sample Data)
```bash
# Load sample data first
python scripts/load_all_videos.py

# Test search functionality
python scripts/test_search_only.py
```

**What it does:**
1. Uses pre-loaded sample video transcripts
2. Tests various search queries
3. Measures response times
4. Validates result relevance

### Custom Python Testing
```python
import requests
import time

# Test video upload
def test_upload():
    with open("my_video.mp4", "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/videos/upload",
            files={"file": f},
            data={"title": "Test Video"}
        )
    print(response.json())

# Test search
def test_search():
    response = requests.post(
        "http://localhost:8000/search",
        json={"query": "machine learning", "top_k": 5}
    )
    print(response.json())
```

---

## 🔧 Method 3: Manual API Testing

### Sample Data Testing

#### 1. Load Sample Data
```bash
# Load 10 sample video transcripts
python scripts/load_all_videos.py
```

#### 2. Verify Data Loading
```bash
curl http://localhost:8000/stats
# Expected: {"total_videos": 10, "total_chunks": 131, "embedding_dimension": 384}
```

#### 3. Test Search Functionality
```bash
# Basic search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How to train a neural network?", "top_k": 3}'

# Programming-related search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What are React hooks?", "top_k": 5}'

# Database-related search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain database normalization", "top_k": 3}'
```

### Video Upload Testing

#### 1. Upload Video
```bash
curl -X POST http://localhost:8000/api/videos/upload \
  -F "file=@/path/to/video.mp4" \
  -F "title=My Custom Title"
```

#### 2. Check Processing Status
```bash
# Replace with actual video_id from upload response
curl http://localhost:8000/api/videos/video_1734353445_sample.mp4/status
```

#### 3. Monitor Progress
```bash
# Run this command repeatedly until status is "completed"
while true; do
  curl -s http://localhost:8000/api/videos/VIDEO_ID/status | jq '.status'
  sleep 5
done
```

#### 4. Test Search on New Video
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your video content query", "top_k": 5}'
```

### Data Management Testing

#### List All Videos
```bash
curl http://localhost:8000/api/videos
```

#### Get Video Details
```bash
curl http://localhost:8000/api/videos/VIDEO_ID
```

#### Get Full Transcript
```bash
curl http://localhost:8000/api/videos/VIDEO_ID/transcript
```

#### Clear Index
```bash
curl -X DELETE http://localhost:8000/index
```

---

## 🎯 Test Scenarios & Validation

### Functional Testing

#### 1. Video Upload Validation
- ✅ **Supported formats**: MP4, AVI, MOV, MKV, WebM
- ✅ **File size limits**: Max 500MB
- ❌ **Invalid formats**: PDF, TXT, DOC should fail
- ❌ **Oversized files**: >500MB should fail

#### 2. Transcription Accuracy
- ✅ **Clear audio**: High accuracy expected
- ✅ **Multiple speakers**: Should handle conversations
- ⚠️ **Background noise**: May reduce accuracy
- ⚠️ **Accents**: May vary in accuracy

#### 3. Search Relevance
- ✅ **Exact matches**: High relevance scores (>0.8)
- ✅ **Semantic similarity**: Related concepts found
- ✅ **Timestamp accuracy**: Results within 30-second chunks
- ❌ **Unrelated queries**: Low/no results expected

### Performance Testing

#### Response Time Benchmarks
```bash
# Measure search performance
time curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

**Expected Performance:**
- **First search**: <200ms (model loading)
- **Subsequent searches**: <10ms
- **Upload processing**: 30-60 seconds per minute of video
- **Memory usage**: ~100MB for 10,000 chunks

#### Load Testing
```bash
# Test concurrent searches
for i in {1..10}; do
  curl -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d '{"query": "test query '$i'", "top_k": 3}' &
done
wait
```

### Error Handling Testing

#### Common Error Scenarios
1. **FFmpeg missing**:
   ```bash
   # Simulate by renaming ffmpeg temporarily
   mv /usr/local/bin/ffmpeg /usr/local/bin/ffmpeg.bak
   # Test upload - should fail gracefully
   # Restore: mv /usr/local/bin/ffmpeg.bak /usr/local/bin/ffmpeg
   ```

2. **Invalid file upload**:
   ```bash
   curl -X POST http://localhost:8000/api/videos/upload \
     -F "file=@document.pdf" \
     -F "title=Invalid File"
   # Expected: 400 error with clear message
   ```

3. **Missing video ID**:
   ```bash
   curl http://localhost:8000/api/videos/nonexistent_id/status
   # Expected: 404 error
   ```

4. **Empty search query**:
   ```bash
   curl -X POST http://localhost:8000/search \
     -H "Content-Type: application/json" \
     -d '{"query": "", "top_k": 5}'
   # Expected: 400 error
   ```

---

## 🛠 Troubleshooting Guide

### Common Issues and Solutions

#### FFmpeg-related Issues
```bash
# Issue: "Processing failed: [Errno 2] No such file or directory: 'ffmpeg'"
# Solution:
# Mac: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/

# Verify installation:
ffmpeg -version
```

#### Memory Issues
```bash
# Issue: "CUDA out of memory" or high RAM usage
# Solutions:
1. Use smaller Whisper model:
   # Edit main.py: TranscriptionService(model_size="tiny")

2. Clear index periodically:
   curl -X DELETE http://localhost:8000/index

3. Process smaller videos or reduce chunk size
```

#### Search Result Issues
```bash
# Issue: No search results
# Check if data is indexed:
curl http://localhost:8000/stats

# If total_videos is 0:
python scripts/load_all_videos.py

# If total_videos > 0 but no results:
# Check query spelling and try broader terms
```

#### Performance Issues
```bash
# Issue: Slow transcription
# Solutions:
1. Use smaller video files for testing
2. Use faster Whisper model (tiny/base instead of large)
3. Consider GPU acceleration for production

# Issue: Slow searches
# Check index size:
curl http://localhost:8000/stats
# Large indexes (>100k chunks) may need optimization
```

### Debug Mode
```bash
# Run server with debug logging
PYTHONPATH=. python -m uvicorn main:app --reload --log-level debug

# Check logs for detailed error information
```

---

## 📋 Test Checklists

### Pre-deployment Checklist
- [ ] ✅ Health check returns 200
- [ ] ✅ Sample data loads successfully (10 videos)
- [ ] ✅ Search returns relevant results
- [ ] ✅ Video upload accepts valid formats
- [ ] ✅ Transcription completes successfully
- [ ] ✅ Status tracking works correctly
- [ ] ✅ All API endpoints respond properly
- [ ] ✅ Error handling works for invalid inputs
- [ ] ✅ Performance meets requirements (<10ms search)

### Production Readiness Checklist
For production deployment, consider:
- [ ] ⏳ Persistent storage (PostgreSQL + pgvector)
- [ ] ⏳ Authentication and authorization
- [ ] ⏳ Rate limiting and security
- [ ] ⏳ Monitoring and logging setup
- [ ] ⏳ Load testing and optimization

---

## 📊 Testing Reports

### Test Coverage Matrix

| Feature | Postman | Python Scripts | Manual API | Status |
|---------|---------|----------------|------------|--------|
| Video Upload | ✅ | ✅ | ✅ | Complete |
| Transcription | ✅ | ✅ | ❌ | Complete |
| Search | ✅ | ✅ | ✅ | Complete |
| Status Tracking | ✅ | ✅ | ✅ | Complete |
| Error Handling | ✅ | ⚠️ | ✅ | Partial |
| Performance | ⚠️ | ✅ | ⚠️ | Partial |
| Load Testing | ❌ | ❌ | ✅ | Minimal |

### Recommended Testing Flow

1. **Development**: Manual API testing for quick iterations
2. **Feature Testing**: Postman collection for comprehensive validation
3. **CI/CD**: Python scripts for automated testing
4. **Production**: All three methods for complete coverage

This testing guide ensures comprehensive validation of all system components and provides clear debugging steps for common issues.