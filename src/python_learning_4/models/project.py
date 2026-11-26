from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from python_learning_4.models.base import Base


class Project(Base):
    id:Mapped[int] = mapped_column(autoincrement=True,nullable=False,primary_key=True)
    name:Mapped[str] =mapped_column(String,nullable=False)
    start_date:Mapped[datetime] = mapped_column(DateTime,nullable=False)

    __tablename__="projects"