# Quick Start Guide - Mimic.AI Backend

## ⚡ 5-Minute Setup

### Step 1: Start Neo4j
```powershell
docker-compose up -d
```

### Step 2: Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Configure
```powershell
copy .env.example .env
# Edit .env and add your OpenRouter API key
```

### Step 4: Run Server
```powershell
python -m app.main
```

### Step 5: Test
Open browser: http://localhost:8000/docs

---

## 📤 Testing the API

### Upload a Chat File
```powershell
# Using PowerShell and curl
curl -X POST "http://localhost:8000/upload" `
  -F "file=@sample_chat.txt"
```

### Get Mimic Response
```powershell
curl -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"Alice\",\"query\":\"What do you think?\"}'
```

---

## 🎯 Sample WhatsApp Chat

Create `sample_chat.txt`:
```
01/11/2025, 10:00 - Alice: Hey! How's the hackathon going?
01/11/2025, 10:01 - Bob: Great! Working on the backend now
01/11/2025, 10:02 - Alice: Awesome! Need any help?
01/11/2025, 10:03 - Bob: I'm good, but thanks! The graph database is really cool
01/11/2025, 10:05 - Alice: Nice! Can't wait to see it working
01/11/2025, 10:10 - Bob: Should be ready soon. Just testing the LLM integration
```

---

## 🔧 Common Commands

### Check Neo4j Status
```powershell
docker ps
```

### View Logs
```powershell
docker-compose logs -f neo4j
```

### Stop Everything
```powershell
docker-compose down
```

### Restart Backend
```powershell
# Just press Ctrl+C and run again
python -m app.main
```

---

## 📞 API Endpoints Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload WhatsApp chat file |
| POST | `/query` | Get mimic response |
| POST | `/messages/add` | Add new messages |
| GET | `/status` | System status |
| GET | `/users` | List all users |
| GET | `/users/{username}/patterns` | User patterns |

Full docs: http://localhost:8000/docs

---

## ❓ Troubleshooting

**Docker not starting?**
- Make sure Docker Desktop is running
- Check Windows Hyper-V is enabled

**Port already in use?**
- Change ports in `docker-compose.yml` and `.env`

**Python import errors?**
- Make sure venv is activated: `.\venv\Scripts\Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

**Neo4j connection refused?**
- Wait 10-20 seconds after `docker-compose up`
- Check http://localhost:7474 in browser

---

For detailed setup, see `README.md`
