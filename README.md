# 🏠 Vastu AI Agent — FastAPI RAG Service

A lightweight **Retrieval-Augmented Generation (RAG)** microservice that returns relevant **Vastu Shastra rules** for a given room type and furniture list. Built with FastAPI and designed to plug into an **n8n AI automation workflow**.

---

## 📐 Architecture

```
[Telegram / Trigger]
        │
        ▼
[n8n Workflow]
        │
        ├─ 1. Get File (image from Telegram)
        │
        ├─ 2. Gemini Vision → identifies room type + furniture list
        │
        ├─ 3. HTTP POST → /api/v1/get_vastu_rules   ◄── this service
        │         returns matching Vastu rules
        │
        └─ 4. Gemini LLM → generates personalised Vastu advice
                   using the retrieved rules as context
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A **Google AI Studio API key** — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey)
- Git

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/smr24projs/vastu-ai-agent.git
cd vastu-ai-agent/vastu-ai-agent
```

---

### Step 2 — Create a virtual environment

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

> You'll see `(venv)` appear at the start of your terminal prompt when it's active.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set up your API key

Copy the example environment file:

**Windows:**
```cmd
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` in any text editor and replace the placeholder:

```
GOOGLE_API_KEY=your_google_api_key_here
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

---

### Step 5 — Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:

```
INFO | vastu-ai | === Vastu AI Service starting up ===
INFO | vastu-ai | Loaded 5 room section(s): ['bedroom', 'living room', 'kitchen', 'bathroom', 'study room']
INFO | vastu-ai | === Startup complete — ready to serve requests ===
INFO | uvicorn  | Application startup complete.
```

---

### Step 6 — Verify it's working

Open your browser and go to:

```
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ready",
  "loaded_rooms": ["bedroom", "living room", "kitchen", "bathroom", "study room"]
}
```

Or test the main endpoint with curl:

```bash
curl -X POST http://localhost:8000/api/v1/get_vastu_rules \
  -H "Content-Type: application/json" \
  -d '{"room_type": "bedroom", "furniture_list": ["bed", "wardrobe", "mirror"]}'
```

---

## 📡 API Reference

### `GET /health`

Check if the service loaded successfully.

| Field | Type | Description |
|---|---|---|
| `status` | string | `"ready"` when rules are loaded |
| `loaded_rooms` | array | List of room sections available |

---

### `POST /api/v1/get_vastu_rules`

Retrieve Vastu rules for a given room and furniture list.

**Request body:**

```json
{
  "room_type": "bedroom",
  "furniture_list": ["bed", "wardrobe", "full-length mirror"]
}
```

**Response:**

```json
{
  "retrieved_rules": [
    "Vastu Rules for Bedroom:\n- The bed should ideally be placed in the South or West direction of the room.\n- Avoid placing a mirror directly facing the bed.\n..."
  ],
  "query_used": "Vastu rules for bedroom"
}
```

---

## 📁 Project Structure

```
vastu-ai-agent/
├── main.py              # FastAPI app — retrieval logic + API endpoints
├── vastu_rules.txt      # Vastu Shastra knowledge base (plain text)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for environment variables
├── .gitignore           # Excludes venv, .env, cache files
└── README.md            # You are here
```

---

## 🌐 Exposing to the Internet (for n8n)

If your n8n instance is in the cloud and your FastAPI server is running locally, use **Pinggy** to create a public tunnel:

```bash
ssh -p 443 -R0:localhost:8000 a.pinggy.io
```

This gives you a temporary public URL like:
```
https://xxxx-xx-xx-xx-xx.run.pinggy-free.link
```

Use that URL in your n8n HTTP Request node.

> ⚠️ Pinggy free URLs expire after ~60 minutes. For production, use a cloud deployment (Railway, Render, etc.).

---

## ✏️ Extending the Knowledge Base

Open `vastu_rules.txt` and add new sections in this exact format:

```
Vastu Rules for Dining Room:
- The dining room should ideally be in the West direction.
- The dining table should be square or rectangular, not round or oval.
- The head of the family should sit facing East while eating.
```

Each section is automatically parsed and indexed on next server startup. No code changes needed.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv activated |
| `GOOGLE_API_KEY not set` | Make sure `.env` exists and has your key |
| Room not found in results | Check that `vastu_rules.txt` has a `Vastu Rules for <Room>:` header |
| n8n timeout | Make sure uvicorn is running and the tunnel is active |

---

## 📄 License

MIT
