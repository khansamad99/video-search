import faiss
import numpy as np
from typing import List, Tuple, Dict, Any
import pickle
import logging
from .models import VideoTranscript, TranscriptChunk

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, embedding_dim: int):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_dim: Dimension of the embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata: List[Dict[str, Any]] = []
        logger.info(f"Initialized FAISS index with dimension {embedding_dim}")
    
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Add embeddings to the index with associated metadata.
        
        Args:
            embeddings: Numpy array of embeddings (n_samples, embedding_dim)
            metadata: List of metadata dictionaries for each embedding
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        self.index.add(embeddings.astype('float32'))
        self.metadata.extend(metadata)
        logger.info(f"Added {len(embeddings)} embeddings to index. Total: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[float], List[Dict[str, Any]]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            Tuple of (distances, metadata) for top k results
        """
        if self.index.ntotal == 0:
            return [], []
        
        # Ensure query embedding is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), min(k, self.index.ntotal))
        
        # Get metadata for results
        results_metadata = [self.metadata[idx] for idx in indices[0]]
        
        # Convert distances to similarity scores (1 - normalized_distance)
        # L2 distance to similarity score
        similarities = 1 / (1 + distances[0])
        
        return similarities.tolist(), results_metadata
    
    def save(self, index_path: str, metadata_path: str):
        """Save index and metadata to disk."""
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Saved index to {index_path} and metadata to {metadata_path}")
    
    def load(self, index_path: str, metadata_path: str):
        """Load index and metadata from disk."""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        logger.info(f"Loaded index from {index_path} with {self.index.ntotal} vectors")
    
    def clear(self):
        """Clear the index and metadata."""
        self.index.reset()
        self.metadata = []
        logger.info("Cleared vector store")