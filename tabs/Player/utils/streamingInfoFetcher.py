import requests

from tabs.utils.RandomStringGenerator import RandomStringGenerator


def get_visitor_id():
    url = 'https://youtubei.googleapis.com/youtubei/v1/visitor_id?prettyPrint=false'
    json_body = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "21.03.36",
                "clientScreen": "WATCH",
                "platform": "MOBILE",
                "osName": "Android",
                "osVersion": "16",
                "androidSdkVersion": 36,
                "hl": "en-GB",
                "gl": "GB",
                "utcOffsetMinutes": 0,
            },
            "request": {
                "internalExperimentFlags": [],
                "useSsl": True,
            },
            "user": {
                "lockedSafetyMode": False,
            },
        }
    }
    headers = {
        "User-Agent": "com.google.android.youtube/21.03.36 (Linux; U; Android 15; GB) gzip",
        "X-Goog-Api-Format-Version": "2",
        "Content-Type": "application/json",
        "Accept-Language": "en-GB, en;q=0.9",
    }
    response = requests.post(url, headers=headers, json=json_body)
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code}\n{response.text}")
    data = response.json()
    return data["responseContext"]["visitorData"]



def android_player_response(
    video_id: str,
) -> dict:
    cpn = RandomStringGenerator.generate_content_playback_nonce()
    t = RandomStringGenerator.generate_t_parameter()
    visitor_data=get_visitor_id()

    url = (
        "https://youtubei.googleapis.com/youtubei/v1/reel/reel_item_watch"
        f"?prettyPrint=false&t={t}&id={video_id}&$fields=playerResponse"
    )

    json_body = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "21.03.36",
                "clientScreen": "WATCH",
                "platform": "MOBILE",
                "osName": "Android",
                "osVersion": "16",
                "androidSdkVersion": 36,
                "hl": "en-GB",
                "gl": "GB",
                "utcOffsetMinutes": 0,
                "visitorData": visitor_data,
            },
            "request": {
                "internalExperimentFlags": [],
                "useSsl": True,
            },
            "user": {
                "lockedSafetyMode": False,
            },
        },
        "playerRequest": {
            "videoId": video_id,
            "cpn": cpn,
            "contentCheckOk": True,
            "racyCheckOk": True,
        },
        "disablePlayerResponse": False,
    }

    headers = {
        "User-Agent": (
            "com.google.android.youtube/21.03.36 "
            "(Linux; U; Android 15; GB) gzip"
        ),
        "X-Goog-Api-Format-Version": "2",
        "Content-Type": "application/json",
        "Accept-Language": "en-GB, en;q=0.9",
    }

    response = requests.post(
        url,
        headers=headers,
        json=json_body,
    )

    if response.status_code != 200:
        raise Exception(
            f"Request failed: {response.status_code}\n{response.text}"
        )

    return response.json()