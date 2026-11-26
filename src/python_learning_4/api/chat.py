from python_learning_4.schemas.chat import ChatRequest,ChatResponse
from fastapi import HTTPException,APIRouter
from groq import AsyncGroq
from config import settings
router = APIRouter()
client = AsyncGroq(
    api_key=settings.groq_api_key
)


chat_history = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    session_id = request.session_id

    if request.is_new_chat:
        
        chat_history[session_id] = [
            {
                "role": "system",
                "content": "You are going to be a simple chatbot answering the user questions in simple terms in 2 lines"
            }
        ]
    if session_id not in chat_history:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    user_message = request.question.strip()

    if user_message.lower() == "end":
        chat_history.pop(session_id, None)
        return ChatResponse(response="Chat ended!")

    chat_history[session_id].append({
        "role": "user",
        "content": user_message
    })

    completion = await client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=chat_history[session_id],
        temperature=0.7,
        max_completion_tokens=2048,
        reasoning_effort="low"
    )

    answer = completion.choices[0].message.content or ""

    chat_history[session_id].append({
        "role": "assistant",
        "content": answer
    })

    return ChatResponse(response=answer)