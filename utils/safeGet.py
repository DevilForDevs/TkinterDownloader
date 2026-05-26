def safe_get(obj, path, default_val=None):
    cur = obj

    try:
        for p in path:
            if cur is None:
                return default_val

            # ---- dict access (JSONObject equivalent)
            if isinstance(p, str):
                if isinstance(cur, dict):
                    cur = cur.get(p, None)
                else:
                    return default_val

            # ---- list access (JSONArray equivalent)
            elif isinstance(p, int):
                if isinstance(cur, list):
                    index = len(cur) + p if p < 0 else p

                    if 0 <= index < len(cur):
                        cur = cur[index]
                    else:
                        return default_val
                else:
                    return default_val

            else:
                return default_val

        return cur if cur is not None else default_val

    except Exception:
        return default_val