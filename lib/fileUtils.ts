
/**
 * Extract person's name from WhatsApp ZIP filename
 * Format: "WhatsApp Chat - Person Name.zip" -> "Person Name"
 */
export function extractPersonNameFromZip(zipFileName: string): string {
  // Remove .zip extension
  const nameWithoutExt = zipFileName.replace(/\.zip$/i, '')
  
  // Check if it matches WhatsApp format: "WhatsApp Chat - Name"
  const match = nameWithoutExt.match(/^WhatsApp Chat - (.+)$/i)
  
  if (match && match[1]) {
    return match[1].trim()
  }
  
  // Fallback: return filename without extension
  return nameWithoutExt
}

/**
 * Extract TXT file from ZIP and return its content
 */
export async function extractTxtFromZip(zipFile: File): Promise<{ content: string; fileName: string }> {
  if (typeof window === 'undefined') {
    throw new Error('ZIP extraction is only available in the browser')
  }
  
  try {
    // Dynamic import for JSZip - this will work after npm install
    const JSZip = (await import('jszip')).default
    const zip = new JSZip()
    const zipData = await zip.loadAsync(zipFile)
    
    console.log('ZIP files found:', Object.keys(zipData.files))
    
    // Find the first .txt file in the ZIP
    const txtFiles = Object.keys(zipData.files).filter(
      fileName => fileName.endsWith('.txt') && !zipData.files[fileName].dir
    )
    
    console.log('TXT files found in ZIP:', txtFiles)
    
    if (txtFiles.length === 0) {
      // List all files for debugging
      const allFiles = Object.keys(zipData.files)
      throw new Error(`No .txt file found in the ZIP archive. Files found: ${allFiles.join(', ')}`)
    }
    
    // Use the first .txt file found
    const txtFileName = txtFiles[0]
    const txtFile = zipData.files[txtFileName]
    
    if (!txtFile) {
      throw new Error('Could not read .txt file from ZIP')
    }
    
    console.log('Reading TXT file:', txtFileName)
    const content = await txtFile.async('text')
    console.log('Extracted content length:', content.length)
    
    if (!content || content.length === 0) {
      throw new Error('TXT file appears to be empty')
    }
    
    return {
      content,
      fileName: txtFileName,
    }
  } catch (error) {
    console.error('Error extracting ZIP:', error)
    throw error
  }
}
