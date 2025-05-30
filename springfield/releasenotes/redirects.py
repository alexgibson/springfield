# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from springfield.redirects.util import redirect

redirectpatterns = (
    # issue 14467
    redirect(r"^firefox/125.0/releasenotes/?$", "/firefox/125.0.1/releasenotes/"),
)
