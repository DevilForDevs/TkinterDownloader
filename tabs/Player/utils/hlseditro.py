import os
import re
import requests

from typing import Optional, List, Dict


def create_resolution_playlists_py(
        manifest_url: str,
        files_dir: str = ".",
        video_id: Optional[str] = None
) -> List[str]:

    os.makedirs(files_dir, exist_ok=True)

    manifest = requests.get(manifest_url).text
    lines = manifest.split('\n')

    audio_lines = [
        l for l in lines
        if l.startswith('#EXT-X-MEDIA') and 'TYPE=AUDIO' in l
    ]

    variant_map: Dict[str, Dict] = {}

    for i in range(len(lines)):

        if lines[i].startswith('#EXT-X-STREAM-INF'):

            info_line = lines[i]

            uri_line = (
                lines[i + 1]
                if i + 1 < len(lines)
                else ""
            )

            res_match = re.search(
                r'RESOLUTION=(\d+x\d+)',
                info_line
            )

            if not res_match or not uri_line:
                continue

            res = res_match.group(1)

            if res not in variant_map:
                variant_map[res] = {
                    'resolution': res,
                    'info_line': info_line,
                    'uri_line': uri_line
                }

    unique_variants = sorted(
        variant_map.values(),
        key=lambda v: int(v['resolution'].split('x')[0])
    )

    resolutions = []

    for v in unique_variants:

        content = '\n'.join([
            '#EXTM3U',
            '#EXT-X-VERSION:3',
            '',
            *audio_lines,
            '',
            v['info_line'],
            v['uri_line'],
            ''
        ])

        filename = (
            f"{video_id}({v['resolution']}).m3u8"
            if video_id
            else f"{v['resolution']}.m3u8"
        )

        file_path = os.path.join(
            files_dir,
            filename
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        resolutions.append(v['resolution'])

    return resolutions