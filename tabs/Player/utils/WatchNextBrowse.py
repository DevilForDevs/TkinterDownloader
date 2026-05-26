import json
import requests


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/143.0.0.0"


def get_suggestions(
    video_id: str,
    continuation: str | None,
    visitor_data: str,
    client_version: str,
):
    body = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "IN",
                "clientName": "WEB",
                "clientVersion": client_version,
                "platform": "DESKTOP",
                "osName": "Windows",
                "osVersion": "10.0",
                "timeZone": "Asia/Calcutta",
                "userAgent": USER_AGENT,
                "visitorData": visitor_data,
            }
        },
        "videoId": video_id,
    }

    if continuation:
        body["continuation"] = continuation

    headers = {
        "content-type": "application/json",
        "origin": "https://www.youtube.com",
        "user-agent": USER_AGENT,
        "referer": f"https://www.youtube.com/watch?v={video_id}",
        "x-youtube-client-name": "1",
        "x-youtube-client-version": client_version,
        "x-youtube-bootstrap-logged-in": "false",
        "x-goog-visitor-id": visitor_data,
    }

    response = requests.post(
        "https://www.youtube.com/youtubei/v1/next?prettyPrint=false",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        timeout=30,
    )

    if not response.ok:
        raise Exception(f"HTTP {response.status_code}")

    data = response.json()

    # same silent failure check
    if "contents" not in data and continuation is None:
        raise Exception("Invalid response (possible outdated client)")

    return data