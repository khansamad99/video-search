import time
from typing import List, Optional
import logging
from .models import VideoTranscript, SearchResult, SearchResponse, SearchQuery
from .embedding_manager import EmbeddingManager
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class VideoSearchEngine:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the search engine with embedding manager and vector store."""
        self.embedding_manager = EmbeddingManager(model_name)
        self.vector_store = VectorStore(self.embedding_manager.get_embedding_dimension())
        self.videos: dict[str, VideoTranscript] = {}
        logger.info("Initialized VideoSearchEngine")
    
    def index_video(self, video: VideoTranscript):
        """
        Index a video transcript by creating embeddings for each chunk.
        
        Args:
            video: VideoTranscript object containing chunks
        """
        start_time = time.time()
        
        # Store video metadata
        self.videos[video.video_id] = video
        
        # Extract texts and create metadata
        texts = []
        metadata_list = []
        
        for chunk in video.chunks:
            texts.append(chunk.text)
            metadata_list.append({
                'video_id': video.video_id,
                'video_title': video.title,
                'chunk_id': chunk.chunk_id,
                'start_time': chunk.start_time,
                'end_time': chunk.end_time,
                'text': chunk.text
            })
        
        # Generate embeddings
        embeddings = self.embedding_manager.encode(texts)
        
        # Add to vector store
        self.vector_store.add_embeddings(embeddings, metadata_list)
        
        elapsed = time.time() - start_time
        logger.info(f"Indexed video {video.video_id} with {len(video.chunks)} chunks in {elapsed:.2f}s")
    
    def index_videos(self, videos: List[VideoTranscript]):
        """Index multiple videos."""
        for video in videos:
            self.index_video(video)
    
    def search(self, query: SearchQuery) -> SearchResponse:
        """
        Search for relevant video chunks based on the query.
        
        Args:
            query: SearchQuery object containing the search text and parameters
            
        Returns:
            SearchResponse with ranked results
        """
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.embedding_manager.encode(query.query)
        
        # Search in vector store
        similarities, metadata_list = self.vector_store.search(
            query_embedding[0], 
            k=query.top_k or 5
        )
        
        # Create search results
        results = []
        for similarity, metadata in zip(similarities, metadata_list):
            result = SearchResult(
                video_id=metadata['video_id'],
                video_title=metadata['video_title'],
                timestamp=metadata['start_time'],
                end_time=metadata['end_time'],
                matched_text=metadata['text'],
                relevance_score=float(similarity)
            )
            results.append(result)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=results,
            query=query.query,
            processing_time_ms=elapsed_ms
        )
    
    def clear_index(self):
        """Clear all indexed data."""
        self.vector_store.clear()
        self.videos.clear()
        logger.info("Cleared all indexed data")
    
    def get_stats(self) -> dict:
        """Get statistics about the indexed data."""
        return {
            'total_videos': len(self.videos),
            'total_chunks': self.vector_store.index.ntotal,
            'embedding_dimension': self.embedding_manager.get_embedding_dimension()
        }