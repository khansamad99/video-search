# Data Storage Architecture

## Overview
This document explains the complete data storage architecture for the Video Semantic Search system, covering both sample data for testing and dynamic video uploads with transcription.

## Storage Architecture Overview

### Two-Tier Storage System

```
┌─────────────────────────────────────────────────────────────────┐
│                    Video Search Data Architecture                │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼──────┐                ┌──────▼──────┐
            │  Tier 1:     │                │  Tier 2:    │
            │ Sample Data  │                │ Upload Data │
            │ (Persistent) │                │ (Runtime)   │
            └──────────────┘                └─────────────┘
                    │                               │
        ┌───────────┼───────────┐      ┌───────────┼────────────┐
        │           │           │      │           │            │
    ┌───▼───┐  ┌───▼───┐  ┌───▼───┐ ┌──▼──┐   ┌──▼──┐   ┌───▼────┐
    │ JSON  │  │ JSON  │  │ JSON  │ │Video│   │Audio│   │In-Memory│
    │Files  │  │Files  │  │Files  │ │File │   │Temp │   │Objects  │
    │(10)   │  │(...)  │  │(...)  │ │     │   │     │   │        │
    └───────┘  └───────┘  └───────┘ └─────┘   └─────┘   └────────┘
```

## Tier 1: Sample Data Layer (`/data/transcripts/`)

### Purpose and Design
- **Immediate Testing**: Ready-to-use demo content
- **Development Support**: Consistent test data across environments
- **Documentation Examples**: Reference implementation patterns
- **CI/CD**: Reliable automated testing data

### Directory Structure
```
data/
└── transcripts/
    ├── summary.json          # Overview of all sample videos
    ├── video_001.json        # Machine Learning content
    ├── video_002.json        # Python Programming
    ├── video_003.json        # React Development
    ├── video_004.json        # AWS Services
    ├── video_005.json        # Database Concepts
    ├── video_006.json        # Software Engineering
    ├── video_007.json        # Data Science
    ├── video_008.json        # DevOps Practices
    ├── video_009.json        # System Design
    └── video_010.json        # Algorithmic Thinking
```

### Sample Data Content Structure
```json
{
  "video_id": "video_001",
  "title": "Introduction to Machine Learning",
  "duration": 1800.0,
  "chunks": [
    {
      "chunk_id": "chunk_0",
      "text": "Machine learning is a subset of artificial intelligence...",
      "start_time": 0.0,
      "end_time": 30.0
    },
    {
      "chunk_id": "chunk_1", 
      "text": "Supervised learning uses labeled training data...",
      "start_time": 30.0,
      "end_time": 60.0
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Sample Data Topics Coverage
| Video ID | Topic | Duration | Chunks | Key Concepts |
|----------|-------|----------|--------|--------------|
| video_001 | Machine Learning | 30 min | 60 | Supervised, Unsupervised, Neural Networks |
| video_002 | Python Programming | 25 min | 50 | Syntax, Functions, OOP, Libraries |
| video_003 | React Development | 28 min | 56 | Components, Hooks, State Management |
| video_004 | AWS Services | 32 min | 64 | EC2, S3, Lambda, RDS |
| video_005 | Database Concepts | 27 min | 54 | SQL, NoSQL, Normalization, Indexing |
| video_006 | Software Engineering | 30 min | 60 | Design Patterns, Testing, Architecture |
| video_007 | Data Science | 26 min | 52 | Analytics, Visualization, Statistics |
| video_008 | DevOps Practices | 29 min | 58 | CI/CD, Containers, Monitoring |
| video_009 | System Design | 31 min | 62 | Scalability, Load Balancing, Caching |
| video_010 | Algorithms | 24 min | 48 | Sorting, Searching, Complexity |

### Loading Sample Data
```bash
# Load all sample videos into the search index
python scripts/load_all_videos.py

# Verification
curl http://localhost:8000/stats
# Expected: {"total_videos": 10, "total_chunks": 564, "embedding_dimension": 384}
```

### Sample Data Use Cases
1. **Quick Demo**: Immediate search functionality demonstration
2. **Development Testing**: Consistent test data for feature development
3. **Performance Benchmarking**: Standardized dataset for performance testing
4. **User Training**: Teaching users how to use the search functionality

## Tier 2: Dynamic Upload Layer (Runtime)

### Purpose and Design
- **Real-time Processing**: Automatic transcription of uploaded videos
- **User Content**: Custom video content from end users
- **Dynamic Scaling**: Handles varying upload volumes
- **Processing Pipeline**: Complete video-to-search workflow

### Processing Workflow
```
1. Video Upload
   ├── Temporary File Storage (/tmp/tmpXXXXXX.mp4)
   ├── File Validation (format, size)
   └── Background Processing Initiation

2. Audio Extraction
   ├── FFmpeg Processing (video → audio)
   ├── Audio Optimization (16kHz mono WAV)
   └── Temporary Audio File (/tmp/tmpXXXXXX_audio.wav)

3. Transcription
   ├── Whisper Model Processing
   ├── Speech-to-Text Conversion
   └── Timestamp Generation

4. Chunking & Storage
   ├── 30-Second Chunk Creation
   ├── Embedding Generation (384-dimensional)
   ├── In-Memory Storage (search_engine.videos)
   └── FAISS Vector Index Update

5. Cleanup
   ├── Delete Temporary Video File
   ├── Delete Temporary Audio File
   └── Update Processing Status
```

### In-Memory Storage Structure
```python
# Runtime storage in SearchEngine
search_engine.videos = {
    "video_1734353445_sample.mp4": VideoTranscript(
        video_id="video_1734353445_sample.mp4",
        title="My Custom Video",
        duration=450.5,
        chunks=[...],
        created_at=datetime.now()
    ),
    # Additional uploaded videos...
}

# Vector storage in FAISS
search_engine.vector_store.index = {
    # Embeddings for all chunks (sample + uploaded)
    # Metadata mapping chunk → video information
}
```

### Status Tracking
```python
# Processing status tracking
processing_status = {
    "video_1734353445_sample.mp4": {
        "status": "completed",
        "progress": 100,
        "message": "Video processed successfully",
        "chunks_created": 15,
        "duration": 450.5
    }
}
```

## Data Flow Architecture

### Complete Data Flow Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Source   │    │   Processing    │    │    Storage      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                       │
    ┌────▼────┐              ┌────▼────┐             ┌────▼────┐
    │ Sample  │              │  JSON   │             │ FAISS   │
    │ JSON    │──────────────┤ Parsing │─────────────│ Vector  │
    │ Files   │              │         │             │ Index   │
    └─────────┘              └─────────┘             └─────────┘
         │                        ▲                       ▲
    ┌────▼────┐              ┌────┴────┐             ┌────┴────┐
    │ Video   │              │ Video   │             │In-Memory│
    │ Upload  │──────────────┤ Trans-  │─────────────│ Video   │
    │ Files   │              │ cription│             │ Objects │
    └─────────┘              └─────────┘             └─────────┘
```

### Search Integration
Both data tiers integrate seamlessly for search:

```python
# Unified search across all data
def search(self, query: SearchQuery) -> SearchResponse:
    # Searches both:
    # 1. Sample data (from /data/transcripts/)
    # 2. Uploaded video data (from uploads)
    
    query_embedding = self.embedding_manager.encode(query.query)
    similarities, metadata_list = self.vector_store.search(
        query_embedding[0], 
        k=query.top_k
    )
    
    # Results can come from either data source
    # User sees unified results regardless of source
```

## Storage Persistence Patterns

### Current Implementation (PoC)
```
Persistence Level:
├── Sample Data: ✅ Persistent (JSON files in /data/)
├── Upload Data: ❌ Runtime only (lost on restart)
├── Vector Index: ❌ In-memory (rebuilt on restart)
└── Processing Status: ❌ Runtime only
```

### Production Implementation (Planned)
```
Persistence Level:
├── Sample Data: ✅ Persistent (Version controlled)
├── Upload Data: ✅ Persistent (PostgreSQL)
├── Vector Index: ✅ Persistent (Vector DB)
├── Processing Status: ✅ Persistent (Redis/DB)
└── Original Videos: 🤔 Optional (S3/MinIO)
```

## API Data Access Patterns

### Sample Data Access
```bash
# Sample data is accessed through same API as uploaded data
curl http://localhost:8000/api/videos
# Returns: Both sample videos and uploaded videos

curl http://localhost:8000/search \
  -d '{"query": "machine learning"}'
# Searches: Both sample and uploaded content
```

### Upload Data Access
```bash
# Upload workflow
curl -X POST http://localhost:8000/api/videos/upload \
  -F "file=@video.mp4"
# Creates: New entry in dynamic storage

curl http://localhost:8000/api/videos/video_123/status
# Tracks: Processing status

curl http://localhost:8000/api/videos/video_123
# Returns: Complete video data with chunks
```

### Unified Search Experience
```bash
# Single search endpoint for all data
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "explain neural networks", 
    "top_k": 5
  }'

# Response includes results from both sources:
{
  "results": [
    {
      "video_id": "video_001",           # Sample data
      "video_title": "Machine Learning Intro",
      "timestamp": 120.0,
      "relevance_score": 0.95
    },
    {
      "video_id": "video_1734353445_upload.mp4", # Upload data
      "video_title": "My Custom ML Video",
      "timestamp": 60.0,
      "relevance_score": 0.87
    }
  ]
}
```

## Performance Characteristics

### Sample Data Performance
- **Loading Time**: ~2-3 seconds for 10 videos
- **Memory Usage**: ~50MB for 564 chunks
- **Search Performance**: <5ms for sample data queries
- **Scalability**: Linear with number of sample files

### Upload Data Performance
- **Processing Time**: 30-60 seconds per minute of video
- **Memory Growth**: ~5MB per hour of transcribed video
- **Search Performance**: <10ms including uploaded content
- **Concurrent Uploads**: Handled by background tasks

### Combined Performance
| Data Size | Videos | Chunks | Memory | Search Time |
|-----------|--------|--------|--------|-------------|
| Sample Only | 10 | 564 | 50MB | <5ms |
| + 1 Upload | 11 | ~580 | 55MB | <6ms |
| + 10 Uploads | 20 | ~1100 | 100MB | <10ms |
| + 100 Uploads | 110 | ~11000 | 800MB | <25ms |

## Data Management Operations

### Sample Data Management
```bash
# Reload sample data
curl -X DELETE http://localhost:8000/index  # Clear all
python scripts/load_all_videos.py          # Reload samples

# Verify sample data
curl http://localhost:8000/stats
# Should show: total_videos: 10, total_chunks: 564
```

### Upload Data Management
```bash
# List all videos (sample + uploaded)
curl http://localhost:8000/api/videos

# Clear everything (including uploads)
curl -X DELETE http://localhost:8000/index

# Reload only sample data
python scripts/load_all_videos.py
```

### Selective Data Operations
```python
# Future: Selective data management
DELETE /api/videos/{video_id}        # Remove specific upload
GET /api/videos?source=sample        # Filter by data source
GET /api/videos?source=upload        # Filter by data source
POST /api/videos/{id}/reindex        # Reprocess specific video
```

## Backup and Recovery

### Current State (PoC)
```
Backup Strategy:
├── Sample Data: ✅ Version controlled (git)
├── Upload Data: ❌ Lost on restart
├── Processing State: ❌ Not persistent
└── Vector Index: ❌ Rebuilt from source data
```

### Production Strategy
For production deployment:
- **Sample Data**: Version controlled with database backup
- **Upload Data**: Persistent database storage with replication
- **Vector Index**: Snapshot capability with rebuild from source
- **Processing State**: Redis persistence for job tracking

## Scaling Considerations

The current PoC architecture supports both sample data for development and dynamic uploads for real-world use. For production scaling, consider migrating to persistent storage (PostgreSQL + pgvector), distributed processing (Celery workers), and cloud vector databases (Pinecone/Weaviate).

This provides a solid foundation for development and testing while maintaining clear upgrade paths to production deployment.