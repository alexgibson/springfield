# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import os
from unittest.mock import Mock, patch
from urllib.parse import parse_qsl, urlparse

from django.core.cache import caches

from springfield.base.tests import TestCase
from springfield.firefox.firefox_details import FirefoxAndroid, FirefoxDesktop, FirefoxIOS

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
PROD_DETAILS_DIR = os.path.join(TEST_DATA_DIR, "product_details_json")


GOOD_PLATS = {"Windows": {}, "OS X": {}, "Linux": {}}

# In the run-up to FF100, these tests support both two-digit and
# three-digit major version numbers
GOOD_BUILDS__TWO_DIGITS = {
    "en-US": {
        "25.0": GOOD_PLATS,  # current release
        "26.0b2": GOOD_PLATS,
        "27.0a1": GOOD_PLATS,
    },
    "de": {"25.0": GOOD_PLATS},
    "fr": {"24.0": GOOD_PLATS},  # prev release
}
GOOD_BUILDS__THREE_DIGITS = {
    "en-US": {
        "125.0": GOOD_PLATS,  # current release
        "126.0b2": GOOD_PLATS,
        "127.0a1": GOOD_PLATS,
    },
    "de": {"125.0": GOOD_PLATS},
    "fr": {"124.0": GOOD_PLATS},  # prev release
}

GOOD_VERSIONS__TWO_DIGITS = {
    "LATEST_FIREFOX_VERSION": "25.0",
    "LATEST_FIREFOX_DEVEL_VERSION": "26.0b2",
    "FIREFOX_DEVEDITION": "26.0b2",
    "FIREFOX_AURORA": "",
    "FIREFOX_ESR": "24.1.0esr",
}
GOOD_VERSIONS__THREE_DIGITS = {
    "LATEST_FIREFOX_VERSION": "125.0",
    "LATEST_FIREFOX_DEVEL_VERSION": "126.0b2",
    "FIREFOX_DEVEDITION": "126.0b2",
    "FIREFOX_AURORA": "",
    "FIREFOX_ESR": "124.1.0esr",
}
GOOD_VERSIONS__TWO_DIGITS_NO_DEV = {
    "LATEST_FIREFOX_VERSION": "25.0",
    "LATEST_FIREFOX_DEVEL_VERSION": "26.0b2",
    "FIREFOX_AURORA": "",
    "FIREFOX_ESR": "24.1.0esr",
}
GOOD_VERSIONS__THREE_DIGITS_NO_DEV = {
    "LATEST_FIREFOX_VERSION": "125.0",
    "LATEST_FIREFOX_DEVEL_VERSION": "126.0b2",
    "FIREFOX_AURORA": "",
    "FIREFOX_ESR": "124.1.0esr",
}


class PatchFirefoxDesktopTwoDigitsMixin:
    firefox_desktop_versions = GOOD_VERSIONS__TWO_DIGITS

    def setUp(self):
        self.firefox_desktop = FirefoxDesktop(json_dir=PROD_DETAILS_DIR)
        self.p1 = patch.object(self.firefox_desktop, "firefox_primary_builds", GOOD_BUILDS__TWO_DIGITS)
        self.p2 = patch.object(self.firefox_desktop, "firefox_beta_builds", {})
        self.p3 = patch.object(self.firefox_desktop, "firefox_versions", self.firefox_desktop_versions)
        self.p1.start()
        self.p2.start()
        self.p3.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.p3.stop()

    def _patch_if_necessary(self, expected):
        # no patching needed for two-digit version numbers
        return expected


class PatchFirefoxDesktopThreeDigitsMixin:
    firefox_desktop_versions = GOOD_VERSIONS__THREE_DIGITS

    def setUp(self):
        self.firefox_desktop = FirefoxDesktop(json_dir=PROD_DETAILS_DIR)
        self.p1 = patch.object(self.firefox_desktop, "firefox_primary_builds", GOOD_BUILDS__THREE_DIGITS)
        self.p2 = patch.object(self.firefox_desktop, "firefox_beta_builds", {})
        self.p3 = patch.object(self.firefox_desktop, "firefox_versions", self.firefox_desktop_versions)
        self.p1.start()
        self.p2.start()
        self.p3.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.p3.stop()

    def _patch_if_necessary(self, expected):
        # Patching is needed for three-digit version numbers
        return f"1{expected}"


class _TestLatestBuildsBase:
    def test_latest_builds(self, expected="25.0"):
        """Should return platforms if localized build does exist."""
        result = self.firefox_desktop.latest_builds("de", "release")
        expected = self._patch_if_necessary(expected)
        self.assertEqual(result[0], expected)
        self.assertIs(result[1], GOOD_PLATS)

    def test_latest_builds_is_none_if_no_build(self):
        """Should return None if the localized build for the channel doesn't exist."""
        result = self.firefox_desktop.latest_builds("fr", "release")
        self.assertIsNone(result)

    def test_latest_builds_channels(self, expected="26.0b2"):
        """Should work with all channels."""
        expected = self._patch_if_necessary(expected)
        result = self.firefox_desktop.latest_builds("en-US", "beta")
        self.assertEqual(result[0], expected)
        self.assertIs(result[1], GOOD_PLATS)

        result = self.firefox_desktop.latest_builds("en-US", "alpha")
        self.assertEqual(result[0], expected)
        self.assertIs(result[1], GOOD_PLATS)


class TestLatestBuildsTwoDigits(
    PatchFirefoxDesktopTwoDigitsMixin,
    _TestLatestBuildsBase,
    TestCase,
):
    pass


class TestLatestBuildsThreeDigits(
    PatchFirefoxDesktopThreeDigitsMixin,
    _TestLatestBuildsBase,
    TestCase,
):
    pass


class _TestLatestBuildsBaseNoDevEditionBase:
    """Should get same results as above and not blow up"""

    firefox_desktop_versions = GOOD_VERSIONS__TWO_DIGITS_NO_DEV

    def test_latest_builds(self, expected="25.0"):
        """Should return platforms if localized build does exist."""
        expected = self._patch_if_necessary(expected)
        result = self.firefox_desktop.latest_builds("de", "release")
        self.assertEqual(result[0], expected)
        self.assertIs(result[1], GOOD_PLATS)

    def test_latest_builds_is_none_if_no_build(self):
        """Should return None if the localized build for the channel doesn't exist."""
        result = self.firefox_desktop.latest_builds("fr", "release")
        self.assertIsNone(result)

    def test_latest_builds_channels(self, expected="26.0b2"):
        """Should work with all channels."""
        expected = self._patch_if_necessary(expected)
        result = self.firefox_desktop.latest_builds("en-US", "beta")
        self.assertEqual(result[0], expected)
        self.assertIs(result[1], GOOD_PLATS)

        result = self.firefox_desktop.latest_builds("en-US", "alpha")
        self.assertEqual(result[0], expected)
        self.assertIs(result[1], GOOD_PLATS)


class TestLatestBuildsNoDevEditionTwoDigits(
    PatchFirefoxDesktopTwoDigitsMixin,
    _TestLatestBuildsBaseNoDevEditionBase,
    TestCase,
):
    pass


class TestLatestBuildsNoDevEditionThreeDigits(
    PatchFirefoxDesktopThreeDigitsMixin,
    _TestLatestBuildsBaseNoDevEditionBase,
    TestCase,
):
    pass


class TestFirefoxDesktopBase(TestCase):
    pd_cache = caches["product-details"]

    def setUp(self):
        self.pd_cache.clear()
        self.firefox_desktop = FirefoxDesktop(json_dir=PROD_DETAILS_DIR)

    def test_get_download_url(self):
        url = self.firefox_desktop.get_download_url("release", "17.0.1", "osx", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-latest-ssl"), ("os", "osx"), ("lang", "pt-BR")],
        )
        # Windows 64-bit
        url = self.firefox_desktop.get_download_url("release", "38.0", "win64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-stub"), ("os", "win64"), ("lang", "en-US")],
        )
        # Windows 64-bit MSI installer
        url = self.firefox_desktop.get_download_url("release", "38.0", "win64-msi", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-msi-latest-ssl"), ("os", "win64"), ("lang", "en-US")],
        )
        # Linux 64-bit
        url = self.firefox_desktop.get_download_url("release", "17.0.1", "linux64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-latest-ssl"), ("os", "linux64"), ("lang", "en-US")],
        )
        # Check three-digit version does not break things
        url = self.firefox_desktop.get_download_url("release", "117.0.1", "osx", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-latest-ssl"), ("os", "osx"), ("lang", "pt-BR")],
        )

    def test_get_download_url_esr(self):
        """
        The ESR version should give us a bouncer url. There is no stub for ESR.
        """
        # MSI installer
        url = self.firefox_desktop.get_download_url("esr", "28.0a2", "win-msi", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-msi-latest-ssl"),
                ("os", "win"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("esr", "28.0a2", "win64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-esr-latest-ssl"), ("os", "win64"), ("lang", "en-US")],
        )
        url = self.firefox_desktop.get_download_url("esr", "28.0a2", "osx", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-esr-latest-ssl"), ("os", "osx"), ("lang", "en-US")],
        )
        url = self.firefox_desktop.get_download_url("esr", "28.0a2", "linux", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-esr-latest-ssl"), ("os", "linux"), ("lang", "en-US")],
        )
        url = self.firefox_desktop.get_download_url("esr", "28.0a2", "linux64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-latest-ssl"),
                ("os", "linux64"),
                ("lang", "en-US"),
            ],
        )

    def test_get_download_url_esr_next(self):
        """
        The ESR_NEXT version should give us a bouncer url with 'esr-next'. There is no stub for ESR.
        """
        url = self.firefox_desktop.get_download_url("esr_next", "52.4.1esr", "win", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-next-latest-ssl"),
                ("os", "win"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("esr_next", "52.4.1esr", "win64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-next-latest-ssl"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("esr_next", "52.4.1esr", "win64-msi", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-next-msi-latest-ssl"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("esr_next", "52.4.1esr", "osx", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-next-latest-ssl"),
                ("os", "osx"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("esr_next", "52.4.1esr", "linux", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-next-latest-ssl"),
                ("os", "linux"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("esr_next", "52.4.1esr", "linux64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-esr-next-latest-ssl"),
                ("os", "linux64"),
                ("lang", "en-US"),
            ],
        )

    def test_get_download_url_devedition(self):
        """
        The Developer Edition version should give us a bouncer url. For Windows,
        a stub url should be returned.
        """
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-devedition-stub"), ("os", "win"), ("lang", "en-US")],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-stub"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        # MSI installer
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win64-msi", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-msi-latest-ssl"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "osx", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "osx"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "linux", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "linux"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "linux64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "linux64"),
                ("lang", "en-US"),
            ],
        )

    def test_get_download_url_devedition_full(self):
        """
        The Developer Edition version should give us a bouncer url. For Windows,
        a full url should be returned.
        """
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "win"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win64", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "osx", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "osx"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "linux", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "linux"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "linux64", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "linux64"),
                ("lang", "en-US"),
            ],
        )

    def test_get_download_url_devedition_l10n(self):
        """
        The Developer Edition version should give us a bouncer url. A stub url
        should be returned for win32/64, while other platforms get a full url.
        The product name is the same as en-US.
        """
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-devedition-stub"), ("os", "win"), ("lang", "pt-BR")],
        )
        # MSI installer
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win-msi", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-msi-latest-ssl"),
                ("os", "win"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "win64", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-stub"),
                ("os", "win64"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "osx", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "osx"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "linux", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "linux"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("alpha", "28.0a2", "linux64", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-devedition-latest-ssl"),
                ("os", "linux64"),
                ("lang", "pt-BR"),
            ],
        )

    def test_get_download_url_nightly(self):
        """
        The Nightly version should give us a bouncer url. For Windows, a stub url
        should be returned.
        """
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-nightly-stub"), ("os", "win"), ("lang", "en-US")],
        )
        # MSI installer
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win64-msi", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-msi-latest-ssl"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-nightly-stub"), ("os", "win64"), ("lang", "en-US")],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "osx", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "osx"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "linux", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "linux"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "linux64", "en-US", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "linux64"),
                ("lang", "en-US"),
            ],
        )

    def test_get_download_url_nightly_full(self):
        """
        The Nightly version should give us a bouncer url. For Windows, a full url
        should be returned.
        """
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "win"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win64", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "win64"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "osx", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "osx"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "linux", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "linux"),
                ("lang", "en-US"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "linux64", "en-US", True, True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-ssl"),
                ("os", "linux64"),
                ("lang", "en-US"),
            ],
        )

    def test_get_download_url_nightly_l10n(self):
        """
        The Nightly version should give us a bouncer url. A stub url should be
        returned for win32/64, while other platforms get a full url. The product
        name is slightly different from en-US.
        """
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-nightly-stub"), ("os", "win"), ("lang", "pt-BR")],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win64", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-nightly-stub"), ("os", "win64"), ("lang", "pt-BR")],
        )
        # MSI installer
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "win64-msi", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-msi-latest-l10n-ssl"),
                ("os", "win64"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "osx", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-l10n-ssl"),
                ("os", "osx"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "linux", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-l10n-ssl"),
                ("os", "linux"),
                ("lang", "pt-BR"),
            ],
        )
        url = self.firefox_desktop.get_download_url("nightly", "50.0a1", "linux64", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "firefox-nightly-latest-l10n-ssl"),
                ("os", "linux64"),
                ("lang", "pt-BR"),
            ],
        )

    def get_download_url_ssl(self):
        """
        SSL-enabled links should always be used except Windows stub installers.
        """
        # SSL-enabled links won't be used for Windows builds (but SSL download
        # is enabled by default for stub installers)
        url = self.firefox_desktop.get_download_url("release", "27.0", "win", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-stub"), ("os", "win"), ("lang", "pt-BR")],
        )

        # SSL-enabled links will be used for OS X builds
        url = self.firefox_desktop.get_download_url("release", "27.0", "osx", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-latest-ssl"), ("os", "osx"), ("lang", "pt-BR")],
        )

        # SSL-enabled links will be used for Linux builds
        url = self.firefox_desktop.get_download_url("release", "27.0", "linux", "pt-BR", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "firefox-latest-ssl"), ("os", "linux"), ("lang", "pt-BR")],
        )

    def test_filter_builds_by_locale_name(self):
        # search english
        builds = self.firefox_desktop.get_filtered_full_builds("release", None, "ujara")
        assert len(builds) == 1
        assert builds[0]["name_en"] == "Gujarati"

        # search native
        builds = self.firefox_desktop.get_filtered_full_builds("release", None, "જરા")
        assert len(builds) == 1
        assert builds[0]["name_en"] == "Gujarati"

        # with a space
        builds = self.firefox_desktop.get_filtered_full_builds("release", None, "british english")
        assert len(builds) == 1
        assert builds[0]["name_en"] == "English (British)"

        # with a comma
        builds = self.firefox_desktop.get_filtered_full_builds("release", None, "French, Français")
        assert len(builds) == 1
        assert builds[0]["name_en"] == "French"

    def test_windows64_build(self):
        # Aurora
        builds = self.firefox_desktop.get_filtered_full_builds("alpha")
        url = builds[0]["platforms"]["win64"]["download_url"]
        assert parse_qsl(urlparse(url).query)[1] == ("os", "win64")

        # Beta
        builds = self.firefox_desktop.get_filtered_full_builds("beta")
        url = builds[0]["platforms"]["win64"]["download_url"]
        assert parse_qsl(urlparse(url).query)[1] == ("os", "win64")

        # Release
        builds = self.firefox_desktop.get_filtered_full_builds("release")
        url = builds[0]["platforms"]["win64"]["download_url"]
        assert parse_qsl(urlparse(url).query)[1] == ("os", "win64")

        # ESR
        builds = self.firefox_desktop.get_filtered_full_builds("esr")
        url = builds[0]["platforms"]["win64"]["download_url"]
        assert parse_qsl(urlparse(url).query)[1] == ("os", "win64")

    def test_linux64_build(self):
        builds = self.firefox_desktop.get_filtered_full_builds("release")
        url = builds[0]["platforms"]["linux64"]["download_url"]
        assert parse_qsl(urlparse(url).query)[1] == ("os", "linux64")

    def test_esr_versions(self):
        """ESR versions should be dynamic based on data."""
        with patch.object(
            self.firefox_desktop._storage,
            "data",
            Mock(return_value=dict(FIREFOX_ESR="24.2")),
        ):
            assert self.firefox_desktop.esr_major_versions == [24]
            assert self.firefox_desktop.esr_minor_versions == ["24.2"]

    def test_esr_versions_prev(self):
        """ESR versions should show previous when available."""
        with patch.object(
            self.firefox_desktop._storage,
            "data",
            Mock(return_value=dict(FIREFOX_ESR="24.6.0", FIREFOX_ESR_NEXT="31.0.0")),
        ):
            assert self.firefox_desktop.esr_major_versions == [24, 31]
            assert self.firefox_desktop.esr_minor_versions == ["24.6.0", "31.0.0"]

    def test_esr_versions_no_latest(self):
        """ESR versions should not blow up if current version is broken."""
        with patch.object(
            self.firefox_desktop._storage,
            "data",
            Mock(return_value=dict(LATEST_FIREFOX_VERSION="Phoenix", FIREFOX_ESR="Albuquerque")),
        ):
            assert self.firefox_desktop.esr_major_versions == []
            assert self.firefox_desktop.esr_minor_versions == []

    def test_latest_major_version(self):
        """latest_major_version should return an int of the major version."""
        for case in (
            ("18", 18),
            ("18.0a1", 18),
            ("18.0.1", 18),
            ("100.0.1", 100),
            ("100", 100),
            ("100.0a1", 100),
            ("119.0.1", 119),
            ("119", 119),
            ("119.0a1", 119),
        ):
            with self.subTest(case=case):
                with patch.object(
                    self.firefox_desktop._storage,
                    "data",
                    Mock(return_value=dict(LATEST_FIREFOX_VERSION=case[0])),
                ):
                    assert self.firefox_desktop.latest_major_version("release") == case[1]

    def test_latest_major_version_no_int(self):
        """latest_major_version should return 0 when no int."""
        with patch.object(
            self.firefox_desktop._storage,
            "data",
            Mock(return_value=dict(LATEST_FIREFOX_VERSION="Phoenix")),
        ):
            assert self.firefox_desktop.latest_major_version("release") == 0

    def test_stub_installer_win_only(self):
        """
        Ensure that builds not in the setting don't get stub.
        """
        url = self.firefox_desktop.get_download_url("release", "19.0", "osx", "en-US")
        assert "product=firefox-stub&" not in url

        url = self.firefox_desktop.get_download_url("beta", "20.0b4", "win", "fr")
        assert "product=firefox-beta-stub&" in url

        url = self.firefox_desktop.get_download_url("beta", "20.0b4", "win64", "fr")
        assert "product=firefox-beta-stub&" in url

        url = self.firefox_desktop.get_download_url("beta", "20.0b4", "linux", "fr")
        assert "product=firefox-beta-stub&" not in url


class TestFirefoxAndroid(TestCase):
    google_play_url_base = "https://play.google.com/store/apps/details?id=org.mozilla."

    def setUp(self):
        self.firefox_android = FirefoxAndroid(json_dir=PROD_DETAILS_DIR)

    def test_latest_release_version(self):
        """latest_version should return the latest release version."""
        for version in ["22.0.1", "100.0.1", "122.0.1"]:
            with self.subTest(version=version):
                with patch.object(
                    self.firefox_android._storage,
                    "data",
                    Mock(return_value=dict(version=version)),
                ):
                    assert self.firefox_android.latest_version("release") == version

    def test_latest_beta_version(self):
        """latest_version should return the latest beta version."""
        for version in ["23.0.1", "101.0.1", "123.0.1"]:
            with self.subTest(version=version):
                with patch.object(
                    self.firefox_android._storage,
                    "data",
                    Mock(return_value=dict(beta_version=version)),
                ):
                    assert self.firefox_android.latest_version("beta") == version

    def test_get_download_url_nightly(self):
        """
        get_download_url should return the same Google Play link of the
        'org.mozilla.fennec_aurora' product regardless of the architecture type,
        if the force_direct option is unspecified.
        """
        assert self.firefox_android.get_download_url("nightly", "arm").startswith(self.google_play_url_base + "fenix")
        assert self.firefox_android.get_download_url("nightly", "x86").startswith(self.google_play_url_base + "fenix")

    def test_get_download_url_nightly_direct(self):
        """
        get_download_url should return a bouncer link depending on the
        architecture type, if the force_direct option is True.
        """
        url = self.firefox_android.get_download_url("nightly", "arm", "multi", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "fennec-nightly-latest"),
                ("os", "android"),
                ("lang", "multi"),
            ],
        )
        url = self.firefox_android.get_download_url("nightly", "x86", "multi", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "fennec-nightly-latest"),
                ("os", "android-x86"),
                ("lang", "multi"),
            ],
        )

    def test_get_download_url_beta(self):
        """
        get_download_url should return the same Google Play link of the
        'org.mozilla.firefox_beta' product regardless of the architecture type,
        if the force_direct option is unspecified.
        """
        assert self.firefox_android.get_download_url("beta", "arm").startswith(self.google_play_url_base + "firefox_beta")
        assert self.firefox_android.get_download_url("beta", "x86").startswith(self.google_play_url_base + "firefox_beta")

    def test_get_download_url_beta_direct(self):
        """
        get_download_url should return a bouncer link depending on the
        architecture type, if the force_direct option is True.
        """
        url = self.firefox_android.get_download_url("beta", "arm", "multi", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "fennec-beta-latest"), ("os", "android"), ("lang", "multi")],
        )
        url = self.firefox_android.get_download_url("beta", "x86", "multi", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [
                ("product", "fennec-beta-latest"),
                ("os", "android-x86"),
                ("lang", "multi"),
            ],
        )

    def test_get_download_url_release(self):
        """
        get_download_url should return the same Google Play link of the
        'org.mozilla.firefox' product regardless of the architecture type,
        if the force_direct option is unspecified.
        """
        assert self.firefox_android.get_download_url("release", "arm").startswith(self.google_play_url_base + "firefox")
        assert self.firefox_android.get_download_url("release", "x86").startswith(self.google_play_url_base + "firefox")

    def test_get_download_url_release_direct(self):
        """
        get_download_url should return a bouncer link depending on the
        architecture type, if the force_direct option is True.
        """
        url = self.firefox_android.get_download_url("release", "arm", "multi", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "fennec-latest"), ("os", "android"), ("lang", "multi")],
        )
        url = self.firefox_android.get_download_url("release", "x86", "multi", True)
        self.assertListEqual(
            parse_qsl(urlparse(url).query),
            [("product", "fennec-latest"), ("os", "android-x86"), ("lang", "multi")],
        )


class TestFirefoxIos(TestCase):
    def setUp(self):
        self.firefox_ios = FirefoxIOS(json_dir=PROD_DETAILS_DIR)
        self.patcher = patch.object(
            self.firefox_ios._storage,
            "data",
            Mock(return_value=dict(ios_version="5.0", ios_beta_version="6.0")),
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_latest_release_version(self):
        """latest_version should return the latest release version."""
        assert self.firefox_ios.latest_version("release") == "5.0"

    def test_latest_beta_version(self):
        """latest_version should return the latest beta version."""
        assert self.firefox_ios.latest_version("beta") == "6.0"


class TestFirefox100Ios(TestCase):
    def setUp(self):
        self.firefox_ios = FirefoxIOS(json_dir=PROD_DETAILS_DIR)
        self.patcher = patch.object(
            self.firefox_ios._storage,
            "data",
            Mock(return_value=dict(ios_version="100.0", ios_beta_version="101.0")),
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_latest_release_version(self):
        """latest_version should return the latest release version."""
        assert self.firefox_ios.latest_version("release") == "100.0"

    def test_latest_beta_version(self):
        """latest_version should return the latest beta version."""
        assert self.firefox_ios.latest_version("beta") == "101.0"
