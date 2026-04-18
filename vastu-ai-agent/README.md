# Vastu AI Agent 🏠

A FastAPI-based Retrieval service that returns relevant **Vastu Shastra rules** for a given room type and furniture list. Designed to be used as part of an n8n AI automation workflow.

## Architecture

```
[n8n Workflow]
      │
      ├─ Image Analysis (Gemini Vision) → detects room type + furniture
      │
      ├─ HTTP POST → /api/v1/get_vastu_rules   ← this service
      │       returns matching Vastu rules
      │
      └─ LLM Node (Gemini) → generates final Vastu advice using retrieved rules
```

## Features

- ⚡ Instant startup — no embedding API calls needed
- 📖 Keyword-based retrieval from a local `vastu_rules.txt` knowledge base
- 🔍 `/health` endpoint to verify service readiness
- 🪵 Structured logging with timestamps and log levels
- 🔁 Hot-reload support via `uvicorn --reload`

## Setup

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd vastu-ai-agent
```

### 2. Create and activate virtual environment
```bash
# Windows (cmd)
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

### 5. Run the server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Reference

### `GET /health`
Check if the service is ready.

**Response:**
```json
{
  "status": "ready",
  "loaded_rooms": ["bedroom", "living room", "kitchen", "bathroom", "study room"]
}
```

---

### `POST /api/v1/get_vastu_rules`
Retrieve Vastu rules for a given room.

**Request body:**
```json
{
  "room_type": "bedroom",
  "furniture_list": ["bed", "wardrobe", "mirror"]
}
```

**Response:**
```json
{
  "retrieved_rules": [
    "Vastu Rules for Bedroom:\n- The bed should ideally be placed in the South or West direction..."
  ],
  "query_used": "Vastu rules for bedroom"
}
```

## Extending the Knowledge Base

Edit `vastu_rules.txt` and add new sections following this format:

```
Vastu Rules for <Room Name>:
- Rule one
- Rule two
```

Each section is automatically parsed and indexed on startup.

## Project Structure

```
vastu-ai-agent/
├── main.py              # FastAPI app with retrieval logic
├── vastu_rules.txt      # Vastu knowledge base
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── .gitignore
```
