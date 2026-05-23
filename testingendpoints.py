import json
import requests


def test_ios_player_request():
    url = "https://youtubei.googleapis.com/youtubei/v1/player"

    params = {
        "prettyPrint": "false",
        "t": "oK_V8v9wyOt2",
        "id": "C3qWEKXfhnw"
    }

    headers = {
        "User-Agent": (
            "com.google.ios.youtube/21.03.2"
            "(iPhone16,2; U; CPU iOS 18_7_2 like Mac OS X; GB)"
        ),

        "X-Goog-Api-Format-Version": "2",

        "Content-Type": "application/json",

        "Accept-Language": "en-GB,en;q=0.9"
    }

    body = {
        "context": {
            "client": {
                "clientName": "IOS",
                "clientVersion": "21.03.2",
                "clientScreen": "WATCH",
                "platform": "MOBILE",

                "visitorData": (
                    "CgtCNU1CNy13QVdiVSim3cDQBjIKCgJJThIEGgAgZzoMCAEg"
                    "spS8wuTUi4hqYt8CCtwCMTguWVQ9ajVPUkxpTGY3NE1IYmRh"
                    "NzNJUDQ3LWdyUXlnLVhrSGxnNVNqNy1maHdmeTJYV1RnWXRY"
                    "Z0J5emhhZjZFekx0RGx4UmxSWFotQlNvQ05yeFlCalBUQ2x1"
                    "UlZ0Y1E5QW5fbFdVTjFhTVBUeE91OXdlWGlSbGNfYkVVdVNs"
                    "QlhSUFVNc2lxN3hhYVZ4c0J0RVo5eUlwaEQyajNKSmpsSE80"
                    "MVBTQi1pY2hFTDN0Mno5NXdJTGVHdldZY1RRNHVfU0d2VFgz"
                    "UGhzXzM0cENCdmx5UVBDc3o5QW10TkMwX0EyZl82TUVtZUlu"
                    "Yk9yTUNDQXBsWTBPZ1JEVUw2WEJ1RHZVdGlDS211emtqeWNx"
                    "a0FMaVNnVGx3dmRXdmEzeFlNaHNWeVJrMkowSDE1R2hUUXkz"
                    "V0pKTE5vck16NlFzV3AyNUVWd1lvb2RvR01OWHFtQ2gxblNl"
                    "azdR"
                ),

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

        "videoId": "C3qWEKXfhnw",

        "cpn": "mbRRH-3qVOT1SvS9",

        "contentCheckOk": True,
        "racyCheckOk": True
    }

    response = requests.post(
        url=url,
        params=params,
        headers=headers,
        json=body
    )

    print("STATUS:", response.status_code)
    print()

    try:
        data = response.json()

        print(json.dumps(data, indent=2))

        print()
        print("PLAYABILITY:")
        print(data.get("playabilityStatus"))

        print()
        print("HLS:")
        print(
            data.get("streamingData", {})
                .get("hlsManifestUrl")
        )

    except Exception:
        print(response.text)

    return response


if __name__ == "__main__":
    test_ios_player_request()