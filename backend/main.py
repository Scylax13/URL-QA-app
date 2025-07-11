# If you see import errors, run: pip install -r requirements.txt
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests as pyrequests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    url: str
    question: str

class AskResponse(BaseModel):
    answer: str

# Helper: Scrape and extract main text from a webpage
def extract_text_from_url(url: str) -> str:
    resp = pyrequests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    # Try to get main content
    main = soup.find("main")
    if main:
        text = main.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)
    # Optionally truncate to a reasonable length
    return text[:8000]  # Gemini context limit safety

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    # 1. Scrape the webpage
    try:
        page_text = extract_text_from_url(request.url)
    except Exception as e:
        return {"answer": f"Error scraping URL: {str(e)}"}

    # 2. Call Gemini API
    if not client:
        return {"answer": "Gemini API key not set. Please set GEMINI_API_KEY in your .env file."}
    try:
        prompt = f"You are an assistant. Use the following webpage content to answer the user's question.\n\nWebpage Content:\n{page_text}\n\nUser Question: {request.question}\n\nAnswer:"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        # Safely extract the answer
        answer = None
        candidates = getattr(response, "candidates", None)
        if isinstance(candidates, list) and len(candidates) > 0:
            candidate = candidates[0]
            if candidate and getattr(candidate, "content", None):
                content = candidate.content
                parts = getattr(content, "parts", None)
                if isinstance(parts, list) and len(parts) > 0:
                    part = parts[0]
                    if hasattr(part, "text") and part.text:
                        answer = part.text.strip()
        if not answer:
            answer = "No answer returned by Gemini API."
    except Exception as e:
        answer = f"Error from Gemini API: {str(e)}"
    return {"answer": answer} 