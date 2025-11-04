# SORI_BE  
소상공인을 위한 SNS 홍보 콘텐츠 자동 생성 백엔드 서비스

---

## 🧩 프로젝트 개요  
**SORI_BE**는 소상공인들이 SNS(Instagram, Twitter 등)를 통해 손쉽게 홍보할 수 있도록  
자동으로 **콘텐츠 이미지, 문구, 해시태그**를 생성해주는 백엔드 API 서버입니다.  

사용자는 로그인 후 홍보 대상(가게명/메뉴명), 타겟층, 콘텐츠 형식, 외부 데이터(리뷰, 날씨 등)를 입력하면  
해당 정보를 바탕으로 홍보용 콘텐츠가 자동 생성됩니다.

---

## 🚀 주요 기능  
- **카카오 로그인 연동** 및 JWT 기반 인증  
- **가게 등록 및 관리**  
  - 가게명, 대표자 이름, 사업자 등록번호, 가게 연락처, 위치 등 입력  
  - 위치 검색을 위해 **카카오맵 API** 연동  
- **키워드 기반 가게 검색** (네이버 검색 API 활용)  
- **콘텐츠 자동 생성 기능**  
  - 사용자 입력 + 외부 데이터(API) → 문구 + 해시태그 + 이미지 URL 생성  
  - 외부 API: OpenWeatherMap, TourAPI, Google Places  
- **DB 저장 및 조회 기능**  
  - 생성된 콘텐츠를 사용자별로 관리 가능  

---

## 🛠 기술 스택  

| 구분 | 기술 |
|------|------|
| 프론트엔드 | React.js |
| 백엔드 | FastAPI |
| 데이터베이스 | PostgreSQL |
| AI / 데이터 처리 | GPT API, Pandas |
| 워크플로우 자동화 | n8n |
| 외부 API | Twitter API, Instagram Graph API, Google SERP API |
| 배포 환경 | AWS (EC2), Vercel |

---

## 📁 디렉토리 구조  
'''
/src
├─ api # FastAPI 라우터 (엔드포인트)
├─ models # SQLAlchemy 모델 정의
├─ services # 비즈니스 로직 및 외부 API 연동
├─ schemas # Pydantic 스키마
├─ utils # 공통 유틸리티 (JWT, 카카오 로그인 등)
└─ main.py # FastAPI 앱 진입점
'''
