import requests


def get_kakao_user_info(access_token: str):
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    response = requests.get(url, headers=headers)
    print("📡 카카오 사용자 정보 요청 응답 코드:", response.status_code)
    print("📡 응답 본문:", response.text)

    if response.status_code != 200:
        raise Exception("카카오 사용자 정보 요청 실패")

    return response.json()


def extract_user_info(user_info: dict):
    kakao_id = user_info["id"]
    profile = user_info.get("kakao_account", {}).get("profile", {})

    nickname = profile.get("nickname")

    return {
        "kakao_id": kakao_id,
        "nickname": nickname,
    }