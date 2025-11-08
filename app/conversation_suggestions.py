"""Conversation Suggestions Service.

Generates intelligent conversation starters and topic recommendations
based on user interaction history and interests.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import logging

from app.parser import ParsedMessage

logger = logging.getLogger(__name__)


class ConversationSuggestionsService:
    """Service for generating conversation suggestions and recommendations."""
    
    def __init__(self):
        self.min_messages_for_suggestions = 10
    
    def suggest_conversation_starters(
        self,
        username: str,
        user_messages: List[ParsedMessage],
        topics: List[Dict[str, Any]],
        recent_days: int = 30
    ) -> Dict[str, Any]:
        """
        Suggest conversation starters based on user interests and patterns.
        
        Args:
            username: Target user
            user_messages: User's message history
            topics: Extracted topics from conversations
            recent_days: Consider topics from last N days
            
        Returns:
            Dictionary with conversation starter suggestions
        """
        if len(user_messages) < self.min_messages_for_suggestions:
            return {
                'suggestions': [],
                'message': 'Not enough conversation history for suggestions'
            }
        
        # Filter recent messages
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=recent_days)
        recent_messages = [
            msg for msg in user_messages 
            if msg.timestamp >= cutoff_date and not msg.is_media
        ]
        
        # Get user's favorite topics
        favorite_topics = self._extract_favorite_topics(topics, limit=5)
        
        # Identify conversation patterns
        question_starters = self._identify_question_patterns(user_messages)
        
        # Generate suggestions
        suggestions = []
        
        # Topic-based starters
        for topic in favorite_topics[:3]:
            topic_name = topic.get('topic', '')
            keywords = topic.get('keywords', [])
            
            suggestions.append({
                'type': 'topic_based',
                'topic': topic_name,
                'starter': f"Have you thought more about {keywords[0] if keywords else topic_name}?",
                'reasoning': f"You frequently discuss {topic_name}",
                'confidence': 0.8
            })
        
        # Time-based starters (if no recent conversation)
        if len(recent_messages) < 5:
            suggestions.append({
                'type': 'reconnection',
                'starter': f"Hey! It's been a while. How have you been?",
                'reasoning': "No recent conversations detected",
                'confidence': 0.9
            })
        
        # Question-based starters
        if question_starters:
            top_question = question_starters[0]
            suggestions.append({
                'type': 'question_based',
                'starter': top_question,
                'reasoning': "Similar to questions you've asked before",
                'confidence': 0.7
            })
        
        # Event-based (if patterns detected)
        suggestions.extend(self._generate_event_based_starters(user_messages))
        
        return {
            'username': username,
            'suggestions': suggestions[:5],  # Top 5 suggestions
            'total_analyzed_messages': len(user_messages),
            'recent_messages_count': len(recent_messages)
        }
    
    def recommend_topics(
        self,
        username: str,
        user_messages: List[ParsedMessage],
        all_topics: List[Dict[str, Any]],
        discussed_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Recommend new topics based on past discussions.
        
        Args:
            username: Target user
            user_messages: User's message history
            all_topics: All available topics in database
            discussed_topics: Topics already discussed by user
            
        Returns:
            Topic recommendations
        """
        # Find topics user hasn't discussed much
        undiscussed = [
            topic for topic in all_topics 
            if topic.get('topic', '') not in discussed_topics
        ]
        
        # Find related topics based on keywords
        user_keywords = self._extract_user_keywords(user_messages)
        
        recommendations = []
        for topic in undiscussed[:10]:
            topic_keywords = set(topic.get('keywords', []))
            overlap = len(topic_keywords.intersection(user_keywords))
            
            if overlap > 0:
                recommendations.append({
                    'topic': topic.get('topic', ''),
                    'keywords': topic.get('keywords', []),
                    'relevance_score': overlap / len(topic_keywords),
                    'reason': f"Related to your interests in {list(topic_keywords.intersection(user_keywords))}"
                })
        
        # Sort by relevance
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'username': username,
            'recommendations': recommendations[:5],
            'total_undiscussed_topics': len(undiscussed)
        }
    
    def predict_response(
        self,
        question: str,
        user_messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Predict likely response patterns based on similar past questions.
        
        Args:
            question: Question being asked
            user_messages: User's message history
            
        Returns:
            Response prediction data
        """
        # Extract question words
        question_words = set(question.lower().split())
        
        # Find similar past messages
        similar_responses = []
        for i, msg in enumerate(user_messages[:-1]):
            if msg.is_media:
                continue
            
            msg_words = set(msg.message.lower().split())
            overlap = len(question_words.intersection(msg_words))
            
            if overlap > 2 and i + 1 < len(user_messages):
                # Get the next message (response)
                next_msg = user_messages[i + 1]
                if not next_msg.is_media:
                    similar_responses.append({
                        'original_question': msg.message,
                        'response': next_msg.message,
                        'similarity': overlap / len(question_words)
                    })
        
        # Sort by similarity
        similar_responses.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Analyze response patterns
        response_lengths = [len(r['response'].split()) for r in similar_responses]
        avg_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        return {
            'question': question,
            'similar_past_questions': len(similar_responses),
            'top_similar_responses': similar_responses[:3],
            'predicted_response_length': int(avg_length),
            'confidence': min(len(similar_responses) / 10, 1.0)
        }
    
    def generate_conversation_summary(
        self,
        messages: List[ParsedMessage],
        max_messages: int = 50
    ) -> Dict[str, Any]:
        """
        Generate a summary of a conversation.
        
        Args:
            messages: Messages to summarize
            max_messages: Maximum messages to analyze
            
        Returns:
            Conversation summary
        """
        recent_messages = messages[-max_messages:]
        
        # Extract key information
        participants = list(set(msg.username for msg in recent_messages))
        total_length = sum(len(msg.message.split()) for msg in recent_messages if not msg.is_media)
        
        # Identify main topics (simple keyword extraction)
        all_words = []
        for msg in recent_messages:
            if not msg.is_media:
                words = [w.lower() for w in msg.message.split() if len(w) > 4]
                all_words.extend(words)
        
        common_keywords = Counter(all_words).most_common(5)
        
        # Find questions
        questions = [
            msg.message for msg in recent_messages 
            if '?' in msg.message and not msg.is_media
        ]
        
        return {
            'message_count': len(recent_messages),
            'participants': participants,
            'total_words': total_length,
            'main_keywords': [word for word, _ in common_keywords],
            'questions_asked': len(questions),
            'sample_questions': questions[:3],
            'time_span': {
                'start': recent_messages[0].timestamp.isoformat(),
                'end': recent_messages[-1].timestamp.isoformat()
            }
        }
    
    def _extract_favorite_topics(
        self,
        topics: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Extract user's most discussed topics."""
        # Sort by score/frequency
        sorted_topics = sorted(
            topics,
            key=lambda t: t.get('score', 0),
            reverse=True
        )
        return sorted_topics[:limit]
    
    def _identify_question_patterns(
        self,
        messages: List[ParsedMessage]
    ) -> List[str]:
        """Identify common question patterns from user's messages."""
        questions = [
            msg.message for msg in messages 
            if '?' in msg.message and not msg.is_media
        ]
        
        # Extract question starters
        starters = []
        for q in questions:
            words = q.split()
            if len(words) > 2:
                starter = ' '.join(words[:3])
                starters.append(starter)
        
        # Get most common patterns
        common = Counter(starters).most_common(3)
        return [starter for starter, _ in common]
    
    def _generate_event_based_starters(
        self,
        messages: List[ParsedMessage]
    ) -> List[Dict[str, Any]]:
        """Generate starters based on recurring events or patterns."""
        suggestions = []
        
        # Analyze time patterns
        hour_counts = Counter(msg.timestamp.hour for msg in messages)
        most_active_hour = hour_counts.most_common(1)[0][0] if hour_counts else 12
        
        # Day of week patterns
        day_counts = Counter(msg.timestamp.weekday() for msg in messages)
        
        # If there's a strong pattern, suggest based on it
        if max(day_counts.values()) > len(messages) * 0.3:
            most_active_day = max(day_counts, key=day_counts.get)
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            suggestions.append({
                'type': 'temporal_pattern',
                'starter': f"Ready for {day_names[most_active_day]}?",
                'reasoning': f"You're most active on {day_names[most_active_day]}s",
                'confidence': 0.6
            })
        
        return suggestions
    
    def _extract_user_keywords(
        self,
        messages: List[ParsedMessage],
        min_length: int = 4
    ) -> set:
        """Extract significant keywords from user's messages."""
        keywords = set()
        for msg in messages:
            if not msg.is_media:
                words = [w.lower() for w in msg.message.split() if len(w) >= min_length]
                keywords.update(words)
        return keywords
