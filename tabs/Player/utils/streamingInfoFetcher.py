from typing import Any

from tabs.utils.RandomStringGenerator import RandomStringGenerator
import requests


def get_visitor_id() -> str:
    url = (
        "https://www.youtube.com/youtubei/v1/visitor_id"
        "?prettyPrint=false"
    )

    body = {
        "context": {
            "client": {
                "clientName": "IOS",
                "clientVersion": "21.03.2",
                "clientScreen": "WATCH",
                "platform": "MOBILE",

                "deviceMake": "Apple",
                "deviceModel": "iPhone16,2",

                "osName": "iOS",
                "osVersion": "18.7.2.22H124",

                "hl": "en-GB",
                "gl": "GB",

                "utcOffsetMinutes": 0
            },

            "request": {
                "internalExperimentFlags": [],
                "useSsl": True
            },

            "user": {
                "lockedSafetyMode": False
            }
        }
    }

    headers = {
        "User-Agent": (
            "com.google.ios.youtube/21.03.2"
            "(iPhone16,2; U; CPU iOS 18_7_2 like Mac OS X; GB)"
        ),

        "Content-Type": "application/json",

        "X-Goog-Api-Format-Version": "2",

        "X-Youtube-Client-Name": "5",

        "X-Youtube-Client-Version": "21.03.2",

        "Accept-Language": "en-GB,en;q=0.9"
    }

    params = {
        "prettyPrint": "false"
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=body
    )

    response.raise_for_status()

    data = response.json()

    return data["responseContext"]["visitorData"]




def get_ios_player_response(video_id: str, visitor_id: str) -> Any:

    cpn = RandomStringGenerator.generate_content_playback_nonce()
    t = RandomStringGenerator.generate_t_parameter()

    url = "https://youtubei.googleapis.com/youtubei/v1/player"

    headers = {
        "User-Agent": (
            "com.google.ios.youtube/21.03.2"
            "(iPhone16,2; U; CPU iOS 18_7_2 like Mac OS X; GB)"
        ),

        "Content-Type": "application/json",

        "X-Goog-Api-Format-Version": "2",

        "X-Youtube-Client-Name": "5",

        "X-Youtube-Client-Version": "21.03.2",

        "Accept-Language": "en-GB,en;q=0.9"
    }

    params = {
        "prettyPrint": "false",
        "t": t,
        "id": video_id
    }

    body = {
        "context": {
            "client": {
                "clientName": "IOS",
                "clientVersion": "21.03.2",
                "clientScreen": "WATCH",
                "platform": "MOBILE",

                "visitorData": visitor_id,

                "deviceMake": "Apple",
                "deviceModel": "iPhone16,2",

                "osName": "iOS",
                "osVersion": "18.7.2.22H124",

                "hl": "en-GB",
                "gl": "GB",

                "utcOffsetMinutes": 0
            },

            "request": {
                "internalExperimentFlags": [],
                "useSsl": True
            },

            "user": {
                "lockedSafetyMode": False
            }
        },

        "videoId": video_id,

        "cpn": cpn,

        "contentCheckOk": True,
        "racyCheckOk": True
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=body
    )

    response.raise_for_status()

    data = response.json()


    return data