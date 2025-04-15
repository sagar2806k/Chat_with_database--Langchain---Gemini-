from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from chatbot import get_response
from database import init_database
import uvicorn

app = FastAPI(title="Sales Inventory Chatbot API")

# Initialize database connection
db_connection = init_database()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_history: List[ChatMessage]

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def root():
    return {"message": "Welcome to Sales Inventory Chatbot API"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Convert chat history to the format expected by get_response
        formatted_chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]
        
        # Get response from chatbot
        response = get_response(request.message, formatted_chat_history)
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
