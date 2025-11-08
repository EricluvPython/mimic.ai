"""Graph database schema and operations for Neo4j.

Defines the knowledge graph structure for capturing user communication patterns,
thinking styles, and knowledge relationships.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from neo4j import GraphDatabase, Driver
from neo4j.time import DateTime as Neo4jDateTime
import logging

from app.parser import ParsedMessage

logger = logging.getLogger(__name__)


def convert_neo4j_types(obj: Any) -> Any:
    """
    Convert Neo4j types to Python native types for JSON serialization.
    
    Args:
        obj: Object that may contain Neo4j types
        
    Returns:
        Object with Neo4j types converted to Python types
    """
    if isinstance(obj, Neo4jDateTime):
        # Convert Neo4j DateTime to ISO string
        return obj.iso_format()
    elif isinstance(obj, dict):
        return {key: convert_neo4j_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_neo4j_types(item) for item in obj]
    else:
        return obj


class GraphSchema:
    """
    Neo4j Graph Schema for Mimic.AI
    
    Nodes:
    - User: Represents a chat participant
        Properties: name, message_count, avg_message_length, common_phrases, 
                   sentiment_tendency, response_speed
    
    - Message: Individual message
        Properties: content, timestamp, is_media, media_type, sentiment, length
    
    - Topic: Extracted topics/concepts from conversations
        Properties: name, frequency, related_keywords
    
    - Phrase: Common phrases or expressions used by user
        Properties: text, frequency, context
    
    Relationships:
    - (User)-[SENT]->(Message): User sent a message
    - (Message)-[REPLIED_TO]->(Message): Message is a reply to another
    - (User)-[DISCUSSES]->(Topic): User discusses a topic (weight: frequency)
    - (User)-[USES_PHRASE]->(Phrase): User uses a phrase (weight: frequency)
    - (Message)-[RELATES_TO]->(Topic): Message relates to a topic
    - (User)-[INTERACTS_WITH]->(User): Communication relationship (weight: frequency)
    """
    
    # Cypher queries for schema creation
    CONSTRAINTS = [
        "CREATE CONSTRAINT user_name IF NOT EXISTS FOR (u:User) REQUIRE u.name IS UNIQUE",
        "CREATE CONSTRAINT message_id IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE",
        "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
    ]
    
    INDEXES = [
        "CREATE INDEX message_timestamp IF NOT EXISTS FOR (m:Message) ON (m.timestamp)",
        "CREATE INDEX user_name_idx IF NOT EXISTS FOR (u:User) ON (u.name)",
    ]


class GraphDatabaseManager:
    """Manages Neo4j graph database operations."""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize the graph database manager.
        
        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ensure_schema()
    
    def close(self):
        """Close the database connection."""
        self.driver.close()
    
    def _ensure_schema(self):
        """Ensure database schema (constraints and indexes) exists."""
        try:
            with self.driver.session() as session:
                # Create constraints
                for constraint in GraphSchema.CONSTRAINTS:
                    try:
                        session.run(constraint)
                    except Exception as e:
                        logger.debug(f"Constraint already exists or error: {e}")
                
                # Create indexes
                for index in GraphSchema.INDEXES:
                    try:
                        session.run(index)
                    except Exception as e:
                        logger.debug(f"Index already exists or error: {e}")
                
                logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    def insert_messages(self, messages: List[ParsedMessage]) -> Dict[str, int]:
        """
        Insert parsed messages into the graph database.
        
        Args:
            messages: List of parsed WhatsApp messages
            
        Returns:
            Dictionary with insertion statistics
        """
        with self.driver.session() as session:
            stats = {
                'messages_created': 0,
                'users_created': 0,
                'relationships_created': 0,
            }
            
            # Group messages by user for efficient processing
            user_messages = {}
            for msg in messages:
                if msg.username not in user_messages:
                    user_messages[msg.username] = []
                user_messages[msg.username].append(msg)
            
            # Create/update users
            for username in user_messages.keys():
                result = session.execute_write(self._create_user, username, user_messages[username])
                if result:
                    stats['users_created'] += 1
            
            # Create messages and relationships
            prev_message_id = None
            for i, msg in enumerate(messages):
                message_id = f"msg_{msg.timestamp.timestamp()}_{i}"
                
                result = session.execute_write(
                    self._create_message,
                    message_id,
                    msg,
                    prev_message_id
                )
                
                if result:
                    stats['messages_created'] += 1
                    if prev_message_id:
                        stats['relationships_created'] += 1
                
                prev_message_id = message_id
            
            # Analyze and create topics/patterns
            session.execute_write(self._analyze_patterns, messages)
            
            logger.info(f"Inserted {stats['messages_created']} messages, {stats['users_created']} users")
            return stats
    
    @staticmethod
    def _create_user(tx, username: str, messages: List[ParsedMessage]):
        """Create or update a user node with communication patterns."""
        # Calculate user statistics
        total_length = sum(len(msg.message) for msg in messages)
        avg_length = total_length / len(messages) if messages else 0
        
        query = """
        MERGE (u:User {name: $username})
        SET u.message_count = $message_count,
            u.avg_message_length = $avg_length,
            u.last_updated = datetime($timestamp)
        RETURN u
        """
        
        result = tx.run(query, 
                       username=username,
                       message_count=len(messages),
                       avg_length=avg_length,
                       timestamp=datetime.now().isoformat())
        
        return result.single()
    
    @staticmethod
    def _create_message(tx, message_id: str, msg: ParsedMessage, prev_message_id: Optional[str]):
        """Create a message node and relationships."""
        query = """
        CREATE (m:Message {
            id: $message_id,
            content: $content,
            timestamp: datetime($timestamp),
            is_media: $is_media,
            media_type: $media_type,
            length: $length
        })
        WITH m
        MATCH (u:User {name: $username})
        CREATE (u)-[:SENT]->(m)
        """
        
        if prev_message_id:
            query += """
            WITH m
            MATCH (prev:Message {id: $prev_message_id})
            CREATE (m)-[:FOLLOWS]->(prev)
            """
        
        query += " RETURN m"
        
        result = tx.run(query,
                       message_id=message_id,
                       content=msg.message,
                       timestamp=msg.timestamp.isoformat(),
                       is_media=msg.is_media,
                       media_type=msg.media_type,
                       length=len(msg.message),
                       username=msg.username,
                       prev_message_id=prev_message_id)
        
        return result.single()
    
    @staticmethod
    def _analyze_patterns(tx, messages: List[ParsedMessage]):
        """
        Analyze messages to extract topics, phrases, and patterns.
        
        NOTE: This is a simplified implementation for the hackathon demo.
        Future improvement: Use NLP (spaCy, transformers) for advanced topic extraction.
        """
        # Extract common words as basic "topics" (demo version)
        # Future: Replace with proper NLP topic modeling
        
        from collections import Counter
        import re
        
        # Simple word frequency analysis
        all_words = []
        for msg in messages:
            if not msg.is_media:
                # Remove punctuation and get words
                words = re.findall(r'\b\w{4,}\b', msg.message.lower())
                all_words.extend(words)
        
        # Get top topics (common words)
        word_freq = Counter(all_words)
        top_topics = word_freq.most_common(20)
        
        # Create topic nodes
        for topic, frequency in top_topics:
            query = """
            MERGE (t:Topic {name: $topic})
            SET t.frequency = $frequency,
                t.last_updated = datetime()
            """
            tx.run(query, topic=topic, frequency=frequency)
        
        # Link users to topics based on their messages
        for msg in messages:
            if not msg.is_media:
                words = set(re.findall(r'\b\w{4,}\b', msg.message.lower()))
                for topic, _ in top_topics:
                    if topic in words:
                        query = """
                        MATCH (u:User {name: $username})
                        MATCH (t:Topic {name: $topic})
                        MERGE (u)-[d:DISCUSSES]->(t)
                        ON CREATE SET d.count = 1
                        ON MATCH SET d.count = d.count + 1
                        """
                        tx.run(query, username=msg.username, topic=topic)
    
    def query_user_patterns(self, username: str) -> Dict[str, Any]:
        """
        Query communication patterns for a specific user.
        
        Args:
            username: User to analyze
            
        Returns:
            Dictionary with user patterns and characteristics
        """
        with self.driver.session() as session:
            # Get user statistics
            user_stats = session.run("""
                MATCH (u:User {name: $username})
                OPTIONAL MATCH (u)-[:SENT]->(m:Message)
                RETURN u.name as name,
                       u.message_count as message_count,
                       u.avg_message_length as avg_length,
                       count(m) as total_messages
            """, username=username).single()
            
            # Get top topics
            topics = session.run("""
                MATCH (u:User {name: $username})-[d:DISCUSSES]->(t:Topic)
                RETURN t.name as topic, d.count as frequency
                ORDER BY d.count DESC
                LIMIT 10
            """, username=username).data()
            
            # Get recent messages for style analysis
            recent_messages = session.run("""
                MATCH (u:User {name: $username})-[:SENT]->(m:Message)
                WHERE NOT m.is_media
                RETURN m.content as content, m.timestamp as timestamp
                ORDER BY m.timestamp DESC
                LIMIT 50
            """, username=username).data()
            
            # Convert Neo4j types to Python types
            recent_messages = convert_neo4j_types(recent_messages)
            
            return {
                'user': dict(user_stats) if user_stats else {},
                'top_topics': topics,
                'recent_messages': recent_messages,
                'message_samples': [msg['content'] for msg in recent_messages[:10]],
            }
    
    def get_conversation_context(self, username: str, limit: int = 20) -> List[Dict]:
        """
        Get recent conversation context for a user.
        
        Args:
            username: User to get context for
            limit: Number of recent messages to retrieve
            
        Returns:
            List of messages with context
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {name: $username})-[:SENT]->(m:Message)
                RETURN m.content as content,
                       m.timestamp as timestamp,
                       m.is_media as is_media
                ORDER BY m.timestamp DESC
                LIMIT $limit
            """, username=username, limit=limit)
            
            # Convert to list and handle Neo4j types
            messages = [dict(record) for record in result]
            return convert_neo4j_types(messages)
    
    def add_new_messages(self, messages: List[ParsedMessage]) -> Dict[str, int]:
        """
        Add new messages to existing graph (incremental update).
        
        Args:
            messages: New messages to add
            
        Returns:
            Statistics about the update
        """
        # Reuse the insert_messages method - it handles merging automatically
        return self.insert_messages(messages)
    
    def get_all_users(self) -> List[str]:
        """Get list of all users in the database."""
        with self.driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u.name as name")
            return [record['name'] for record in result]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        with self.driver.session() as session:
            stats = session.run("""
                MATCH (u:User)
                OPTIONAL MATCH (m:Message)
                OPTIONAL MATCH (t:Topic)
                RETURN count(DISTINCT u) as user_count,
                       count(DISTINCT m) as message_count,
                       count(DISTINCT t) as topic_count
            """).single()
            
            return dict(stats) if stats else {}
