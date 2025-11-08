/**
 * Parser for WhatsApp chat exports
 * WhatsApp exports typically have the format:
 * [DD/MM/YYYY, HH:MM:SS AM/PM] Sender Name: Message text
 */

export interface ParsedMessage {
  date: Date
  sender: string
  text: string
}

/**
 * Check if a message is the encryption warning message
 */
function isEncryptionWarning(text: string): boolean {
  const encryptionWarningPatterns = [
    /Messages and calls are end-to-end encrypted/i,
    /end-to-end encrypted/i,
    /Only people in this chat can read/i,
  ]
  
  return encryptionWarningPatterns.some(pattern => text.match(pattern))
}

export function parseWhatsAppChat(chatText: string): ParsedMessage[] {
  if (!chatText || chatText.trim().length === 0) {
    console.warn('parseWhatsAppChat: Empty chat text provided')
    return []
  }

  const lines = chatText.split('\n')
  const messages: ParsedMessage[] = []
  let currentMessage: ParsedMessage | null = null
  let linesProcessed = 0
  let linesMatched = 0
  let encryptionWarningsFiltered = 0

  for (const line of lines) {
    linesProcessed++
    
    // Skip empty lines
    if (!line.trim()) {
      continue
    }

    // Match WhatsApp export format: [DD/MM/YYYY, HH:MM:SS AM/PM] Sender: Message
    // Some lines may have a left-to-right mark (U+200E) or other invisible characters before the bracket
    // First, remove any leading/trailing whitespace and invisible characters
    let cleanedLine = line.trim()
    
    // Remove common invisible characters that WhatsApp might add
    // U+200E = Left-to-right mark, U+200F = Right-to-left mark
    cleanedLine = cleanedLine.replace(/^[\u200E\u200F\u202A-\u202E\u2066-\u2069]+/, '')
    
    // Match format: [DD/MM/YYYY, HH:MM:SS AM/PM] Sender: Message
    // Updated regex to be more flexible with spaces and handle various formats
    const messageMatch = cleanedLine.match(/^\[(\d{1,2}\/\d{1,2}\/\d{4}),\s*(\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM))\]\s*(.+?):\s*(.+)$/)
    
    if (messageMatch) {
      linesMatched++
      // Save previous message if exists
      if (currentMessage) {
        messages.push(currentMessage)
      }

      const [, dateStr, timeStr, sender, text] = messageMatch
      const dateTimeStr = `${dateStr} ${timeStr.trim()}`
      
      try {
        const date = parseDate(dateTimeStr)

        // Clean the text - remove any invisible characters
        const cleanText = text.replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069]/g, '').trim()

        // Skip the encryption warning message
        if (isEncryptionWarning(cleanText)) {
          encryptionWarningsFiltered++
          // Skip this message - don't add it to messages array
          continue
        }

        currentMessage = {
          date,
          sender: sender.trim(),
          text: cleanText || text.trim(), // Use cleaned text if not empty, otherwise use original
        }
      } catch (error) {
        console.warn('Error parsing date:', dateTimeStr, error)
        // Continue with current line even if date parsing fails
        if (linesMatched === 1 && linesProcessed < 5) {
          console.log('First few lines that failed to match:', lines.slice(0, 5))
        }
      }
    } else if (currentMessage && cleanedLine) {
      // Multi-line message continuation (skip empty lines)
      // Clean continuation lines as well
      const cleanContinuation = cleanedLine.replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069]/g, '')
      if (cleanContinuation.trim()) {
        currentMessage.text += '\n' + cleanContinuation.trim()
      }
    } else if (linesProcessed <= 5) {
      // Log first few non-matching lines for debugging
      console.log(`Line ${linesProcessed} did not match pattern:`, cleanedLine.substring(0, 100))
    }
  }

  // Add the last message (if it's not an encryption warning)
  if (currentMessage && !isEncryptionWarning(currentMessage.text)) {
    messages.push(currentMessage)
  } else if (currentMessage && isEncryptionWarning(currentMessage.text)) {
    encryptionWarningsFiltered++
  }

  console.log(`Parsed ${messages.length} messages from ${linesProcessed} lines (${linesMatched} matched, ${encryptionWarningsFiltered} encryption warnings filtered)`)

  return messages
}

function parseDate(dateTimeStr: string): Date {
    // Clean invisible chars & commas
    const cleaned = dateTimeStr
      .replace(/[\u200E\u200F\u202A-\u202E\u2066-\u2069\u202F]/g, '') // remove LRM, RTL, narrow spaces
      .replace(',', '')
      .trim()
  
    // Extract pieces like "01/02/2024 8:00:16 AM"
    const match = cleaned.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})\s?(AM|PM)?$/i)
    if (!match) throw new Error(`Unrecognized date format: ${dateTimeStr}`)
  
    const [, d, m, y, h, min, s, period] = match.map(v => v && v.trim())
    let day = parseInt(d, 10)
    let month = parseInt(m, 10) - 1 // zero-based
    let year = parseInt(y, 10)
    let hour = parseInt(h, 10)
    const minute = parseInt(min, 10)
    const second = parseInt(s, 10)
  
    if (period?.toUpperCase() === 'PM' && hour !== 12) hour += 12
    if (period?.toUpperCase() === 'AM' && hour === 12) hour = 0
  
    return new Date(year, month, day, hour, minute, second)
  }
  

/**
 * Extract unique senders from parsed messages
 */
export function extractSenders(messages: ParsedMessage[]): string[] {
  const senders = new Set(messages.map(msg => msg.sender))
  return Array.from(senders).sort()
}

/**
 * Filter messages by sender
 */
export function filterBySender(messages: ParsedMessage[], sender: string): ParsedMessage[] {
  return messages.filter(msg => msg.sender === sender)
}
