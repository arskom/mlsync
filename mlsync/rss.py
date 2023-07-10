import logging

logger = logging.getLogger(__name__)

import socket

import requests

from time import sleep, time
from datetime import datetimegit
from readability import Document
from spyne.util.six.moves.urllib.parse import urlparse


class RssItem:
    def __init__(self, url, dt, title, summary):
        # TODO
        self.url = url
        self.dt = dt
        self.title = title
        self.summary = summary


def _scrape_url(item):
    url = item.link
    purl = urlparse(url)
    headers = {
        "User-Agent": "mlstore 1.0.0",
    }

    # fetch url
    if purl.scheme in ("http", "https"):
        try:
            response = requests.get(url, headers=headers)
            data = response.text
            logger.info("Scraping %s", url)
        except socket.error as e:
            logger.exception(e)
            logger.error("Skipping %s", url)
            return

    else:
        logger.warning("Unknown url '%s'", url)
        return

    # fetch url
    document = Document(data, unwanted_tags=["img"])

    summary = document.summary(html_partial=True)
    summary = (
        summary.replace(u"\u0091", "'")
        .replace(u"\u0092", "'")
        .replace(u"\u0093", '"')
        .replace(u"\u0094", '"')
    )

    title = document.short_title()
    title = (
        title.replace(u"\u0091", "'")
        .replace(u"\u0092", "'")
        .replace(u"\u0093", '"')
        .replace(u"\u0094", '"')
    )

    sleep(2)  # prevent too fast scraping

    pub_date = item.pub_date
    if pub_date is None:
        logger.warning("%s has no publication date -- defaulting to now", url)
        pub_date = datetime.utcnow()

    return RssItem(url=url, dt=pub_date, title=title, summary=summary,)
