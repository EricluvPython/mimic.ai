'use client'

import { useState, useRef } from 'react'
import ChatContainer from '@/components/ChatContainer'
import { extractTxtFromZip, extractPersonNameFromZip } from '@/lib/fileUtils'

export default function Home() {
  const [isDragging, setIsDragging] = useState(false)
  const [pendingFile, setPendingFile] = useState<{ file: File; content: string; chatName?: string } | null>(null)
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const dragCounter = useRef(0)
  const containerRef = useRef<HTMLDivElement>(null)

  // Drag and drop handlers for the entire screen
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current++
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current--
    if (dragCounter.current === 0) {
      setIsDragging(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    dragCounter.current = 0

    const files = Array.from(e.dataTransfer.files)
    
    // Check for ZIP file first, then TXT file
    const zipFile = files.find(file => file.name.endsWith('.zip'))
    const txtFile = files.find(file => file.name.endsWith('.txt'))

    if (!zipFile && !txtFile) {
      alert('Please drop a .zip or .txt file (WhatsApp chat export). ZIP files should contain a .txt file inside.')
      return
    }

    try {
      let content: string
      let extractedChatName: string | undefined = undefined

      if (zipFile) {
        // Extract TXT from ZIP
        console.log('Extracting ZIP file:', zipFile.name)
        const result = await extractTxtFromZip(zipFile)
        content = result.content
        console.log('Extracted content length:', content.length)
        console.log('First 500 chars of content:', content.substring(0, 500))
        // Extract person name from ZIP filename
        extractedChatName = extractPersonNameFromZip(zipFile.name)
        setPendingFile({ file: zipFile, content, chatName: extractedChatName })
      } else if (txtFile) {
        // Direct TXT file
        content = await txtFile.text()
        console.log('TXT file content length:', content.length)
        setPendingFile({ file: txtFile, content })
      } else {
        throw new Error('No valid file found')
      }

      if (!content || content.length === 0) {
        throw new Error('File appears to be empty')
      }

      setShowConfirmModal(true)
    } catch (error) {
      console.error('Error processing file:', error)
      alert(`Error processing file: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const handleFileProcessed = () => {
    setShowConfirmModal(false)
    setPendingFile(null)
  }

  const handleCancelUpload = () => {
    setShowConfirmModal(false)
    setPendingFile(null)
  }

  return (
    <main
      ref={containerRef}
      className="h-screen overflow-hidden"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Drag Overlay - covers entire screen */}
      {isDragging && (
        <div className="fixed inset-0 z-50 bg-whatsapp-green bg-opacity-20 border-4 border-dashed border-whatsapp-green flex items-center justify-center pointer-events-none">
          <div className="bg-white rounded-lg p-8 shadow-2xl text-center max-w-md mx-4">
            <div className="text-6xl mb-4">📄</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Drop your WhatsApp chat file here</h3>
            <p className="text-gray-600">Release to upload .txt or .zip file</p>
          </div>
        </div>
      )}

      <ChatContainer 
        pendingFile={pendingFile}
        showConfirmModal={showConfirmModal}
        onFileProcessed={handleFileProcessed}
        onCancelUpload={handleCancelUpload}
      />
    </main>
  )
}
