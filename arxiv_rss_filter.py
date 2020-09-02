#!/usr/bin/env python3

import argparse
import os
import re
import sys

import feedparser
import jinja2
import yaml


def get_feed(feed):
    return feedparser.parse(feed)


def filter_feed(rss, config):

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
        entry.description += ('<p>'
                              '[<a href="{pdf_link}">PDF</a>]'
                              '</p>').format(**locals())
        rss.entries[i] = entry

    # Author and keyword includes
    filtered_entries = []
    authors_include = config['authors_include']
    keywords_include = [kw.lower() for kw in config['keywords_include']]
    for entry in rss.entries:
        for a in authors_include:
            if a in entry.authors:
                filtered_entries.append(entry)
        for kw in keywords_include:
            if (kw in entry.title) or (kw in entry.description):
                filtered_entries.append(entry)
    rss['entries'] = filtered_entries  # assigning rss.entries doesn't work

    return rss


def render_feed(rss, template):
    with open(template) as f:
        template = jinja2.Template(f.read())
    return template.render(**rss)


def write_feed(xml, output):
    with open(output, 'w') as f:
        f.write(xml)


if __name__ == '__main__':

    p = argparse.ArgumentParser(prog='arxiv_rss_filter')
    p.add_argument('-c', '--config',
                   help='Config file (default: <script_dir>/config.yml)')
    p.add_argument('-o', '--output',
                   help='Output file (default: <script_dir>/feed.rss)')
    args = p.parse_args()
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    if args.config is None:
        args.config = os.path.join(script_dir, 'config.yml')
    if args.output is None:
        args.output = os.path.join(script_dir, 'feed.rss')
    args.template = os.path.join(script_dir, 'template.xml.j2')

    with open(args.config) as f:
        config = yaml.safe_load(f)

    rss = get_feed(config['source'])
    rss = filter_feed(rss, config)
    xml = render_feed(rss, template=args.template)
    write_feed(xml, args.output)
