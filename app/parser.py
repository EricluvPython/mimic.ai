"""WhatsApp chat export parser.

Parses WhatsApp chat exports in .txt format and extracts structured message data.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedMessage:
    """Represents a parsed WhatsApp message."""
    timestamp: datetime
    username: str
    message: str
    is_media: bool = False
    media_type: Optional[str] = None


class WhatsAppParser:
    """Parser for WhatsApp chat export files."""
    
    # Pattern for WhatsApp message formats
    # Supports multiple international formats
    MESSAGE_PATTERNS = [
        # Pattern 1: [YYYY/M/D HH:MM:SS] Username: Message (Chinese/Asian format)
        re.compile(r'\[(\d{4}/\d{1,2}/\d{1,2})\s+(\d{1,2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+)', re.UNICODE),
        # Pattern 2: [DD/MM/YYYY, HH:MM:SS] Username: Message (European format)
        re.compile(r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.+)'),
        # Pattern 3: DD/MM/YYYY, HH:MM - Username: Message (Standard format)
        re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.+)'),
        # Pattern 4: YYYY/M/D, HH:MM - Username: Message (Asian format without brackets)
        re.compile(r'(\d{4}/\d{1,2}/\d{1,2}),\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)'),
    ]
    
    # Media indicators (including Chinese)
    MEDIA_PATTERNS = [
        r'<Media omitted>',
        r'<attached:.*?>',
        r'image omitted',
        r'video omitted',
        r'audio omitted',
        r'document omitted',
        r'sticker omitted',
        r'GIF omitted',
        r'‎',  # Zero-width character used in system messages
    ]
    
    # System message patterns (to skip)
    SYSTEM_MESSAGE_PATTERNS = [
        r'消息和通话已进行端到端加密',  # Chinese encryption notice
        r'Messages and calls are end-to-end encrypted',
        r'joined using this group',
        r'left',
        r'changed the subject',
        r'changed this group',
        r'You created group',
        r'security code changed',
        r'added',
        r'removed',
    ]
    
    def __init__(self):
        """Initialize the WhatsApp parser."""
        self.media_pattern = re.compile('|'.join(self.MEDIA_PATTERNS), re.IGNORECASE)
        self.system_pattern = re.compile('|'.join(self.SYSTEM_MESSAGE_PATTERNS), re.IGNORECASE)
    
    def parse_file(self, file_content: str) -> List[ParsedMessage]:
        """
        Parse WhatsApp chat export file content.
        
        Args:
            file_content: Raw text content from WhatsApp export
            
        Returns:
            List of ParsedMessage objects
        """
        messages = []
        lines = file_content.split('\n')
        current_message = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to parse as new message
            parsed = self._parse_message_line(line)
            
            if parsed:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                current_message = parsed
            elif current_message:
                # This is a continuation of the previous message (multi-line)
                current_message.message += "\n" + line
        
        # Add the last message
        if current_message:
            messages.append(current_message)
        
        logger.info(f"Parsed {len(messages)} messages from chat export")
        return messages
    
    def _parse_message_line(self, line: str) -> Optional[ParsedMessage]:
        """
        Parse a single message line.
        
        Args:
            line: Single line from chat export
            
        Returns:
            ParsedMessage if successfully parsed, None otherwise
        """
        for pattern in self.MESSAGE_PATTERNS:
            match = pattern.match(line)
            if match:
                date_str, time_str, username, message = match.groups()
                
                # Skip system messages
                if self.system_pattern.search(message):
                    logger.debug(f"Skipping system message: {message[:50]}...")
                    return None
                
                # Parse timestamp
                timestamp = self._parse_timestamp(date_str, time_str)
                if not timestamp:
                    continue
                
                # Check if message contains media
                is_media = bool(self.media_pattern.search(message))
                media_type = self._detect_media_type(message) if is_media else None
                
                if is_media:
                    logger.debug(f"Media reference detected: {media_type} (Demo limitation - media parsing not implemented)")
                
                # Clean message text (remove special characters at the start)
                message_clean = message.strip().lstrip('‎')
                
                # Skip if message is empty after cleaning
                if not message_clean:
                    return None
                
                return ParsedMessage(
                    timestamp=timestamp,
                    username=username.strip(),
                    message=message_clean,
                    is_media=is_media,
                    media_type=media_type
                )
        
        return None
    
    def _parse_timestamp(self, date_str: str, time_str: str) -> Optional[datetime]:
        """
        Parse timestamp from date and time strings.
        
        Args:
            date_str: Date string (DD/MM/YYYY, MM/DD/YYYY, YYYY/M/D, etc.)
            time_str: Time string (HH:MM or HH:MM:SS, optionally with AM/PM)
            
        Returns:
            datetime object or None if parsing fails
        """
        # Common date formats - including Asian YYYY/M/D format
        date_formats = [
            '%Y/%m/%d',     # YYYY/M/D (Asian format)
            '%Y/%m/%d',     # YYYY/MM/DD
            '%d/%m/%Y',     # DD/MM/YYYY (European)
            '%d/%m/%y',     # DD/MM/YY
            '%m/%d/%Y',     # MM/DD/YYYY (US)
            '%m/%d/%y',     # MM/DD/YY
        ]
        
        # Common time formats
        time_formats = [
            '%H:%M:%S',     # 24-hour with seconds
            '%H:%M',        # 24-hour without seconds
            '%I:%M:%S %p',  # 12-hour with seconds and AM/PM
            '%I:%M %p',     # 12-hour with AM/PM
        ]
        
        for date_fmt in date_formats:
            for time_fmt in time_formats:
                try:
                    datetime_str = f"{date_str} {time_str}"
                    full_format = f"{date_fmt} {time_fmt}"
                    return datetime.strptime(datetime_str, full_format)
                except ValueError:
                    continue
        
        logger.warning(f"Failed to parse timestamp: {date_str} {time_str}")
        return None
    
    def _detect_media_type(self, message: str) -> Optional[str]:
        """
        Detect the type of media from message content.
        
        Args:
            message: Message text
            
        Returns:
            Media type string or None
        """
        message_lower = message.lower()
        
        if 'image' in message_lower or 'photo' in message_lower:
            return 'image'
        elif 'video' in message_lower:
            return 'video'
        elif 'audio' in message_lower or 'voice' in message_lower:
            return 'audio'
        elif 'document' in message_lower or 'pdf' in message_lower:
            return 'document'
        elif 'sticker' in message_lower:
            return 'sticker'
        elif 'gif' in message_lower:
            return 'gif'
        else:
            return 'media'
    
    def get_statistics(self, messages: List[ParsedMessage]) -> Dict:
        """
        Get statistics about parsed messages.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Dictionary with statistics
        """
        if not messages:
            return {
                'total_messages': 0,
                'unique_users': 0,
                'media_messages': 0,
                'text_messages': 0,
            }
        
        users = set(msg.username for msg in messages)
        media_count = sum(1 for msg in messages if msg.is_media)
        
        return {
            'total_messages': len(messages),
            'unique_users': len(users),
            'media_messages': media_count,
            'text_messages': len(messages) - media_count,
            'date_range': {
                'start': min(msg.timestamp for msg in messages).isoformat(),
                'end': max(msg.timestamp for msg in messages).isoformat(),
            },
            'users': list(users),
        }
