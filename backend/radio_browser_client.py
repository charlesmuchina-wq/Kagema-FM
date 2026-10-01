"""Resilient shared client for the Radio Browser API (radio-browser.info).

State-of-the-art gap this addresses
-----------------------------------
The backend previously hardcoded a single mirror ("de1.api.radio-browser.info")
in several modules with no failover, no mirror discovery, and inconsistent
User-Agents. Radio Browser's own guidance is to spread load across mirrors and
fail over when one is unavailable, and to send a stable, descriptive
User-Agent. This module centralizes that behavior so every consumer shares one
mirror list, one User-Agent, and one failover implementation.

Design notes
------------
* Importing this module pulls in **stdlib only** — ``aiohttp`` is imported
  lazily inside the async request path, so modules that only need the shared
  constants (mirror list, base URL, User-Agent) can import them cheaply.
* ``de1`` is kept first in the mirror order to preserve the previous default
  behavior; the difference is that the client now transparently rolls over to
  ``nl1`` / ``at1`` / ``fi1`` when a mirror errors or returns a non-2xx status.
* The failover core (:func:`resolve_working_base`) and mirror ordering
  (:func:`ordered_mirrors`) are pure and synchronous so they can be unit-tested
  without any network access.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Known Radio Browser mirrors. "de1" first to preserve prior default behavior.
DEFAULT_MIRRORS: List[str] = [
    "https://de1.api.radio-browser.info",
    "https://nl1.api.radio-browser.info",
    "https://at1.api.radio-browser.info",
    "https://fi1.api.radio-browser.info",
]

# DNS round-robin host that resolves to a random healthy mirror. Used for
# optional runtime discovery of the current mirror list.
DISCOVERY_HOST: str = "https://all.api.radio-browser.info"

# Backwards-compatible single source of truth for the primary mirror.
PRIMARY_BASE_URL: str = DEFAULT_MIRRORS[0]

# One canonical, descriptive User-Agent (radio-browser.info etiquette asks for a
# stable UA that identifies the application rather than a spoofed browser UA).
USER_AGENT: str = "KagemaFM/1.0 (+https://github.com/charlesmuchina-wq/kagema-fm)"


def json_base(base_url: str) -> str:
    """Return the ``/json`` API root for a given mirror base URL."""
    return base_url.rstrip("/") + "/json"


def ordered_mirrors(
    preferred: Optional[str] = None,
    mirrors: Optional[Iterable[str]] = None,
) -> List[str]:
    """Return the mirror list with ``preferred`` first, de-duplicated.

    Trailing slashes are normalized so equivalent URLs collapse to one entry.
    """
    result: List[str] = []
    if preferred:
        result.append(preferred.rstrip("/"))
    for mirror in (mirrors if mirrors is not None else DEFAULT_MIRRORS):
        normalized = mirror.rstrip("/")
        if normalized not in result:
            result.append(normalized)
    return result


def resolve_working_base(
    probe: Callable[[str], bool],
    mirrors: Optional[Iterable[str]] = None,
    preferred: Optional[str] = None,
) -> Optional[str]:
    """Return the first mirror for which ``probe(base)`` is truthy.

    ``probe`` takes a mirror base URL and returns whether it is usable. It is
    synchronous and side-effect free from this function's perspective, which
    makes the failover order trivially unit-testable without a network.
    Returns ``None`` when no mirror passes.
    """
    for base in ordered_mirrors(preferred, mirrors):
        try:
            if probe(base):
                return base
        except Exception as exc:  # noqa: BLE001 - a failing probe just skips it
            logger.debug("Radio Browser mirror probe failed for %s: %s", base, exc)
    return None


# An async fetcher takes (url, headers, params, timeout) and returns
# (http_status, decoded_json). Injectable so failover can be tested offline.
Fetcher = Callable[[str, dict, Optional[dict], float], Awaitable[Tuple[int, Any]]]


class RadioBrowserClient:
    """Async Radio Browser client with automatic mirror failover.

    ``aiohttp`` is imported lazily inside :meth:`_default_fetch`, so constructing
    or importing this class never requires network libraries to be installed.
    """

    def __init__(
        self,
        mirrors: Optional[List[str]] = None,
        user_agent: str = USER_AGENT,
        timeout: float = 15.0,
        fetcher: Optional[Fetcher] = None,
    ) -> None:
        self.mirrors = ordered_mirrors(mirrors=mirrors or DEFAULT_MIRRORS)
        self.user_agent = user_agent
        self.timeout = timeout
        self._fetcher = fetcher  # override for testing / custom transports
        self.last_working_base: Optional[str] = None

    async def _default_fetch(
        self, url: str, headers: dict, params: Optional[dict], timeout: float
    ) -> Tuple[int, Any]:
        import aiohttp  # lazy import: keeps module import stdlib-only

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                data = await response.json(content_type=None)
                return response.status, data

    async def get_json(self, path: str, params: Optional[dict] = None) -> Any:
        """GET ``path`` (relative to a mirror root) with mirror failover.

        Example: ``await client.get_json("json/stations/search", {"limit": 10})``.
        Tries the last-known-good mirror first, then the rest in order. Returns
        the decoded JSON from the first mirror that answers with a 2xx status.
        Raises ``RuntimeError`` if every mirror fails.
        """
        fetch = self._fetcher or self._default_fetch
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        errors: List[str] = []
        for base in ordered_mirrors(self.last_working_base, self.mirrors):
            url = base.rstrip("/") + "/" + path.lstrip("/")
            try:
                status, data = await fetch(url, headers, params, self.timeout)
                if 200 <= status < 300:
                    self.last_working_base = base
                    return data
                errors.append(f"{base} -> HTTP {status}")
            except Exception as exc:  # noqa: BLE001 - try the next mirror
                errors.append(f"{base} -> {exc}")
        raise RuntimeError(
            "All Radio Browser mirrors failed: " + "; ".join(errors)
        )
