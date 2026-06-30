import requests
import json

def user_token_to_cookie(user_token):
    url = 'https://api.facebook.com/method/auth.getSessionforApp'
    payload = {
        'access_token': user_token,
        'format': 'json',
        'new_app_id': '350685531728',
        'generate_session_cookies': '1'
    }
    resp = requests.post(url, data=payload, timeout=30)
    return resp.json()

def main():
    token = input("Nhập user access token: ").strip()
    data = user_token_to_cookie(token)
    if 'error' in data:
        print("Lỗi:", json.dumps(data, indent=2))
        return
    cookies = data.get('session_cookies', [])
    if cookies:
        cookie_str = '; '.join(f"{c['name']}={c['value']}" for c in cookies)
        print("[<>] >> Cookie Từ Token:", cookie_str)
    else:
        print("Không có cookie trong response")
#     print("\nResponse:", json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
