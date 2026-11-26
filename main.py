from fastapi import Depends, FastAPI, HTTPException
from python_learning_4.api.chat import router as chatbot_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from python_learning_4.schemas.project import ProjectResponse
from python_learning_4.schemas.chat import ChatRequest,ChatResponse
from python_learning_4.database import get_session
from python_learning_4.models.project import Project

app = FastAPI()

app.include_router(chatbot_router, prefix="/api")   

@app.get("/hello")
def printhello():
    print(settings.database_url)
    return "Hello World"

@app.get("/projects",response_model=list[ProjectResponse])
async def get_projects(db:AsyncSession = Depends(get_session)):
    result = await db.scalars(select(Project))
    return result.all()




