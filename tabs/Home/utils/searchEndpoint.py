import json

import requests


def send_youtube_search_request(query: str, continuation: str, params: str):
    json_body = {}

    if continuation != "":
        json_body["continuation"] = continuation
    else:
        json_body["query"] = query
        json_body["params"] = params

    json_body["context"] = {
        "request": {
            "internalExperimentFlags": [],
            "useSsl": True
        },
        "client": {
            "utcOffsetMinutes": 0,
            "hl": "en-GB",
            "gl": "IN",
            "clientName": "WEB",
            "originalUrl": "https://www.youtube.com",
            "clientVersion": "2.20250613.00.00",
            "platform": "DESKTOP"
        },
        "user": {
            "lockedSafetyMode": False
        }
    }

    headers = {
        "Origin": "https://www.youtube.com",
        "Referer": "https://www.youtube.com",
        "X-YouTube-Client-Version": "2.20250613.00.00",
        "X-YouTube-Client-Name": "1",
        "Content-Type": "application/json",
        "Accept-Language": "en-GB, en;q=0.9"
    }

    response = requests.post(
        "https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
        headers=headers,
        data=json.dumps(json_body),
        timeout=20
    )

    response.raise_for_status()  # raise exception if request failed
    response_json = response.json()

    total_videos = []
    total_result = {}

    estimated_result = response_json.get("estimatedResults", "")
    total_result["estimatedResult"] = estimated_result

    # First block: "contents"
    if "contents" in response_json:
        contents_array = deep_get(
            response_json,
            "contents",
            "twoColumnSearchResultsRenderer",
            "primaryContents",
            "sectionListRenderer",
            "contents", 0,
            "itemSectionRenderer",
            "contents"
        )

        if isinstance(contents_array, list):
            for item in contents_array:
                if "videoRenderer" in item:
                    total_videos.append(create_video_tree(item["videoRenderer"]))
                if "reelShelfRenderer" in item:
                    shorts = item["reelShelfRenderer"]["items"]
                    for short_item in shorts:
                        total_videos.append(extract_shorts_info(short_item))

            continuation_token = deep_get(
                response_json,
                "contents",
                "twoColumnSearchResultsRenderer",
                "primaryContents",
                "sectionListRenderer",
                "contents", 1,
                "continuationItemRenderer",
                "continuationEndpoint",
                "continuationCommand",
                "token"
            )

            total_result["continuation"] = continuation_token
            total_result["videos"] = total_videos

    # Second block: "onResponseReceivedCommands"
    if "onResponseReceivedCommands" in response_json:
        contents_array = deep_get(
            response_json,
            "onResponseReceivedCommands", 0,
            "appendContinuationItemsAction",
            "continuationItems", 0,
            "itemSectionRenderer",
            "contents"
        )

        if isinstance(contents_array, list):
            for item in contents_array:
                if "videoRenderer" in item:
                    vt = create_video_tree(item["videoRenderer"])
                    if vt not in total_videos:
                        total_videos.append(vt)
                if "reelShelfRenderer" in item:
                    shorts = item["reelShelfRenderer"]["items"]
                    for short_item in shorts:
                        mk = extract_shorts_info(short_item)
                        if mk not in total_videos:
                            total_videos.append(mk)

        continuation_token = deep_get(
            response_json,
            "onResponseReceivedCommands", 0,
            "appendContinuationItemsAction",
            "continuationItems", 1,
            "continuationItemRenderer",
            "continuationEndpoint",
            "continuationCommand",
            "token"
        )

        total_result["continuation"] = continuation_token
        total_result["videos"] = total_videos

    return total_result


def extract_shorts_info(json_obj: dict) -> dict:
    root = json_obj["shortsLockupViewModel"]
    video_id = root["inlinePlayerData"]["onVisible"]["innertubeCommand"]["watchEndpoint"]["videoId"]
    title = root["overlayMetadata"]["primaryText"]["content"]
    return {
        "videoId": video_id,
        "title": title,
        "duration": "short"
    }


def deep_get(obj, *keys):
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and isinstance(key, int):
            if 0 <= key < len(current):
                current = current[key]
            else:
                return None
        else:
            return None
    return current


def create_video_tree(video_renderer: dict) -> dict:
    video_id = video_renderer["videoId"]
    title = video_renderer["title"]["runs"][0]["text"]
    duration = video_renderer.get("lengthText", {}).get("simpleText", "Unknown")
    return {
        "videoId": video_id,
        "duration": duration,
        "title": title
    }