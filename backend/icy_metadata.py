"""
Best-effort ICY (SHOUTcast/Icecast) now-playing metadata extraction.

React Native / expo-av cannot read ICY in-band metadata from a stream, so the
backend does it: it opens the stream with ``Icy-MetaData: 1``, skips one audio
block, reads the first metadata block, and parses ``StreamTitle``. This is
best-effort — it returns None when the stream exposes no ICY metadata (e.g. a
plain file or an HLS/playlist URL) or on any network error.
"""
import re

_TITLE_RE = re.compile(r"StreamTitle='(.*?)';")
USER_AGENT = "KagemaFM/1.0 (+https://github.com/charlesmuchina-wq/kagema-fm)"


async def fetch_icy_now_playing(url, timeout=8):
    """Return the current ICY StreamTitle for a stream URL, or None."""
    if not url:
        return None

    import aiohttp

    headers = {"Icy-MetaData": "1", "User-Agent": USER_AGENT, "Accept": "*/*"}
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(url, headers=headers) as resp:
                raw_metaint = resp.headers.get("icy-metaint")
                if not raw_metaint:
                    return None
                metaint = int(raw_metaint)
                # Skip one audio block, then read the metadata block.
                await resp.content.readexactly(metaint)
                length_byte = await resp.content.readexactly(1)
                meta_len = length_byte[0] * 16
                if meta_len <= 0:
                    return None
                meta = await resp.content.readexactly(meta_len)
                match = _TITLE_RE.search(meta.decode("utf-8", errors="replace"))
                if not match:
                    return None
                return match.group(1).strip() or None
    except Exception:
        # Best-effort: any failure (timeout, non-ICY stream, short read) -> None.
        return None


def split_title(stream_title):
    """Split an ICY StreamTitle ('Artist - Title') into (title, artist)."""
    if not stream_title:
        return None, None
    if " - " in stream_title:
        artist, _, title = stream_title.partition(" - ")
        return (title.strip() or None), (artist.strip() or None)
    return stream_title, None
