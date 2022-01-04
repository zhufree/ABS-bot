import httpx
import uuid, json, re
from config import jike_access_token, jike_refresh_token

DEVICE_ID = "4653BFCE-9D54-471C-809C-422AC240DA7B"
IDFV = "5C5FC6BB-F6E6-4689-BB5A-E88763186C55"
JIKE_HOST = "https://api.ruguoapp.com/"
ACCESS_TOKEN = "x-jike-access-token"
REFRESH_TOKEN = "x-jike-refresh-token"
JSON_UTF_8 = "Content-Type: application/json; charset=utf-8"
REFRESH_TOKEN_URL = "app_auth_tokens.refresh"
post_url = 'https://api.ruguoapp.com/1.0/originalPosts/create'
refresh_token_url = 'https://api.ruguoapp.com/app_auth_tokens.refresh'
cur_access_token = jike_access_token
cur_refresh_token = jike_refresh_token

headers = {
    "Host": "api.ruguoapp.com",
    "king-card-status": "unavailable",
    "User-Agent": "jike/7.18.1 (com.ruguoapp.jike; build:1901; iOS 14.7.0) Alamofire/5.4.3",
    "x-jike-device-properties": "{\"idfv\":\"" + IDFV + "\"}",
    "x-jike-device-id": DEVICE_ID,
    "x-jike-access-token": cur_access_token,
}
# print(headers)
retry_count = 0

def update_token(a_token, r_token):
    with open('config.py', 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('jike_access_token'):
                lines[i] = "jike_access_token = '{}'\n".format(a_token)
            if line.startswith('jike_refresh_token'):
                lines[i] = "jike_refresh_token = '{}'\n".format(r_token)
        f.seek(0)
        f.truncate()
        f.writelines(lines)


def refreshToken():
    global cur_refresh_token
    global cur_access_token
    headers['x-jike-refresh-token'] = cur_refresh_token
    res = httpx.post(url=refresh_token_url, data="https://api.ruguoapp.com/app_auth_tokens.refresh", headers=headers)
    if res.status_code == 200:
        result = json.loads(res.text)
        if result['success'] == True:
            cur_access_token = result['x-jike-access-token']
            cur_refresh_token = result['x-jike-refresh-token']
            update_token(cur_access_token, cur_refresh_token)
            return True
        else:
            return False
    else:
        return False

def jike_post(msg):
    global retry_count
    post_data = {
        'content': msg
        # 'pictureKeys': 'xx.jpg'
    }
    res = httpx.post(url=post_url, json=post_data, headers=headers)
    if res.status_code == 200:
        retry_count = 0
        return {
            'success': True
        }
    elif res.status_code == 401:
        if refreshToken() and retry_count == 0:
            retry_count += 1
            jike_post(msg)
        else:
            return {
                'success': False,
                'error': 401
            }
    else:
        return {
            'success': False,
            'error': res.status_code
        } 

