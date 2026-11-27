from python_learning_4.schemas.chat import ChatRequest,ChatResponse
from fastapi import HTTPException,APIRouter
from groq import AsyncGroq
from config import settings
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
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


langchain_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.groq_api_key,
    temperature=0.7,
    max_tokens=2048
)

langchain_chat_history = {}

@router.post("/chat-langchain", response_model=ChatResponse)
async def chat_langchain(request: ChatRequest):



    session_id = request.session_id

    if request.is_new_chat:
        langchain_chat_history[session_id] = [
            SystemMessage(
                content="You are a simple chatbot answering user questions "
                        "in simple terms in 2 lines."
            )
        ]

    if session_id not in langchain_chat_history:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    user_message = request.question.strip()

    if user_message.lower() == "end":
        langchain_chat_history.pop(session_id, None)
        return ChatResponse(response="Chat ended!")

    langchain_chat_history[session_id].append(
        HumanMessage(content=user_message)
    )

    completion = await langchain_llm.ainvoke(
        langchain_chat_history[session_id]
    )

    answer = completion.content or ""

    langchain_chat_history[session_id].append(
        AIMessage(content=answer)
    )

    return ChatResponse(response=answer)





def process_question(data):
    return {
        **data,
        "question": data["question"].strip()
    }

question_runnable = RunnableLambda(process_question)


chat_template_history = {}

def get_session_history(session_id:str):
    if session_id not in chat_template_history:
        chat_template_history[session_id] = InMemoryChatMessageHistory()
        
    return chat_template_history[session_id]
    
@router.post(
    "/chat-prompt-template-langchain",
    response_model=ChatResponse
)
async def chat_template(request:ChatRequest):

    session_id = request.session_id 
    user_message = request.question
    
    if user_message.lower() == "end":
        chat_template_history.pop(session_id, None)
        return ChatResponse(response="Chat ended!")
    
    if(request.is_new_chat == False and session_id not in chat_template_history):
        raise HTTPException(status_code=404,detail="Invalid Chat session!!")
    
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a simple chatbot answering user questions in simple terms in 2 lines."),
         MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = question_runnable | template | langchain_llm

    chain_with_history = RunnableWithMessageHistory(chain,
                                                    get_session_history,
                                                    input_messages_key="question",
                                                    history_messages_key="history")

    ai_answer = await chain_with_history.ainvoke(
        {"question": request.question},
        config={"configurable":{"session_id":request.session_id}}
    )

    return ChatResponse(response=ai_answer.content)

    
