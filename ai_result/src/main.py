from fastapi import FastAPI
from app.api import content
from app.database.session import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(content.router, prefix="/api/content")
