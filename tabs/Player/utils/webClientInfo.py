import requests
import re
import json


def get_web_visitor_and_client_from_html():
    url = "https://www.youtube.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/143.0.0.0",
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")

    html = response.text

    # -----------------------------
    # 1. Extract INNERTUBE API KEY + CLIENT VERSION
    # -----------------------------
    client_version_match = re.search(
        r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"',
        html
    )

    api_key_match = re.search(
        r'"INNERTUBE_API_KEY":"([^"]+)"',
        html
    )

    if not client_version_match:
        raise Exception("Client version not found in HTML")

    client_version = client_version_match.group(1)
    api_key = api_key_match.group(1) if api_key_match else None

    # -----------------------------
    # 2. Extract visitorData (from ytInitialData / responseContext fallback)
    # -----------------------------
    visitor_match = re.search(
        r'"VISITOR_DATA":"([^"]+)"',
        html
    )

    if not visitor_match:
        # fallback: sometimes inside ytcfg
        visitor_match = re.search(
            r'visitorData":"([^"]+)"',
            html
        )

    if not visitor_match:
        raise Exception("visitorData not found in HTML")

    visitor_id = visitor_match.group(1)

    return visitor_id, client_version, api_key