"""Personal Knowledge Base Service.

Provides semantic search and memory recall over conversation history.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import re
import logging

from app.parser import ParsedMessage

logger = logging.getLogger(__name__)


class PersonalKnowledgeBase:
    """Service for searching and recalling information from conversation history."""
    
    def __init__(self):
        self.min_query_length = 3
    
    def search_conversations(
        self,
        query: str,
        all_messages: List[ParsedMessage],
        username: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search conversations for specific topics or keywords.
        
        Args:
            query: Search query
            all_messages: All messages to search through
            username: Optional filter by specific user
            limit: Maximum results to return
            
        Returns:
            Search results with relevant messages
        """
        if len(query) < self.min_query_length:
            return {
                'error': f'Query must be at least {self.min_query_length} characters',
                'results': []
            }
        
        # Prepare search terms
        query_terms = set(query.lower().split())
        
        # Search through messages
        results = []
        for msg in all_messages:
            # Skip if filtering by username
            if username and msg.username != username:
                continue
            
            if msg.is_media:
                continue
            
            # Calculate relevance score
            msg_lower = msg.message.lower()
            msg_words = set(msg_lower.split())
            
            # Exact phrase match
            if query.lower() in msg_lower:
                relevance_score = 10.0
            else:
                # Word overlap score
                overlap = len(query_terms.intersection(msg_words))
                relevance_score = overlap / len(query_terms) * 5
            
            if relevance_score > 0:
                results.append({
                    'message': msg.message,
                    'username': msg.username,
                    'timestamp': msg.timestamp.isoformat(),
                    'relevance_score': relevance_score,
                    'context': self._get_context(msg, all_messages, window=2)
                })
        
        # Sort by relevance and timestamp
        results.sort(key=lambda x: (x['relevance_score'], x['timestamp']), reverse=True)
        
        return {
            'query': query,
            'total_results': len(results),
            'results': results[:limit],
            'searched_messages': len(all_messages)
        }
    
    def find_discussion_about(
        self,
        topic: str,
        all_messages: List[ParsedMessage],
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find when a specific topic was discussed.
        
        Args:
            topic: Topic to search for
            all_messages: All messages to search
            username: Optional filter by user
            
        Returns:
            Timeline of topic discussions
        """
        search_results = self.search_conversations(topic, all_messages, username, limit=100)
        
        if not search_results['results']:
            return {
                'topic': topic,
                'discussions': [],
                'message': f'No discussions about "{topic}" found'
            }
        
        # Group by date
        discussions_by_date = defaultdict(list)
        for result in search_results['results']:
            date = datetime.fromisoformat(result['timestamp']).date()
            discussions_by_date[date].append(result)
        
        # Create timeline
        timeline = []
        for date, messages in sorted(discussions_by_date.items()):
            timeline.append({
                'date': date.isoformat(),
                'message_count': len(messages),
                'participants': list(set(m['username'] for m in messages)),
                'sample_messages': [m['message'] for m in messages[:3]],
                'avg_relevance': sum(m['relevance_score'] for m in messages) / len(messages)
            })
        
        return {
            'topic': topic,
            'total_discussions': len(timeline),
            'first_mentioned': timeline[0]['date'] if timeline else None,
            'last_mentioned': timeline[-1]['date'] if timeline else None,
            'timeline': timeline
        }
    
    def recall_last_mention(
        self,
        keyword: str,
        all_messages: List[ParsedMessage],
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find the last time a keyword or topic was mentioned.
        
        Args:
            keyword: Keyword to search for
            all_messages: All messages to search
            username: Optional filter by user
            
        Returns:
            Last mention information
        """
        keyword_lower = keyword.lower()
        
        # Search in reverse (most recent first)
        for msg in reversed(all_messages):
            if username and msg.username != username:
                continue
            
            if msg.is_media:
                continue
            
            if keyword_lower in msg.message.lower():
                # Calculate days ago with timezone awareness
                from datetime import timezone
                now = datetime.now(timezone.utc)
                # Make msg.timestamp timezone-aware if it isn't already
                msg_time = msg.timestamp
                if msg_time.tzinfo is None:
                    msg_time = msg_time.replace(tzinfo=timezone.utc)
                
                return {
                    'keyword': keyword,
                    'found': True,
                    'last_mention': {
                        'message': msg.message,
                        'username': msg.username,
                        'timestamp': msg.timestamp.isoformat(),
                        'days_ago': (now - msg_time).days,
                        'context': self._get_context(msg, all_messages, window=3)
                    }
                }
        
        return {
            'keyword': keyword,
            'found': False,
            'message': f'"{keyword}" was never mentioned in the conversation history'
        }
    
    def extract_facts(
        self,
        all_messages: List[ParsedMessage],
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract factual statements and information from conversations.
        
        Args:
            all_messages: All messages to analyze
            username: Optional filter by user
            
        Returns:
            Extracted facts and information
        """
        # Patterns that often indicate factual statements
        fact_patterns = [
            r'(?:is|are|was|were)\s+(?:a|an|the)\s+\w+',
            r'(?:lives?|lived)\s+(?:in|at)\s+[\w\s]+',
            r'(?:works?|worked)\s+(?:at|for|in)\s+[\w\s]+',
            r'(?:likes?|loved?|hates?)\s+[\w\s]+',
            r'\b(?:my|his|her|their)\s+(?:name|job|home|favorite)\s+is\s+[\w\s]+',
        ]
        
        facts = []
        for msg in all_messages:
            if username and msg.username != username:
                continue
            
            if msg.is_media:
                continue
            
            # Check for fact patterns
            for pattern in fact_patterns:
                matches = re.finditer(pattern, msg.message, re.IGNORECASE)
                for match in matches:
                    facts.append({
                        'statement': match.group(),
                        'full_message': msg.message,
                        'username': msg.username,
                        'timestamp': msg.timestamp.isoformat(),
                        'confidence': 0.7  # Basic confidence score
                    })
        
        # Group similar facts
        fact_categories = self._categorize_facts(facts)
        
        return {
            'total_facts_extracted': len(facts),
            'facts_by_category': fact_categories,
            'sample_facts': facts[:20]
        }
    
    def build_knowledge_graph_query(
        self,
        entity: str,
        all_messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Build a knowledge graph query for a specific entity (person, place, thing).
        
        Args:
            entity: Entity to build graph for
            all_messages: All messages to analyze
            
        Returns:
            Knowledge graph data
        """
        entity_lower = entity.lower()
        
        # Find all mentions
        mentions = []
        related_entities = set()
        
        for msg in all_messages:
            if msg.is_media:
                continue
            
            msg_lower = msg.message.lower()
            if entity_lower in msg_lower:
                mentions.append({
                    'message': msg.message,
                    'username': msg.username,
                    'timestamp': msg.timestamp.isoformat()
                })
                
                # Extract related entities (simple capitalized words)
                words = msg.message.split()
                for word in words:
                    if len(word) > 3 and word[0].isupper() and word.lower() != entity_lower:
                        related_entities.add(word)
        
        # Extract relationships
        relationships = self._extract_relationships(entity, mentions)
        
        return {
            'entity': entity,
            'total_mentions': len(mentions),
            'first_mention': mentions[0]['timestamp'] if mentions else None,
            'last_mention': mentions[-1]['timestamp'] if mentions else None,
            'related_entities': list(related_entities)[:10],
            'relationships': relationships,
            'sample_context': mentions[:5]
        }
    
    def semantic_search(
        self,
        query: str,
        all_messages: List[ParsedMessage],
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Perform semantic search (meaning-based, not just keyword matching).
        
        Args:
            query: Search query
            all_messages: All messages to search
            limit: Maximum results
            
        Returns:
            Semantic search results
        """
        # Simplified semantic search using synonym expansion
        # In production, use embeddings and vector similarity
        
        # Synonym mapping for common queries
        synonyms = {
            'happy': ['glad', 'joyful', 'excited', 'pleased', 'delighted'],
            'sad': ['unhappy', 'depressed', 'down', 'upset', 'disappointed'],
            'work': ['job', 'office', 'career', 'employment', 'workplace'],
            'home': ['house', 'apartment', 'place', 'residence'],
            'food': ['eat', 'dinner', 'lunch', 'meal', 'restaurant'],
            'friend': ['buddy', 'pal', 'mate', 'companion']
        }
        
        # Expand query with synonyms
        expanded_terms = set(query.lower().split())
        for term in query.lower().split():
            if term in synonyms:
                expanded_terms.update(synonyms[term])
        
        # Search with expanded terms
        results = []
        for msg in all_messages:
            if msg.is_media:
                continue
            
            msg_lower = msg.message.lower()
            msg_words = set(msg_lower.split())
            
            # Calculate semantic similarity
            overlap = len(expanded_terms.intersection(msg_words))
            if overlap > 0:
                relevance = overlap / len(expanded_terms)
                results.append({
                    'message': msg.message,
                    'username': msg.username,
                    'timestamp': msg.timestamp.isoformat(),
                    'relevance_score': relevance,
                    'matched_terms': list(expanded_terms.intersection(msg_words))
                })
        
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'query': query,
            'expanded_terms': list(expanded_terms),
            'total_results': len(results),
            'results': results[:limit]
        }
    
    def _get_context(
        self,
        target_message: ParsedMessage,
        all_messages: List[ParsedMessage],
        window: int = 2
    ) -> List[Dict[str, str]]:
        """Get surrounding messages for context."""
        try:
            idx = all_messages.index(target_message)
            start = max(0, idx - window)
            end = min(len(all_messages), idx + window + 1)
            
            context = []
            for msg in all_messages[start:end]:
                if not msg.is_media:
                    context.append({
                        'username': msg.username,
                        'message': msg.message,
                        'is_target': msg == target_message
                    })
            return context
        except ValueError:
            return []
    
    def _categorize_facts(self, facts: List[Dict[str, Any]]) -> Dict[str, List]:
        """Categorize extracted facts."""
        categories = {
            'personal_info': [],
            'preferences': [],
            'locations': [],
            'work_related': [],
            'other': []
        }
        
        for fact in facts:
            statement = fact['statement'].lower()
            
            if any(word in statement for word in ['name', 'age', 'birthday']):
                categories['personal_info'].append(fact)
            elif any(word in statement for word in ['like', 'love', 'hate', 'favorite']):
                categories['preferences'].append(fact)
            elif any(word in statement for word in ['live', 'city', 'country', 'home']):
                categories['locations'].append(fact)
            elif any(word in statement for word in ['work', 'job', 'company', 'office']):
                categories['work_related'].append(fact)
            else:
                categories['other'].append(fact)
        
        return {k: v for k, v in categories.items() if v}
    
    def _extract_relationships(
        self,
        entity: str,
        mentions: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract relationships for an entity."""
        relationships = []
        
        # Relationship patterns
        rel_patterns = [
            (r'(?:is|was)\s+(?:a|an|the)\s+(\w+)', 'is_a'),
            (r'(?:works?|worked)\s+(?:at|for)\s+([\w\s]+)', 'works_at'),
            (r'(?:lives?|lived)\s+(?:in|at)\s+([\w\s]+)', 'lives_in'),
            (r'(?:likes?|loved?)\s+([\w\s]+)', 'likes'),
        ]
        
        for mention in mentions:
            msg = mention['message']
            for pattern, rel_type in rel_patterns:
                matches = re.finditer(pattern, msg, re.IGNORECASE)
                for match in matches:
                    relationships.append({
                        'type': rel_type,
                        'value': match.group(1).strip(),
                        'source': msg
                    })
        
        return relationships[:10]
