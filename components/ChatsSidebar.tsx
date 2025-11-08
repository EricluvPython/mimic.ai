'use client'

export interface Chat {
  id: string
  name: string
  lastMessage: string
  lastMessageTime: Date
  unreadCount?: number
  avatar?: string
}

interface ChatsSidebarProps {
  chats: Chat[]
  activeChatId: string | null
  onSelectChat: (chatId: string) => void
  onNewChat: () => void
}

export default function ChatsSidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
}: ChatsSidebarProps) {
  const formatTime = (date: Date) => {
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    } else if (diffInHours < 168) {
      return date.toLocaleDateString('en-US', { weekday: 'short' })
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }
  }

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200 w-full md:w-80 flex-shrink-0">
      {/* Header */}
      <div className="bg-whatsapp-dark text-white p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold">Chats</h1>
          <button
            onClick={onNewChat}
            className="p-2 hover:bg-whatsapp-darker rounded-full transition-colors"
            title="New Chat"
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
                d="M12 4v16m8-8H4"
              />
            </svg>
          </button>
        </div>
        {/* Search bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search or start new chat"
            className="w-full bg-white text-gray-800 px-4 pl-10 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-whatsapp-green"
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 absolute left-3 top-2.5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {chats.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 p-4">
            <div className="text-5xl mb-4">💬</div>
            <p className="text-sm text-center">No chats yet</p>
            <p className="text-xs text-center mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {chats.map((chat) => (
              <button
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`w-full p-4 hover:bg-gray-50 transition-colors text-left ${
                  activeChatId === chat.id ? 'bg-gray-100' : ''
                }`}
              >
                <div className="flex items-center space-x-3">
                  {/* Avatar */}
                  <div className="w-12 h-12 rounded-full bg-whatsapp-green flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-semibold text-lg">
                      {chat.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  
                  {/* Chat Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-gray-900 text-sm truncate">
                        {chat.name}
                      </h3>
                      <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                        {formatTime(chat.lastMessageTime)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600 truncate">
                        {chat.lastMessage}
                      </p>
                      {chat.unreadCount && chat.unreadCount > 0 && (
                        <span className="bg-whatsapp-green text-white text-xs rounded-full px-2 py-0.5 ml-2 flex-shrink-0">
                          {chat.unreadCount}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
