import os
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  #env에서 불러온
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 예시: 사용자 정보
data = {"sub": "2", "role": "user"}
token = create_access_token(data)
print("✅ 발급된 토큰:\n", token)


url = 'https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'xml')
items = soup.find_all('item')

for item in items:
    title = item.title.text
    traffic = item.approx_traffic.text if item.approx_traffic else 'N/A'
    pub_date = item.pubDate.text
    print(f"{title} - {traffic} - {pub_date}")
