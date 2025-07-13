# Video Transcription Architecture

## Overview
This document outlines the technical architecture for automatic video transcription integration in the Video Semantic Search system. The transcription feature enables users to upload video files and automatically generate searchable transcripts using OpenAI Whisper.

## System Architecture

### High-Level Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Video Upload  │ →  │   Transcription  │ →  │  Semantic Search │
│   (REST API)    │    │     Pipeline     │    │   (FAISS Index) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Temp File Store │    │ Whisper + FFmpeg │    │ Vector Database │
│ (Secure Upload) │    │ (Audio → Text)   │    │ (Embeddings)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Detailed Processing Pipeline

#### 1. Video Upload & Validation
```python
# Endpoint: POST /api/videos/upload
# File: main.py:102-168

Flow:
├── File Upload (multipart/form-data)
├── Format Validation (.mp4, .avi, .mov, etc.)
├── Size Validation (max 500MB)
├── Temporary Storage (secure temp directory)
└── Background Processing Initiation
```

#### 2. Audio Extraction
```python
# Service: TranscriptionService._extract_audio()
# File: src/transcription_service.py:53-77

Flow:
├── FFmpeg Audio Extraction
├── Convert to 16kHz Mono WAV
├── Optimization for Whisper Processing
└── Temporary Audio File Creation
```

#### 3. Speech-to-Text Transcription
```python
# Service: TranscriptionService.transcribe_video()
# File: src/transcription_service.py:28-51

Flow:
├── Whisper Model Loading (base model, 74MB)
├── Audio → Text Conversion
├── Timestamp Generation
└── Segment-based Output
```

#### 4. Chunking & Indexing
```python
# Service: TranscriptionService._create_chunks()
# File: src/transcription_service.py:79-121

Flow:
├── 30-Second Chunk Creation
├── Text Embedding Generation (384-dimensional)
├── Vector Storage (FAISS)
└── Metadata Indexing
```

## Technical Components

### 1. Transcription Service (`src/transcription_service.py`)

#### Key Features:
- **OpenAI Whisper Integration**: Multiple model sizes (tiny, base, small, medium, large)
- **FFmpeg Audio Processing**: Automatic audio extraction and optimization
- **Chunking Algorithm**: Intelligent 30-second segment creation
- **Error Handling**: Comprehensive error management and cleanup

#### Configuration:
```python
class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        # Model sizes and characteristics:
        # - tiny (39MB): Fastest, lowest accuracy
        # - base (74MB): Good balance (recommended)
        # - small (244MB): Better accuracy
        # - medium (769MB): High accuracy
        # - large (1550MB): Best accuracy, slowest
```

### 2. Background Processing (`main.py`)

#### Features:
- **Non-blocking Processing**: FastAPI BackgroundTasks
- **Status Tracking**: Real-time progress monitoring
- **Resource Management**: Automatic cleanup of temporary files
- **Error Recovery**: Graceful failure handling

#### Status Management:
```python
processing_status = {
    "video_id": {
        "status": "processing|completed|failed",
        "progress": 0-100,
        "message": "Current operation description",
        "chunks_created": int,
        "duration": float
    }
}
```

### 3. Storage Architecture

#### Two-Tier Data System:

##### Tier 1: Sample Data (`/data/transcripts/`)
- **Purpose**: Demo content for immediate testing
- **Format**: Pre-transcribed JSON files
- **Content**: 10 sample videos covering various topics
- **Loading**: Manual via `scripts/load_all_videos.py`

##### Tier 2: Dynamic Uploads (In-Memory)
- **Purpose**: User-uploaded video transcripts
- **Format**: Complete VideoTranscript objects
- **Storage**: Runtime memory (search_engine.videos dict)
- **Persistence**: Lost on server restart (PoC limitation)

#### Data Flow Comparison:
```
Sample Data Flow:
JSON Files → Manual Loading → FAISS Index → Search Ready

Upload Data Flow:
Video File → Transcription → Chunking → FAISS Index → Search Ready
```

## API Design

### Upload Endpoint
```
POST /api/videos/upload
Content-Type: multipart/form-data

Parameters:
- file: Video file (required)
- title: Custom title (optional)

Response:
{
  "video_id": "video_1734353445_filename.mp4",
  "status": "processing",
  "message": "Video uploaded successfully. Transcription in progress.",
  "title": "Custom Title",
  "file_size_mb": 25.3
}
```

### Status Endpoint
```
GET /api/videos/{video_id}/status

Response (Processing):
{
  "status": "processing",
  "progress": 45,
  "message": "Extracting audio from video..."
}

Response (Completed):
{
  "status": "completed",
  "progress": 100,
  "message": "Video processed successfully",
  "chunks_created": 15,
  "duration": 450.5
}
```

### Video Management Endpoints
```
GET /api/videos                    # List all videos
GET /api/videos/{id}               # Get video details + chunks
GET /api/videos/{id}/transcript    # Get full transcript text
```

## Performance Characteristics

### Transcription Performance
| Video Length | Processing Time (CPU) | Processing Time (GPU) |
|--------------|----------------------|----------------------|
| 1 minute     | 30-60 seconds        | 3-6 seconds          |
| 5 minutes    | 3-5 minutes          | 15-30 seconds        |
| 10 minutes   | 8-10 minutes         | 1-2 minutes          |

### Model Performance Comparison
| Model | Size | Accuracy | Speed | Recommended Use |
|-------|------|----------|-------|-----------------|
| tiny  | 39MB | Basic    | Fastest | Quick testing |
| base  | 74MB | Good     | Fast    | **PoC (Current)** |
| small | 244MB| Better   | Medium  | Production balance |
| medium| 769MB| High     | Slow    | High accuracy needs |
| large | 1550MB| Best    | Slowest | Maximum accuracy |

### Search Performance
- **Embedding Generation**: ~1ms per query
- **Vector Search**: ~0.5ms across hundreds of chunks
- **End-to-end API Response**: <10ms
- **Concurrent Request Support**: Full FastAPI async support

## PoC Limitations and Scaling Considerations

### Current PoC Limitations
- **Storage**: In-memory (data lost on restart)
- **Processing**: Single server, sequential uploads
- **Authentication**: None (open API)
- **File Storage**: Temporary only (deleted after processing)

### Production Scaling Options
For production deployment, consider:
- **Persistent Storage**: PostgreSQL + pgvector for metadata and embeddings
- **Queue System**: Celery + Redis for background job processing
- **Vector Database**: Pinecone, Weaviate, or Qdrant for scalable search
- **Cloud Transcription**: AWS Transcribe or Google Cloud STT for faster processing
- **Authentication**: JWT tokens or API keys for secure access

## Monitoring

### Key Metrics
- Processing time per video minute
- Success/failure rates
- API response times
- Memory usage during processing
- Total videos processed and search queries

### Logging
```python
logger.info(f"Video upload started: {video_id}")
logger.info(f"Transcription completed: {video_id}, chunks: {len(chunks)}")
logger.error(f"Processing failed: {video_id}, error: {str(e)}")
```