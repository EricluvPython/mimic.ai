"""OpenRouter LLM service for generating user-mimicking responses.

Uses OpenRouter API to access various LLMs for response generation based on
user communication patterns extracted from the graph database.
"""

import httpx
from typing import Dict, Any, List, Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize OpenRouter service."""
        self.settings = get_settings()
        self.base_url = self.settings.openrouter_base_url
        self.api_key = self.settings.openrouter_api_key
        self.model = self.settings.openrouter_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/EricluvPython/mimic.ai",
            "X-Title": "Mimic.AI",
            "Content-Type": "application/json",
        }
    
    async def generate_mimic_response(
        self,
        user_patterns: Dict[str, Any],
        query: str,
        context_messages: List[Dict] = None
    ) -> str:
        """
        Generate a response that mimics the user's communication style.
        
        Args:
            user_patterns: User communication patterns from graph database
            query: The query/prompt to respond to
            context_messages: Recent conversation context
            
        Returns:
            Generated response mimicking the user's style
        """
        # Build system prompt with user patterns
        system_prompt = self._build_mimic_prompt(user_patterns, context_messages)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,  # Balance between creativity and consistency
                        "max_tokens": 500,
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"]
                
                logger.info(f"Generated mimic response for query: {query[:50]}...")
                return generated_text
                
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _build_mimic_prompt(
        self,
        user_patterns: Dict[str, Any],
        context_messages: Optional[List[Dict]] = None
    ) -> str:
        """
        Build a system prompt that instructs the LLM to mimic the user's style.
        
        Args:
            user_patterns: User patterns from graph database
            context_messages: Recent messages for context
            
        Returns:
            System prompt string
        """
        user_info = user_patterns.get('user', {})
        topics = user_patterns.get('top_topics', [])
        samples = user_patterns.get('message_samples', [])
        
        # Build the prompt
        prompt_parts = [
            "You are tasked with mimicking a specific user's communication style and way of thinking.",
            f"\nUser: {user_info.get('name', 'Unknown')}",
        ]
        
        # Add communication statistics
        if user_info.get('avg_length'):
            avg_len = user_info['avg_length']
            if avg_len < 30:
                style = "very brief and concise"
            elif avg_len < 60:
                style = "moderately concise"
            elif avg_len < 100:
                style = "fairly detailed"
            else:
                style = "detailed and expressive"
            
            prompt_parts.append(f"\nCommunication Style: {style} messages (avg {avg_len:.0f} characters)")
        
        # Add topics of interest
        if topics:
            topic_list = ", ".join([t['topic'] for t in topics[:5]])
            prompt_parts.append(f"\nFrequent Topics: {topic_list}")
        
        # Add message samples for style learning
        if samples:
            prompt_parts.append("\nExample messages from this user:")
            for i, sample in enumerate(samples[:5], 1):
                prompt_parts.append(f"{i}. \"{sample}\"")
        
        # Add context if available
        if context_messages:
            prompt_parts.append("\nRecent conversation context:")
            for msg in context_messages[:5]:
                if not msg.get('is_media'):
                    content = msg.get('content', '')[:100]
                    prompt_parts.append(f"- {content}")
        
        # Instructions
        prompt_parts.extend([
            "\n\nInstructions:",
            "1. Analyze the user's communication patterns from the examples above",
            "2. Match their typical message length and structure",
            "3. Use similar vocabulary and phrasing style",
            "4. Reflect their way of thinking and topic preferences",
            "5. Maintain their level of formality/informality",
            "6. Generate a response that this user would naturally write",
            "\nRespond to the user's query in this person's style."
        ])
        
        return "\n".join(prompt_parts)
    
    async def analyze_message_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a message.
        
        NOTE: For demo - simplified implementation.
        Future: Use dedicated sentiment analysis models.
        
        Args:
            message: Message to analyze
            
        Returns:
            Sentiment analysis result
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Analyze the sentiment of the message. Respond with only: positive, negative, or neutral."
                            },
                            {
                                "role": "user",
                                "content": message
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 10,
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                sentiment = result["choices"][0]["message"]["content"].strip().lower()
                
                return {
                    "sentiment": sentiment,
                    "message": message
                }
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "message": message}
    
    async def extract_topics(self, messages: List[str]) -> List[str]:
        """
        Extract topics from a list of messages.
        
        NOTE: For demo - LLM-based extraction.
        Future: Use NLP topic modeling (LDA, BERTopic, etc.)
        
        Args:
            messages: List of message strings
            
        Returns:
            List of extracted topics
        """
        if not messages:
            return []
        
        combined_messages = "\n".join(messages[:20])  # Limit for token efficiency
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Extract 5-10 main topics from these messages. Return only a comma-separated list of topics."
                            },
                            {
                                "role": "user",
                                "content": combined_messages
                            }
                        ],
                        "temperature": 0.5,
                        "max_tokens": 100,
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                topics_str = result["choices"][0]["message"]["content"]
                
                # Parse comma-separated topics
                topics = [t.strip() for t in topics_str.split(',')]
                
                logger.info(f"Extracted {len(topics)} topics from messages")
                return topics
                
        except Exception as e:
            logger.error(f"Topic extraction error: {e}")
            return []
