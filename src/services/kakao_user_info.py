import requests


def get_kakao_user_info(access_token: str):
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("카카오 사용자 정보 요청 실패")

    return response.json()


def extract_user_info(user_info: dict):
    kakao_id = user_info["id"]
    profile = user_info.get("kakao_account", {}).get("profile", {})

    nickname = profile.get("nickname")
    profile_image = profile.get("profile_image_url")
    thumbnail_image = profile.get("thumbnail_image_url")

    return {
        "kakao_id": kakao_id,
        "nickname": nickname,
        "profile_image": profile_image,
        "thumbnail_image": thumbnail_image,
    }