import requests
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 주소에서 도시 조회(날씨)
def get_city_from_address(address: str) -> str:
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['results']:
        # 주소 컴포넌트에서 "locality" 필드(도시명) 찾기
        for component in data['results'][0]['address_components']:
            if "locality" in component["types"]:
                return component["long_name"]
    return None

#주소에서 좌표 조회(행사)
def get_coordinates_from_address(address: str) -> tuple:
    api_key = os.getenv("GOOGLE_MAP_API_KEY")  # 환경변수에서 Google API 키 가져오기
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"

    response = requests.get(url)
    data = response.json()

    # 응답 상태 코드가 200이고, 결과가 존재하는 경우
    if response.status_code == 200 and data['status'] == 'OK' and data['results']:
        # 결과에서 위도(lat)와 경도(lng) 추출
        location = data['results'][0]['geometry']['location']
        lat = location['lat']
        lng = location['lng']
        return lat, lng

    return None, None  # 응답에 위도와 경도가 없으면 None 반환

#주소에서 장소id 조회(리뷰)
def get_place_id_from_address(address: str) -> str:
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={address}&inputtype=textquery&fields=place_id&key={api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK' and data['candidates']:
        return data['candidates'][0]['place_id']
    return None


address = "경기도 성남시 수정구 복정로 18 1층"
latitude, longitude = get_coordinates_from_address(address)
if latitude and longitude:
    print(f"위도: {latitude}, 경도: {longitude}")
else:
    print("위도와 경도를 가져올 수 없습니다.")


# 날씨 정보 가져오기 (OpenWeatherMap API)
def get_weather_data(city: str) -> str:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        return f"현재 {city}의 날씨는 {description}이고, 기온은 {temperature}°C입니다."
    else:
        return "날씨 정보를 가져오는데 실패했습니다."

#점포 위치 기반으로 주변 2km 내 행사 조회
def get_tour_events_by_location(lat: float, lng: float):
    service_key = os.getenv("TOUR_API_KEY")
    url = f"http://apis.data.go.kr/B551011/KorService1/locationBasedList1?serviceKey={service_key}&mapX={lng}&mapY={lat}&radius=2000&MobileApp=AppTest&MobileOS=ETC&listYN=Y&arrange=A&contentTypeId=15"

    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    #print(f"Response Text: {response.text}") 전체 xml 출력

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            items = root.find(".//items")
            if items is None:
                print("행사 아이템이 없습니다.")
                return []
            events= []
            for item in items.findall('item'):
                event = {
                    "title": item.find('title').text,
                    "address": item.find('addr1').text,
                    "distance": item.find('dist').text,
                    "content_id": item.find('contentid').text
                }
                events.append(event)
            return events
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return []
    else:
        print("API 요청 실패")
        return []
# 주변 행사의 id로 행사일 조회
def get_event_dates(content_id: str) -> tuple:
    service_key = os.getenv("TOUR_API_KEY")
    url = f"http://apis.data.go.kr/B551011/KorService1/detailIntro1?serviceKey={service_key}&MobileApp=AppTest&MobileOS=ETC&pageNo=1&numOfRows=10&contentId={content_id}&contentTypeId=15"

    response = requests.get(url)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            item = root.find(".//item")
            if item is not None:
                start_date = item.find('eventstartdate').text if item.find('eventstartdate') is not None else None
                end_date = item.find('eventenddate').text if item.find('eventenddate') is not None else None
                return start_date, end_date
        except ET.ParseError as e:
            print(f"Error parsing XML (event dates): {e}")
    return None, None

#행사의 개요 조회
def get_event_details(content_id: str) -> list:
    service_key = os.getenv("TOUR_API_KEY")
    url = f"http://apis.data.go.kr/B551011/KorService1/detailInfo1?serviceKey={service_key}&MobileApp=AppTest&MobileOS=ETC&pageNo=1&numOfRows=10&contentId={content_id}&contentTypeId=15"

    response = requests.get(url)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            items = root.find(".//items")
            details = []
            if items is not None:
                for item in items.findall('item'):
                    infoname = item.find('infoname').text if item.find('infoname') is not None else ""
                    infotext = item.find('infotext').text if item.find('infotext') is not None else ""
                    details.append({"infoname": infoname, "infotext": infotext})
                return details
            else:
                print("상세 정보 없음 (items=None)")
        except ET.ParseError as e:
            print(f"Error parsing XML (event details): {e}")
    return []

# 구글 리뷰 가져오기 (Google Maps API)
def get_google_reviews(store_name, store_address):
    api_key = os.getenv("GOOGLE_MAP_API_KEY")

    # Step 1: place_id 가져오기
    find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    find_place_params = {
        "input": f"{store_name} {store_address}",
        "inputtype": "textquery",
        "fields": "place_id",
        "key": api_key
    }
    find_response = requests.get(find_place_url, params=find_place_params)
    find_data = find_response.json()

    if find_response.status_code == 200 and find_data['status'] == 'OK' and find_data['candidates']:
        place_id = find_data['candidates'][0]['place_id']

        # Step 2: 리뷰 가져오기
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "reviews",
            "language": "ko",
            "key": api_key
        }
        details_response = requests.get(details_url, params=details_params)
        details_data = details_response.json()

        if details_response.status_code == 200 and details_data['status'] == 'OK':
            reviews = details_data['result'].get('reviews', [])
            filtered_reviews = []
            for r in reviews:
                rating = r.get('rating')
                language = r.get('language')
                if rating in [4, 5] and language == 'ko':  # 4점, 5점만 가져오기
                    filtered_reviews.append({
                        'author': r.get('author_name', '익명'),
                        'rating': rating,
                        'text': r.get('text', '')
                    })
            return filtered_reviews
    return []

store_name = "겐코쇼쿠도 복정점"
store_address = "경기도 성남시 수정구 복정로 18"

reviews = get_google_reviews(store_name, store_address)

if reviews:
    print("⭐ 4점, 5점 리뷰:")
    for r in reviews:
        author = r['author']
        rating = r['rating']
        text = r['text']
        print(f"- {author} ({rating}점): {text}")
else:
    print("리뷰가 없거나 가져오기 실패했습니다.")

# 유행 정보 가져오기 (Google Trends / Naver Search API)
def get_trending_data():
    import openai

    SERPAPI_KEY = os.getenv("SERP_API_KEY")
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_top_queries():
        endpoint = "https://serpapi.com/search"
        params = {
            "engine": "google_trends_trending_now",
            "geo": "KR",
            "hours": 48,
            "hl": "ko",
            "api_key": SERPAPI_KEY,
            "output": "json"
        }
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            print("SerpApi error")
            return []
        data = response.json()
        trends = data.get('trending_searches', [])
        sorted_trends = sorted(trends, key=lambda x: x.get('search_volume', 0), reverse=True)
        return [t.get('query') for t in sorted_trends[:10]]

    def search_naver_news(query):
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        params = {"query": query, "display": 1, "start": 1, "sort": "sim"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return ""
        items = response.json().get('items', [])
        return " ".join([item.get('description', '') for item in items])

    def check_with_openai(text):
        prompt = f"다음 내용에 정치, 논란, 성적 내용, 특정 유명인의 죽음, 자살, 사고사, 타살, 범죄 관련 내용이 포함되어 있습니까? (예/아니오만 답하세요)\n\n{text}"
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10
            )
            answer = response.choices[0].message.content.strip()
            return '예' in answer
        except Exception as e:
            print("OpenAI error:", e)
            return True  # 에러 발생 시 차단 처리

    top_queries = get_top_queries()
    safe_queries = []

    for query in top_queries:
        news_summary = search_naver_news(query)
        if not news_summary:
            continue
        if not check_with_openai(news_summary):
            safe_queries.append((query, news_summary))

    return safe_queries

# 외부 데이터에 맞는 함수 호출
def get_external_data(external_data_name: str, address: str, name: str) -> str:
    if external_data_name == "weather":
        city = get_city_from_address(address)
        if city:
            return get_weather_data(city)
        else:
            return "도시명을 찾을 수 없습니다."

    elif external_data_name == "event":
        lat, lng = get_coordinates_from_address(address)
        return get_tour_events_by_location(lat, lng)
    elif external_data_name == "review":
        return get_google_reviews(name, address)
    elif external_data_name == "trend":
        return get_trending_data()
    else:
        return "외부 데이터 정보를 선택하지 않았습니다."
