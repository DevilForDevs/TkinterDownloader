from utils.safeGet import safe_get



def get_content_array(response_context: dict, flags: str) -> list:
    # watch initial page
    if flags == "watchInitial":
        result = safe_get(
            response_context,
            [
                "contents",
                "twoColumnWatchNextResults",
                "secondaryResults",
                "secondaryResults",
                "results",
            ],
            default_val=[],
        )

        return result if isinstance(result, list) else []

    # watch continuation page
    if flags == "watchContinuation":
        result = safe_get(
            response_context,
            [
                "onResponseReceivedEndpoints",
                0,
                "appendContinuationItemsAction",
                "continuationItems",
            ],
            default_val=[],
        )

        return result if isinstance(result, list) else []

    return []


def extract_comments(root: dict) -> str:
    panels = safe_get(root, ["engagementPanels"])
    if not isinstance(panels, list):
        return ""

    for panel in panels:
        contextual_info = safe_get(panel, [
            "engagementPanelSectionListRenderer",
            "header",
            "engagementPanelTitleHeaderRenderer",
            "contextualInfo",
        ])

        runs = None
        if isinstance(contextual_info, list):
            runs = contextual_info
        elif isinstance(contextual_info, dict):
            runs = contextual_info.get("runs")

        if isinstance(runs, list) and len(runs) > 0:
            first = runs[0]
            if isinstance(first, dict):
                text = first.get("text")
                if text:
                    return text

    return ""


def extract_video_details(root: dict):
    try:
        contents = safe_get(root, [
            "contents",
            "twoColumnWatchNextResults",
            "results",
            "results",
            "contents",
        ])

        if not isinstance(contents, list):
            return None

        primary_info = safe_get(contents, [0, "videoPrimaryInfoRenderer"])
        secondary_info = safe_get(contents, [1, "videoSecondaryInfoRenderer"])

        owner = safe_get(secondary_info, [
            "owner",
            "videoOwnerRenderer",
        ])

        channel_photo = safe_get(secondary_info, [
            "owner",
            "videoOwnerRenderer",
            "thumbnail",
            "thumbnails",
            1,
            "url",
        ])

        subscriber_count = safe_get(owner, [
            "subscriberCountText",
            "simpleText",
        ])

        title_run = safe_get(owner, [
            "title",
            "runs",
            0,
        ])

        channel_name = safe_get(title_run, [
            "title",
            "runs",
            0,
        ])

        channel_url = safe_get(title_run, [
            "navigationEndpoint",
            "browseEndpoint",
            "canonicalBaseUrl",
        ])

        top_bar = safe_get(primary_info, [
            "videoActions",
            "menuRenderer",
            "topLevelButtons",
        ])

        likes = safe_get(top_bar, [
            0,
            "segmentedLikeDislikeButtonViewModel",
            "likeButtonViewModel",
            "likeButtonViewModel",
            "toggleButtonViewModel",
            "toggleButtonViewModel",
            "defaultButtonViewModel",
            "buttonViewModel",
            "title",
        ])

        return {
            "title": "title",
            "likes": likes,
            "dislikes": "Dislikes",
            "channelBigThumb": channel_photo,
            "commentsCount": extract_comments(root),
            "localLizedViewsandUploadedAgo": "",
            "subscriberCount": subscriber_count,
            "firstHasTag": "",
            "hashTags": "",
            "channelName": channel_name,
            "channelUrl": channel_url,
        }

    except Exception:
        return None


def parse_watch_items(items: list):
    videos_list = []
    continuation_token = None

    for item in items:

        # ---------------- LOCKUP VIEW (videos/playlists) ----------------
        if isinstance(item, dict) and "lockupViewModel" in item:
            lv = item["lockupViewModel"]

            def lv_get(path, default=""):
                return safe_get(lv, path, default)

            title = lv_get([
                "metadata",
                "lockupMetadataViewModel",
                "title",
                "content",
            ], "No Title")

            views = lv_get([
                "metadata",
                "lockupMetadataViewModel",
                "metadata",
                "contentMetadataViewModel",
                "metadataRows",
                1,
                "metadataParts",
                0,
                "text",
                "content",
            ], "No views")

            uploaded_ago = lv_get([
                "metadata",
                "lockupMetadataViewModel",
                "metadata",
                "contentMetadataViewModel",
                "metadataRows",
                1,
                "metadataParts",
                1,
                "text",
                "content",
            ], "No uploadedAgo")

            channel_photo = lv_get([
                "metadata",
                "lockupMetadataViewModel",
                "image",
                "decoratedAvatarViewModel",
                "avatar",
                "avatarViewModel",
                "image",
                "sources",
                0,
                "url",
            ], None)

            duration = lv_get([
                "contentImage",
                "thumbnailViewModel",
                "overlays",
                0,
                "thumbnailOverlayBadgeViewModel",
                "thumbnailBadges",
                0,
                "thumbnailBadgeViewModel",
                "text",
            ], None)

            channel_name = lv_get([
                "metadata",
                "lockupMetadataViewModel",
                "metadata",
                "contentMetadataViewModel",
                "metadataRows",
                0,
                "metadataParts",
                0,
                "text",
                "content",
            ], "")

            channel_url = lv_get([
                "metadata",
                "lockupMetadataViewModel",
                "image",
                "decoratedAvatarViewModel",
                "rendererContext",
                "commandContext",
                "onTap",
                "innertubeCommand",
                "browseEndpoint",
                "browseId",
            ], "")

            content_type = lv_get(["contentType"], "")

            content_id = lv_get(["contentId"])

            # VIDEO
            if content_type == "LOCKUP_CONTENT_TYPE_VIDEO":
                videos_list.append({
                    "videoId": content_id,
                    "title": title,
                    "channelName": channel_name,
                    "channelAvatar": channel_photo,
                    "channelUrl": channel_url,
                    "views": views,
                    "duration": duration,
                    "playlistId": None,
                    "shortsArray": None,
                    "publishedOn": uploaded_ago,
                })

            # PLAYLIST
            elif content_type == "LOCKUP_CONTENT_TYPE_PLAYLIST":
                try:
                    playlist_id = safe_get(item, [
                        "lockupViewModel",
                        "rendererContext",
                        "commandContext",
                        "onTap",
                        "innertubeCommand",
                        "watchEndpoint",
                        "videoId",
                    ])

                    videos_list.append({
                        "videoId": content_id,
                        "title": title,
                        "channelName": channel_name,
                        "channelAvatar": channel_photo,
                        "channelUrl": channel_url,
                        "views": views,
                        "duration": duration,
                        "playlistId": playlist_id,
                        "shortsArray": None,
                        "publishedOn": uploaded_ago,
                    })

                except Exception:
                    pass

        # ---------------- SHORTS SHELF ----------------
        if isinstance(item, dict) and "reelShelfRenderer" in item:
            shorts_list = []

            shorts_items = safe_get(item, [
                "reelShelfRenderer",
                "items",
            ], [])

            if isinstance(shorts_items, list):
                for s in shorts_items:
                    raw_id = safe_get(s, [
                        "shortsLockupViewModel",
                        "entityId",
                    ], "")

                    video_id = raw_id.replace("shorts-shelf-item-", "")

                    title = safe_get(s, [
                        "shortsLockupViewModel",
                        "overlayMetadata",
                        "primaryText",
                        "content",
                    ], "")

                    views = safe_get(s, [
                        "shortsLockupViewModel",
                        "overlayMetadata",
                        "secondaryText",
                        "content",
                    ], "")

                    shorts_list.append({
                        "videoId": video_id,
                        "title": title,
                        "views": views,
                    })

            if shorts_list:
                videos_list.append({
                    "videoId": shorts_list[0]["videoId"],
                    "title": "shorts",
                    "shortsArray": shorts_list,
                })

        # ---------------- CONTINUATION ----------------
        if isinstance(item, dict) and "continuationItemRenderer" in item:
            continuation_token = safe_get(item, [
                "continuationItemRenderer",
                "continuationEndpoint",
                "continuationCommand",
                "token",
            ])

    return videos_list, continuation_token


def parse_watch_json(response: dict, flags: str):
    contents_array = get_content_array(response, flags)  # assumed external
    videos, continuation = parse_watch_items(contents_array)
    details = extract_video_details(response)

    return {
        "videoDetails": details,
        "videos": videos,
        "continuation": continuation,
    }