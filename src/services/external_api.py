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
            events = []
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
            return None
    else:
        print("API 요청 실패")
        return None
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

#행사 출력 테스트
events = get_tour_events_by_location(latitude, longitude)
if events:
    for event in events:
        content_id = event["content_id"]
        start_date_str, end_date_str = get_event_dates(content_id)
        if start_date_str and end_date_str and start_date_str.strip() and end_date_str.strip():
            try:
                start_date = datetime.strptime(start_date_str, "%Y%m%d")
                end_date = datetime.strptime(end_date_str, "%Y%m%d")
                today = datetime.today()

                if start_date <= today <= end_date:
                    print(f"✅ 현재 진행 중인 행사: {event['title']} ({start_date_str} ~ {end_date_str})")
                    details = get_event_details(content_id)
                    for detail in details:
                        print(f" - {detail['infoname']}: {detail['infotext']}")
                else:
                    print(f"❌ 행사 기간 아님: {event['title']} ({start_date_str} ~ {end_date_str})")
            except ValueError:
                print(f"⚠️ 날짜 형식 오류 (content_id={content_id})")
        else:
            print(f"⚠️ 행사 날짜 정보 없음 (content_id={content_id})")
else:
    print("행사 정보를 가져오지 못했습니다.")


# 구글 리뷰 가져오기 (Google Maps API)
def get_place_id_by_name(name, address):
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{name} {address}",
        "inputtype": "textquery",
        "fields": "place_id",
        "key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK' and data['candidates']:
        return data['candidates'][0]['place_id']
    return None

def get_reviews(place_id):
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "reviews",
        "key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        return data['result'].get('reviews', [])
    return []

store_name = "겐코쇼쿠도 복정점"
store_address = "경기도 성남시 수정구 복정로 18"

place_id = get_place_id_by_name(store_name, store_address)

if place_id:
    reviews = get_reviews(place_id)
    if reviews:
        print("⭐ 리뷰 정보:")
        for r in reviews:
            author = r.get('author_name', '익명')
            rating = r.get('rating', 'N/A')
            text = r.get('text', '')
            print(f"- {author} ({rating}점): {text}")
    else:
        print("리뷰가 없습니다.")
else:
    print("장소를 찾을 수 없습니다.")

# 유행 정보 가져오기 (Google Trends / Naver Search API)
def get_trending_data() -> str:
    # Google Trends 또는 Naver Search API를 통해 유행 데이터를 가져오는 코드 작성
    pass

# 외부 데이터에 맞는 함수 호출
def get_external_data(external_data_name: str, address: str) -> str:
    if external_data_name == "weather":
        return get_weather_data(address)
    elif external_data_name == "event":
        lat, lng = get_coordinates_from_address(address)
        return get_tour_events_by_location(lat, lng)
    elif external_data_name == "review":
        return get_google_reviews(address)
    elif external_data_name == "trend":
        return get_trending_data()
    else:
        return "외부 데이터가 선택되지 않았습니다."