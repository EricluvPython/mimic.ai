'use client'
import React from 'react'
type Chat = {
  id: string
  name?: string
  lastMessage?: string
  lastMessageTime?: string | number | Date
}

// ChatsSidebarProps defined below with theme support
type ChatsSidebarProps = {
  chats: Chat[]
  activeChatId?: string | null
  onSelectChat: (id: string) => void
  onNewChat: () => void
  theme?: 'green' | 'futuristic'
}

export default function ChatsSidebar({ chats, activeChatId, onSelectChat, onNewChat, theme = 'green' }: any) {
  const isFuturistic = theme === 'futuristic'
  return (
    <div className="h-full flex flex-col bg-[var(--mimic-bg)]">
      {/* Top strip */}
      <div className="top-strip h-16 flex items-center px-4 rounded-tl-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-on-dark" style={{ background: 'linear-gradient(90deg,var(--mimic-green-500),var(--mimic-green-700))' }}>M</div>
          <div className="text-on-dark">
            <div className="text-sm font-semibold">Mimic AI</div>
            <div className="text-xs opacity-80">Chats • Smart insights</div>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={onNewChat}
            className="btn-mimic px-3 py-2 text-sm rounded-lg shadow-sm btn-clean"
            style={{
              background: 'white',
              color: 'var(--mimic-green-600)',
              border: '1px solid var(--mimic-green-600)',
              boxShadow: '0 6px 18px rgba(2,6,23,0.04)'
            }}
            title="New chat"
          >
            New
          </button>
        </div>
      </div>

      <div className="p-4 flex-1 flex flex-col">
        <div className="mb-3">
          <input
            placeholder="Search chats..."
            className="w-full px-3 py-2 rounded-lg bg-[var(--mimic-surface)] border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[var(--mimic-green-500)] text-on-light"
          />
        </div>

        <div className="overflow-y-auto space-y-3 pb-6">
          {chats.map((chat: any) => {
            const isActive = activeChatId === chat.id
            return (
              <button
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors flex items-center gap-3 shadow-sm ${isActive ? 'card' : 'hover:bg-[rgba(4,120,87,0.03)]'}`}
                style={{ boxShadow: '0 6px 14px rgba(2,6,23,0.06)', backgroundColor: isActive ? 'rgba(16,185,129,0.06)' : undefined }}
              >
                <div
                  className="w-11 h-11 rounded-full flex items-center justify-center font-semibold shadow-sm"
                  style={{ background: '#f3faf6', color: 'var(--mimic-green-700)' }}
                >
                  {chat.name?.charAt(0)?.toUpperCase() || 'C'}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-on-light">{chat.name}</div>
                  <div className="text-xs text-[var(--mimic-muted)] truncate">{chat.lastMessage}</div>
                </div>
                <div className="text-[11px] text-gray-400">{chat.lastMessageTime ? new Date(chat.lastMessageTime).toLocaleDateString() : ''}</div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
