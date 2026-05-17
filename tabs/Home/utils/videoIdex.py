import re


def extract_video_id( yt_url: str) -> str | None:
    regex = r"""^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/|shorts\/|live\/)|(?:(?:watch)?\?v(?:i)?=|\&v(?:i)?=))([^#\&\?]*).*"""
    match_result = re.match(regex, yt_url)
    if match_result:
        return match_result.group(1)
    return None