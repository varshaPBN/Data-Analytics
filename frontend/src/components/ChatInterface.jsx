import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ResultDisplay from './ResultDisplay'
import './ChatInterface.css'

function ChatInterface({ datasetId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    // Add user message
    const newUserMessage = {
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newUserMessage])

    try {
      const response = await axios.post('http://localhost:8000/api/query', {
        dataset_id: datasetId,
        query: userMessage
      })

      const assistantMessage = {
        type: 'assistant',
        content: response.data,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: {
          type: 'error',
          data: error.response?.data?.detail || error.message,
          metadata: { notes: 'An error occurred' }
        },
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-chat">
            <p>💬 Ask a question about your data!</p>
            <p className="examples">
              Try: "What are the top 5 products by sales?" or "Show me monthly trends"
            </p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            {msg.type === 'user' && (
              <div className="message-bubble user-bubble">
                {msg.content}
              </div>
            )}
            {(msg.type === 'assistant' || msg.type === 'error') && (
              <div className="message-bubble assistant-bubble">
                <ResultDisplay result={msg.content} />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-bubble assistant-bubble">
              <div className="loading">Analyzing your query...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your data..."
          disabled={loading}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="send-button"
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatInterface

