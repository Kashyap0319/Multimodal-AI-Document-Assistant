# 📚✨ Ask The Storytell AI

> **Ever wished you could chat with Alice in Wonderland? Or have Gulliver explain his wild travels? Now you can!**

**🎉 FULLY FUNCTIONAL PROJECT - All Features Working! 🎉**

This isn't your grandma's book club. This is an **AI-powered storytelling companion** that brings classic literature to life with:
- 🎭 **Witty, sarcastic commentary** (because who reads boring summaries?)
- 🎨 **AI-generated vintage illustrations** (straight out of a 1920s storybook)
- 🎙️ **Voice narration** (like having a storyteller in your pocket)
- 🎤 **Voice input** (ChatGPT-style recording with live duration timer)
- 💬 **Follow-up suggestions** (contextual question recommendations)
- 📖 **Actual book sources** (no hallucinations, we promise!)

## 🚀 What Makes This Cool?

Instead of just *reading* about Alice's tea party or Gulliver's giant adventures, you can **ask questions and get instant, entertaining answers** backed by the actual books!

### See It In Action

```
You: "What was the weirdest moment at the Mad Hatter's tea party?"

✨ Magic happens in 8 seconds:
1. AI scans Alice in Wonderland for relevant passages
2. Gemini crafts a witty response with emojis
3. Stability AI generates a vintage storybook illustration
4. ElevenLabs narrator reads it aloud in a warm voice
5. Sources appear: "Chapter 7, pages 52-53"

Result: "Probably when they argued about time while dunking 
        watches in tea — classic Wonderland hospitality! ☕️😂"
```

**Try asking:**
- "What happened when Alice ate the mushroom?"
- "Tell me about Gulliver waking up in Lilliput"
- "Why is the Cheshire Cat always smiling?"
- "What did Gulliver think about the giants?"

Ask something random like "What's the capital of France?" and watch it politely roast you for going off-topic! 😄

## 🎯 The Tech Magic Behind It

Think of it like this:
1. **PDFs go in** → Books get chopped into bite-sized chunks
2. **You ask a question** → AI finds the most relevant passages
3. **Gemini reads them** → Generates a witty, accurate answer
4. **Stability paints it** → Creates a beautiful vintage illustration  
5. **ElevenLabs narrates it** → Reads aloud like a professional storyteller

All in less time than it takes to find the chapter yourself!

### Why These Technologies?

| Tech | Why We Chose It | What It Does |
|------|----------------|--------------|
| **Google Gemini** | Fast, smart, affordable | Generates witty responses from book context |
| **Stability AI** | Beautiful image quality | Creates vintage storybook illustrations |
| **ElevenLabs** | Most realistic voices | Narrates answers like a professional storyteller |
| **React + Vite** | Lightning-fast dev experience | Powers the sleek chat interface |
| **FastAPI** | Modern Python framework | Handles all the backend magic |
| **SentenceTransformers** | Works on CPU, super accurate | Finds relevant book passages instantly |

**No expensive GPUs needed!** Everything runs on APIs, so your laptop won't catch fire 🔥

## 🛠️ Get It Running (5 Minutes!)

### What You'll Need

- **Python 3.9+** (check: `python --version`)
- **Node.js 18+** (check: `node --version`)
- **FFmpeg** (for voice transcription - see installation below)
- **3 Free API Keys** (takes 2 mins total):
  - [Google Gemini](https://makersuite.google.com/app/apikey) - Free tier is generous
  - [Stability AI](https://platform.stability.ai/) - $10 free credits
  - [ElevenLabs](https://elevenlabs.io/) - 10,000 free characters/month

### Installing FFmpeg (Required for Voice Input)

**Windows:**
```powershell
# Download and install via winget
winget install --id=Gyan.FFmpeg -e

# Or download manually from https://ffmpeg.org/download.html
# Add to PATH environment variable
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

### Quick Setup

#### 1️⃣ Get Your Story PDFs Ready

Drop your PDFs into the `data/pdfs/` folder. We've got Alice in Wonderland and Gulliver's Travels ready to go!

```powershell
# Already have these? Skip this step!
copy "path\to\Alice_In_Wonderland.pdf" "data\pdfs\"
copy "path\to\Gullivers_Travels.pdf" "data\pdfs\"
```

#### 2️⃣ Add Your API Keys

```powershell
# Copy the template
copy .env.example .env

# Open and add your keys
notepad .env
```

Paste in your API keys:
```env
GEMINI_API_KEY=your_gemini_key_here
STABILITY_API_KEY=your_stability_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

#### 3️⃣ Start the Backend

```powershell
# Install Python stuff
pip install -r requirements.txt

# Fire it up! (this will process the PDFs first time)
python backend.py
```

**Wait for:** `✨ Loaded 939 chunks from 2 books!` - Now you're ready!

#### 4️⃣ Start the Frontend (New Terminal!)

```powershell
cd frontend

# Install React stuff
npm install

# Launch the UI
npm run dev
```

#### 5️⃣ Open Your Browser!

Go to **http://localhost:5173** and start chatting! 🎉

## 🎮 How to Use

### Basic Chat
1. Type a question or click a suggestion pill
2. Wait ~8 seconds for the full experience
3. Enjoy the witty response, image, and narration!
4. Click "View Sources" to see where the answer came from

### Voice Input (NEW! ✨)
1. **Click the microphone button** at the bottom left
2. **Speak your question clearly** (you'll see "Recording 2.3s" with a blinking red dot)
3. **Click mic again to stop** (shows square icon while recording)
4. **Transcription appears** in the input box - edit if needed
5. **Press Enter** to send your question!

**Requirements for Voice Input:**
- FFmpeg must be installed (see setup below)
- Works in modern browsers (Chrome, Edge, Firefox)
- Powered by OpenAI Whisper for accurate transcription

### Pro Tips
- **Use voice input** for hands-free questions - just like ChatGPT!
- **Click follow-up suggestions** after each answer to continue the conversation
- **Try different languages** - It can respond in Spanish, French, Hindi, and more!
- **Ask follow-up questions** - It remembers your conversation
- **Test the limits** - Ask something random to see the witty fallback response

### What If I Ask Something Not in the Books?

The AI is smart enough to know when you're asking about something irrelevant. Try:

```
You: "What's the weather like today?"

AI: "I'm a storyteller, not a meteorologist! 😅 
     Ask me about Alice, Gulliver, or fairy tales!"
```

No hallucinations, no making stuff up - just honest, witty redirects!

## 🎨 Features That Make You Go "Wow!"

### ✅ Core Features
- **RAG-Powered Accuracy** - Answers come from actual book text, not AI's imagination
- **Witty Storyteller Tone** - Every response has personality and humor
- **Source Citations** - See exactly which book pages were used
- **Beautiful UI** - Glass morphism design, smooth animations, rotating suggestions
- **Vintage Illustrations** - Every image looks like it belongs in a 1920s storybook
- **Voice Input** ✨ - ChatGPT-style recording with Whisper transcription
- **Follow-up Suggestions** - Contextual question recommendations after each answer

### 🎁 Bonus Features
- **Voice Narration** - Professional storyteller voice reads every answer
- **Multi-Language Support** - Chat in English, Spanish, French, German, Hindi, Chinese, Japanese, Arabic, Portuguese, or Russian
- **Image Generation** - Get a custom illustration with every response
- **Conversation Memory** - Remembers the last 6 messages for context
- **Simple Recording UI** - Minimalist design with duration timer (not fancy, just functional)

## 📊 Behind the Scenes

### How the AI Stays Accurate

```
Your Question
    ↓
[Embedding Generation] - Convert to numbers
    ↓
[Semantic Search] - Find top 5 most similar book chunks
    ↓
[Relevance Check] - Score must be > 0.25 to proceed
    ↓
[Context Injection] - Feed relevant passages to Gemini
    ↓
[Witty Response] - Gemini generates answer from ONLY the context
    ↓
[Image + Audio] - Generated in parallel for speed
    ↓
Your Answer! ✨
```

### Speed Stats

| What | How Long | Notes |
|------|----------|-------|
| First PDF load | 1-2 mins | One-time setup |
| Text answer | 1-3 secs | Gemini is fast! |
| Image generation | 5-10 secs | Worth the wait |
| Audio narration | 1-2 secs | ElevenLabs magic |
| **Total response** | **~8 secs** | With ALL features on |

**Too slow?** Disable images/audio in `config.py` for instant text responses!

## 🧠 The Smart Stuff (For Nerds)

### RAG Architecture
- **Chunking Strategy**: 1200 characters with 250 overlap (keeps context together)
- **Embedding Model**: all-MiniLM-L6-v2 (384-dim vectors, CPU-friendly)
- **Retrieval**: Top-5 chunks via cosine similarity (NumPy, in-memory)
- **Threshold**: 0.25+ similarity score (filters out irrelevant queries)

### Prompt Engineering
We spent hours crafting the **perfect prompt** to make Gemini:
- Read context carefully before responding
- Quote specific details from the books
- Add witty commentary AFTER stating facts
- Admit when it doesn't know (with humor)
- Keep responses concise for narration

### Image Generation Magic
Every image prompt includes:
- Keywords extracted from your question + the answer
- Style preset: "vintage storybook illustration, Arthur Rackham style"
- Character-specific details (Alice, Gulliver, Mad Hatter, etc.)
- Negative prompts to avoid modern/photographic styles

Result: **Consistently beautiful, contextual illustrations!**

## 📁 Project Structure

```
Ask The Storytell AI/
├── 🐍 backend.py              # FastAPI server (the brain)
├── ✨ storyteller.py           # Gemini + Stability + ElevenLabs magic
├── 📚 document_processor.py   # PDF → Embeddings pipeline
├── ⚙️ config.py               # All settings in one place
├── 📦 requirements.txt        # Python packages
├── 🔐 .env                    # Your secret API keys
│
├── 📖 data/
│   └── pdfs/                  # Drop your story PDFs here
│
├── 🖼️ static/
│   ├── images/                # Generated illustrations
│   └── audio/                 # Generated narrations
│
└── 🎨 frontend/
    ├── src/
    │   ├── App.jsx            # Main chat interface
    │   ├── App.css            # Beautiful styling
    │   └── components/        # Chat bubbles, suggestions
    └── package.json
```

## 🐛 Common Issues & Fixes

### "No PDFs found!"
```powershell
# Make sure PDFs are in the right spot
dir data\pdfs\*.pdf

# If empty, copy them in
copy "path\to\your\book.pdf" "data\pdfs\"
```

### "Gemini API Error 401"
- Your API key is wrong or missing in `.env`
- Get a new one: https://makersuite.google.com/app/apikey
- Make sure there are no extra spaces in the `.env` file!

### "Responses are too slow!"
```python
# Edit config.py and turn off image/audio
IMAGE_GENERATION_ENABLED = False
AUDIO_ENABLED = False

# Restart backend - now responses in 1-3 seconds!
```

### "Frontend won't connect to backend"
- Make sure backend is running on port 9000: `http://localhost:9000/api/health`
- Check browser console for CORS errors
- Try restarting both servers

### "Images look weird"
Stability AI can be unpredictable! Try:
- Asking more specific questions
- Mentioning character names (Alice, Gulliver, etc.)
- Regenerating by asking again

## 🚀 What's Next? (Future Ideas)

- [x] **Voice Input** ✅ - Ask questions by speaking (COMPLETED!)
- [x] **Follow-up Suggestions** ✅ - Contextual question recommendations (COMPLETED!)
- [ ] **More Books** - Add Sherlock Holmes, Dracula, Grimm's Fairy Tales
- [ ] **User Uploads** - Let anyone upload their own PDFs
- [ ] **Chat History** - Save conversations for later
- [ ] **Character Voices** - Select different narrators (villain voice, hero voice, etc.)
- [ ] **Image Styles** - Choose between vintage, modern, manga, comic book
- [ ] **Export Chats** - Download conversations as PDF
- [ ] **Mobile App** - Native iOS/Android versions

**Want to contribute?** Fork the repo and send a PR! 💪

## 🏆 Why This Project Rocks

### Educational Value
- Learn **RAG architecture** (the hottest AI trend of 2024)
- Understand **multimodal AI** (text + image + audio)
- Master **prompt engineering** for better AI responses
- Practice **full-stack development** (React + Python)

### Portfolio Worthy
- **Complete system**: Frontend + Backend + AI integration
- **Modern tech stack**: Gemini, Stability AI, ElevenLabs, FastAPI, React
- **Production-ready**: Error handling, async operations, clean code
- **Impressive demo**: Show off at interviews!

### Actually Fun
- Make classic literature engaging for kids
- Explore stories in a new way
- Test the limits of AI accuracy
- See what silly questions you can ask!

## 🙏 Credits

**Built with love by Shrey** using these amazing tools:

- 🧠 **Google Gemini** - For witty, accurate responses
- 🎨 **Stability AI** - For gorgeous vintage illustrations
- 🎙️ **ElevenLabs** - For professional narration
- ⚡ **FastAPI** - For blazing-fast backend
- ⚛️ **React + Vite** - For smooth, modern UI
- 🤖 **SentenceTransformers** - For smart semantic search

Special thanks to:
- **Project Gutenberg** for free public domain books
- **Hugging Face** for amazing open-source models
- **The AI community** for constant inspiration

## 📜 License

This project is for **educational and demo purposes**. 

**Books**: Only use public domain PDFs or ones you have permission to use.

**APIs**: Respect the terms of service for Gemini, Stability AI, and ElevenLabs.

## 💬 Let's Connect!

Got questions? Want to share your experience? Found a bug?

- **Open an issue** on GitHub
- **Star this repo** if you think it's cool! ⭐
- **Share it** with fellow AI enthusiasts

---

**Made with ❤️ and ☕ | Making classic literature fun, witty, and multimodal!**

*"Because reading should be an adventure, not a chore!"* ✨📚🎭

P.S. - Try asking about the Cheshire Cat. You won't be disappointed 😏
