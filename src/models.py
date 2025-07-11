from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TranscriptChunk(BaseModel):
    text: str
    start_time: float  # in seconds
    end_time: float
    chunk_id: str
    

class VideoTranscript(BaseModel):
    video_id: str
    title: str
    duration: float  # total duration in seconds
    chunks: List[TranscriptChunk]
    created_at: Optional[datetime] = None


class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5


class SearchResult(BaseModel):
    video_id: str
    video_title: str
    timestamp: float
    end_time: float
    matched_text: str
    relevance_score: float
    

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    processing_time_ms: float