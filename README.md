
# arXiv RSS filter

*Filter arXiv RSS feed by keywords and authors.*


# Installation

1. Clone the current repository to an HTTP server with Python 3, [feedparser],
[Jinja2], and [PyYAML] installed (we assume `/srv/http/arxiv_rss_filter` in the
following instructions).

2. Create a cron job to run the script once a day (arXiv feeds are updated daily):

~~~crontab
12 4 * * * /srv/http/arxiv_rss_filter/arxiv_rss_filter.py
~~~

3. Optionally, protect every file except `arxiv_filtered.xml`. Eg with Apache:

~~~apache
<Directory "/srv/http/arxiv_rss_filter" >
    <Files "arxiv_filtered.xml" >
        Require all granted
    </Files>
    Require all denied
</Directory>
~~~

[feedparser]: https://pypi.org/project/feedparser/
[Jinja2]: https://pypi.org/project/Jinja2/
[PyYAML]: https://pypi.org/project/PyYAML/

4. Add `https://your_server.example/arxiv_rss_filter/arxiv_filtered.xml` to
   your feed reader.


# Configuration

The script’s configuration is stored in `config.yml`, and contains the
following entries:

- `source`: link to an arXiv RSS feed
  (eg. <http://export.arxiv.org/rss/astro-ph.SR>),
- `authors_include`: list of authors,
- `keywords_include`: list of keywords.

The script keeps an arXiv entry if at least one included author is in its
author list, or if one included keyword is in the title or in the abstract.
