# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.base import BasePage


class PlatformDownloadPage(BasePage):
    _URL_TEMPLATE = "/{locale}/browsers/desktop/{slug}/"

    _windows_download_button_locator = (By.ID, "download-button-desktop-release-win")
    _mac_download_button_locator = (By.ID, "download-button-desktop-release-osx")
    _linux_download_button_locator = (By.ID, "download-button-desktop-release-linux")
    _linux64_download_button_locator = (By.ID, "download-button-desktop-release-linux-64")

    @property
    def is_windows_download_button_displayed(self):
        return self.is_element_displayed(*self._windows_download_button_locator)

    @property
    def is_mac_download_button_displayed(self):
        return self.is_element_displayed(*self._mac_download_button_locator)

    @property
    def is_linux_download_button_displayed(self):
        return self.is_element_displayed(*self._linux_download_button_locator)

    @property
    def is_linux64_download_button_displayed(self):
        return self.is_element_displayed(*self._linux64_download_button_locator)
