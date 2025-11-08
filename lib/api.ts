/**
 * API client for Mimic.AI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface UploadResponse {
  success: boolean
  message: string
  statistics: {
    total_messages: number
    unique_senders: number
    date_range?: {
      start: string
      end: string
    }
    [key: string]: any
  }
}

export interface QueryRequest {
  username: string
  query: string
  context?: Array<{ sender: string; text: string; timestamp?: string }>
}

export interface QueryResponse {
  response: string
  user_patterns?: {
    user: any
    topics: any[]
    common_words: any[]
    sentiment?: any
  }
  context_used?: any[]
}

/**
 * Upload a WhatsApp chat file to the backend
 */
export async function uploadChatFile(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  console.log('API: Uploading file to backend:', file.name, file.size, 'bytes')
  console.log('API: Target URL:', `${API_BASE_URL}/upload`)

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  })

  console.log('API: Response status:', response.status, response.statusText)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    console.error('API: Upload failed with error:', error)
    throw new Error(error.detail || 'Upload failed')
  }

  const data = await response.json()
  console.log('API: Upload response data:', data)
  return data
}

/**
 * Query the AI to generate a response mimicking a user's style
 */
export async function queryMimic(
  username: string, 
  query: string,
  conversationContext?: Array<{ sender: string; text: string; timestamp?: string }>
): Promise<QueryResponse> {
  const requestBody: QueryRequest = {
    username,
    query,
  }

  // Add context if provided
  if (conversationContext && conversationContext.length > 0) {
    requestBody.context = conversationContext
  }

  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Query failed' }))
    throw new Error(error.detail || 'Query failed')
  }

  return response.json()
}

/**
 * Get list of all users in the database
 */
export async function getUsers(): Promise<{ users: string[]; count: number }> {
  const response = await fetch(`${API_BASE_URL}/users`)

  if (!response.ok) {
    throw new Error('Failed to fetch users')
  }

  return response.json()
}

/**
 * Get user communication patterns
 */
export async function getUserPatterns(username: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/users/${username}/patterns`)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch patterns' }))
    throw new Error(error.detail || 'Failed to fetch patterns')
  }

  return response.json()
}

/**
 * Get system status
 */
export async function getStatus(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/status`)

  if (!response.ok) {
    throw new Error('Failed to fetch status')
  }

  return response.json()
}

/**
 * Get conversation starter suggestions for a user
 */
export async function getConversationStarters(username: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/suggestions/starters/${username}`)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch suggestions' }))
    throw new Error(error.detail || 'Failed to fetch suggestions')
  }

  return response.json()
}
