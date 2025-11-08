# Mimic.AI Backend

WhatsApp Chat Analysis & User Mimicry System - A hackathon project that analyzes WhatsApp chat exports to build a knowledge graph and mimic user communication patterns.

## 🎯 Features

- **Chat Import**: Upload WhatsApp chat exports (.txt format)
- **Intelligent Graph Database**: Neo4j-powered knowledge graph capturing user thinking patterns, topics, and speech characteristics
- **AI-Powered Mimicry**: OpenRouter LLM integration to generate responses that match user's communication style
- **Incremental Updates**: Add new messages to existing knowledge graph
- **REST API**: FastAPI-based backend for easy frontend integration

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │ (Your teammate's message app)
│   (React/etc)   │
└────────┬────────┘
         │ REST API
         │
┌────────▼────────┐
│  FastAPI Backend│
│  - Parser       │
│  - LLM Service  │
│  - Graph Mgr    │
└────┬───────┬────┘
     │       │
     │       │
┌────▼────┐  │  ┌──────────┐
│ Neo4j   │  └──┤OpenRouter│
│ Graph DB│     │   LLM    │
└─────────┘     └──────────┘
```

## 📋 Prerequisites

- **Windows** (with VS Code)
- **Docker Desktop** (for Neo4j)
- **Python 3.11+**
- **OpenRouter API Key**

## 🚀 Setup Instructions

### 1. Install Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop/
2. Install and start Docker Desktop
3. Ensure it's running (check system tray)

### 2. Clone & Setup

```powershell
cd d:\CodeRepos\mimic.ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
notepad .env
```

Update the following in `.env`:
```env
OPENROUTER_API_KEY=your_actual_api_key_here
NEO4J_PASSWORD=mimicai2025  # Or choose your own
```

### 4. Start Neo4j Database

```powershell
# Start Neo4j using Docker
docker-compose up -d

# Verify it's running
docker ps
```

**Access Neo4j Browser**: http://localhost:7474
- Username: `neo4j`
- Password: `mimicai2025` (or what you set in .env)

### 5. Run the Backend

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the FastAPI server
python -m app.main
```

The API will be available at: **http://localhost:8000**

API Documentation (Swagger UI): **http://localhost:8000/docs**

## 📡 API Endpoints

### 1. Upload WhatsApp Chat
```http
POST /upload
Content-Type: multipart/form-data

file: <whatsapp_chat.txt>
```

### 2. Get Mimic Response
```http
POST /query
Content-Type: application/json

{
  "username": "John",
  "query": "What do you think about the project?"
}
```

### 3. Add New Messages
```http
POST /messages/add
Content-Type: application/json

{
  "messages": "01/11/2025, 10:30 - John: New message here"
}
```

### 4. Get System Status
```http
GET /status
```

### 5. Get All Users
```http
GET /users
```

### 6. Get User Patterns
```http
GET /users/{username}/patterns
```

## 📝 WhatsApp Chat Export Format

Export your WhatsApp chat:
1. Open WhatsApp chat
2. Tap menu (⋮) → More → Export chat
3. Choose "Without Media"
4. Save as `.txt` file

**Supported formats:**

**Format 1: Asian/International (YYYY/M/D with brackets)**
```
[2022/7/21 05:11:12] Eric Gao: Hi Sunaya, this is Eric
[2022/7/21 05:21:28] Sunaya: Yes
```

**Format 2: European (DD/MM/YYYY with dash)**
```
01/11/2025, 10:30 - John: Hello there!
01/11/2025, 10:31 - Jane: Hey! How are you?
```

**Format 3: US (MM/DD/YYYY with dash)**
```
11/01/2025, 10:30 - John: Hello there!
```

The parser automatically detects and handles:
- Multiple date formats (YYYY/M/D, DD/MM/YYYY, MM/DD/YYYY)
- Different separators (brackets, dashes, commas)
- System messages (encryption notices, etc.) - automatically skipped
- Chinese/Unicode characters
- Multi-line messages

## 🗄️ Graph Database Schema

### Nodes
- **User**: Chat participants with communication statistics
- **Message**: Individual messages with content and metadata
- **Topic**: Extracted topics and concepts

### Relationships
- `(User)-[:SENT]->(Message)`: User sent a message
- `(Message)-[:FOLLOWS]->(Message)`: Message sequence
- `(User)-[:DISCUSSES]->(Topic)`: User discusses topic
- `(User)-[:INTERACTS_WITH]->(User)`: User interaction patterns

## 🧪 Testing with Sample Data

You can test with a sample chat file:

```text
01/11/2025, 10:00 - Alice: Hey! How's the hackathon going?
01/11/2025, 10:01 - Bob: Great! Working on the backend now
01/11/2025, 10:02 - Alice: Awesome! Need any help?
01/11/2025, 10:03 - Bob: I'm good, but thanks!
```

Save this as `sample_chat.txt` and upload via the API.

## 🔧 Troubleshooting

### Docker Issues
```powershell
# Check if Docker is running
docker ps

# Restart Neo4j container
docker-compose restart

# View Neo4j logs
docker-compose logs neo4j
```

### Python/Dependencies
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

### Neo4j Connection
```powershell
# Test Neo4j connection
# Visit http://localhost:7474 in browser
# Should see Neo4j Browser login page
```

## 🎨 Frontend Integration

For your teammate building the frontend:

### Example: Upload Chat
```javascript
const formData = new FormData();
formData.append('file', chatFile);

const response = await fetch('http://localhost:8000/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.statistics);
```

### Example: Get Mimic Response
```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'Alice',
    query: 'What should I say about the project?'
  })
});

const result = await response.json();
console.log(result.response);  // AI-generated response in Alice's style
```

## 📊 Future Improvements

See `FUTURE_IMPROVEMENTS.md` for planned enhancements:
- Media file parsing and analysis
- Advanced NLP for better pattern extraction
- Visualization API endpoints
- User authentication
- Multi-language support
- Real-time updates via WebSockets

## 🤝 Team

- **Backend**: Your implementation
- **Frontend**: Your teammate's message app
- **Database**: Neo4j + MCP
- **LLM**: OpenRouter (Claude 3.5 Sonnet)

## 📄 License

Hackathon Project - MIT License

---

**Questions or Issues?** Check the API docs at http://localhost:8000/docs