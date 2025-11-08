'use client'

import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import FileUpload from './FileUpload'
import { type ParsedMessage } from '@/lib/chatParser'
import dayjs from 'dayjs' // ✅ Added for date dividers

export interface Message {
  id: string
  text: string
  sender: 'user' | 'ai'
  timestamp: Date
}

interface ChatInterfaceProps {
  chatId: string
  chatName: string
  messages: Message[]
  uploadedChat?: ParsedMessage[]
  chatSenders?: string[]
  onFileUpload: (content: string, fileName?: string, chatName?: string) => void
  onSendMessage: (message: Message) => void
  onMenuClick?: () => void
}

export default function ChatInterface({
  chatId,
  chatName,
  messages,
  uploadedChat = [],
  chatSenders = [],
  onFileUpload,
  onSendMessage,
  onMenuClick,
}: ChatInterfaceProps) {
  const [inputText, setInputText] = useState('')
  const [isAiMode, setIsAiMode] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputText.trim()) return

    const userMessage: Message = {
      id: `${chatId}-${Date.now()}`,
      text: inputText,
      sender: 'user',
      timestamp: new Date(),
    }

    onSendMessage(userMessage)
    setInputText('')

    // If AI mode is on, simulate AI response (you'll integrate your AI here later)
    if (isAiMode) {
      setIsProcessing(true)
      // Simulate AI processing delay
      setTimeout(() => {
        const aiMessage: Message = {
          id: `${chatId}-${Date.now() + 1}`,
          text: 'AI response will appear here once integrated...',
          sender: 'ai',
          timestamp: new Date(),
        }
        onSendMessage(aiMessage)
        setIsProcessing(false)
      }, 1000)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden">
      {/* Header */}
      <div className="bg-whatsapp-dark text-white p-4 flex items-center justify-between border-b border-whatsapp-darker">
        <div className="flex items-center space-x-3">
          {/* Mobile Menu Button */}
          {onMenuClick && (
            <button
              onClick={onMenuClick}
              className="md:hidden p-2 hover:bg-whatsapp-darker rounded-full transition-colors"
              title="Menu"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          )}
          <div className="w-10 h-10 rounded-full bg-whatsapp-green flex items-center justify-center">
            <span className="text-white font-bold">
              {chatName.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h2 className="font-semibold">{chatName}</h2>
            <p className="text-xs text-whatsapp-light">
              {uploadedChat.length > 0
                ? `${uploadedChat.length} messages loaded • ${chatSenders.length} sender(s)`
                : 'Online'}
            </p>
          </div>
        </div>
        <FileUpload onFileUpload={onFileUpload} />
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-whatsapp-lighter">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-6xl mb-4">💬</div>
            <p className="text-lg font-medium">No messages yet</p>
            <p className="text-sm mt-2">
              Start a conversation or upload a WhatsApp chat
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {messages.map((message, i) => {
              const prev = messages[i - 1]
              const showDateHeader =
                !prev || !dayjs(message.timestamp).isSame(prev.timestamp, 'day')

              const label = dayjs(message.timestamp).isSame(dayjs(), 'day')
                ? 'Today'
                : dayjs(message.timestamp).isSame(dayjs().subtract(1, 'day'), 'day')
                ? 'Yesterday'
                : dayjs(message.timestamp).format('MMM D, YYYY')

              return (
                <div key={message.id}>
                  {showDateHeader && (
                    <div className="flex justify-center my-3">
                      <span className="text-xs text-gray-600 bg-white/70 backdrop-blur-sm px-3 py-1 rounded-full shadow-sm">
                        {label}
                      </span>
                    </div>
                  )}
                  <MessageBubble message={message} />
                </div>
              )
            })}

            {isProcessing && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
                  <div className="flex space-x-1">
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0ms' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '150ms' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '300ms' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-gray-100 p-4 border-t border-gray-300">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsAiMode(!isAiMode)}
            className={`flex items-center justify-center w-12 h-12 rounded-full transition-all ${
              isAiMode
                ? 'bg-whatsapp-green text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-200'
            }`}
            title={isAiMode ? 'AI Mode: ON' : 'AI Mode: OFF'}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </button>
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              isAiMode
                ? 'Type a message (AI will respond)...'
                : 'Type a message...'
            }
            className="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-whatsapp-green focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim()}
            className="bg-whatsapp-green text-white w-12 h-12 rounded-full flex items-center justify-center hover:bg-whatsapp-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
        {isAiMode && (
          <div className="mt-2 flex items-center space-x-2 text-xs text-whatsapp-dark">
            <div className="w-2 h-2 bg-whatsapp-green rounded-full animate-pulse"></div>
            <span>AI Mode Active - Responses will be generated</span>
          </div>
        )}
      </div>
    </div>
  )
}
