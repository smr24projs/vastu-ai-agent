import os
import logging
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vastu-ai")

# ── Globals ────────────────────────────────────────────────────────────────────
VASTU_FILE = "vastu_rules.txt"
vastu_sections: dict[str, str] = {}   # e.g. {"bedroom": "Vastu Rules for Bedroom:\n- ..."}


def load_vastu_sections(filepath: str) -> dict[str, str]:
    """
    Parse vastu_rules.txt into a dict keyed by lowercase room name.
    Sections are separated by blank lines and start with 'Vastu Rules for <Room>:'.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections: dict[str, str] = {}
    # Split on double newlines to get paragraphs/sections
    blocks = [b.strip() for b in re.split(r"\n{2,}", content) if b.strip()]

    for block in blocks:
        # Look for a header like "Vastu Rules for Bedroom:"
        match = re.match(r"Vastu Rules for (.+?):", block, re.IGNORECASE)
        if match:
            room_name = match.group(1).strip().lower()   # "bedroom"
            sections[room_name] = block
            logger.debug(f"Loaded section: '{room_name}' ({len(block)} chars)")
        else:
            logger.debug(f"Skipping block (no header): {block[:40]!r}")

    return sections


def search_rules(room_type: str, k: int = 3) -> list[str]:
    """
    Return up to k matching rule-blocks for the given room type.
    Tries exact match first, then partial match.
    """
    room_lower = room_type.strip().lower()
    results: list[str] = []

    # 1. Exact key match
    if room_lower in vastu_sections:
        results.append(vastu_sections[room_lower])
        logger.debug(f"Exact match found for '{room_lower}'")

    # 2. Partial match for remaining slots
    if len(results) < k:
        for key, text in vastu_sections.items():
            if key != room_lower and room_lower in key:
                results.append(text)
                if len(results) >= k:
                    break

    # 3. Fallback: return all sections if nothing matched
    if not results:
        logger.warning(f"No match for '{room_lower}' — returning all sections as fallback")
        results = list(vastu_sections.values())[:k]

    return results[:k]


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global vastu_sections
    logger.info("=== Vastu AI Service starting up ===")

    if not os.path.exists(VASTU_FILE):
        logger.error(f"'{VASTU_FILE}' not found! Place it next to main.py")
    else:
        vastu_sections = load_vastu_sections(VASTU_FILE)
        logger.info(f"Loaded {len(vastu_sections)} room section(s): {list(vastu_sections.keys())}")

    logger.info("=== Startup complete — ready to serve requests ===")
    yield
    logger.info("=== Vastu AI Service shutting down ===")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Vastu RAG Service", lifespan=lifespan)


class VastuRequest(BaseModel):
    room_type: str
    furniture_list: list[str]


@app.get("/health")
async def health():
    """Quick health-check — call this before hitting the main endpoint."""
    return {
        "status": "ready",
        "loaded_rooms": list(vastu_sections.keys()),
    }


@app.post("/api/v1/get_vastu_rules")
async def get_rules(request: VastuRequest):
    logger.info(f"Incoming → room_type='{request.room_type}'  furniture={request.furniture_list}")

    if not vastu_sections:
        raise HTTPException(status_code=503, detail="Vastu rules not loaded. Check vastu_rules.txt.")

    query = f"Vastu rules for {request.room_type}"
    rules = search_rules(request.room_type, k=3)

    logger.info(f"Returning {len(rules)} rule block(s) for '{request.room_type}'")
    for i, rule in enumerate(rules):
        logger.debug(f"Rule {i+1} preview: {rule[:80].strip()!r}")

    return {
        "retrieved_rules": rules,
        "query_used": query,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)