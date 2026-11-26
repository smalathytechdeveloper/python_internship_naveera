from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id:str
    question:str
    
    is_new_chat: bool = False

class ChatResponse(BaseModel):
    response:str