import requests
import os

def search_places(query: str) -> list[dict]:
    client_id = os.getenv("NAVER_CLIENT_ID", "YOUR_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET", "YOUR_CLIENT_SECRET")

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": query,
        "display": 5
    }

    response = requests.get(url, headers=headers, params=params)

    # 디버깅 코드
    print("🔍 검색 쿼리:", query)
    print("🔗 요청 URL:", response.url)
    print("📡 응답 상태 코드:", response.status_code)
    print("📄 응답 내용:", response.text)

    items = response.json().get("items", [])

    places = []
    for item in items:
        places.append({
            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
            "category": item.get("category", ""),
            "address": item.get("roadAddress", ""),
        })

    return places
