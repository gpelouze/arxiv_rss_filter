#!/usr/bin/env python3

import feedparser
import jinja2


def get_feed(feed):
    return feedparser.parse(feed)


def filter_feed(rss):
    return rss


def write_feed(rss, output, template_src='arxiv_rss_template.xml.j2'):
    with open(template_src) as f:
        template = jinja2.Template(f.read())
    with open(output, 'w') as f:
        f.write(template.render(**rss))


if __name__ == '__main__':

    # rss = get_feed('http://export.arxiv.org/rss/astro-ph.SR')
    rss = get_feed('dev/feed_in.xml')
    rss = filter_feed(rss)
    write_feed(rss, 'dev/feed_out.xml')
