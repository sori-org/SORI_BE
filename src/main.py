from fastapi import FastAPI, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .db.database import Base, engine
from .routers import kakao_login, users, jwt_token, refresh, content
from fastapi.middleware.cors import CORSMiddleware
from src.api import store, search
from fastapi.openapi.utils import get_openapi

import logging, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_IMAGES_PATH = os.path.join(BASE_DIR, "generated_images")
UPLOADED_IMAGES_PATH = os.path.join(BASE_DIR, "uploaded_images")
print("======== 경로 체크 (실제 경로) ========")
print("os.getcwd():", os.getcwd())
print("os.path.abspath('generated_images'):", os.path.abspath("generated_images"))
print("GENERATED_IMAGES_PATH:", GENERATED_IMAGES_PATH)
print("UPLOADED_IMAGES_PATH:", UPLOADED_IMAGES_PATH)
print("실제 generated_images 파일 목록:", os.listdir(GENERATED_IMAGES_PATH))
print("실제 uploaded_images 파일 목록:", os.listdir(UPLOADED_IMAGES_PATH))
print("=======================================")

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


@app.middleware("http")
async def add_cors_for_generated_images(request: Request, call_next):
    response: Response = await call_next(request)
    if request.method == "GET" and request.url.path.startswith("/generated_images/"):
        # 요청이 /generated_images/로 시작하면 CORS 헤더 추가
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Methods"] = "GET"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sori-fe.vercel.app",
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
app.include_router(content.router)


app.mount("/generated_images", StaticFiles(directory=GENERATED_IMAGES_PATH), name="generated_images")
app.mount("/uploaded_images", StaticFiles(directory=UPLOADED_IMAGES_PATH), name="uploaded_images")

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