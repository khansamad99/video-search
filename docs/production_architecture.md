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
