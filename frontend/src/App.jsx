import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { BookOpen, Send, Sparkles, Volume2, Image as ImageIcon, Mic, Square, Globe, Plus, Settings, Moon, Sun, Menu, X, Clock, MessageSquare } from 'lucide-react'
import './App.css'
import ChatMessage from './components/ChatMessage'
import SuggestionPill from './components/SuggestionPill'

const API_BASE = '/api'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [currentSuggestionIndex, setCurrentSuggestionIndex] = useState(0)
  const [languages, setLanguages] = useState({})
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [darkMode, setDarkMode] = useState(false)
  const [chatHistory, setChatHistory] = useState([])
  const [currentChatTitle, setCurrentChatTitle] = useState('')
  const [followUpSuggestions, setFollowUpSuggestions] = useState([])
  const messagesEndRef = useRef(null)

  // Fetch suggestions and languages on mount
  useEffect(() => {
    axios.get(`${API_BASE}/suggestions`)
      .then(res => setSuggestions(res.data.suggestions))
      .catch(err => console.error('Error fetching suggestions:', err))
    
    axios.get(`${API_BASE}/languages`)
      .then(res => setLanguages(res.data.languages))
      .catch(err => console.error('Error fetching languages:', err))
  }, [])

  // Rotate suggestions every 5 seconds
  useEffect(() => {
    if (suggestions.length === 0) return
    
    const interval = setInterval(() => {
      setCurrentSuggestionIndex((prev) => (prev + 1) % suggestions.length)
    }, 5000)
    
    return () => clearInterval(interval)
  }, [suggestions])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
  }, [darkMode])

  // Generate chat title from first message
  useEffect(() => {
    if (messages.length > 0 && !currentChatTitle) {
      const firstUserMsg = messages.find(m => m.role === 'user')
      if (firstUserMsg) {
        const title = firstUserMsg.content.slice(0, 40) + (firstUserMsg.content.length > 40 ? '...' : '')
        setCurrentChatTitle(title)
      }
    }
  }, [messages, currentChatTitle])

  const handleNewChat = () => {
    // Save current chat to history if it has messages
    if (messages.length > 0 && currentChatTitle) {
      const chatSummary = {
        id: sessionId,
        title: currentChatTitle,
        timestamp: new Date(),
        messageCount: messages.length
      }
      setChatHistory(prev => [chatSummary, ...prev.slice(0, 9)]) // Keep last 10 chats
    }

    // Reset chat state
    setMessages([])
    setSessionId(`session_${Date.now()}`)
    setCurrentChatTitle('')
    setInputValue('')
    setFollowUpSuggestions([])
  }

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev)
  }

  const generateFollowUpSuggestions = (question, answer) => {
    // Extract key topics from question and answer
    const text = (question + ' ' + answer).toLowerCase()
    const followUps = []

    // Topic-based follow-up questions
    if (text.includes('alice') || text.includes('wonderland')) {
      followUps.push(
        "What happened next in Alice's adventure?",
        "Tell me more about the characters Alice met",
        "What was the most bizarre thing Alice saw?"
      )
    }
    if (text.includes('hatter') || text.includes('tea party')) {
      followUps.push(
        "Who else was at the tea party?",
        "Why was the Hatter so mad?",
        "What riddles did they ask at the tea party?"
      )
    }
    if (text.includes('queen') || text.includes('hearts')) {
      followUps.push(
        "What did the Queen of Hearts do?",
        "How did Alice deal with the Queen?",
        "What was the Queen's famous saying?"
      )
    }
    if (text.includes('gulliver') || text.includes('lilliput')) {
      followUps.push(
        "How did Gulliver escape?",
        "What were the Lilliputians like?",
        "What adventures came next for Gulliver?"
      )
    }
    if (text.includes('cheshire') || text.includes('cat')) {
      followUps.push(
        "What advice did the Cheshire Cat give?",
        "Why could the cat disappear?",
        "What was the cat's riddle?"
      )
    }
    if (text.includes('arabian') || text.includes('nights') || text.includes('aladdin') || text.includes('sinbad')) {
      followUps.push(
        "Tell me another Arabian Nights story",
        "What magical items appeared in the tales?",
        "How did the story end?"
      )
    }

    // Generic follow-ups if no specific topic matched
    if (followUps.length === 0) {
      followUps.push(
        "Tell me more about that",
        "What happened next in the story?",
        "Who were the other characters involved?"
      )
    }

    // Set only first 3 unique suggestions
    setFollowUpSuggestions([...new Set(followUps)].slice(0, 3))
  }

  const handleSend = async (question = null) => {
    const textToSend = question || inputValue.trim()
    
    if (!textToSend || isLoading) return

    // Add user message
    const userMessage = {
      role: 'user',
      content: textToSend,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        question: textToSend,
        generate_image: true,  // Always generate images
        generate_audio: true,  // Enable audio narration
        language: selectedLanguage,
        session_id: sessionId
      })

      const botMessage = {
        role: 'assistant',
        content: response.data.answer,
        imageUrl: response.data.image_url,
        audioUrl: response.data.audio_url,
        sources: response.data.sources,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
      
      // Generate follow-up suggestions based on the topic
      generateFollowUpSuggestions(textToSend, response.data.answer)
    } catch (error) {
      console.error('Error:', error)
      
      const errorMessage = {
        role: 'assistant',
        content: '😅 Oops! Something went wrong. Please try again!',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      })
      
      // Use better audio format if available
      let options
      try {
        options = { mimeType: 'audio/webm;codecs=opus' }
        new MediaRecorder(stream, options)
      } catch (e) {
        options = { mimeType: 'audio/webm' }
      }
      
      const recorder = new MediaRecorder(stream, options)
      const chunks = []
      let recordingStartTime = Date.now()
      
      // Start duration timer
      const durationInterval = setInterval(() => {
        setRecordingDuration((Date.now() - recordingStartTime) / 1000)
      }, 100)

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data)
        }
      }
      
      recorder.onstop = async () => {
        clearInterval(durationInterval)
        setRecordingDuration(0)
        
        const duration = (Date.now() - recordingStartTime) / 1000
        console.log('🎤 Recording stopped, duration:', duration.toFixed(1), 'seconds')
        
        const blob = new Blob(chunks, { type: 'audio/webm' })
        console.log('📦 Audio blob size:', blob.size, 'bytes')
        
        // Stop stream tracks
        stream.getTracks().forEach(track => track.stop())
        
        if (blob.size < 1000) {
          alert('❌ No audio detected. Please try again and speak clearly.')
          return
        }
        
        const formData = new FormData()
        formData.append('audio', blob, 'recording.webm')

        try {
          setIsLoading(true)
          console.log('🚀 Sending audio for transcription...')
          
          const response = await axios.post(`${API_BASE}/transcribe`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          
          console.log('✅ Transcription received:', response.data.text)
          setInputValue(response.data.text)
          setIsLoading(false)
          
          // Focus input for editing
          setTimeout(() => {
            document.querySelector('.chat-input')?.focus()
          }, 100)
          
        } catch (error) {
          console.error('❌ Transcription error:', error)
          setIsLoading(false)
          
          const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
          console.error('Full error:', errorMsg)
          
          alert(`❌ Failed to transcribe audio.\n\n${errorMsg}\n\nPlease try typing your question instead.`)
        }
      }

      recorder.start()
      console.log('🎙️ Recording started...')
      setMediaRecorder(recorder)
      setIsRecording(true)
    } catch (error) {
      console.error('❌ Microphone access error:', error)
      alert('🎤 Microphone access denied! Please allow microphone access and try again.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop()
      setIsRecording(false)
      setMediaRecorder(null)
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const visibleSuggestions = suggestions.slice(currentSuggestionIndex, currentSuggestionIndex + 3)
  if (visibleSuggestions.length < 3 && suggestions.length >= 3) {
    visibleSuggestions.push(...suggestions.slice(0, 3 - visibleSuggestions.length))
  }

  return (
    <div className={`app-wrapper ${darkMode ? 'dark-mode' : ''}`}>
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <BookOpen size={24} />
            <span className="logo-text">Storytell AI</span>
          </div>
          <button className="new-chat-btn" onClick={handleNewChat}>
            <Plus size={18} />
            New Chat
          </button>
        </div>

        <div className="sidebar-content">
          <div className="knowledge-sources">
            <h3 className="sidebar-section-title">
              <Sparkles size={16} />
              Knowledge Sources
            </h3>
            <div className="source-list">
              <div className="source-item active">
                <div className="source-icon">🎩</div>
                <div className="source-info">
                  <div className="source-name">Alice in Wonderland</div>
                  <div className="source-meta">190 passages</div>
                </div>
              </div>
              <div className="source-item active">
                <div className="source-icon">⛵</div>
                <div className="source-info">
                  <div className="source-name">Gulliver's Travels</div>
                  <div className="source-meta">749 passages</div>
                </div>
              </div>
              <div className="source-item active">
                <div className="source-icon">🧞</div>
                <div className="source-info">
                  <div className="source-name">Arabian Nights</div>
                  <div className="source-meta">1224 passages</div>
                </div>
              </div>
            </div>
          </div>

          {chatHistory.length > 0 && (
            <div className="chat-history">
              <h3 className="sidebar-section-title">
                <Clock size={16} />
                Recent Chats
              </h3>
              <div className="history-list">
                {chatHistory.map((chat) => (
                  <div key={chat.id} className="history-item">
                    <MessageSquare size={14} />
                    <span>{chat.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          <button className="sidebar-action" onClick={toggleDarkMode}>
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
          <button className="sidebar-action">
            <Settings size={18} />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Top Bar */}
        <header className="top-bar">
          <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <div className="top-bar-title">
            <Sparkles size={20} className="title-icon" />
            <h1>Ask The Storytell AI</h1>
          </div>

          <div className="top-bar-actions">
            <div className="language-selector-compact">
              <Globe size={16} />
              <select 
                value={selectedLanguage} 
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="language-dropdown-compact"
              >
                {Object.entries(languages).map(([code, name]) => (
                  <option key={code} value={code}>{name}</option>
                ))}
              </select>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="chat-area">
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="welcome-message-modern">
                <div className="welcome-content">
                  <Sparkles size={56} className="welcome-icon-modern" />
                  <h2>Ask me anything about Alice, Gulliver, or Arabian adventures</h2>
                  <p className="welcome-hint-modern">Get witty answers • AI illustrations • Audio narration</p>
                  
                  {suggestions.length > 0 && (
                    <div className="welcome-suggestions">
                      {visibleSuggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          className="suggestion-card"
                          onClick={() => handleSend(suggestion)}
                        >
                          <MessageSquare size={16} />
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}

            {/* Follow-up suggestions after last message */}
            {!isLoading && messages.length > 0 && followUpSuggestions.length > 0 && (
              <div className="follow-up-suggestions">
                <p className="follow-up-title">💡 Continue exploring:</p>
                <div className="follow-up-pills">
                  {followUpSuggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      className="follow-up-pill"
                      onClick={() => handleSend(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {isLoading && (
              <div className="loading-indicator-modern">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>Crafting witty response...</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="input-area-modern">
          <div className="input-wrapper">
            {/* Simple recording indicator like ChatGPT */}
            {isRecording && (
              <div className="recording-indicator">
                <div className="recording-dot"></div>
                <span>Recording {recordingDuration.toFixed(1)}s</span>
              </div>
            )}
            
            <button
              onClick={toggleRecording}
              className={`mic-button-modern ${isRecording ? 'recording' : ''}`}
              disabled={isLoading}
              title={isRecording ? 'Stop recording' : 'Voice input'}
            >
              {isRecording ? <Square size={16} fill="white" /> : <Mic size={20} />}
            </button>
            
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isRecording ? "Listening..." : "Ask about Alice, Gulliver, or Arabian adventures..."}
              disabled={isLoading || isRecording}
              className="chat-input-modern chat-input"
            />
            
            <button
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || isLoading || isRecording}
              className="send-button-modern"
              title="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
