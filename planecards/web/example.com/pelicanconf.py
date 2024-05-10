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

DISPLAY_PAGES_ON_MENU = False

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
# LINKS = (
#     ('You can modify those links in your config file', '#'),
# )

# Menu items
MENUITEMS = (
    # ('plane cards', 'planecards.html'),
    ('model cards', 'modelcards.html'),
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

# PLUGIN_PATHS = ['./plugins']
# PLUGINS = ['load_repository_yaml']

PLUGIN_PATHS = ['../../pelican_plugins']
PLUGINS = ['load_pkgs']

LOAD_CONTENT_CACHE = False
