import { Message } from './ChatInterface'
import React from 'react'

interface MessageBubbleProps {
  message: Message
  theme?: 'green' | 'futuristic'
  chatSenders?: string[]
}

export default function MessageBubble({ message, theme = 'green', chatSenders = [] }: MessageBubbleProps) {
  // A message is considered 'user' (right-aligned) if it's explicitly the
  // special 'user' token OR if the upload parsing marked it as from the
  // primary participant via `isFromPrimary`.
  const isUser = Boolean((message as any).isFromPrimary) || message.sender === 'user'
  const timeLabel = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const isFuturistic = theme === 'futuristic'

  // Determine display name: if parser uses single-letter IDs (A, B, ...), map them
  // to the real names provided via `chatSenders`. Otherwise, use the sender string.
  const getDisplayName = () => {
    if (typeof message.sender !== 'string' || message.sender.length === 0) return 'Unknown'

    // single-letter sender IDs (e.g. 'A', 'B') -> map to chatSenders
    if (/^[A-Z]$/.test(message.sender)) {
      const idx = message.sender.charCodeAt(0) - 65 // 'A' -> 0
      if (chatSenders && chatSenders[idx]) return chatSenders[idx]
    }

    // preserve special tokens like 'user' or 'ai' as-is
    return message.sender
  }

  const displayName = getDisplayName()

  // Avatar initial: prefer the mapped/display name's first letter, otherwise fall back to 'U'
  const avatarLetter = displayName && displayName.length > 0 ? displayName.charAt(0).toUpperCase() : 'U'

  // Keep the bubble color consistent with the brand green for non-user messages
  const standardGreenGradient = 'linear-gradient(90deg,var(--mimic-green-600),var(--mimic-green-500))'

  return (
    <div className={`flex items-end gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Left avatar for non-user messages */}
      {!isUser && (
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center font-semibold shadow-sm flex-shrink-0"
          style={
            isFuturistic
              ? { background: standardGreenGradient, color: 'white', border: '1.5px solid rgba(2,6,23,0.08)', boxShadow: '0 8px 24px rgba(2,6,23,0.08)' }
              : { background: standardGreenGradient, color: 'white', border: '1.5px solid rgba(2,6,23,0.10)', boxShadow: '0 8px 24px rgba(2,6,23,0.08)' }
          }
          aria-hidden
        >
          {avatarLetter}
        </div>
      )}

      {/* Message bubble */}
      <div className="max-w-[78%] break-words">
        <div
          className="relative p-3 rounded-2xl transition-all duration-200"
          style={{
            borderRadius: 18,
            background: isUser ? 'white' : standardGreenGradient,
            color: isUser ? 'var(--mimic-text-dark, #0f172a)' : '#ffffff',
            boxShadow: isUser ? '0 2px 8px rgba(2,6,23,0.06)' : '0 6px 18px rgba(2,6,23,0.10)',
          }}
        >
          <div className="whitespace-pre-wrap text-sm leading-6" style={{ color: isUser ? 'var(--mimic-text-dark, #0f172a)' : 'white' }}>{message.text}</div>
          <div className="text-[11px] opacity-70 mt-2 text-right" style={{ color: isUser ? 'var(--mimic-muted)' : 'rgba(255,255,255,0.85)' }}>{timeLabel}</div>
        </div>
      </div>

      {/* Right avatar for user */}
      {isUser && (
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center font-semibold shadow-sm flex-shrink-0"
          style={{
            background: 'white',
            color: 'var(--mimic-text-dark, #0f172a)',
            border: '1.5px solid rgba(15,23,42,0.12)',
            boxShadow: '0 10px 28px rgba(2,6,23,0.10)'
          }}
          aria-hidden
        >
          {avatarLetter}
        </div>
      )}
    </div>
  )
}
