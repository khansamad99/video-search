import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
from scripts.sample_data_generator import generate_sample_videos

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test the semantic search API."""
    
    print("1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.json()}\n")
    
    print("2. Checking initial stats...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Initial stats: {response.json()}\n")
    
    print("3. Loading and indexing sample videos...")
    videos = generate_sample_videos()
    
    # Convert to dict for JSON serialization
    videos_data = [video.model_dump() for video in videos]
    
    # Index videos
    response = requests.post(
        f"{BASE_URL}/index",
        json=videos_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Indexing response: {response.json()}\n")
    
    print("4. Checking stats after indexing...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Stats after indexing: {response.json()}\n")
    
    # Test queries
    test_queries = [
        "How do I train a neural network?",
        "What is supervised learning?",
        "How to create a list in Python?",
        "What are React hooks?",
        "Explain binary search trees",
        "How does AWS Lambda work?",
        "What is Flutter hot reload?",
        "How to join tables in SQL?",
        "What is multi-factor authentication?",
        "What is continuous integration?"
    ]
    
    print("5. Testing search queries...\n")
    for query in test_queries:
        print(f"Query: '{query}'")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/search",
            json={"query": query, "top_k": 3},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Processing time: {data['processing_time_ms']:.2f}ms")
            
            for i, result in enumerate(data['results'][:3], 1):
                print(f"  Result {i}:")
                print(f"    Video: {result['video_title']}")
                print(f"    Timestamp: {result['timestamp']}s - {result['end_time']}s")
                print(f"    Relevance: {result['relevance_score']:.3f}")
                print(f"    Text preview: {result['matched_text'][:100]}...")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
        
        print()

if __name__ == "__main__":
    print("Starting Video Semantic Search API Test\n")
    print("Make sure the API is running at http://localhost:8000\n")
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure the server is running.")
        print("Run: python main.py")