import requests

def get_fb_id(access_token):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get('https://graph.facebook.com/me?access_token=' +
                       access_token)
    return req.json()["id"]