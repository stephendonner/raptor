# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from mozlog import get_proxy_logger


here = os.path.abspath(os.path.dirname(__file__))
webext_dir = os.path.join(os.path.dirname(here), 'webext', 'raptor')
LOG = get_proxy_logger(component="gen_test_url")


def gen_test_config(browser, test):
    LOG.info("writing test settings url background js, so webext can get it")

    data = """
    // this file is auto-generated by raptor, do not edit directly
    function getTestConfig() {
      return {'browser': '%s', 'test_settings_url': 'http://localhost:8000/%s.json'};
    }
    """ % (browser, test)

    webext_background_script = (os.path.join(webext_dir, 'auto_gen_test_config.js'))

    file = open(webext_background_script, "w")
    file.write(data)
    file.close()

    LOG.info("finished writing test config into webext")
