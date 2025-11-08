'use client'

import { useState, useEffect, useRef } from 'react'
import ChatsSidebar, { type Chat } from './ChatsSidebar'
import ChatInterface from './ChatInterface'
import { type Message } from './ChatInterface'
import { parseWhatsAppChat, extractSenders, type ParsedMessage } from '@/lib/chatParser'
import ConfirmModal from './ConfirmModal'
import { extractTxtFromZip, extractPersonNameFromZip } from '@/lib/fileUtils'

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
  const [chats, setChats] = useState<Chat[]>([])
  const [chatData, setChatData] = useState<Map<string, ChatData>>(new Map())
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [internalPendingFile, setInternalPendingFile] = useState<{ file: File; content: string; chatId: string; chatName?: string } | null>(null)
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
        sender: msg.sender === senders[0] ? 'user' : 'ai',
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
      setActiveChatId(newChatId)

      // Mirror the external pending file into internalPendingFile with the new chatId
      setInternalPendingFile({
        file: externalPendingFile.file,
        content: externalPendingFile.content,
        chatId: newChatId,
        chatName: inferredName,
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
    if (onCancelUpload) {
      onCancelUpload()
    } else {
      setInternalShowConfirmModal(false)
      setInternalPendingFile(null)
    }
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
    <div className="flex h-screen bg-gray-100 relative">

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

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`absolute md:relative z-50 h-full w-80 flex-shrink-0 transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <ChatsSidebar
          chats={sortedChats}
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
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
          />
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center text-gray-500">
              <button
                onClick={() => setSidebarOpen(true)}
                className="md:hidden mb-4 bg-whatsapp-green text-white px-4 py-2 rounded-lg hover:bg-whatsapp-dark transition-colors"
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
