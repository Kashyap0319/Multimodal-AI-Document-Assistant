"""
Storyteller Module
Handles text generation (Gemini/OpenAI), image generation (Stability AI/OpenAI), 
audio generation (ElevenLabs), and audio transcription (Whisper)
"""

import os
import logging
import hashlib
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai
from openai import AsyncOpenAI
import whisper
import config

logger = logging.getLogger(__name__)


class Storyteller:
    """Witty storyteller with multimodal generation capabilities"""
    
    def __init__(self, document_processor):
        """
        Initialize storyteller
        
        Args:
            document_processor: Initialized DocumentProcessor instance
        """
        self.processor = document_processor
        self.openai_client = None
        self.gemini_model = None
        self.whisper_model = None
        
        # Initialize LLM based on provider
        if config.LLM_PROVIDER == "gemini" and config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(config.LLM_MODEL)
            logger.info(f"✅ Gemini initialized: {config.LLM_MODEL}")
        elif config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            logger.info(f"✅ OpenAI initialized: {config.LLM_MODEL}")
        else:
            logger.warning(f"⚠️  No valid LLM configured for provider: {config.LLM_PROVIDER}")
        
        # Initialize Whisper for audio transcription
        try:
            self.whisper_model = whisper.load_model("base")
            logger.info("✅ Whisper initialized for audio transcription")
        except Exception as e:
            logger.warning(f"⚠️  Whisper not available: {str(e)}")
    
    async def generate_response(
        self,
        question: str,
        generate_image: bool = True,
        generate_audio: bool = True,
        language: str = "en",
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Generate complete multimodal response
        
        Args:
            question: User's question
            generate_image: Whether to generate image
            generate_audio: Whether to generate audio
            language: Target language code
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with answer, image_url, audio_url, sources
        """
        if conversation_history is None:
            conversation_history = []
        
        # Retrieve relevant context - INCREASED TO 5 for better coverage
        results = self.processor.semantic_search(question, top_k=5)
        
        # Check relevance
        is_relevant = self._is_relevant(results)
        
        if not is_relevant:
            # Return witty fallback but still try to generate media so UI always shows a photo/audio
            fallback = self._get_fallback_message(language)

            image_url = None
            audio_url = None
            if generate_image and config.IMAGE_GENERATION_ENABLED:
                try:
                    image_url = await self._generate_image(question, fallback)
                except Exception as _e:
                    image_url = None

            if generate_audio and config.AUDIO_ENABLED:
                try:
                    audio_url = await self._generate_audio(fallback, language)
                except Exception as _e:
                    audio_url = None

            return {
                "answer": fallback,
                "image_url": image_url,
                "audio_url": audio_url,
                "is_relevant": False,
                "sources": []
            }
        
        # Extract context and sources
        context = "\n\n".join([chunk for chunk, _, _ in results])
        sources = [
            {
                "text": chunk[:200] + "...",
                "source": meta["source"],
                "score": f"{score:.2f}"
            }
            for chunk, meta, score in results
        ]
        
        # Generate witty text response
        answer = await self._generate_text(question, context, language, conversation_history)
        
        # Generate image and audio in parallel
        tasks = []
        if generate_image and config.IMAGE_GENERATION_ENABLED:
            tasks.append(self._generate_image(question, answer))
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))
        
        if generate_audio and config.AUDIO_ENABLED:
            tasks.append(self._generate_audio(answer, language))
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results with proper None fallback
        image_url = results[0] if not isinstance(results[0], Exception) and results[0] is not None else None
        audio_url = results[1] if not isinstance(results[1], Exception) and results[1] is not None else None
        
        return {
            "answer": answer,
            "image_url": image_url,
            "audio_url": audio_url,
            "is_relevant": True,
            "sources": sources
        }
    
    def _is_relevant(self, results: List[Tuple]) -> bool:
        """Check if retrieved results are relevant"""
        if not results:
            return False
        
        # Check average similarity score - LOWERED threshold for better recall
        avg_score = sum(score for _, _, score in results) / len(results)
        
        # Threshold for relevance (lowered from 0.3 to 0.25)
        return avg_score > 0.25
    
    def _get_fallback_message(self, language: str) -> str:
        """Get fallback message in specified language"""
        fallbacks = {
            "en": config.UNKNOWN_QUERY_RESPONSE,
            "es": "¡Espera, detente! 🤚 Eso no está en mi colección de cuentos. Estoy aquí para contar historias sobre las aventuras de Alicia en el país de las maravillas y los problemas gigantes de Gulliver, ¡no para resolver los misterios del universo! Pregúntame algo de los cuentos clásicos que realmente conozco! 📚✨",
            "fr": "Whoa, arrêtez! 🤚 Ce n'est pas dans ma collection de livres d'histoires. Je suis ici pour raconter des histoires sur les aventures d'Alice au pays des merveilles et les problèmes géants de Gulliver - pas pour résoudre les mystères de l'univers! Demandez-moi quelque chose des histoires classiques que je connais vraiment! 📚✨",
            "de": "Moment mal! 🤚 Das ist nicht in meiner Geschichtenbuch-Sammlung. Ich bin hier, um Geschichten über Alices Abenteuer im Wunderland und Gullivers Riesenprobleme zu erzählen - nicht um die Geheimnisse des Universums zu lösen! Frag mich etwas aus den klassischen Geschichten, die ich wirklich kenne! 📚✨",
            "hi": "रुको, ठहरो! 🤚 यह मेरी कहानियों के संग्रह में नहीं है। मैं यहाँ एलिस के अद्भुत देश के रोमांच और गुलिवर की विशाल समस्याओं की कहानियाँ सुनाने के लिए हूँ - ब्रह्मांड के रहस्यों को सुलझाने के लिए नहीं! मुझसे उन क्लासिक कहानियों के बारे में पूछें जो मैं वास्तव में जानता हूँ! 📚✨",
        }
        return fallbacks.get(language, fallbacks["en"])
    
    async def _generate_text(
        self, 
        question: str, 
        context: str, 
        language: str = "en",
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate witty text response using Gemini or OpenAI
        
        Args:
            question: User's question
            context: Retrieved context from books
            language: Target language code
            conversation_history: Previous conversation messages
            
        Returns:
            Witty answer string
        """
        if conversation_history is None:
            conversation_history = []
        
        try:
            # Add STRONG language instruction
            lang_name = config.SUPPORTED_LANGUAGES.get(language, "English")
            if language != "en":
                lang_instruction = f"\n\n**CRITICAL: You MUST respond ENTIRELY in {lang_name}. Do NOT use English. Translate everything to {lang_name}.**"
            else:
                lang_instruction = ""
            
            # Build prompt with conversation context
            base_prompt = config.STORYTELLER_PROMPT.format(
                context=context,
                question=question
            ) + lang_instruction
            
            if config.LLM_PROVIDER == "openai" and self.openai_client:
                # Use OpenAI
                messages = []
                
                # Add conversation history
                for msg in conversation_history[-6:]:  # Last 3 exchanges
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # Add current prompt
                messages.append({
                    "role": "user",
                    "content": base_prompt
                })
                
                response = await self.openai_client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=messages,
                    temperature=config.LLM_TEMPERATURE,
                    max_tokens=config.LLM_MAX_TOKENS
                )
                
                answer = response.choices[0].message.content.strip()
                logger.info(f"✅ OpenAI generated response ({len(answer)} chars)")
                return answer
                
            elif config.LLM_PROVIDER == "gemini" and self.gemini_model:
                # Use Gemini
                # Add conversation history to prompt
                if conversation_history:
                    history_text = "\n\nPrevious conversation:\n"
                    for msg in conversation_history[-6:]:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        history_text += f"{role}: {msg['content']}\n"
                    base_prompt = history_text + "\n" + base_prompt
                
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    base_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=config.LLM_TEMPERATURE,
                        max_output_tokens=config.LLM_MAX_TOKENS,
                    )
                )
                
                answer = response.text.strip()
                logger.info(f"✅ Gemini generated response ({len(answer)} chars)")
                return answer
            else:
                return "Sorry, text generation is not available. Please configure LLM API key."
            
        except Exception as e:
            logger.error(f"❌ Error generating text: {str(e)}", exc_info=True)
            logger.error(f"Full exception details: {repr(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            traceback.print_exc()
            # Return error with details for debugging
            return f"Oops! My wit machine broke down. Try asking again! 😅 (Error: {str(e)[:100]})"
    
    async def _generate_image(self, question: str, answer: str) -> str:
        """
        Generate AI image using Pollinations.ai (FREE, fast, reliable)
        
        Args:
            question: Original question
            answer: Generated answer
            
        Returns:
            URL to generated AI image
        """
        try:
            if not config.IMAGE_GENERATION_ENABLED:
                return None
            
            logger.info("🎨 Generating AI image from answer...")
            
            # Create enhanced image prompt from question+answer for better relevance even on fallback
            try:
                prompt = self._create_image_prompt(question, answer)
            except Exception:
                # Fallback to simple prompt from answer
                prompt = self._create_image_prompt_from_answer(answer)
            
            # Use Pollinations.ai FREE image generation
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&model=flux&nologo=true&enhance=true"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        filename = hashlib.md5(prompt.encode()).hexdigest() + ".png"
                        filepath = config.IMAGES_DIR / filename
                        
                        with open(filepath, "wb") as f:
                            f.write(image_data)
                        
                        logger.info(f"✅ AI image generated: {filename}")
                        return f"/static/images/{filename}"
                    else:
                        logger.warning(f"⚠️ Image API returned status {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Image generation error: {str(e)}")
            return None
    
    def _create_image_prompt_from_answer(self, answer: str) -> str:
        """Create AI image prompt from the answer content"""
        import re
        # Remove emojis and clean text
        clean_answer = re.sub(r'[^\w\s.,!?\'\"-]', '', answer)
        
        # Take first 2 sentences for context
        sentences = clean_answer.split('.')[:2]
        context = '. '.join(sentences).strip()
        
        # Enhanced prompt for better images
        prompt = f"""A beautiful whimsical storybook illustration of: {context}. 
        Art style: fantasy storybook painting, vibrant colors, magical atmosphere, 
        detailed characters, fairy tale aesthetic, classic literature illustration"""
        
        return prompt[:800]
    
    async def _generate_audio(self, text: str, language: str = "en") -> str:
        """
        Generate audio narration using ElevenLabs
        
        Args:
            text: Text to narrate
            language: Language code for narration
            
        Returns:
            URL path to generated audio
        """
        if not config.ELEVENLABS_API_KEY:
            logger.warning("⚠️ ELEVENLABS_API_KEY not set - skipping audio generation")
            return None
        
        if not config.AUDIO_ENABLED:
            logger.info("ℹ️ Audio generation disabled in config")
            return None
        
        try:
            logger.info(f"🎵 Starting audio generation for {len(text)} chars...")
            
            # Clean text for TTS (remove emojis)
            import re
            clean_text = re.sub(r'[^\w\s.,!?\'\"-]', '', text)
            
            if len(clean_text) == 0:
                logger.warning("⚠️ No text to generate audio from")
                return None
            
            # Call ElevenLabs API
            url = f"{config.ELEVENLABS_API_URL}/{config.ELEVENLABS_VOICE_ID}"
            
            logger.info(f"📡 Calling ElevenLabs API: {url}")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "xi-api-key": config.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": clean_text[:500],  # Limit to 500 chars for faster generation
                    "model_id": "eleven_multilingual_v2" if language != "en" else "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": config.AUDIO_STABILITY,
                        "similarity_boost": config.AUDIO_SIMILARITY_BOOST
                    }
                }
                
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ ElevenLabs API error {response.status}: {error_text}")
                        return None
                    
                    audio_data = await response.read()
                    
                    # Save audio
                    filename = hashlib.md5(clean_text.encode()).hexdigest() + ".mp3"
                    filepath = config.AUDIO_DIR / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(audio_data)
                    
                    logger.info(f"✅ Audio generated successfully: {filename} ({len(audio_data)} bytes)")
                    return f"/static/audio/{filename}"
                    
        except Exception as e:
            logger.error(f"❌ Error generating audio: {str(e)}", exc_info=True)
            return None
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not self.whisper_model:
            logger.error("❌ Whisper model not initialized")
            raise Exception("Whisper model not initialized")
        
        try:
            logger.info(f"🎙️ Transcribing audio file: {audio_path}")
            
            # Check if file exists
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            # Check file size
            file_size = os.path.getsize(audio_path)
            logger.info(f"📦 Audio file size: {file_size} bytes")
            
            if file_size < 1000:  # Less than 1KB
                logger.warning(f"⚠️ Audio file too small: {file_size} bytes")
                return "Recording too short or empty. Please speak clearly for at least 1-2 seconds."
            
            # Check if FFmpeg is available
            import shutil
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                logger.error("❌ FFmpeg not found in PATH")
                raise Exception("FFmpeg not found. Please install FFmpeg and add it to your system PATH, then restart the backend.")
            
            logger.info(f"✅ FFmpeg found at: {ffmpeg_path}")
            
            # Transcribe with language hint (Whisper handles various audio formats including webm)
            logger.info(f"🎯 Starting Whisper transcription...")
            result = await asyncio.to_thread(
                self.whisper_model.transcribe,
                audio_path,
                fp16=False,  # Disable fp16 for CPU compatibility
                language='en',  # Hint English for better accuracy
                task='transcribe'
            )
            
            text = result["text"].strip()
            
            if not text:
                logger.warning("⚠️ Transcription returned empty text")
                return "Sorry, I couldn't hear anything clearly. Please speak louder and try again."
            
            logger.info(f"✅ Audio transcribed successfully: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"❌ Error transcribing audio: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Provide helpful error message based on error type
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "av" in error_msg.lower():
                raise Exception("FFmpeg not found. Please install FFmpeg to use audio transcription. Download from: https://ffmpeg.org/download.html")
            else:
                raise Exception(f"Transcription failed: {str(e)}")
    
    def _create_image_prompt(self, question: str, answer: str) -> str:
        """
        Create optimized image prompt for Stability AI
        
        Args:
            question: User's question
            answer: Generated answer
            
        Returns:
            Image prompt string
        """
        # IMPROVED keyword detection with more story elements
        keywords = {
            'alice': 'Alice, young Victorian girl in blue dress with white apron',
            'wonderland': 'magical Wonderland with strange creatures and talking animals',
            'rabbit': 'white rabbit wearing waistcoat with pocket watch, running',
            'queen': 'Queen of Hearts with playing card soldiers, red and black',
            'hatter': 'Mad Hatter at tea party with oversized hat, teacups everywhere',
            'cheshire': 'Cheshire Cat with wide grin, purple stripes, disappearing',
            'caterpillar': 'blue caterpillar smoking hookah on giant mushroom',
            'gulliver': 'Gulliver the explorer in 18th century clothing',
            'lilliput': 'tiny Lilliputian people, miniature buildings, giant human',
            'giant': 'enormous giants, Brobdingnagians, tiny human',
            'travel': 'sailing ship, ocean voyage, exotic lands',
            'tea party': 'mad tea party with March Hare, Dormouse, chaotic table setting',
            'arabian': 'Arabian Nights, middle eastern palace, ornate decorations',
            'aladdin': 'Aladdin with magic lamp, genie, flying carpet',
            'sinbad': 'Sinbad the sailor, ship, sea monsters',
            'scheherazade': 'Scheherazade storytelling, sultan, Arabian palace',
            'genie': 'magical genie emerging from lamp, smoke, wishes',
        }
        
        combined = (question + " " + answer).lower()
        
        # Find ALL matching keywords
        found = []
        for key, desc in keywords.items():
            if key in combined:
                found.append(desc)
        
        # Build detailed scene description
        if found:
            scene = ", ".join(found[:3])  # Use up to 3 elements
        else:
            # Fallback: extract main subject from question
            scene = "classic storybook scene"
        
        # Enhanced style for better story illustration
        style = "vintage storybook illustration, detailed ink drawing with watercolor, whimsical fantasy art, Arthur Rackham style, classic children's literature, intricate details, magical atmosphere"
        
        return f"{scene}, {style}"


if __name__ == "__main__":
    # Test module
    from document_processor import get_processor
    
    async def test():
        processor = get_processor()
        storyteller = Storyteller(processor)
        
        test_question = "What was the weirdest moment at the Mad Hatter's tea party?"
        result = await storyteller.generate_response(test_question)
        
        print(f"\n✨ Question: {test_question}")
        print(f"📝 Answer: {result['answer']}")
        print(f"🖼️  Image: {result['image_url']}")
        print(f"🔊 Audio: {result['audio_url']}")
    
    asyncio.run(test())
