import base64
import io
import secrets
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import Response, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from groq import GroqClient
from uuid import uuid4
from backend import app
from backend.app.agent.nodes.retrieve import retrieve
from backend.app.agent.nodes.search_dec import route
from backend.app.agent.nodes.intent import web_search
from backend.app.agent.nodes.generator import answer
from backend.app.agent.state import State
from backend.app.agent.graph import graph, memory

ROOT = Path(__file__).resolve().parent.parent
app.mount("/static",title = "medical agent education api", version = '1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=["Authorization", "Content-Type"],
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question")
    history: list = Field(default_factory=list, description="The conversation history")
    image_description: str = Field(default="", description="Description of the image if provided")
    kb: list = Field(default_factory=list, description="Knowledge base search results")
    web: list = Field(default_factory=list, description="Web search results")
    answer: str = Field(default="", description="The generated answer")
    route: str = Field(default="", description="The routing decision")
    message: str = Field(default="", description="The message to be sent to the user")
    history: list = Field(default_factory=list, description="The conversation history")
    image_data: str = Field(default="", description="Base64 encoded image data if provided")

def auth(authorization: str = Form(...)):
    if authorization != f"Bearer {app.settings.api_key}":
        raise HTTPException(status_code=401, detail="Unauthorized")


def insert    