# --- server.py ---
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai
from backend import hash_api_key
import config as cfg

# --- Load env vars ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

# --- Gemini Setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- FastAPI App Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Pydantic Schema ---
class ChatRequest(BaseModel):
    prompt: str
    email: str
    api_key: str

# --- Chat Endpoint ---
@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    hashed_input = hash_api_key(req.api_key)

    conn = sqlite3.connect(cfg.DB_NAME)
    c = conn.cursor()
    c.execute("SELECT usage_count FROM api_keys WHERE email = ? AND hashed_api_key = ?", (req.email, hashed_input))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=403, detail="Invalid API key or email.")

    try:
        response = model.generate_content(req.prompt)
        reply = getattr(response, "text", None)

        if not reply:
            raise ValueError("Gemini returned no response.")

        new_count = row[0] + 1
        c.execute("UPDATE api_keys SET usage_count = ? WHERE email = ? AND hashed_api_key = ?",
                  (new_count, req.email, hashed_input))
        conn.commit()
        conn.close()

        return {"reply": reply.strip()}

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Gemini error occurred.")
        
# --- Root Check ---
@app.get("/")
def root():
    return {"status": "Server is up and running."}
