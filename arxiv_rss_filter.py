#!/usr/bin/env python3

import re

import feedparser
import jinja2


def get_feed(feed):
    return feedparser.parse(feed)


def filter_feed(rss):

    # Cosmetic filtering
    title_regex = re.compile(
        r'^(?P<title>.*)\. '
        r'\((?P<id>arXiv:[\d.v]+) '
        r'\[(?P<category>[\w\.-]+)\](?P<extra>.*)\)$')
    for i, entry in enumerate(rss.entries):
        m = title_regex.match(entry.title)
        if m:
            entry.title = m.group('title')
            entry.description += ('<p>'
                                  '{id} [{category}] {extra}'
                                  '</p>').format(**m.groupdict())
        pdf_link = re.sub(r'\/abs\/', '/pdf/', entry.link)
        entry.description += f'<p>[<a href="{pdf_link}">PDF</a>]</p>'
        rss.entries[i] = entry

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
