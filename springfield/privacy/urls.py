# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from springfield.base.util import page

urlpatterns = (page("websites/cookie-settings/", "privacy/cookie-settings.html", ftl_files=["privacy/cookie-settings"]),)
