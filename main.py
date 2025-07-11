from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from typing import List

from src.models import SearchQuery, SearchResponse, VideoTranscript
from src.search_engine import VideoSearchEngine

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

@app.get("/")
def read_root():
    return {
        "message": "Video Semantic Search API",
        "endpoints": {
            "/search": "POST - Search for relevant video timestamps",
            "/index": "POST - Index video transcripts",
            "/stats": "GET - Get indexing statistics",
            "/health": "GET - Health check"
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)