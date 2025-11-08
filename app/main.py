"""FastAPI application for Mimic.AI backend.

REST API endpoints for WhatsApp chat analysis and user mimicry.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from contextlib import asynccontextmanager

from app.config import get_settings
from app.parser import WhatsAppParser, ParsedMessage
from app.graph_db import GraphDatabaseManager
from app.llm_service import OpenRouterService
from app.nlp_analyzer import AdvancedNLPAnalyzer
from app.conversation_analyzer import ConversationPatternAnalyzer
from app.visualization_service import VisualizationService
from app.conversation_suggestions import ConversationSuggestionsService
from app.relationship_insights import RelationshipInsightsService
from app.knowledge_base import PersonalKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
db_manager: Optional[GraphDatabaseManager] = None
llm_service: OpenRouterService = OpenRouterService()
nlp_analyzer: AdvancedNLPAnalyzer = AdvancedNLPAnalyzer()
conversation_analyzer: ConversationPatternAnalyzer = ConversationPatternAnalyzer()
viz_service: VisualizationService = VisualizationService()
suggestions_service: ConversationSuggestionsService = ConversationSuggestionsService()
insights_service: RelationshipInsightsService = RelationshipInsightsService()
knowledge_base: PersonalKnowledgeBase = PersonalKnowledgeBase()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    global db_manager
    
    # Startup
    settings = get_settings()
    logger.info("Starting Mimic.AI backend...")
    
    try:
        db_manager = GraphDatabaseManager(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password
        )
        logger.info("Connected to Neo4j database")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise
    
    yield
    
    # Shutdown
    if db_manager:
        db_manager.close()
        logger.info("Closed Neo4j connection")


app = FastAPI(
    title="Mimic.AI Backend",
    description="WhatsApp Chat Analysis & User Mimicry System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for querying the system."""
    username: str
    query: str


class QueryResponse(BaseModel):
    """Response model for query results."""
    response: str
    user_patterns: Optional[Dict[str, Any]] = None
    context_used: Optional[List[Dict]] = None


class MessageBatch(BaseModel):
    """Request model for adding new messages."""
    messages: str  # Raw text messages in WhatsApp format


class UploadResponse(BaseModel):
    """Response model for upload operations."""
    success: bool
    message: str
    statistics: Dict[str, Any]


class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    database_stats: Dict[str, Any]
    users: List[str]


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mimic.AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "add_messages": "/messages/add",
            "status": "/status",
            "users": "/users"
        }
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_chat(file: UploadFile = File(...)):
    """
    Upload WhatsApp chat export file.
    
    Args:
        file: WhatsApp chat export in .txt format
        
    Returns:
        Upload statistics and success status
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Parse messages
        parser = WhatsAppParser()
        messages = parser.parse_file(text_content)
        
        if not messages:
            raise HTTPException(
                status_code=400,
                detail="No valid messages found in the file"
            )
        
        # Get statistics before insertion
        stats = parser.get_statistics(messages)
        
        # Insert into graph database
        db_stats = db_manager.insert_messages(messages)
        
        logger.info(f"Successfully uploaded chat with {len(messages)} messages")
        
        return UploadResponse(
            success=True,
            message=f"Successfully processed {len(messages)} messages",
            statistics={
                **stats,
                **db_stats
            }
        )
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File encoding error. Please ensure the file is UTF-8 encoded"
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query_mimic(request: QueryRequest):
    """
    Get a response suggestion that mimics the user's style.
    
    Args:
        request: Query request with username and query text
        
    Returns:
        Generated response mimicking the user's communication style
    """
    try:
        # Query user patterns from graph database
        user_patterns = db_manager.query_user_patterns(request.username)
        
        if not user_patterns.get('user'):
            raise HTTPException(
                status_code=404,
                detail=f"User '{request.username}' not found in database"
            )
        
        # Get conversation context
        context = db_manager.get_conversation_context(request.username, limit=10)
        
        # Generate mimic response using LLM
        response = await llm_service.generate_mimic_response(
            user_patterns=user_patterns,
            query=request.query,
            context_messages=context
        )
        
        logger.info(f"Generated response for user: {request.username}")
        
        return QueryResponse(
            response=response,
            user_patterns=user_patterns,
            context_used=context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


@app.post("/messages/add", response_model=UploadResponse)
async def add_messages(batch: MessageBatch):
    """
    Add new messages to the database incrementally.
    
    Args:
        batch: New messages in WhatsApp format
        
    Returns:
        Statistics about the added messages
    """
    try:
        # Parse new messages
        parser = WhatsAppParser()
        messages = parser.parse_file(batch.messages)
        
        if not messages:
            raise HTTPException(
                status_code=400,
                detail="No valid messages found"
            )
        
        # Add to database
        stats = db_manager.add_new_messages(messages)
        parse_stats = parser.get_statistics(messages)
        
        logger.info(f"Added {len(messages)} new messages")
        
        return UploadResponse(
            success=True,
            message=f"Successfully added {len(messages)} new messages",
            statistics={
                **parse_stats,
                **stats
            }
        )
        
    except Exception as e:
        logger.error(f"Add messages error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding messages: {str(e)}"
        )


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get system status and database statistics.
    
    Returns:
        System status and statistics
    """
    try:
        db_stats = db_manager.get_database_stats()
        users = db_manager.get_all_users()
        
        return StatusResponse(
            status="operational",
            database_stats=db_stats,
            users=users
        )
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving status: {str(e)}"
        )


@app.get("/users")
async def get_users():
    """
    Get list of all users in the database.
    
    Returns:
        List of usernames
    """
    try:
        users = db_manager.get_all_users()
        return {"users": users, "count": len(users)}
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users: {str(e)}"
        )


@app.get("/users/{username}/patterns")
async def get_user_patterns(username: str):
    """
    Get detailed communication patterns for a specific user.
    
    Args:
        username: Username to analyze
        
    Returns:
        User patterns and statistics
    """
    try:
        patterns = db_manager.query_user_patterns(username)
        
        if not patterns.get('user'):
            raise HTTPException(
                status_code=404,
                detail=f"User '{username}' not found"
            )
        
        return patterns
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get patterns error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving patterns: {str(e)}"
        )


# Visualization Endpoints

@app.get("/visualize/graph")
async def visualize_graph():
    """
    Get graph structure for network visualization.
    
    Returns:
        Plotly-compatible network graph with nodes and edges
    """
    try:
        graph_structure = db_manager.get_graph_structure()
        
        # Create visualization
        chart_data = viz_service.create_network_graph(graph_structure)
        
        return {
            'chart': chart_data,
            'analysis': graph_structure
        }
        
    except Exception as e:
        logger.error(f"Graph visualization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating graph visualization: {str(e)}"
        )


@app.get("/visualize/sentiment/{username}")
async def visualize_sentiment(username: str):
    """
    Get sentiment progression visualization for a user.
    
    Args:
        username: Username to analyze
        
    Returns:
        Plotly-compatible sentiment chart data
    """
    try:
        # Get messages for user
        messages = db_manager.get_all_messages_for_user(username)
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail=f"No messages found for user '{username}'"
            )
        
        # Analyze sentiment
        sentiment_data = nlp_analyzer.analyze_sentiment_progression(messages)
        
        # Create visualization
        chart_data = viz_service.create_sentiment_timeline_chart(sentiment_data)
        
        return {
            'chart': chart_data,
            'analysis': sentiment_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment visualization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating sentiment visualization: {str(e)}"
        )


@app.get("/visualize/topics")
async def visualize_topics(method: str = "lda"):
    """
    Get topic distribution visualization.
    
    Args:
        method: Topic modeling method ('lda' or 'bertopic')
        
    Returns:
        Plotly-compatible topic distribution chart
    """
    try:
        # Get all messages
        messages = db_manager.get_all_messages()
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail="No messages found in database"
            )
        
        # Analyze topics
        if method.lower() == 'bertopic':
            topics_data = nlp_analyzer.extract_topics_bertopic(messages)
        else:
            topics_data = nlp_analyzer.extract_topics_lda(messages)
        
        # Create visualization
        chart_data = viz_service.create_topic_distribution_chart(topics_data)
        
        return {
            'chart': chart_data,
            'analysis': topics_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Topic visualization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating topic visualization: {str(e)}"
        )


@app.get("/visualize/personality/{username}")
async def visualize_personality(username: str):
    """
    Get personality traits visualization for a user.
    
    Args:
        username: Username to analyze
        
    Returns:
        Plotly-compatible personality radar chart
    """
    try:
        messages = db_manager.get_all_messages_for_user(username)
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail=f"No messages found for user '{username}'"
            )
        
        # Analyze personality
        personality_data = nlp_analyzer.analyze_personality_traits(messages)
        
        # Create visualization
        chart_data = viz_service.create_personality_radar_chart(personality_data)
        
        return {
            'chart': chart_data,
            'analysis': personality_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Personality visualization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating personality visualization: {str(e)}"
        )


@app.get("/visualize/patterns")
async def visualize_patterns():
    """
    Get conversation pattern visualizations.
    
    Returns:
        Multiple chart data for conversation patterns
    """
    try:
        messages = db_manager.get_all_messages()
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail="No messages found in database"
            )
        
        # Analyze patterns
        patterns = conversation_analyzer.analyze_comprehensive(messages)
        
        # Create visualizations
        response_time_chart = viz_service.create_response_time_distribution(patterns['response_times'])
        activity_chart = viz_service.create_activity_heatmap(patterns['activity_patterns'])
        length_chart = viz_service.create_message_length_distribution(patterns['message_lengths'])
        
        return {
            'response_times': {
                'chart': response_time_chart,
                'analysis': patterns['response_times']
            },
            'activity': {
                'chart': activity_chart,
                'analysis': patterns['activity_patterns']
            },
            'message_lengths': {
                'chart': length_chart,
                'analysis': patterns['message_lengths']
            },
            'conversation_flow': patterns['conversation_flow'],
            'question_patterns': patterns['question_patterns']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pattern visualization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating pattern visualizations: {str(e)}"
        )


@app.get("/visualize/formality/{username}")
async def visualize_formality(username: str):
    """
    Get formality level visualization for a user.
    
    Args:
        username: Username to analyze
        
    Returns:
        Plotly-compatible formality gauge chart
    """
    try:
        messages = db_manager.get_all_messages_for_user(username)
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail=f"No messages found for user '{username}'"
            )
        
        # Analyze formality
        formality_data = nlp_analyzer.analyze_formality(messages)
        
        # Create visualization
        chart_data = viz_service.create_formality_gauge(formality_data)
        
        return {
            'chart': chart_data,
            'analysis': formality_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Formality visualization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating formality visualization: {str(e)}"
        )


@app.get("/analyze/comprehensive/{username}")
async def analyze_comprehensive(username: str):
    """
    Get comprehensive analysis for a user (all analytics combined).
    
    Args:
        username: Username to analyze
        
    Returns:
        Complete analysis with all metrics
    """
    try:
        messages = db_manager.get_all_messages_for_user(username)
        all_messages = db_manager.get_all_messages()
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail=f"No messages found for user '{username}'"
            )
        
        # Run all analyses
        nlp_analysis = nlp_analyzer.analyze_comprehensive(messages)
        conversation_analysis = conversation_analyzer.analyze_comprehensive(all_messages)
        
        return {
            'username': username,
            'total_messages': len(messages),
            'nlp_analysis': nlp_analysis,
            'conversation_patterns': conversation_analysis,
            'graph_patterns': db_manager.query_user_patterns(username)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating comprehensive analysis: {str(e)}"
        )


# ============================================================================
# CONVERSATION SUGGESTIONS ENDPOINTS
# ============================================================================

@app.get("/suggestions/starters/{username}")
async def get_conversation_starters(username: str, recent_days: int = 30):
    """
    Get AI-generated conversation starter suggestions for a user.
    
    Args:
        username: Target user
        recent_days: Consider topics from last N days
        
    Returns:
        Conversation starter suggestions
    """
    try:
        # Get user's messages
        messages = db_manager.get_all_messages_for_user(username)
        if not messages:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        # Get user's topics
        patterns = db_manager.query_user_patterns(username)
        topics = patterns.get('topics', [])
        
        # Generate suggestions
        suggestions = suggestions_service.suggest_conversation_starters(
            username, messages, topics, recent_days
        )
        
        return suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation starters error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating conversation starters: {str(e)}"
        )


@app.get("/suggestions/topics/{username}")
async def get_topic_recommendations(username: str):
    """
    Recommend new topics based on user's conversation history.
    
    Args:
        username: Target user
        
    Returns:
        Topic recommendations
    """
    try:
        messages = db_manager.get_all_messages_for_user(username)
        if not messages:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        # Get all topics and user's discussed topics
        graph_structure = db_manager.get_graph_structure()
        all_topics = graph_structure.get('nodes', [])
        all_topics = [n for n in all_topics if n.get('type') == 'topic']
        
        patterns = db_manager.query_user_patterns(username)
        discussed_topics = [t['topic'] for t in patterns.get('topics', [])]
        
        recommendations = suggestions_service.recommend_topics(
            username, messages, all_topics, discussed_topics
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Topic recommendations error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating topic recommendations: {str(e)}"
        )


@app.post("/suggestions/predict-response")
async def predict_response(request: QueryRequest):
    """
    Predict likely response patterns based on a question.
    
    Body:
        {
            "user_context": "username",
            "query": "question to predict response for"
        }
        
    Returns:
        Response prediction
    """
    try:
        username = request.user_context
        question = request.query
        
        messages = db_manager.get_all_messages_for_user(username)
        if not messages:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        prediction = suggestions_service.predict_response(question, messages)
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Response prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting response: {str(e)}"
        )


# ============================================================================
# RELATIONSHIP INSIGHTS ENDPOINTS
# ============================================================================

@app.get("/insights/compatibility/{user1}/{user2}")
async def analyze_user_compatibility(user1: str, user2: str):
    """
    Analyze communication style compatibility between two users.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        Compatibility analysis
    """
    try:
        user1_messages = db_manager.get_all_messages_for_user(user1)
        user2_messages = db_manager.get_all_messages_for_user(user2)
        
        if not user1_messages:
            raise HTTPException(status_code=404, detail=f"User '{user1}' not found")
        if not user2_messages:
            raise HTTPException(status_code=404, detail=f"User '{user2}' not found")
        
        compatibility = insights_service.analyze_compatibility(
            user1_messages, user2_messages, user1, user2
        )
        
        return compatibility
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compatibility analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing compatibility: {str(e)}"
        )


@app.get("/insights/interaction/{user1}/{user2}")
async def analyze_interaction_frequency(user1: str, user2: str):
    """
    Analyze interaction frequency and patterns between two users.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        Interaction frequency analysis
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        analysis = insights_service.analyze_interaction_frequency(
            all_messages, user1, user2
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Interaction frequency error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing interactions: {str(e)}"
        )


@app.get("/insights/support/{user1}/{user2}")
async def analyze_emotional_support(user1: str, user2: str):
    """
    Analyze emotional support patterns between two users.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        Emotional support analysis
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        analysis = insights_service.analyze_emotional_support(
            all_messages, user1, user2
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Emotional support analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing emotional support: {str(e)}"
        )


@app.get("/insights/conflicts/{user1}/{user2}")
async def detect_conversation_conflicts(user1: str, user2: str):
    """
    Detect potential conflict patterns in conversations.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        Conflict detection analysis
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        analysis = insights_service.detect_conflicts(
            all_messages, user1, user2
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Conflict detection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting conflicts: {str(e)}"
        )


@app.get("/insights/dynamics/{user1}/{user2}")
async def analyze_conversation_dynamics(user1: str, user2: str):
    """
    Comprehensive analysis of conversation dynamics between two users.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        Conversation dynamics analysis
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        analysis = insights_service.analyze_conversation_dynamics(
            all_messages, user1, user2
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Dynamics analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing conversation dynamics: {str(e)}"
        )


# ============================================================================
# PERSONAL KNOWLEDGE BASE ENDPOINTS
# ============================================================================

@app.get("/knowledge/search")
async def search_knowledge_base(q: str, username: Optional[str] = None, limit: int = 10):
    """
    Search conversation history for specific topics or keywords.
    
    Query params:
        q: Search query
        username: Optional filter by user
        limit: Maximum results (default: 10)
        
    Returns:
        Search results
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        results = knowledge_base.search_conversations(
            q, all_messages, username, limit
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching knowledge base: {str(e)}"
        )


@app.get("/knowledge/topic/{topic}")
async def find_topic_discussions(topic: str, username: Optional[str] = None):
    """
    Find when a specific topic was discussed.
    
    Args:
        topic: Topic to search for
        username: Optional filter by user
        
    Returns:
        Timeline of topic discussions
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        timeline = knowledge_base.find_discussion_about(
            topic, all_messages, username
        )
        
        return timeline
        
    except Exception as e:
        logger.error(f"Topic discussion search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error finding topic discussions: {str(e)}"
        )


@app.get("/knowledge/last-mention/{keyword}")
async def recall_last_mention(keyword: str, username: Optional[str] = None):
    """
    Find the last time a keyword was mentioned.
    
    Args:
        keyword: Keyword to search for
        username: Optional filter by user
        
    Returns:
        Last mention information
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        result = knowledge_base.recall_last_mention(
            keyword, all_messages, username
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Last mention recall error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error recalling last mention: {str(e)}"
        )


@app.get("/knowledge/facts")
async def extract_conversation_facts(username: Optional[str] = None):
    """
    Extract factual statements from conversations.
    
    Query params:
        username: Optional filter by user
        
    Returns:
        Extracted facts
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        facts = knowledge_base.extract_facts(all_messages, username)
        
        return facts
        
    except Exception as e:
        logger.error(f"Fact extraction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting facts: {str(e)}"
        )


@app.get("/knowledge/entity/{entity}")
async def query_entity_knowledge(entity: str):
    """
    Build knowledge graph for a specific entity.
    
    Args:
        entity: Entity to query (person, place, thing)
        
    Returns:
        Knowledge graph data for entity
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        graph = knowledge_base.build_knowledge_graph_query(
            entity, all_messages
        )
        
        return graph
        
    except Exception as e:
        logger.error(f"Entity knowledge query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error querying entity knowledge: {str(e)}"
        )


@app.get("/knowledge/semantic-search")
async def semantic_search_knowledge(q: str, limit: int = 10):
    """
    Perform semantic (meaning-based) search across conversations.
    
    Query params:
        q: Search query
        limit: Maximum results
        
    Returns:
        Semantic search results
    """
    try:
        all_messages = db_manager.get_all_messages()
        
        results = knowledge_base.semantic_search(q, all_messages, limit)
        
        return results
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing semantic search: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        reload_dirs=["app"] if settings.debug else None
    )
