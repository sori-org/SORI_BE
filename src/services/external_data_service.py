import os
import requests
from dotenv import load_dotenv

load_dotenv()


# 날씨 정보 (OpenWeatherMap)
def get_weather_data(city: str = "Seoul") -> str:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=kr&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{city}의 현재 날씨는 {description}이며 기온은 {temp}°C입니다."
    return "날씨 정보를 불러오지 못했습니다."


# 행사 정보 (TourAPI)
def get_event_data(area_code: str = "1") -> str:
    api_key = os.getenv("TOUR_API_KEY")
    url = (
        "http://apis.data.go.kr/B551011/KorService1/searchFestival1"
        f"?serviceKey={api_key}"
        "&MobileOS=ETC&MobileApp=AppTest&_type=json"
        f"&areaCode={area_code}&numOfRows=1"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if items:
            event = items[0]
            title = event.get("title", "행사명 없음")
            return f"현재 지역에서 열리는 주요 행사: {title}"
    return "행사 정보를 불러오지 못했습니다."


# 리뷰 정보 (Google Places API)
def get_review_data(place_name: str = "스타벅스") -> str:
    api_key = os.getenv("GOOGLE_MAP_API_KEY")

    # Step 1: place_id 검색
    search_url = (
        f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        f"?input={place_name}&inputtype=textquery&fields=place_id&key={api_key}"
    )
    search_res = requests.get(search_url).json()
    candidates = search_res.get("candidates")
    if not candidates:
        return "리뷰 정보를 찾을 수 없습니다."

    place_id = candidates[0]["place_id"]

    # Step 2: 리뷰 상세 조회
    detail_url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=name,rating,user_ratings_total,reviews&language=ko&key={api_key}"
    )
    detail_res = requests.get(detail_url).json()
    result = detail_res.get("result", {})

    name = result.get("name", place_name)
    rating = result.get("rating", "N/A")
    total = result.get("user_ratings_total", "N/A")

    return f"{name}에 대한 평점은 {rating}점이며 총 {total}개의 리뷰가 있습니다."
