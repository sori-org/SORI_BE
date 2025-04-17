import requests

def unlink_kakao_user(access_token: str):
    response = requests.post(
        "https://kapi.kakao.com/v1/user/unlink",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code != 200:
        raise Exception(f"카카오 언링크 실패: {response.text}")