import whisper
import ffmpeg
import os
from typing import Dict, List
import logging
from .models import TranscriptChunk

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        """
        Initialize with Whisper model.
        Model sizes: tiny (39MB), base (74MB), small (244MB), medium (769MB), large (1550MB)
        Base model provides good balance between speed and accuracy for POC.
        """
        logger.info(f"Loading Whisper {model_size} model...")
        try:
            self.model = whisper.load_model(model_size)
            logger.info(f"Whisper {model_size} model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_video(self, video_path: str) -> List[Dict]:
        """
        Main method to transcribe video and return chunked transcript.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of transcript chunks with timestamps
        """
        audio_path = None
        try:
            # Extract audio from video
            audio_path = self._extract_audio(video_path)
            
            # Transcribe audio
            logger.info(f"Starting transcription of {video_path}")
            result = self.model.transcribe(
                audio_path, 
                language="en",
                task="transcribe",
                verbose=False
            )
            
            # Convert to chunks
            chunks = self._create_chunks(result['segments'])
            logger.info(f"Transcription completed: {len(chunks)} chunks created")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
        finally:
            # Clean up temporary audio file
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
    
    def _extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file using ffmpeg.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        # Generate audio file path
        audio_path = video_path.rsplit('.', 1)[0] + '_audio.wav'
        
        try:
            # Extract audio as 16kHz mono WAV (optimal for Whisper)
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream, 
                audio_path, 
                acodec='pcm_s16le',  # 16-bit PCM
                ac=1,                 # Mono
                ar='16k'              # 16kHz sample rate
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True, cmd='ffmpeg')
            logger.info(f"Audio extracted successfully to {audio_path}")
            return audio_path
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise Exception(f"Failed to extract audio: {str(e)}")
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise
    
    def _create_chunks(self, segments: List[Dict], chunk_duration: int = 30) -> List[Dict]:
        """
        Group transcript segments into chunks of specified duration.
        
        Args:
            segments: List of transcript segments from Whisper
            chunk_duration: Target chunk duration in seconds (default: 30)
            
        Returns:
            List of chunks with text and timestamps
        """
        if not segments:
            return []
        
        chunks = []
        current_text = []
        current_start = 0
        chunk_id = 0
        
        for segment in segments:
            # Check if adding this segment would exceed chunk duration
            if segment['end'] - current_start > chunk_duration and current_text:
                # Create chunk from accumulated text
                chunk_text = " ".join(current_text).strip()
                if chunk_text:  # Only add non-empty chunks
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id}",
                        "text": chunk_text,
                        "start_time": round(current_start, 2),
                        "end_time": round(segment['start'], 2)
                    })
                    chunk_id += 1
                
                # Start new chunk
                current_text = [segment['text'].strip()]
                current_start = segment['start']
            else:
                # Add segment to current chunk
                current_text.append(segment['text'].strip())
        
        # Create final chunk with remaining text
        if current_text:
            chunk_text = " ".join(current_text).strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "start_time": round(current_start, 2),
                    "end_time": round(segments[-1]['end'], 2)
                })
        
        return chunks
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported video formats."""
        return ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']