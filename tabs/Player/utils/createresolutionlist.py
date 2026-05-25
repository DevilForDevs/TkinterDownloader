
from typing import List, Dict, Optional

def get_videos_by_codec(
    adaptive_formats: List[Dict],
    codecs: List[str],
    fallback_codecs: Optional[List[str]] = None,
) -> List[Dict]:

    """
    Returns matching video formats by preferred codecs.
    If no preferred codec matches are found, fallback codecs are used.
    """

    def filter_formats(target_codecs: List[str]) -> List[Dict]:
        results = []

        for item in adaptive_formats:
            mimeType = item.get("mimeType", "")
            height = item.get("height")
            url = item.get("url")

            # Skip audio-only formats
            if height is None:
                continue

            # Skip formats without URL
            if url is None:
                continue

            # True if any codec from target_codecs is found in mimeType
            if any(target in mimeType for target in target_codecs):
                results.append({
                    "height": height,
                    "url": url,
                })

        return results

    # Try primary codecs first
    primary_results = filter_formats(codecs)
    if primary_results:
        return primary_results

    # Use fallback codecs if provided
    if fallback_codecs:
        return filter_formats(fallback_codecs)

    # If still none, return empty list
    return []