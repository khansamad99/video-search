# Production Architecture for Video Search

## Current PoC vs Production System

### Current PoC Architecture
```
JSON Files → Load into Memory → FAISS Index (RAM) → Search
```

### Production Architecture
```
Video Files → Transcription Service → Database → Processing Pipeline → Vector Store → Search API
```

## How Real Videos Would Be Processed

### 1. Video Upload & Transcription Pipeline

```python
# Example production flow
async def process_new_video(video_file: UploadFile):
    # Step 1: Upload video to storage
    video_url = await upload_to_s3(video_file)
    
    # Step 2: Extract audio
    audio_file = extract_audio(video_url)
    
    # Step 3: Transcribe with timestamps
    transcript = await transcribe_video(audio_file)  # Using Whisper, AWS Transcribe, etc.
    
    # Step 4: Store in database
    video_id = await store_video_metadata(video_url, transcript)
    
    # Step 5: Process for search
    await index_video_transcript(video_id, transcript)
```

### 2. Transcription Services Options

#### Option A: OpenAI Whisper
```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("video_audio.mp3")

# Returns:
{
    "segments": [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "Hello, welcome to this tutorial"
        },
        ...
    ]
}
```

#### Option B: AWS Transcribe
```python
import boto3

transcribe = boto3.client('transcribe')
response = transcribe.start_transcription_job(
    TranscriptionJobName='job_name',
    Media={'MediaFileUri': 's3://bucket/video.mp4'},
    OutputBucketName='output-bucket',
    Settings={'ShowSpeakerLabels': True}
)
```

#### Option C: Google Speech-to-Text
```python
from google.cloud import speech

client = speech.SpeechClient()
response = client.recognize(config=config, audio=audio)
```

### 3. Data Storage Architecture

#### Database Schema (PostgreSQL/MongoDB)
```sql
-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    url TEXT,
    duration FLOAT,
    uploaded_at TIMESTAMP,
    processed_at TIMESTAMP
);

-- Transcripts table
CREATE TABLE transcripts (
    id UUID PRIMARY KEY,
    video_id UUID REFERENCES videos(id),
    chunk_index INTEGER,
    text TEXT,
    start_time FLOAT,
    end_time FLOAT,
    embedding_id UUID
);

-- Embeddings table (optional, or use vector DB)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    transcript_id UUID REFERENCES transcripts(id),
    vector FLOAT[]  -- or use pgvector extension
);
```

#### MongoDB Schema
```javascript
{
  "_id": "video_123",
  "title": "Machine Learning Tutorial",
  "url": "s3://videos/ml_tutorial.mp4",
  "duration": 3600,
  "transcripts": [
    {
      "chunk_id": "chunk_001",
      "text": "Welcome to machine learning...",
      "start_time": 0,
      "end_time": 30,
      "embedding": [0.23, -0.45, ...]  // Optional
    }
  ],
  "metadata": {
    "uploaded_at": "2024-01-15T10:00:00Z",
    "processed_at": "2024-01-15T10:30:00Z",
    "language": "en",
    "speaker_count": 1
  }
}
```

### 4. Production Vector Storage Options

#### Option 1: Persistent FAISS
```python
class PersistentVectorStore:
    def __init__(self, index_path="indexes/"):
        self.index_path = index_path
        self.load_or_create_index()
    
    def save_index(self):
        faiss.write_index(self.index, f"{self.index_path}/main.index")
        with open(f"{self.index_path}/metadata.pkl", 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def load_index(self):
        self.index = faiss.read_index(f"{self.index_path}/main.index")
        with open(f"{self.index_path}/metadata.pkl", 'rb') as f:
            self.metadata = pickle.load(f)
```

#### Option 2: Dedicated Vector Databases

**Pinecone:**
```python
import pinecone

pinecone.init(api_key="your-key")
index = pinecone.Index("video-search")

# Upsert vectors
index.upsert(vectors=[
    ("chunk_123", embedding.tolist(), {
        "video_id": "video_001",
        "timestamp": 30,
        "text": "chunk text"
    })
])
```

**Weaviate:**
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

client.data_object.create(
    data_object={
        "text": "chunk text",
        "video_id": "video_001",
        "timestamp": 30
    },
    class_name="VideoChunk",
    vector=embedding.tolist()
)
```

**Qdrant:**
```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
client.upsert(
    collection_name="video_chunks",
    points=[
        {
            "id": "chunk_123",
            "vector": embedding.tolist(),
            "payload": {
                "video_id": "video_001",
                "timestamp": 30
            }
        }
    ]
)
```

### 5. Complete Production Pipeline

```python
# production_pipeline.py
class VideoProcessingPipeline:
    def __init__(self):
        self.transcriber = WhisperTranscriber()
        self.chunker = TranscriptChunker(chunk_duration=30)
        self.embedder = EmbeddingManager()
        self.vector_store = PineconeVectorStore()
        self.database = PostgreSQLDatabase()
    
    async def process_video(self, video_url: str, title: str):
        # 1. Transcribe video
        transcript = await self.transcriber.transcribe(video_url)
        
        # 2. Store video metadata
        video_id = await self.database.create_video({
            "title": title,
            "url": video_url,
            "duration": transcript.duration
        })
        
        # 3. Chunk transcript
        chunks = self.chunker.chunk_transcript(transcript)
        
        # 4. Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.encode(texts)
        
        # 5. Store in database
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = await self.database.create_chunk({
                "video_id": video_id,
                "text": chunk.text,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time
            })
            
            # 6. Store in vector database
            await self.vector_store.upsert(
                id=chunk_id,
                vector=embedding,
                metadata={
                    "video_id": video_id,
                    "timestamp": chunk.start_time,
                    "text": chunk.text
                }
            )
        
        return video_id
```

### 6. API Endpoints for Production

```python
@app.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    background_tasks: BackgroundTasks
):
    # Upload to S3
    video_url = await upload_to_storage(file)
    
    # Process in background
    background_tasks.add_task(
        process_video_pipeline,
        video_url,
        title
    )
    
    return {"status": "processing", "video_url": video_url}

@app.get("/videos/{video_id}/status")
async def get_processing_status(video_id: str):
    status = await database.get_video_status(video_id)
    return {"video_id": video_id, "status": status}
```

## Cost Considerations

### Transcription Costs
- **Whisper (self-hosted)**: Free but needs GPU
- **AWS Transcribe**: $0.024/minute
- **Google Speech**: $0.016/minute
- **Azure Speech**: $0.02/minute

### Storage Costs
- **PostgreSQL**: ~$100/month for 100GB
- **S3 Videos**: $0.023/GB/month
- **Vector DB**: 
  - Pinecone: $0.025/million vectors/month
  - Weaviate: Self-hosted or cloud
  - Qdrant: Self-hosted or cloud

### Example for 1000 Videos (1 hour each)
- Transcription: 1000 hours × $0.024 × 60 = $1,440 (one-time)
- Video Storage: 1000 × 5GB = 5TB × $0.023 = $115/month
- Vector Storage: ~100K chunks × $0.025/M = $2.5/month
- Database: ~$100/month

## Scaling Considerations

### For 10K+ Videos
1. **Distributed Processing**: Use Celery/RabbitMQ for async processing
2. **CDN**: Serve videos through CloudFront/Cloudflare
3. **Caching**: Redis for frequent queries
4. **Sharding**: Split vector index across multiple servers
5. **Read Replicas**: For database queries

### Performance Optimizations
1. **Pre-compute embeddings** during quiet hours
2. **Use GPU** for batch embedding generation
3. **Implement pagination** for large result sets
4. **Cache popular searches** in Redis
5. **Use streaming transcription** for real-time processing

## Migration Path from PoC

1. **Phase 1**: Add database storage while keeping FAISS
2. **Phase 2**: Implement video upload and transcription
3. **Phase 3**: Add background processing with queues
4. **Phase 4**: Migrate to distributed vector store
5. **Phase 5**: Add monitoring and analytics