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
    
    - Topic: Extracted topics/concepts from conversations using BERTopic/LDA
        Properties: name, keywords (list), score (float), method (bertopic/lda), last_updated
    
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
        Analyze messages to extract topics using BERTopic.
        
        Uses advanced NLP topic modeling to extract meaningful topics.
        Falls back to LDA if BERTopic fails (small datasets).
        """
        from app.nlp_analyzer import AdvancedNLPAnalyzer
        
        # Prepare messages for analysis
        message_texts = [msg.message for msg in messages if not msg.is_media and msg.message.strip()]
        
        if len(message_texts) < 3:
            logger.warning("Not enough messages for topic analysis, skipping")
            return
        
        # Use NLP analyzer for topic extraction
        nlp_analyzer = AdvancedNLPAnalyzer()
        
        try:
            # Try BERTopic first (more advanced)
            topics_result = nlp_analyzer.extract_topics_bertopic(messages)
            topic_method = "bertopic"
            logger.info("Using BERTopic for topic extraction")
        except Exception as e:
            logger.warning(f"BERTopic failed ({e}), falling back to LDA")
            try:
                # Fall back to LDA
                topics_result = nlp_analyzer.extract_topics_lda(messages)
                topic_method = "lda"
                logger.info("Using LDA for topic extraction")
            except Exception as e2:
                logger.error(f"Both topic extraction methods failed: {e2}")
                return
        
        # Extract topics from result
        topics = topics_result.get('topics', [])
        
        if not topics:
            logger.warning("No topics extracted")
            return
        
        # Create topic nodes with more details
        for topic_info in topics[:15]:  # Limit to top 15 topics
            topic_name = topic_info.get('topic', '')
            if not topic_name or topic_name == '-1':
                continue
                
            keywords = topic_info.get('keywords', [])
            score = topic_info.get('score', 0.0)
            
            query = """
            MERGE (t:Topic {name: $topic})
            SET t.keywords = $keywords,
                t.score = $score,
                t.method = $method,
                t.last_updated = datetime()
            """
            tx.run(query, 
                   topic=topic_name, 
                   keywords=keywords,
                   score=float(score),
                   method=topic_method)
        
        # Link users to topics based on their message content
        # Build a mapping of which topics appear in which messages
        user_topic_counts = {}  # {(username, topic): count}
        
        for msg in messages:
            if msg.is_media or not msg.message.strip():
                continue
            
            msg_lower = msg.message.lower()
            
            for topic_info in topics[:15]:
                topic_name = topic_info.get('topic', '')
                if not topic_name or topic_name == '-1':
                    continue
                
                # Check if any keyword from this topic appears in the message
                keywords = topic_info.get('keywords', [])
                for keyword in keywords[:3]:  # Check top 3 keywords per topic
                    if keyword.lower() in msg_lower:
                        key = (msg.username, topic_name)
                        user_topic_counts[key] = user_topic_counts.get(key, 0) + 1
                        break
        
        # Create DISCUSSES relationships
        for (username, topic), count in user_topic_counts.items():
            query = """
            MATCH (u:User {name: $username})
            MATCH (t:Topic {name: $topic})
            MERGE (u)-[d:DISCUSSES]->(t)
            SET d.count = $count
            """
            tx.run(query, username=username, topic=topic, count=count)
    
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
    
    def get_all_messages_for_user(self, username: str) -> List[ParsedMessage]:
        """
        Get all messages for a specific user.
        
        Args:
            username: Username to retrieve messages for
            
        Returns:
            List of ParsedMessage objects
        """
        from datetime import datetime
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {name: $username})-[:SENT]->(m:Message)
                RETURN m.content as content,
                       m.timestamp as timestamp,
                       m.is_media as is_media,
                       m.media_type as media_type,
                       u.name as username
                ORDER BY m.timestamp ASC
            """, username=username)
            
            messages = []
            for record in result:
                # Convert Neo4j DateTime to Python datetime
                timestamp_str = str(record['timestamp'])
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except:
                    timestamp = datetime.now()
                
                messages.append(ParsedMessage(
                    timestamp=timestamp,
                    username=record['username'],
                    message=record['content'],
                    is_media=record['is_media'],
                    media_type=record['media_type']
                ))
            
            return messages
    
    def get_all_messages(self) -> List[ParsedMessage]:
        """
        Get all messages from the database.
        
        Returns:
            List of all ParsedMessage objects
        """
        from datetime import datetime
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[:SENT]->(m:Message)
                RETURN m.content as content,
                       m.timestamp as timestamp,
                       m.is_media as is_media,
                       m.media_type as media_type,
                       u.name as username
                ORDER BY m.timestamp ASC
            """)
            
            messages = []
            for record in result:
                # Convert Neo4j DateTime to Python datetime
                timestamp_str = str(record['timestamp'])
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except:
                    timestamp = datetime.now()
                
                messages.append(ParsedMessage(
                    timestamp=timestamp,
                    username=record['username'],
                    message=record['content'],
                    is_media=record['is_media'],
                    media_type=record['media_type']
                ))
            
            return messages
    
    def get_graph_structure(self) -> Dict[str, Any]:
        """
        Get graph structure for visualization.
        
        Returns:
            Dictionary with nodes and edges for graph visualization
        """
        with self.driver.session() as session:
            # Get user nodes
            users = session.run("""
                MATCH (u:User)
                RETURN u.name as name, u.message_count as message_count
            """).data()
            
            # Get topic nodes
            topics = session.run("""
                MATCH (t:Topic)
                RETURN t.name as name, 
                       COALESCE(t.score, t.frequency, 0) as score,
                       t.keywords as keywords
                ORDER BY score DESC
                LIMIT 20
            """).data()
            
            # Get user-topic relationships
            user_topic_edges = session.run("""
                MATCH (u:User)-[d:DISCUSSES]->(t:Topic)
                RETURN u.name as source, t.name as target, d.count as weight
            """).data()
            
            # Get user-user interactions
            user_interactions = session.run("""
                MATCH (u1:User)-[:SENT]->(m1:Message)-[:FOLLOWS]->(m2:Message)<-[:SENT]-(u2:User)
                WHERE u1.name <> u2.name
                RETURN u1.name as source, u2.name as target, count(*) as weight
            """).data()
            
            # Format nodes
            nodes = []
            node_index = {}
            idx = 0
            
            # Add user nodes
            for user in users:
                nodes.append({
                    'id': user['name'],
                    'label': user['name'],
                    'type': 'user',
                    'size': min(50, 10 + (user.get('message_count', 0) or 0) / 2),
                    'value': user.get('message_count', 0) or 0
                })
                node_index[user['name']] = idx
                idx += 1
            
            # Add topic nodes
            for topic in topics[:15]:  # Limit to top 15 topics
                score = topic.get('score', 0) or 0
                nodes.append({
                    'id': topic['name'],
                    'label': topic['name'],
                    'type': 'topic',
                    'size': min(30, 5 + float(score) * 2),
                    'value': float(score),
                    'keywords': topic.get('keywords', [])
                })
                node_index[topic['name']] = idx
                idx += 1
            
            # Format edges
            edges = []
            
            # Add user-topic edges
            for edge in user_topic_edges:
                if edge['source'] in node_index and edge['target'] in node_index:
                    edges.append({
                        'source': edge['source'],
                        'target': edge['target'],
                        'weight': edge.get('weight', 1) or 1,
                        'type': 'discusses'
                    })
            
            # Add user-user interaction edges
            for edge in user_interactions:
                if edge['source'] in node_index and edge['target'] in node_index:
                    edges.append({
                        'source': edge['source'],
                        'target': edge['target'],
                        'weight': edge.get('weight', 1) or 1,
                        'type': 'interacts'
                    })
            
            return {
                'nodes': nodes,
                'edges': edges
            }
