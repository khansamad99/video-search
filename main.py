from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from typing import List, Optional
import tempfile
import shutil
import time
import json

from src.models import SearchQuery, SearchResponse, VideoTranscript
from src.search_engine import VideoSearchEngine
from src.transcription_service import TranscriptionService

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Semantic Search API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine
search_engine = VideoSearchEngine()

# Initialize transcription service
transcription_service = TranscriptionService(model_size="base")

# Store for tracking video processing status
processing_status = {}

@app.get("/")
def read_root():
    return {
        "message": "Video Semantic Search API",
        "endpoints": {
            "/search": "POST - Search for relevant video timestamps",
            "/index": "POST - Index video transcripts",
            "/stats": "GET - Get indexing statistics",
            "/health": "GET - Health check",
            "/api/videos/upload": "POST - Upload and transcribe video",
            "/api/videos": "GET - List all indexed videos",
            "/api/videos/{video_id}": "GET - Get video details and chunks",
            "/api/videos/{video_id}/status": "GET - Check video processing status",
            "/api/videos/{video_id}/transcript": "GET - Get full video transcript"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "video-search"}

@app.get("/stats")
def get_stats():
    """Get statistics about indexed videos and chunks."""
    return search_engine.get_stats()

@app.post("/search", response_model=SearchResponse)
async def search_videos(query: SearchQuery):
    """
    Search for relevant video timestamps based on semantic similarity.
    """
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = search_engine.search(query)
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/index")
async def index_videos(videos: List[VideoTranscript]):
    """
    Index video transcripts for searching.
    """
    try:
        search_engine.index_videos(videos)
        return {
            "status": "success",
            "indexed_videos": len(videos),
            "total_videos": len(search_engine.videos)
        }
    except Exception as e:
        logger.error(f"Indexing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.delete("/index")
async def clear_index():
    """Clear all indexed data."""
    search_engine.clear_index()
    return {"status": "success", "message": "Index cleared"}

@app.post("/api/videos/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """
    Upload a video file for transcription and indexing.
    Supported formats: mp4, avi, mov, mkv, webm, flv, wmv, m4v
    """
    # Validate file type
    supported_formats = transcription_service.get_supported_formats()
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in supported_formats:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"
        )
    
    # Validate file size (limit to 500MB for POC)
    max_size = 500 * 1024 * 1024  # 500MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 500MB"
        )
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            temp_path = tmp_file.name
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    # Generate video ID and title
    video_id = f"video_{int(time.time())}_{file.filename.replace(' ', '_')}"
    video_title = title or file.filename
    
    # Initialize status
    processing_status[video_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Video uploaded. Starting transcription..."
    }
    
    # Process in background
    background_tasks.add_task(
        process_video_upload,
        video_id=video_id,
        video_path=temp_path,
        video_title=video_title
    )
    
    return {
        "video_id": video_id,
        "status": "processing",
        "message": "Video uploaded successfully. Transcription in progress.",
        "title": video_title,
        "file_size_mb": round(file_size / (1024 * 1024), 2)
    }

async def process_video_upload(video_id: str, video_path: str, video_title: str):
    """Background task to process uploaded video."""
    try:
        # Update status
        processing_status[video_id]["progress"] = 10
        processing_status[video_id]["message"] = "Extracting audio from video..."
        
        # Transcribe video
        logger.info(f"Starting transcription for video {video_id}")
        chunks = transcription_service.transcribe_video(video_path)
        
        # Update status
        processing_status[video_id]["progress"] = 80
        processing_status[video_id]["message"] = "Indexing transcript chunks..."
        
        # Calculate total duration from chunks
        total_duration = chunks[-1]["end_time"] if chunks else 0
        
        # Create transcript data in expected format
        transcript_data = VideoTranscript(
            video_id=video_id,
            title=video_title,
            duration=total_duration,
            chunks=chunks
        )
        
        # Index in search engine
        search_engine.index_videos([transcript_data])
        
        # Update final status
        processing_status[video_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Video processed successfully",
            "chunks_created": len(chunks),
            "duration": total_duration
        }
        
        logger.info(f"Successfully processed video {video_id}: {len(chunks)} chunks created")
        
    except Exception as e:
        logger.error(f"Failed to process video {video_id}: {str(e)}")
        processing_status[video_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Processing failed: {str(e)}"
        }
    finally:
        # Clean up temporary file
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"Cleaned up temporary file: {video_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

@app.get("/api/videos/{video_id}/status")
async def check_video_status(video_id: str):
    """Check the processing status of an uploaded video."""
    # Check if video is being processed
    if video_id in processing_status:
        return processing_status[video_id]
    
    # Check if video exists in search engine
    if video_id in search_engine.videos:
        video = search_engine.videos[video_id]
        return {
            "status": "completed",
            "progress": 100,
            "message": "Video indexed and ready for search",
            "indexed": True,
            "chunk_count": len(video.chunks),
            "duration": video.duration,
            "title": video.title
        }
    
    # Video not found
    return {
        "status": "not_found",
        "progress": 0,
        "message": "Video not found"
    }

@app.get("/api/videos")
async def list_videos():
    """Get a list of all indexed videos."""
    videos = []
    for video_id, video in search_engine.videos.items():
        videos.append({
            "video_id": video_id,
            "title": video.title,
            "duration": video.duration,
            "chunk_count": len(video.chunks),
            "created_at": video.created_at
        })
    return {"videos": videos, "total_count": len(videos)}

@app.get("/api/videos/{video_id}")
async def get_video_details(video_id: str):
    """Get detailed information about a specific video including all chunks."""
    if video_id not in search_engine.videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = search_engine.videos[video_id]
    return {
        "video_id": video.video_id,
        "title": video.title,
        "duration": video.duration,
        "created_at": video.created_at,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time
            }
            for chunk in video.chunks
        ]
    }

@app.get("/api/videos/{video_id}/transcript")
async def get_video_transcript(video_id: str):
    """Get the full transcript of a video as plain text."""
    if video_id not in search_engine.videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = search_engine.videos[video_id]
    full_transcript = "\n".join([chunk.text for chunk in video.chunks])
    
    return {
        "video_id": video.video_id,
        "title": video.title,
        "transcript": full_transcript,
        "word_count": len(full_transcript.split())
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)