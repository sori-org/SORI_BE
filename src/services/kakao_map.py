import requests
import os
from dotenv import load_dotenv

load_dotenv()

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")

def search_place_by_keyword(keyword: str):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": keyword}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    if data["documents"]:
        place = data["documents"][0]
        return {
            "place_name": place["place_name"],
            "address": place["road_address_name"] or place["address_name"],
            "latitude": float(place["y"]),
            "longitude": float(place["x"]),
        }
    else:
        return None
