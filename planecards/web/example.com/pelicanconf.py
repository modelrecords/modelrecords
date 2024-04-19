# https://docs.getpelican.com/en/latest/settings.html
# example: https://docs.getpelican.com/en/latest/settings.html#example-settings

AUTHOR = 'planecards'
SITENAME = 'Plane cards'
SITESUBTITLE = "site subtitle"
SITEURL = 'https://example.com'
TIMEZONE = 'America/Regina'

THEME = 'themes/planecards'

PATH = 'content'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ('Pelican', 'https://getpelican.com/'),
    ('Python.org', 'https://www.python.org/'),
    ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
    ('You can modify those links in your config file', '#'),
)

# Social widget
SOCIAL = (
    ('You can add links in your config file', '#'),
    ('Another social link', '#'),
)

DEFAULT_PAGINATION = False

# https://docs.getpelican.com/en/latest/faq.html#is-pelican-only-suitable-for-blogs
TAGS_SAVE_AS = ''
TAG_SAVE_AS = ''

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
