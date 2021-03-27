# coding=utf-8
import json
import requests
import re

get_headers = {
    'app_version': '6.9.4',
    'platform': 'ios',
    "User-agent": "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)",
    "Accept": "application/json",
    'X-Auth-Token': '99c7cb23-663d-4fcc-bc76-e0d4fa93fcb5'
}
headers = get_headers.copy()
headers['content-type'] = "application/json"
host = 'https://api.gotinder.com'


def get_fb_id(access_token):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get('https://graph.facebook.com/me?access_token=' +
                       access_token)
    return req.json()["id"]


def authorize(form_input):
    # get fb token and ID from user
	revised_form_input = '<script type="text/javascript" nonce="9pF6859V">window.location.href="fb464891386855067:\/\/authorize\/#granted_scopes=user_birthday\u00252Cuser_likes\u00252Cuser_photos\u00252Cemail\u00252Cpublic_profile&denied_scopes=&signed_request=yYeXS0tLtJ1fh7X4a0UCLbftKJM5ks20gIRsiSUtjF0.eyJ1c2VyX2lkIjoiMTAwNDMzNDQzMjkyODQ5MCIsImNvZGUiOiJBUUE5S0lJaVlVdDFoXzRodkg3emxldTNsZzBzTWNlcUVTT2JVeDQwd040MUE1dXNJYjZrc19abmhMTGZjUld2ZHFOaXNSMDIyZWRXSi01TG5zMnNQS1VZRzJVaUF5bEVtbHhNWUVZOXkzbWNLdjNxd1NTbFFQc040TnRxY3VPbkVlTzVQUmptOU1SbEtQLVlsemFQQ0ZHM0FiaUhmeTFYVnFweUd1Rl85dUhoT0haaEwwdnJ4TVRsRVZFUC1RaVh5ZlVPeHFzeFBRZDJ4a3UtbmxVTlVmZ3RQc0NkTkQxOHFqRVJPenJJUkw5ZG9nUkFoZHlyQTNKMkdrRHB0cmlUTU9uSnhzZTJBVDZPWFpvMXAzd2dTTVBiQXVpZ1RZQWg3cW45cHpWWWw5bVk5NzZzejdscHVVX3NxbEdaU01tQW1QQ1l0aXJtV0JjMHRteWw4TElmXzdKaGRqYXZMYzFWd0phV3JCVHhEd3RLNFptTVgzTXg2WWRUcmpRelhMT1BEWUVBcXpOUklHVDFfbUw4SndIZGtLanUiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTYxNjYwNzI4NX0&access_token=EAAGm0PX4ZCpsBAD4j1WHa7hJwvLEXHWEMVZB9sjPBAB1AqHv58CD53Nq7bFxemmlS89eedKkDSWoAJclQA0afqlnf67M2ZAZBnnFloPbvi37hSV5zk2Wgod1PonRDmfSJFWeqjIOLuwvYVlPJae2gTbFQvBZBQAodY0GkUd0MGKctrH9gOCYj8v8B6sLZB2WmGBczX9z33bwVyy6Gm5dlmPeUvD2BEyPx1kvZBDO0989QZDZD&data_access_expiration_time=1624383285&expires_in=5116586&state=\u00257B\u002522challenge\u002522\u00253A\u002522IUUkEUqIGud332lfu\u0025252BMJhxL4Wlc\u0025253D\u002522\u00252C\u0025220_auth_logger_id\u002522\u00253A\u00252230F06532-A1B9-4B10-BB28-B29956C71AB1\u002522\u00252C\u002522com.facebook.sdk_client_state\u002522\u00253Atrue\u00252C\u0025223_method\u002522\u00253A\u002522sfvc_auth\u002522\u00257D";</script>' if form_input == "" else form_input
	
	fb_access_token = re.search(r"access_token=([\w\d]+)", revised_form_input).groups()[0]
	fb_user_id = get_fb_id(fb_access_token)
    # get tinder token and update api headers
    # tinder_api.get_auth_token(fb_access_token, fb_user_id)
    # To check you are authorized
	auth_status, auth_color = ("was successfully authorized!",
                               "green") if authverif(
                                   fb_access_token, fb_user_id) == True else (
                                       "failed to authorize :(", "tomato")

	return auth_status, auth_color


def get_auth_token(fb_auth_token, fb_user_id):
    if "error" in fb_auth_token:
        return {"error": "could not retrieve fb_auth_token"}
    if "error" in fb_user_id:
        return {"error": "could not retrieve fb_user_id"}
    url = host + '/v2/auth/login/facebook'
    req = requests.post(url,
                        headers=headers,
                        data=json.dumps({
                            'token': fb_auth_token,
                            'facebook_id': fb_user_id
                        }))
    try:
        tinder_auth_token = req.json()["data"]["api_token"]
        headers.update({"X-Auth-Token": tinder_auth_token})
        get_headers.update({"X-Auth-Token": tinder_auth_token})
        print("You have been successfully authorized!")
        print(headers)
        return tinder_auth_token
    except Exception as e:
        print(e)
        return {
            "error":
            "Something went wrong. Sorry, but we could not authorize you."
        }


def authverif(fb_access_token, fb_user_id):
    res = get_auth_token(fb_access_token, fb_user_id)
    if "error" in res:
        return False
    return True


def get_recommendations():
    '''
    Returns a list of users that you can swipe on
    '''
    try:
        r = requests.get('https://api.gotinder.com/user/recs', headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong with getting recomendations:", e)


def get_read_receipts(match_id):
    '''
    Returns a 404, with v2 too
    '''
    try:
        r = requests.get('https://api.gotinder.com/readreceipt/' + match_id,
                         headers=headers)
        print(r.text)
        print(r.status_code)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong with getting recomendations:", e)


def get_updates(last_activity_date=""):
    '''
    Returns all updates since the given activity date.
    The last activity date is defaulted at the beginning of time.
    Format for last_activity_date: "2017-07-09T10:28:13.392Z"
    '''
    try:
        url = host + '/updates'
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(
                              {"last_activity_date": last_activity_date}))
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong with getting updates:", e)


def get_self():
    '''
    Returns your own profile data
    '''
    try:
        url = host + '/profile'
        r = requests.get(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your data:", e)


def change_preferences(**kwargs):
    '''
    ex: change_preferences(age_filter_min=30, gender=0)
    kwargs: a dictionary - whose keys become separate keyword arguments and the values become values of these arguments
    age_filter_min: 18..46
    age_filter_max: 22..55
    age_filter_min <= age_filter_max - 4
    gender: 0 == seeking males, 1 == seeking females
    distance_filter: 1..100
    discoverable: true | false
    {"photo_optimizer_enabled":false}
    '''
    try:
        url = host + '/profile'
        r = requests.post(url, headers=headers, data=json.dumps(kwargs))
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not change your preferences:", e)


def get_meta():
    '''
    Returns meta data on yourself. Including the following keys:
    ['globals', 'client_resources', 'versions', 'purchases',
    'status', 'groups', 'products', 'rating', 'tutorials',
    'travel', 'notifications', 'user']
    '''
    try:
        url = host + '/meta'
        r = requests.get(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your metadata:", e)


def get_meta_v2():
    '''
    Returns meta data on yourself from V2 API. Including the following keys:
    ['account', 'client_resources', 'plus_screen', 'boost',
    'fast_match', 'top_picks', 'paywall', 'merchandising', 'places',
    'typing_indicator', 'profile', 'recs']
    '''
    try:
        url = host + '/v2/meta'
        r = requests.get(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your metadata:", e)


def update_location(lat, lon):
    '''
    Updates your location to the given float inputs
    Note: Requires a passport / Tinder Plus
    '''
    try:
        url = host + '/passport/user/travel'
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps({
                              "lat": lat,
                              "lon": lon
                          }))
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not update your location:", e)


def reset_real_location():
    try:
        url = host + '/passport/user/reset'
        r = requests.post(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not update your location:", e)


def get_recs_v2():
    '''
    This works more consistently then the normal get_recommendations becuase it seeems to check new location
    '''
    try:
        url = host + '/v2/recs/core?locale=en-US'
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        print('excepted')


def set_webprofileusername(username):
    '''
    Sets the username for the webprofile: https://www.gotinder.com/@YOURUSERNAME
    '''
    try:
        url = host + '/profile/username'
        r = requests.put(url,
                         headers=headers,
                         data=json.dumps({"username": username}))
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not set webprofile username:", e)


def reset_webprofileusername(username):
    '''
    Resets the username for the webprofile
    '''
    try:
        url = host + '/profile/username'
        r = requests.delete(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not delete webprofile username:", e)


def get_person(id):
    '''
    Gets a user's profile via their id
    returns 401, even with ?locale=en&count=60
    '''
    try:
        url = host + '/user/{}'.format(id)
        #         print(headers)
        r = requests.get(url, headers=headers)
        #         print(r.status_code)
        #         print(r.text)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get that person:", e)


def send_msg(match_id, msg):
    try:
        url = host + '/user/matches/%s' % match_id
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps({"message": msg}))
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not send your message:", e)


def unmatch(match_id):
    try:
        url = host + '/user/matches/%s' % match_id
        r = requests.delete(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not unmatch person:", e)


def superlike(person_id):
    try:
        url = host + '/like/%s/super' % person_id
        r = requests.post(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not superlike:", e)


def like(person_id):
    try:
        url = host + '/like/%s' % person_id
        r = requests.get(url, headers=get_headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not like:", e)


def dislike(person_id):
    try:
        url = host + '/pass/%s' % person_id
        r = requests.get(url, headers=get_headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not dislike:", e)


def report(person_id, cause, explanation=''):
    '''
    There are three options for cause:
        0 : Other and requires an explanation
        1 : Feels like spam and no explanation
        4 : Inappropriate Photos and no explanation
    '''
    try:
        url = host + '/report/%s' % person_id
        r = requests.post(url,
                          headers=headers,
                          data={
                              "cause": cause,
                              "text": explanation
                          })
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not report:", e)


def match_info(match_id):
    try:
        url = host + '/v2/matches/%s' % match_id
        r = requests.get(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your match info:", e)


def match_info_v2(match_id, count=60, message=0, page_token=None):
    try:
        url = host + '/v2/matches?locale=en&count=' + str(
            count) + '&message=' + str(message) + '&is_tinder_u=false/' + str(
                match_id)
        if page_token:
            url = url + '&page_token=' + page_token
        r = requests.get(url, headers=headers)
        json = r.json()
        if 'data' in json and 'next_page_token' in json['data']:
            next_page_data = all_matches(count, message,
                                         json['data']['next_page_token'])
            json['data']['matches'] = json['data']['matches'] + next_page_data[
                'data']['matches']
        elif message <= 0:
            next_page_data = all_matches(count, 1, None)
            json['data']['matches'] = json['data']['matches'] + next_page_data[
                'data']['matches']
        return json
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your match info:", e)


#         curl -v GET 'https://api.gotinder.com/v2/matches?count=60&is_tinder_u=false&locale=en&message=1' -H 'x-supported-image-formats': 'webp,jpeg'\
# -H 'persistent-device-id': ''\
# -H 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'\
# -H 'user-session-id': ''\
# -H 'Accept': 'application/json'\
# -H 'app-session-time-elapsed': '77290'\
# -H 'X-Auth-Token': 'ea75d1aa-bb4d-498d-8248-728f29e6bc01'\
# -H 'user-session-time-elapsed': '437'\
# -H 'Referer': 'https://tinder.com/'\
# -H 'platform': 'web'\
# -H 'app-session-id': ''\
# -H 'app-version': '1020500'

# def all_matches():
#     try:
#         url = host + '/v2/matches?count=60&is_tinder_u=false&locale=en&message=1' #/v2/matches'
#         r = requests.get(url, headers=headers)
#         return r.json()
#     except requests.exceptions.RequestException as e:
#         print("Something went wrong. Could not get your match info:", e)


def all_matches(count=60, message=0, page_token=None):
    try:
        url = host + '/v2/matches?locale=en&count=' + str(
            count) + '&message=' + str(message) + '&is_tinder_u=false'
        if page_token:
            url = url + '&page_token=' + page_token
        r = requests.get(url, headers=headers)
        json = r.json()
        if 'data' in json and 'next_page_token' in json['data']:
            next_page_data = all_matches(count, message,
                                         json['data']['next_page_token'])
            json['data']['matches'] = json['data']['matches'] + next_page_data[
                'data']['matches']
        elif message <= 0:
            next_page_data = all_matches(count, 1, None)
            json['data']['matches'] = json['data']['matches'] + next_page_data[
                'data']['matches']
        return json
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your match info:", e)


def fast_match_info():
    try:
        url = host + '/v2/fast-match/preview'
        r = requests.get(url, headers=headers)
        count = r.headers['fast-match-count']
        # image is in the response but its in hex..
        return count
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your fast-match count:", e)


def trending_gifs(limit=3):
    try:
        url = host + '/giphy/trending?limit=%s' % limit
        r = requests.get(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get the trending gifs:", e)


def gif_query(query, limit=3):
    try:
        url = host + '/giphy/search?limit=%s&query=%s' % (limit, query)
        r = requests.get(url, headers=headers)
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Something went wrong. Could not get your gifs:", e)


# def see_friends():
#     try:
#         url = host + '/group/friends'
#         r = requests.get(url, headers=headers)
#         return r.json()['results']
#     except requests.exceptions.RequestException as e:
#         print("Something went wrong. Could not get your Facebook friends:", e)
