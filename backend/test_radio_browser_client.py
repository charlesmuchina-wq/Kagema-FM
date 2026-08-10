"""Offline unit tests for radio_browser_client.

These use only the standard library (``unittest`` + ``asyncio``) and an injected
fake fetcher, so they run with no network access and no third-party packages.

Run:  python -m unittest test_radio_browser_client
"""
import asyncio
import unittest

import radio_browser_client as rb


class OrderingTests(unittest.TestCase):
    def test_default_primary_is_de1(self):
        self.assertEqual(rb.PRIMARY_BASE_URL, "https://de1.api.radio-browser.info")
        self.assertEqual(rb.DEFAULT_MIRRORS[0], rb.PRIMARY_BASE_URL)

    def test_json_base(self):
        self.assertEqual(
            rb.json_base("https://de1.api.radio-browser.info/"),
            "https://de1.api.radio-browser.info/json",
        )

    def test_preferred_first_and_deduped(self):
        order = rb.ordered_mirrors(preferred="https://at1.api.radio-browser.info")
        self.assertEqual(order[0], "https://at1.api.radio-browser.info")
        # No duplicates even though at1 is also in DEFAULT_MIRRORS.
        self.assertEqual(len(order), len(set(order)))

    def test_user_agent_is_descriptive_not_spoofed(self):
        self.assertIn("KagemaFM", rb.USER_AGENT)
        self.assertNotIn("Mozilla", rb.USER_AGENT)


class ResolveWorkingBaseTests(unittest.TestCase):
    def test_returns_first_passing_mirror(self):
        # de1 fails its probe, nl1 passes -> nl1 chosen.
        def probe(base):
            return "nl1" in base

        self.assertEqual(
            rb.resolve_working_base(probe),
            "https://nl1.api.radio-browser.info",
        )

    def test_returns_none_when_all_fail(self):
        self.assertIsNone(rb.resolve_working_base(lambda base: False))

    def test_probe_exception_skips_mirror(self):
        def probe(base):
            if "de1" in base:
                raise RuntimeError("boom")
            return "at1" in base

        self.assertEqual(
            rb.resolve_working_base(probe),
            "https://at1.api.radio-browser.info",
        )


class AsyncFailoverTests(unittest.TestCase):
    def test_failover_to_next_mirror(self):
        attempted = []

        async def fake_fetch(url, headers, params, timeout):
            attempted.append(url)
            # de1 and nl1 raise; at1 succeeds.
            if "de1" in url or "nl1" in url:
                raise ConnectionError("mirror down")
            return 200, [{"name": "station"}]

        client = rb.RadioBrowserClient(fetcher=fake_fetch)
        data = asyncio.run(client.get_json("json/stations/topvote/5"))

        self.assertEqual(data, [{"name": "station"}])
        self.assertEqual(client.last_working_base, "https://at1.api.radio-browser.info")
        # It tried de1 then nl1 then at1, in order.
        self.assertEqual(len(attempted), 3)
        self.assertTrue(attempted[0].startswith("https://de1"))

    def test_sends_descriptive_user_agent(self):
        seen = {}

        async def fake_fetch(url, headers, params, timeout):
            seen.update(headers)
            return 200, []

        client = rb.RadioBrowserClient(fetcher=fake_fetch)
        asyncio.run(client.get_json("json/stats"))
        self.assertEqual(seen.get("User-Agent"), rb.USER_AGENT)

    def test_non_2xx_triggers_failover(self):
        async def fake_fetch(url, headers, params, timeout):
            if "de1" in url:
                return 503, None
            return 200, {"ok": True}

        client = rb.RadioBrowserClient(fetcher=fake_fetch)
        data = asyncio.run(client.get_json("json/stats"))
        self.assertEqual(data, {"ok": True})
        self.assertEqual(client.last_working_base, "https://nl1.api.radio-browser.info")

    def test_all_mirrors_fail_raises(self):
        async def fake_fetch(url, headers, params, timeout):
            raise TimeoutError("nope")

        client = rb.RadioBrowserClient(fetcher=fake_fetch)
        with self.assertRaises(RuntimeError):
            asyncio.run(client.get_json("json/stats"))


if __name__ == "__main__":
    unittest.main()
