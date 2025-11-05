"""
FastAPI Backend for Ask The Storytell AI
Handles API requests for chat, image generation, audio generation, and audio transcription
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import uvicorn
import config
from document_processor import get_processor
from storyteller import Storyteller
import tempfile
import os

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ask The Storytell AI",
    description="Witty storytelling chatbot with multimodal responses",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components on startup
processor = None
storyteller = None
conversation_sessions: Dict[str, List[Dict]] = {}  # Session-based conversation memory

@app.on_event("startup")
async def startup_event():
    """Initialize document processor and storyteller on startup"""
    global processor, storyteller
    
    logger.info("🚀 Starting Ask The Storytell AI...")
    
    # Initialize document processor
    processor = get_processor()
    
    if not processor.is_initialized():
        logger.error("❌ No PDFs found or processed. Please add PDF files to data/pdfs/")
    else:
        logger.info(f"✅ Knowledge base loaded with {len(processor.chunks)} chunks")
    
    # Initialize storyteller
    storyteller = Storyteller(processor)
    logger.info("✅ Storyteller initialized")
    
    logger.info(f"🎯 Server ready at http://{config.API_HOST}:{config.API_PORT}")


# Request/Response models
class ChatRequest(BaseModel):
    question: str
    generate_image: bool = True
    generate_audio: bool = True
    language: str = "en"
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    is_relevant: bool
    sources: list = []
    conversation_history: list = []


# API Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "name": config.STORYTELLER_NAME,
        "chunks_loaded": len(processor.chunks) if processor else 0
    }


@app.get("/api/suggestions")
async def get_suggestions():
    """Get suggested questions for the frontend"""
    return {"suggestions": config.SUGGESTED_QUESTIONS}


@app.get("/api/languages")
async def get_languages():
    """Get supported languages"""
    return {"languages": config.SUPPORTED_LANGUAGES}


@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text using Whisper"""
    temp_path = None
    try:
        logger.info(f"🎤 Received audio file: {audio.filename}, type: {audio.content_type}")
        
        # Save uploaded file temporarily with original extension
        file_ext = os.path.splitext(audio.filename)[1] if audio.filename else ".webm"
        if not file_ext:
            file_ext = ".webm"
            
        # Create temp file but keep it open so Windows doesn't delete it
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        try:
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()  # Ensure data is written to disk
            temp_path = temp_file.name
        finally:
            temp_file.close()  # Close but don't delete yet
        
        logger.info(f"📁 Saved to: {temp_path}, size: {os.path.getsize(temp_path)} bytes")
        
        # Verify file exists and is readable
        if not os.path.exists(temp_path):
            raise Exception(f"Temp file not found: {temp_path}")
        
        # Transcribe
        text = await storyteller.transcribe_audio(temp_path)
        
        logger.info(f"✅ Transcription successful: {text[:50]}...")
        return {"text": text}
        
    except Exception as e:
        logger.error(f"❌ Error transcribing audio: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.info(f"🗑️ Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temp file {temp_path}: {e}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Main chat endpoint - processes question and returns multimodal response
    Supports conversation history and multi-language
    """
    try:
        if not processor or not processor.is_initialized():
            raise HTTPException(
                status_code=503,
                detail="Knowledge base not initialized. Please add PDF files."
            )
        
        logger.info(f"📝 Question received: {request.question[:100]}...")
        
        # Get or create conversation history
        session_id = request.session_id
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
        
        conversation_history = conversation_sessions[session_id]
        
        # Generate response
        result = await storyteller.generate_response(
            question=request.question,
            generate_image=request.generate_image,
            generate_audio=request.generate_audio,
            language=request.language,
            conversation_history=conversation_history
        )
        
        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": request.question
        })
        conversation_history.append({
            "role": "assistant",
            "content": result["answer"]
        })
        
        # Trim history to max length
        if len(conversation_history) > config.MAX_CONVERSATION_HISTORY * 2:
            conversation_history = conversation_history[-config.MAX_CONVERSATION_HISTORY * 2:]
        
        conversation_sessions[session_id] = conversation_history
        
        # Normalize media URLs to absolute using request base URL to avoid broken links across origins/proxies
        try:
            base_url = str(http_request.base_url).rstrip('/')
            for key in ("image_url", "audio_url"):
                url_val = result.get(key)
                if isinstance(url_val, str) and url_val.startswith("/"):
                    result[key] = f"{base_url}{url_val}"
        except Exception as _e:
            # Non-fatal; keep relative URLs if any issue occurs
            pass

        # Add history to response
        result["conversation_history"] = conversation_history
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "knowledge_base": {
            "initialized": processor.is_initialized() if processor else False,
            "chunks": len(processor.chunks) if processor else 0
        },
        "apis": {
            "gemini": bool(config.GEMINI_API_KEY),
            "stability": bool(config.STABILITY_API_KEY) and config.IMAGE_GENERATION_ENABLED,
            "elevenlabs": bool(config.ELEVENLABS_API_KEY) and config.AUDIO_ENABLED
        }
    }


def main():
    """Run the FastAPI server"""
    uvicorn.run(
        "backend:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD,
        log_level=config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
