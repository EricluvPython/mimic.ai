'use client'

import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import FileUpload from './FileUpload'
import { type ParsedMessage } from '@/lib/chatParser'
import dayjs from 'dayjs' // ✅ Added for date dividers

export interface Message {
  id: string
  text: string
  // allow arbitrary sender strings (e.g. 'user', 'AI', or a person's name)
  sender: string
  // mark messages that belong to the primary chat participant (used to align bubbles to the right)
  isFromPrimary?: boolean
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
  theme?: 'green' | 'futuristic'
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
  theme = 'green',
}: ChatInterfaceProps) {
  const isFuturistic = theme === 'futuristic'
  const [inputText, setInputText] = useState('')
  const [isAiMode, setIsAiMode] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const prevChatIdRef = useRef<string | null>(null)
  const prevMessagesCountRef = useRef<number>(0)

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior })
  }

  useEffect(() => {
    if (prevChatIdRef.current !== chatId) {
      scrollToBottom('auto')
    } else {
      const prevCount = prevMessagesCountRef.current || 0
      if (messages.length > prevCount) {
        scrollToBottom('smooth')
      }
    }

    prevChatIdRef.current = chatId
    prevMessagesCountRef.current = messages.length
  }, [messages, chatId])

  const handleSendMessage = async () => {
    if (!inputText.trim()) return

    const userMessage: Message = {
      id: `${chatId}-${Date.now()}`,
      text: inputText,
      sender: 'user',
      isFromPrimary: true,
      timestamp: new Date(),
    }

    onSendMessage(userMessage)
    setInputText('')

    if (isAiMode) {
      setIsProcessing(true)
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
    <div className="flex flex-col h-full bg-[var(--mimic-bg)] overflow-hidden">
      {/* Header */}
      <div className="top-strip flex items-center justify-between border-b" style={{ borderColor: 'rgba(0,0,0,0.04)' }}>
        <div className="flex items-center space-x-3">
          {onMenuClick && (
            <button
              onClick={onMenuClick}
              className="md:hidden p-2 hover:bg-green-700 rounded-full transition-colors"
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
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: 'linear-gradient(90deg,var(--mimic-green-500),var(--mimic-green-700))', color: 'white', boxShadow: '0 6px 18px rgba(16,185,129,0.12)' }}>
            <span className="text-on-dark font-bold">
              {chatName.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h2 className="font-semibold text-on-dark">{chatName}</h2>
            <p className="text-xs text-on-dark" style={{ opacity: 0.9 }}>
              {uploadedChat.length > 0
                ? `${uploadedChat.length} messages loaded • ${chatSenders.length} sender(s)`
                : 'Online'}
            </p>
          </div>
        </div>
        <FileUpload onFileUpload={onFileUpload} theme={theme} />
      </div>

    {/* Messages Area */}
    <div className="flex-1 overflow-y-auto p-4 bg-[var(--mimic-surface)]">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="mb-4">
                <div className="w-24 h-24 rounded-full flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(90deg,var(--mimic-green-500),var(--mimic-green-300))', color: 'white' }}>
                  <div className="text-4xl">💬</div>
                </div>
              </div>
            <p className="text-xl font-semibold text-on-light mb-2">No messages yet</p>
            <p className="text-sm text-[var(--mimic-muted)] mb-4">Start a conversation or upload a WhatsApp chat</p>
            {/* <div className="flex gap-2">
              <button className="px-4 py-2 bg-green-600 text-white rounded-md">Upload chat</button>
              <button className="px-4 py-2 bg-white border border-gray-200 rounded-md">Create sample</button>
            </div> */}
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
                  <MessageBubble message={message} theme={theme} chatSenders={chatSenders} />
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

      {/* ✅ AI suggestion bubbles (show when AI Mode is ON) */}
      {isAiMode && (
        <div className="px-4 py-3 flex flex-wrap gap-2 justify-center ai-area">
          {[
            'Summarize this chat 🧠',
            'Write a funny reply 😂',
            'Give me key insights 💡',
          ].map((suggestion, i) => (
            <button
              key={i}
              onClick={() => setInputText(suggestion)}
              className="text-sm px-3 py-1 rounded-full shadow-sm"
              style={isFuturistic
                ? (i === 0
                  ? { background: 'linear-gradient(90deg,#60A5FA,#3B82F6)', color: 'white', boxShadow: '0 0 6px rgba(96,165,250,0.18)' }
                  : { background: 'linear-gradient(90deg,#EFF8FF,#E9F2FF)', color: 'var(--futuristic-text-navy)' })
                : (i === 0
                  ? { background: 'linear-gradient(90deg,#34D399,#10B981)', color: 'white' }
                  : { background: '#ECFDF5', color: '#065F46' })
              }
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

  {/* Input Area */}
  <div className="p-4 border-t" style={{ background: 'transparent', borderColor: 'rgba(0,0,0,0.06)' }}>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsAiMode(!isAiMode)}
            className={`flex items-center justify-center w-12 h-12 rounded-full transition-all ${isFuturistic ? (isAiMode ? 'bg-gradient-to-r from-indigo-500 to-sky-400 text-white shadow-lg' : 'bg-white text-gray-200 hover:bg-gray-900') : (isAiMode ? 'bg-green-600 text-white shadow-lg' : 'bg-white text-gray-600 hover:bg-gray-200')}`}
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
            className="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[var(--mimic-green-500)] focus:border-transparent text-on-light bg-white"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim()}
            className={`w-12 h-12 rounded-full flex items-center justify-center hover:opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
            style={{ background: 'linear-gradient(90deg,var(--mimic-green-500),var(--mimic-green-700))', color: 'white' }}
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
          <div className="mt-2 flex items-center space-x-2 text-xs text-gray-700">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>AI Mode Active - Responses will be generated</span>
          </div>
        )}
      </div>
    </div>
  )
}
