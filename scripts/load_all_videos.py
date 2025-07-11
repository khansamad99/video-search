import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from glob import glob

# API base URL
BASE_URL = "http://localhost:8000"

def load_all_videos():
    """Load all video transcripts from JSON files and index them."""
    
    # Get all JSON files
    json_files = glob("data/transcripts/video_*.json")
    
    if not json_files:
        print("No video JSON files found in data/transcripts/")
        return
    
    all_videos = []
    
    # Read each JSON file
    for file_path in sorted(json_files):
        print(f"Reading {file_path}...")
        with open(file_path, 'r') as f:
            video_data = json.load(f)
            all_videos.append(video_data)
    
    print(f"\nLoaded {len(all_videos)} videos")
    print("Indexing videos...")
    
    # Send to API
    response = requests.post(
        f"{BASE_URL}/index",
        json=all_videos,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success! Indexed {result['indexed_videos']} videos")
        print(f"Total videos in index: {result['total_videos']}")
        
        # Check stats
        stats_response = requests.get(f"{BASE_URL}/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"Total chunks indexed: {stats['total_chunks']}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Loading all sample videos into the search index...\n")
    load_all_videos()
    
    print("\n\nNow try searching with queries like:")
    print('- "What is AWS Lambda?"')
    print('- "How to train a neural network?"')
    print('- "Explain React hooks"')