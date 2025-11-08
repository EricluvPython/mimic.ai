'use client'

import { useRef, useState } from 'react'
import { extractTxtFromZip, extractPersonNameFromZip } from '@/lib/fileUtils'
import { uploadChatFile } from '@/lib/api'
import React from 'react'

interface FileUploadProps {
  onFileUpload: (content: string, fileName: string, chatName?: string) => void
  theme?: 'green' | 'futuristic'
}

export default function FileUpload({ onFileUpload, theme = 'green' }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Check if it's a text file or zip file
    const isTxt = file.name.endsWith('.txt')
    const isZip = file.name.endsWith('.zip')

    if (!isTxt && !isZip) {
      alert('Please upload a .txt or .zip file (WhatsApp chat export)')
      return
    }

    setIsUploading(true)

    try {
      let content: string
      let fileName: string
      let chatName: string | undefined = undefined
      let fileToUpload: File = file

      if (isZip) {
        // Extract TXT from ZIP
        const result = await extractTxtFromZip(file)
        content = result.content
        fileName = result.fileName
        // Extract person name from ZIP filename
        chatName = extractPersonNameFromZip(file.name)
        
        // Create a new File object from the extracted text content
        fileToUpload = new File([content], fileName, { type: 'text/plain' })
      } else {
        // Direct TXT file
        content = await file.text()
        fileName = file.name
        fileToUpload = file
      }

      // Upload to backend (don't block if this fails)
      uploadChatFile(fileToUpload)
        .then((response) => {
          console.log('Backend upload successful:', response)
          const stats = response.statistics || {}
          const successMsg = 
            `✅ Backend Upload Successful!\n\n` +
            `Messages: ${stats.total_messages || stats.messages_inserted || 0}\n` +
            `Senders: ${stats.unique_senders || stats.users_created || 0}\n` +
            (stats.date_range 
              ? `\nPeriod: ${stats.date_range.start} to ${stats.date_range.end}` 
              : '')
          
          alert(successMsg)
        })
        .catch((apiError) => {
          console.error('Backend upload failed:', apiError)
          // Silently fail or show a toast - don't block the user
        })

      // Continue with local processing immediately (don't wait for backend)
      onFileUpload(content, fileName, chatName)
      
    } catch (error) {
      console.error('Error reading file:', error)
      alert(`Error reading file: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="relative">
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.zip"
        onChange={handleFileSelect}
        className="hidden"
      />
       <button
         onClick={handleButtonClick}
         disabled={isUploading}
         className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed btn-clean"
         title="Upload WhatsApp chat export"
         style={
           theme === 'futuristic'
             ? { background: 'linear-gradient(90deg,#60A5FA,#3B82F6)', color: 'white', border: '1px solid rgba(0,0,0,0.04)' }
             : { background: 'white', color: 'var(--mimic-green-600)', border: '1px solid var(--mimic-green-600)' }
         }
       >
        {isUploading ? (
          <>
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>Uploading...</span>
          </>
        ) : (
          <>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <span>Upload Chat</span>
          </>
        )}
      </button>
    </div>
  )
}