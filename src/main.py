from fastapi import FastAPI
from .database.database import Base, engine
from .routers import kakao_login, platform_test, users
from fastapi.middleware.cors import CORSMiddleware
from src.models import *

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://29be-210-178-112-177.ngrok-free.app"],  # 프론트 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kakao_login.router)
app.include_router(platform_test.router)
app.include_router(users.router)
