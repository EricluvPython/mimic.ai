# 🤖 Mimic.AI

AI-powered WhatsApp chat analyzer and personality mimic system. Upload your WhatsApp chat exports to analyze conversation patterns, extract insights, and generate AI responses that mimic specific communication styles.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Core Capabilities
- **Chat Upload & Analysis**: Upload WhatsApp `.txt` or `.zip` exports for instant processing
- **AI Personality Mimicry**: Generate responses that match a user's unique communication style
- **Contextual Conversations**: AI maintains conversation context for coherent, relevant responses
- **Smart Suggestions**: Get AI-generated conversation starters based on user patterns

### 📊 Analytics & Insights
- **Sentiment Analysis**: Track emotional progression over time
- **Topic Extraction**: Identify key discussion topics using LDA and BERTopic
- **Personality Profiling**: Radar chart visualization of communication traits
- **Communication Patterns**: Response times, activity heatmaps, message lengths
- **Relationship Insights**: Compatibility analysis between conversation participants
- **Knowledge Base**: Semantic search across conversation history

### 🎨 User Interface
- **Modern Chat Interface**: WhatsApp-like UI with message bubbles and date dividers
- **AI Mode Toggle**: Switch between normal chat and AI-powered responses
- **Theme Support**: Green and Futuristic theme options
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Smooth scrolling and message rendering

## 🏗️ Architecture

### Frontend (Next.js + React)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom CSS variables
- **Components**: Modular, reusable React components
- **State Management**: React hooks and local state
- **API Client**: Type-safe API integration

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: Neo4j graph database for relationship mapping
- **AI/LLM**: OpenRouter API with Claude 3.5 Sonnet
- **NLP**: Advanced text analysis with sentence transformers
- **Parser**: WhatsApp chat format parser

### Key Technologies
- **Graph Database**: Neo4j for storing messages, users, and relationships
- **Vector Embeddings**: Sentence transformers for semantic search
- **Topic Modeling**: LDA and BERTopic for conversation themes
- **Sentiment Analysis**: NLP-based emotional tone detection

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **Docker** (for Neo4j database)
- **OpenRouter API Key** (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/EricluvPython/mimic.ai.git
cd mimic.ai
```

2. **Set up the backend**
```bash
# Create Python virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt
```

3. **Set up the frontend**
```bash
# Install Node.js dependencies
npm install
```

4. **Start Neo4j database**
```bash
docker-compose up -d
```

5. **Configure environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your-api-key-here
```

### Running the Application

1. **Start the backend server**
```bash
python -m app.main
```
The backend will run on `http://localhost:8000`

2. **Start the frontend (in a new terminal)**
```bash
npm run dev
```
The frontend will run on `http://localhost:3000`

3. **Access the application**
Open your browser to `http://localhost:3000`

## 📖 Usage

### Upload a Chat
1. Click the "Upload Chat" button
2. Select a WhatsApp chat export (`.txt` or `.zip` file)
3. Chat messages will appear in the interface
4. Backend will process and store in Neo4j database

### AI Mode
1. Toggle the 💡 button to enable AI Mode
2. AI-generated conversation starters will appear
3. Type a message and send
4. AI will respond mimicking the target user's style
5. Conversation context is maintained across messages

### Export WhatsApp Chats
**On Mobile:**
1. Open WhatsApp chat
2. Tap ⋮ (menu) → More → Export chat
3. Choose "Without Media"
4. Save the `.txt` file

**On Desktop:**
1. Open WhatsApp chat
2. Click ⋮ (menu) → More → Export chat
3. Choose "Without Media"
4. Download the `.txt` file

## 🛠️ API Endpoints

### Chat Management
- `POST /upload` - Upload WhatsApp chat file
- `POST /messages/add` - Add new messages incrementally
- `GET /users` - List all users in database
- `GET /users/{username}/patterns` - Get user communication patterns

### AI & Queries
- `POST /query` - Generate AI response mimicking user style
- `GET /suggestions/starters/{username}` - Get conversation starters
- `GET /suggestions/topics/{username}` - Get topic recommendations

### Analytics
- `GET /visualize/sentiment/{username}` - Sentiment timeline
- `GET /visualize/topics` - Topic distribution
- `GET /visualize/personality/{username}` - Personality traits
- `GET /visualize/patterns` - Conversation patterns
- `GET /analyze/comprehensive/{username}` - Complete analysis

### Insights
- `GET /insights/compatibility/{user1}/{user2}` - Communication compatibility
- `GET /insights/interaction/{user1}/{user2}` - Interaction patterns
- `GET /knowledge/search?q={query}` - Semantic search conversations

## 📁 Project Structure

```
mimic.ai/
├── app/                          # Backend (Python/FastAPI)
│   ├── main.py                   # API endpoints
│   ├── config.py                 # Configuration management
│   ├── parser.py                 # WhatsApp chat parser
│   ├── graph_db.py              # Neo4j database manager
│   ├── llm_service.py           # OpenRouter/LLM integration
│   ├── nlp_analyzer.py          # NLP and sentiment analysis
│   ├── conversation_analyzer.py # Pattern detection
│   ├── visualization_service.py # Chart generation
│   ├── conversation_suggestions.py # AI suggestions
│   ├── relationship_insights.py # Relationship analysis
│   └── knowledge_base.py        # Semantic search
├── components/                   # Frontend React components
│   ├── ChatContainer.tsx        # Main chat container
│   ├── ChatInterface.tsx        # Chat UI with AI mode
│   ├── MessageBubble.tsx        # Message display
│   ├── FileUpload.tsx           # File upload component
│   └── Sidebar.tsx              # Chat list sidebar
├── lib/                         # Utility libraries
│   ├── api.ts                   # Backend API client
│   ├── chatParser.ts            # Chat parsing utilities
│   └── fileUtils.ts             # File handling utilities
├── app/                         # Next.js app directory
├── public/                      # Static assets
├── neo4j_data/                  # Neo4j database files
├── docker-compose.yml           # Neo4j container config
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies
└── .env.example                 # Environment variables template
```

## 🔧 Configuration

### Environment Variables

**Backend:**
- `OPENROUTER_API_KEY` - OpenRouter API key for AI features
- `OPENROUTER_MODEL` - Model to use (default: `anthropic/claude-3.5-sonnet`)
- `NEO4J_URI` - Neo4j connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER` - Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD` - Neo4j password
- `APP_PORT` - Backend port (default: `8000`)

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)

## 🧪 Development

### Backend Development
```bash
# Run with auto-reload
python -m app.main

# View API docs
# Navigate to http://localhost:8000/docs
```

### Frontend Development
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Database Management
```bash
# Clear all data from Neo4j
docker exec mimic-ai-neo4j cypher-shell -u neo4j -p mimicai2025 "MATCH (n) DETACH DELETE n;"

# View Neo4j browser
# Navigate to http://localhost:7474
```

## 📊 Analytics Features

### Sentiment Analysis
Tracks emotional tone progression throughout conversations using NLP sentiment classification.

### Topic Modeling
- **LDA**: Latent Dirichlet Allocation for topic extraction
- **BERTopic**: BERT-based topic modeling for semantic clustering

### Personality Insights
Analyzes communication style across dimensions:
- Formality level
- Emotional expressiveness
- Message length patterns
- Response time behavior

### Relationship Analysis
- Communication compatibility scoring
- Interaction frequency patterns
- Emotional support detection
- Conflict pattern identification

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenRouter** - AI/LLM API integration
- **Neo4j** - Graph database technology
- **Hugging Face** - Sentence transformers and NLP models
- **Next.js** - React framework
- **FastAPI** - Python web framework

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ by the Mimic.AI team**
