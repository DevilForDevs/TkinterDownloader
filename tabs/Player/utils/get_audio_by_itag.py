from typing import List, Dict, Optional


def get_audio_by_itag(
    adaptive_formats: List[Dict],
    itag: int,
    fallback_itag: int | None = None,
) -> Optional[Dict]:
    """
    Returns audio format info using preferred itag.
    Falls back to fallback_itag if primary itag is not found.
    """

    def find_audio(target_itag: int) -> Optional[Dict]:
        for item in adaptive_formats:
            if item.get("itag") != target_itag:
                continue

            # Skip video entries
            if item.get("height") is not None:
                continue

            return {
                "itag": item.get("itag"),
                "bitrate": item.get("bitrate"),
                "url": item.get("url"),
                "mimeType": item.get("mimeType"),
            }

        return None

    # Try primary itag
    result = find_audio(itag)

    if result:
        return result

    # Try fallback itag
    if fallback_itag is not None:
        return find_audio(fallback_itag)

    return None