from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from src.db.database import Base, engine
from src.routers import (kakao_login, users, jwt_token, refresh)
from fastapi.middleware.cors import CORSMiddleware
from src.api import store, search
from fastapi.openapi.utils import get_openapi

import logging, os

# UTF8 Response 설정
class UTF8JSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        self.media_type = "application/json; charset=utf-8"
        return super().render(content)

# FastAPI 앱 생성
app = FastAPI(default_response_class=UTF8JSONResponse)
print("🔍 현재 DATABASE_URL:", os.getenv("DATABASE_URL"))
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
app.include_router(kakao_login.router)
app.include_router(users.router)
app.include_router(jwt_token.router)
app.include_router(refresh.router)
app.include_router(store.router)
app.include_router(search.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="SORI API",
        version="1.0.0",
        description="API 문서 (JWT 인증 필요 시 Bearer Token 입력)",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]  # 모든 API에 적용

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi