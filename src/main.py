from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .db.database import Base, engine
from .routers import kakao_login, users #, refresh
from fastapi.middleware.cors import CORSMiddleware
from src.api import store, search

import logging

# UTF8 Response 설정
class UTF8JSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        self.media_type = "application/json; charset=utf-8"
        return super().render(content)

# FastAPI 앱 생성
app = FastAPI(default_response_class=UTF8JSONResponse)

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# DB 초기화
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://29be-210-178-112-177.ngrok-free.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(kakao_login.router, prefix="/api")
app.include_router(users.router, prefix="/api")
# app.include_router(refresh.router, prefix="/api")
app.include_router(store.router, prefix="/stores")
app.include_router(search.router, prefix="/search")

