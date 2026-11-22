# python3 test_tp_page.py  (Seth Nov 22 2026 hard rule: real portal screenshots, fail closed, checked wording)
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tp_page

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tp_page_fixture")


class T(unittest.TestCase):
    def setUp(self):
        self.env = dict(os.environ)

    def tearDown(self):
        os.environ.clear(); os.environ.update(self.env)

    def test_old_set_is_refused(self):
        os.environ.pop("LF_TP_PAGE_FIXTURE", None)
        real = tp_page.current_design_version
        tp_page.current_design_version = lambda c=None: ("aaaaaaaaaaaa", "test")
        tp_page._get_saved = tp_page._get
        tp_page._get = lambda url, timeout=30: b'{"design_version":"467855c7babe","files":[]}' if url.endswith("manifest.json") else b""
        try:
            with self.assertRaises(tp_page.TpPageUnavailable) as e:
                tp_page.load(tempfile.mkdtemp())
            self.assertIn("design", str(e.exception))
        finally:
            tp_page.current_design_version = real
            tp_page._get = tp_page._get_saved

    def test_missing_version_is_refused(self):
        tp_page._get_saved = tp_page._get
        def boom(url, timeout=30):
            raise OSError("offline")
        tp_page._get = boom
        try:
            with self.assertRaises(tp_page.TpPageUnavailable):
                tp_page.current_design_version(None)
            with self.assertRaises(tp_page.TpPageUnavailable):
                tp_page.load(tempfile.mkdtemp())
        finally:
            tp_page._get = tp_page._get_saved

    def test_fixture_needs_test_mode(self):
        os.environ["LF_TP_PAGE_FIXTURE"] = FIX
        os.environ.pop("LF_TEST", None)
        tp_page._get_saved = tp_page._get
        tp_page._get = lambda url, timeout=30: (_ for _ in ()).throw(OSError("offline"))
        try:
            with self.assertRaises(tp_page.TpPageUnavailable):
                tp_page.load(tempfile.mkdtemp())
        finally:
            tp_page._get = tp_page._get_saved

    def test_page_shows_shots_captions_label_note_and_link(self):
        os.environ["LF_TP_PAGE_FIXTURE"] = FIX; os.environ["LF_TEST"] = "1"
        s = tp_page.load(tempfile.mkdtemp())
        h = tp_page.page_html(s)
        self.assertIn("Your private client page", h)
        for k in ("overview", "systems", "edition"):
            self.assertIn(tp_page.CAPTIONS[k], h)
        self.assertIn("See the sample at", h)
        self.assertIn("my.launchforte.com/demo", h)
        self.assertNotIn("portal-sample-top", h)

    def test_wording_check(self):
        for k, c in tp_page.CAPTIONS.items():
            self.assertEqual(tp_page.lint(c), [], k)
        for bad in ("I monitor your systems", "Your data is protected", "Guaranteed uptime", "Verified healthy", "Critical, act now", "All clear", "AI writes it"):
            self.assertTrue(tp_page.lint(bad), bad)


if __name__ == "__main__":
    unittest.main()
