import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from curated_latest import load_contract, prepare, render_cards, select, timestamp


def fixture(topic, expires=None):
    item = dict(topic=topic, source="Approved source", title=topic, summary="Summary", href=f"/{topic}/", link_label="Read", reviewed_on="2026-11-05")
    item.update({"expires_at": expires} if expires else {"evergreen": True})
    return item


class CuratedLatestTests(unittest.TestCase):
    def setUp(self):
        self.primary = [fixture("event", "2026-11-09T15:00:00+00:00"), fixture("programme", "2026-11-11T00:00:00+00:00"), fixture("resource")]
        self.fallbacks = [fixture("practice"), fixture("reading"), fixture("learning")]

    def test_expiry_is_exclusive_and_does_not_need_a_new_build(self):
        data = prepare(self.primary, self.fallbacks, timestamp("2026-11-05T12:00:00Z"))
        self.assertEqual([x["topic"] for x in select(data["candidates"], timestamp("2026-11-09T14:59:59Z"))], ["event", "programme", "resource"])
        self.assertEqual([x["topic"] for x in select(data["candidates"], timestamp("2026-11-09T15:00:00Z"))], ["programme", "resource", "practice"])
        later = prepare(self.primary, self.fallbacks, timestamp("2026-11-11T00:00:00Z"))
        self.assertEqual([x["topic"] for x in later["selected"]], ["resource", "practice", "reading"])
        self.assertTrue(later["review_needed"])
        self.assertEqual(later["expired_topics"], ["event", "programme"])

    def test_offsets_and_future_items(self):
        self.primary[0]["valid_from"] = "2026-03-29T02:00:00+01:00"
        self.assertNotIn("event", [x["topic"] for x in prepare(self.primary, self.fallbacks, timestamp("2026-03-29T00:59:59Z"))["selected"]])
        self.assertIn("event", [x["topic"] for x in prepare(self.primary, self.fallbacks, timestamp("2026-03-29T01:00:00Z"))["selected"]])

    def test_invalid_or_missing_expiry_fails_build(self):
        for value in (None, "2026-11-09", "2026-11-09T15:00:00"):
            primary = copy.deepcopy(self.primary)
            primary[0]["expires_at"] = value
            with self.assertRaises(ValueError):
                prepare(primary, self.fallbacks)

    def test_duplicates_and_unsafe_links_fail_build(self):
        for key, value in (("topic", "programme"), ("href", "/programme/"), ("href", "javascript:alert(1)")):
            primary = copy.deepcopy(self.primary)
            primary[0][key] = value
            with self.assertRaises(ValueError):
                prepare(primary, self.fallbacks)
        self.fallbacks[0] = fixture("resource")
        data = prepare(self.primary, self.fallbacks, timestamp("2027-01-01T00:00:00Z"))
        self.assertEqual([x["topic"] for x in data["selected"]], ["resource", "reading", "learning"])

    def test_three_evergreen_replacements_are_required(self):
        with self.assertRaises(ValueError):
            prepare(self.primary, self.fallbacks[:2])
        self.fallbacks[0] = fixture("temporary", "2026-11-06T00:00:00Z")
        with self.assertRaises(ValueError):
            prepare(self.primary, self.fallbacks)

    def test_render_escapes_content(self):
        self.primary[0]["title"] = '<script>example</script>'
        markup = render_cards(self.primary, "latest")
        self.assertEqual(markup.count("<article>"), 3)
        self.assertNotIn("<script>", markup)
        self.assertIn("&lt;script&gt;", markup)

    def test_browser_and_build_selectors_match_at_rollover(self):
        dates = ["2026-11-05T12:00:00Z", "2026-11-09T15:00:00Z", "2026-11-11T00:00:00Z", "2027-05-01T00:00:00Z"]
        for candidates in (prepare(self.primary, self.fallbacks)["candidates"], load_contract(REPO)["candidates"]):
            payload = dict(candidates=candidates, dates=dates)
            script = "const fs=require('node:fs'), {select}=require('./scripts/curated-latest.js'); const p=JSON.parse(fs.readFileSync(0,'utf8')); console.log(JSON.stringify(p.dates.map(d=>select(p.candidates,Date.parse(d)).map(i=>i.topic))));"
            actual = json.loads(subprocess.check_output(["node", "-e", script], input=json.dumps(payload).encode(), cwd=REPO))
            expected = [[item["topic"] for item in select(candidates, timestamp(day))] for day in dates]
            self.assertEqual(actual, expected)
            self.assertTrue(all(len(set(row)) == 3 for row in actual))


if __name__ == "__main__":
    unittest.main()
