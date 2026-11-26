from datetime import datetime
from pydantic import BaseModel, ConfigDict
class ProjectResponse(BaseModel):
    id:int
    name:str
    start_date:datetime

    model_config = ConfigDict(from_attributes=True)