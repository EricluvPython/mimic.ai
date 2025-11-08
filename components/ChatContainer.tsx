'use client'

import { useState, useEffect, useRef } from 'react'
import ChatsSidebar from './ChatsSidebar'
import ChatInterface from './ChatInterface'
import { type Message } from './ChatInterface'
import { parseWhatsAppChat, extractSenders, type ParsedMessage } from '@/lib/chatParser'
import ConfirmModal from './ConfirmModal'
import { extractTxtFromZip, extractPersonNameFromZip } from '@/lib/fileUtils'

interface Chat {
  id: string
  name: string
  lastMessage: string
  lastMessageTime: Date
}

interface ChatData {
  id: string
  name: string
  messages: Message[]
  uploadedChat?: ParsedMessage[]
  chatSenders?: string[]
  originalFileContent?: string // Store the original TXT content
  originalFileName?: string // Store the original file name
}

interface ChatContainerProps {
  pendingFile?: { file: File; content: string; chatName?: string } | null
  showConfirmModal?: boolean
  onFileProcessed?: () => void
  onCancelUpload?: () => void
}

export default function ChatContainer({ 
  pendingFile: externalPendingFile, 
  showConfirmModal: externalShowConfirmModal, 
  onFileProcessed,
  onCancelUpload 
}: ChatContainerProps = {}) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // mark mounted to avoid CSS transition flicker on first render
    setMounted(true)
  }, [])
  // Theme state: 'green' (original) or 'futuristic'
  const [theme, setTheme] = useState<'green' | 'futuristic'>(() => {
    try {
      if (typeof window === 'undefined') return 'green'
      const t = localStorage.getItem('mimic:theme') as 'green' | 'futuristic' | null
      return t || 'green'
    } catch {
      return 'green'
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem('mimic:theme', theme)
    } catch {}
  }, [theme])
  const [chats, setChats] = useState<Chat[]>([])
  const [chatData, setChatData] = useState<Map<string, ChatData>>(new Map())
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [internalPendingFile, setInternalPendingFile] = useState<{ file: File; content: string; chatId: string; chatName?: string; prevActiveChatId?: string } | null>(null)
  const [internalShowConfirmModal, setInternalShowConfirmModal] = useState(false)

  // Use external props if provided (from page-level drag), otherwise use internal state (from button upload)
  // Prefer internalPendingFile if we created one for an external drop.
  const pendingFile = internalPendingFile ?? (externalPendingFile ? { ...externalPendingFile, chatId: activeChatId || 'default-chat' } : null)
  const showConfirmModal = externalShowConfirmModal !== undefined ? externalShowConfirmModal : internalShowConfirmModal

  // Initialize with a default chat
  useEffect(() => {
    const defaultChatId = 'default-chat'
    const defaultChat: Chat = {
      id: defaultChatId,
      name: 'New Chat',
      lastMessage: 'Start a conversation...',
      lastMessageTime: new Date(),
    }
    setChats([defaultChat])
    setActiveChatId(defaultChatId)
    setChatData(
      new Map([
        [
          defaultChatId,
          {
            id: defaultChatId,
            name: 'New Chat',
            messages: [],
          },
        ],
      ])
    )
  }, [])

  // Migration: convert any previously-processed uploaded chats that stored
  // normalized 'user'/'ai' sender tokens back to the original sender tokens
  // (and set isFromPrimary) when we mount. This fixes chats uploaded before
  // the change that preserved parsed `uploadedChat` data.
  useEffect(() => {
    setChatData((prev) => {
      let changed = false
      const newMap = new Map(prev)
      for (const [id, data] of prev.entries()) {
        if (data.uploadedChat && Array.isArray(data.uploadedChat) && data.uploadedChat.length > 0) {
          const firstMsg = data.messages && data.messages[0]
          // If messages look like old normalized form ('user'|'ai'), rebuild them
          if (firstMsg && (firstMsg.sender === 'user' || firstMsg.sender === 'ai')) {
            const senders = extractSenders(data.uploadedChat)
            const rebuilt: Message[] = data.uploadedChat.map((msg, idx) => ({
              id: `uploaded-${id}-${idx}`,
              text: msg.text,
              sender: msg.sender,
              isFromPrimary: msg.sender === senders[0],
              timestamp: msg.date,
            }))
            newMap.set(id, {
              ...data,
              messages: rebuilt,
              chatSenders: senders,
            })
            changed = true
          }
        }
      }
      return changed ? newMap : prev
    })
  }, [])

  const handleSelectChat = (chatId: string) => {
    setActiveChatId(chatId)
    setSidebarOpen(false) // Close sidebar on mobile after selection
  }

  const handleNewChat = () => {
    const newChatId = `chat-${Date.now()}`
    const newChat: Chat = {
      id: newChatId,
      name: 'New Chat',
      lastMessage: 'Start a conversation...',
      lastMessageTime: new Date(),
    }
    setChats((prev) => [newChat, ...prev])
    setActiveChatId(newChatId)
    setSidebarOpen(false) // Close sidebar on mobile after creating new chat
    setChatData((prev) => {
      const newMap = new Map(prev)
      newMap.set(newChatId, {
        id: newChatId,
        name: 'New Chat',
        messages: [],
      })
      return newMap
    })
  }

  const processFileUpload = (fileContent: string, chatId: string, fileName: string, preferredChatName?: string) => {
    try {
      console.log('Processing file upload:', { fileName, contentLength: fileContent.length })
      console.log('First 500 chars:', fileContent.substring(0, 500))
      
      if (!fileContent || fileContent.trim().length === 0) {
        throw new Error('File content is empty')
      }

      const parsedMessages = parseWhatsAppChat(fileContent)
      console.log('Parsed messages count:', parsedMessages.length)
      
      if (parsedMessages.length === 0) {
        console.warn('No messages parsed. Content preview:', fileContent.substring(0, 1000))
        // Try to identify the issue
        const lines = fileContent.split('\n').slice(0, 10)
        console.log('First 10 lines:', lines)
      }
      
      const senders = extractSenders(parsedMessages)
      console.log('Senders found:', senders)
      
      // Use preferred name (from ZIP), first sender, or filename
      const chatName = preferredChatName || (senders.length > 0 ? senders[0] : fileName.replace('.txt', ''))
      
      // Convert parsed messages to chat format - show ALL messages, not just last 50
      const chatMessages: Message[] = parsedMessages.map((msg, idx) => ({
        id: `uploaded-${chatId}-${idx}`,
        text: msg.text,
        // Keep the original sender token (e.g. 'A', 'B' or a real name). We'll
        // mark messages from the primary sender via isFromPrimary so the UI can
        // align bubbles and still resolve initials correctly.
        sender: msg.sender,
        isFromPrimary: msg.sender === senders[0],
        timestamp: msg.date,
      }))

      // Update chat data
      setChatData((prev) => {
        const newMap = new Map(prev)
        const existing = newMap.get(chatId) || {
          id: chatId,
          name: chatName,
          messages: [],
        }
        newMap.set(chatId, {
          ...existing,
          name: chatName,
          messages: chatMessages,
          uploadedChat: parsedMessages,
          chatSenders: senders,
          originalFileContent: fileContent, // Store the original TXT content
          originalFileName: fileName, // Store the original file name
        })
        return newMap
      })

      // Update chat list
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                name: chatName,
                lastMessage: chatMessages[chatMessages.length - 1]?.text || 'No messages',
                lastMessageTime: chatMessages[chatMessages.length - 1]?.timestamp || new Date(),
              }
            : chat
        )
      )

      console.log(`Chat uploaded successfully! Found ${parsedMessages.length} messages from ${senders.length} sender(s).`)
      alert(`Chat uploaded successfully! Found ${parsedMessages.length} messages from ${senders.length} sender(s).\n\nChat name: ${chatName}\nSenders: ${senders.join(', ')}`)
    } catch (error) {
      console.error('Error parsing chat:', error)
      alert('Error parsing chat file. Please make sure it\'s a valid WhatsApp export.')
    }
  }

  const handleFileUpload = (fileContent: string, chatId: string, fileName?: string, chatName?: string) => {
    // For button uploads, process immediately (no confirmation needed)
    // For drag-and-drop, the confirmation modal will be shown by the page component
    processFileUpload(fileContent, chatId, fileName || 'chat.txt', chatName)
  }

  // When an external pending file (drag-drop from page) arrives with the confirm flag,
  // create a NEW chat and associate the pending file with that chatId so the upload
  // replaces that new chat when confirmed.
  useEffect(() => {
    if (externalPendingFile && externalShowConfirmModal) {
      const newChatId = `chat-${Date.now()}`
      const inferredName =
        externalPendingFile.chatName ||
        externalPendingFile.file?.name?.replace(/\.(zip|txt)$/i, '') ||
        'New Chat'

      const newChat: Chat = {
        id: newChatId,
        name: inferredName,
        lastMessage: 'Chat file ready to upload...',
        lastMessageTime: new Date(),
      }

      setChats((prev) => [newChat, ...prev])
      setChatData((prev) => {
        const newMap = new Map(prev)
        newMap.set(newChatId, {
          id: newChatId,
          name: inferredName,
          messages: [],
        })
        return newMap
      })
      // Activate the new chat immediately so the UI shows the new conversation
      // capture previous active chat so we can restore it if the user cancels
      const previousActive = activeChatId
      setActiveChatId(newChatId)

      // Mirror the external pending file into internalPendingFile with the new chatId
      setInternalPendingFile({
        file: externalPendingFile.file,
        content: externalPendingFile.content,
        chatId: newChatId,
        chatName: inferredName,
        prevActiveChatId: previousActive ?? undefined,
      })
      // Ensure internal modal state is set too (harmless if external modal is controlling)
      setInternalShowConfirmModal(true)
    }
  }, [externalPendingFile, externalShowConfirmModal])

  const handleConfirmUpload = () => {
    if (pendingFile) {
      const targetChatId = pendingFile.chatId || activeChatId || 'default-chat'
      processFileUpload(pendingFile.content, targetChatId, pendingFile.file.name, pendingFile.chatName)
      
      if (onFileProcessed) {
        onFileProcessed()
      } else {
        setInternalShowConfirmModal(false)
        setInternalPendingFile(null)
      }
    }
  }

  const handleCancelUpload = () => {
    // If we created a temporary chat for this pending file, remove it.
    if (internalPendingFile) {
      const createdId = internalPendingFile.chatId
      const prevId = internalPendingFile.prevActiveChatId ?? null

      // Remove the chat entry and its data map
      setChatData((prev) => {
        const newMap = new Map(prev)
        newMap.delete(createdId)
        return newMap
      })

      // Remove from chats list
      setChats((prev) => prev.filter((c) => c.id !== createdId))

      // Restore previous active chat (if any)
      setActiveChatId(prevId)
    }

    if (onCancelUpload) {
      onCancelUpload()
    }

    // Clear internal modal/pending state
    setInternalShowConfirmModal(false)
    setInternalPendingFile(null)
  }

  const handleSendMessage = (message: Message, chatId: string) => {
    // Update chat data with new message
    setChatData((prev) => {
      const newMap = new Map(prev)
      const existing = newMap.get(chatId)
      if (existing) {
        newMap.set(chatId, {
          ...existing,
          messages: [...existing.messages, message],
        })
      }
      return newMap
    })

    // Update chat list with last message and sort by most recent
    setChats((prev) => {
      const updated = prev.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              lastMessage: message.text,
              lastMessageTime: message.timestamp,
            }
          : chat
      )
      // Sort by most recent first
      return updated.sort((a, b) => b.lastMessageTime.getTime() - a.lastMessageTime.getTime())
    })
  }

  // Sort chats by most recent
  const sortedChats = [...chats].sort((a, b) => b.lastMessageTime.getTime() - a.lastMessageTime.getTime())

  const activeChat = activeChatId ? chatData.get(activeChatId) : null

  return (
    <div className={`flex h-screen bg-gray-50 relative ${mounted ? 'mounted' : 'not-mounted'}`}>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={showConfirmModal}
        title="Upload WhatsApp Chat"
        message={
          pendingFile
            ? `Do you want to upload this chat file${pendingFile.chatName ? ` (${pendingFile.chatName})` : ''} to "${chatData.get(pendingFile.chatId || activeChatId || '')?.name || 'this conversation'}"? This will replace any existing messages in this chat.`
            : 'Do you want to upload this chat file? This will replace any existing messages in this chat.'
        }
        fileName={pendingFile?.file.name}
        onConfirm={handleConfirmUpload}
        onCancel={handleCancelUpload}
        confirmText="Upload"
        cancelText="Cancel"
      />

      {/* Mobile overlay and sidebar */}
      {sidebarOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-40 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="fixed z-50 left-0 top-0 h-full w-80 md:hidden">
            <ChatsSidebar
              chats={sortedChats}
              activeChatId={activeChatId}
              onSelectChat={handleSelectChat}
              onNewChat={handleNewChat}
              theme={theme}
              setTheme={setTheme}
            />
          </div>
        </>
      )}

      {/* Desktop Sidebar (always visible on md+) */}
      <div className="hidden md:block z-20 h-full w-80 flex-shrink-0">
        <ChatsSidebar
          chats={sortedChats}
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
          theme={theme}
          setTheme={setTheme}
        />
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col relative">
        {activeChat ? (
          <ChatInterface
            chatId={activeChat.id}
            chatName={activeChat.name}
            messages={activeChat.messages}
            uploadedChat={activeChat.uploadedChat}
            chatSenders={activeChat.chatSenders}
            onFileUpload={(content, fileName, chatName) => handleFileUpload(content, activeChat.id, fileName, chatName)}
            onSendMessage={(message) => handleSendMessage(message, activeChat.id)}
            onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            theme={theme}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center text-gray-500">
              <button
                onClick={() => setSidebarOpen(true)}
                className="md:hidden mb-4 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                Open Chats
              </button>
              <div className="text-6xl mb-4">💬</div>
              <p className="text-lg">Select a chat to start messaging</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
