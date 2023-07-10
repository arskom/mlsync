# pragma: no cover

from __future__ import print_function

import logging

logger = logging.getLogger(__name__)

from neurons.daemon.config.daemon import ServiceDaemon


def main_rss_job():
    config = ServiceDaemon.parse_config("ink").apply()

    from inknews.rss import _periodic_rss_job_impl
    from twisted.internet import reactor

    _periodic_rss_job_impl(config)

    return reactor.run()
