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


def filter_feed(rss, config, args):

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
    authors_include = config['authors_include']
    keywords_include = [kw for kw in config['keywords_include']]
    keywords_exclude = [kw for kw in config['keywords_exclude']]
    for entry in rss.entries:
        entry.filter_matches = []
        entry.filter_exclude_matches = []
        for a in authors_include:
            if a in entry.authors:
                entry.filter_matches.append(a)
        kw_search_text = entry.title + " " + entry.description
        for kw in keywords_include:
            this_kw_search_text = kw_search_text
            if kw.islower():
                this_kw_search_text = kw_search_text.lower()
            if kw in this_kw_search_text:
                entry.filter_matches.append(kw)
        for kw in keywords_exclude:
            this_kw_search_text = kw_search_text
            if kw.islower():
                this_kw_search_text = kw_search_text.lower()
            if kw in this_kw_search_text:
                entry.filter_exclude_matches.append(kw)
        if entry.filter_matches:
            kw_title = ' [{}]'.format(', '.join(entry.filter_matches))
            entry.title += kw_title
        if entry.filter_exclude_matches:
            kw_title = ' >{}<'.format(', '.join(entry.filter_exclude_matches))
            entry.title += kw_title

        entry.rank = (len(entry.filter_matches)
                      - len(entry.filter_exclude_matches))

        matches_includes = (len(entry.filter_matches) > 0)
        matches_excludes = (len(entry.filter_exclude_matches) > 0)
        if matches_includes and not matches_excludes:
            entry.title = "✅ " + entry.title
        elif matches_excludes and not matches_includes:
            entry.title = "❌ " + entry.title
        else:
            entry.title = "❔ " + entry.title

    if args.sort:
        rss['entries'] = sorted(rss.entries, key=lambda e: e.rank, reverse=True)
    else:
        rss['entries'] = list(filter(lambda e: e.rank > 0, rss.entries))

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
    p.add_argument('--sort', action='store_true',
                   help='Sort the entries instead of filtering them')
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
    rss = filter_feed(rss, config, args)
    xml = render_feed(rss, template=args.template)
    write_feed(xml, args.output)
