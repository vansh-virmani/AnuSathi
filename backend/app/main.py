import sys
import io

# Force UTF-8 encoding globally — prevents 'charmap' errors on Windows
# when processing text with Unicode characters (e.g. Greek letters in ML papers)
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.upload import router as upload_router
from app.routes.query import router as query_router

app = FastAPI(
    title="Research Paper Explainer API",
    version="1.0.0",
    description="API for uploading research papers and querying them using RAG."
)

# Allow browser to call the API from any origin (needed for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(query_router)

# Serve the frontend static files from the frontend/ folder
# Structure: backend/app/main.py → ../../.. = project root → /frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/style.css")
def serve_css():
    return FileResponse(FRONTEND_DIR / "style.css", media_type="text/css")

@app.get("/app.js")
def serve_js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")




