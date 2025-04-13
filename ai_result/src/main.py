from fastapi import FastAPI
from src.api import content
from src.database.session import engine
from src.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(content.router, prefix="/api/content")
