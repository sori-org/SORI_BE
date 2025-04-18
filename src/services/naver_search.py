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
    items = response.json().get("items", [])

    places = []
    for item in items:
        places.append({
            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
            "category": item.get("category", ""),
            "address": item.get("roadAddress", ""),
        })

    return places
