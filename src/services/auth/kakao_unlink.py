import requests

def unlink_kakao_user(access_token: str):
    url = "https://kapi.kakao.com/v1/user/unlink"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    res = requests.post(url, headers=headers)
    print("📡 언링크 응답 코드:", res.status_code)
    print("📡 응답 본문:", res.text)

    if res.status_code != 200:
        raise Exception(f"카카오 언링크 실패: {res.text}")

    return res.json()