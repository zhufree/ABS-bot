import httpx

def save_to_flomo(msg):
    post_data = {
        'content': msg
    }
    res = httpx.post(url=flomo_api_url, json=post_data)
    return res.status_code