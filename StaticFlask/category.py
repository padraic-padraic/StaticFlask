"""Defines the 'Category' class, with represents a category of posts."""

from os.path import isfile, join, split

from six import iteritems
from werkzeug.utils import cached_property

import yaml

# Category object
# Init from a dir path
# Load config, fetch all subcategories
# Todo: How to efficiently handle subposts? (If needed)
#   => Use the pages instance and store a set of paths?
#   => Use relative paths...?

class Category(object):
    
    default_config = (
        ('display_type', 'category'),
        ('subcategory-depth', '1'),
    )
    default_template = {
        'index': 'index.html',
        'category': 'category.html'
    }

    validation = {
        'display_type': ['index', 'category', 'custom']
    }
    type_validation = (
        ('subcategory-depth', int),
        ('display_type', str),
        ('template', str),
        ('title', str)
    )

    def __init__(self, pages_root, relative_path, 
                 cfg_file='settings.yml'):
        self.path = relative_path
        self._cfg_file = cfg_file
        self._dir_path = join((pages_root, relative_path, cfg_file))

    def _load_config(self):
        config = {}
        if not isfile(self._dir_path):
            if self._cfg_file != 'settings.yml':
                raise FileNotFoundError(
                    'StaticFlask was not able to locate the specified config '
                    'file for the category. The path given was:\n {} \n '
                    'Which I looked for at the absolute path:\n'
                    ' {}'.format(self._cfg_file, self._dir_path)
                )
        else:
            with open(self._dir_path, 'r') as _f:
                cfg = yaml.load(_f)
            for key, val in iteritems(cfg):
                config[key] = val
        for key, val in self.default_config:
            config.setdefault(key, val)
        config.setdefault('template',
                          self.default_template.get(
                              config['display_type'], None)
                         )
        config.setdefault('title',
                          self._format_category_name(split(self.path)[1]))
        self._validate_config(config)
        config['parents'] = []
        parent = self.path.rsplit('/', maxsplit=1)[0]
        while parent:
            config['parents'].append(parent)
            parent = parent.rsplit('/', maxsplit=1)[0]
        return config

    def _validate_config(self, config):
        if not 'tempalte' in config:
            raise ValueError(
                'No template specified for the Category. If using a '
                '"custom" category layout, you must also specify a '
                'template file.'
            )
        for key, val in self.validation:
            if config[key] not in val:
                raise ValueError('')
        for key, val in self.type_validation:
            if not isinstance(config[key], val):
                raise TypeError('')

    @cached_property
    def config(self):
        config = self._load_config()
        return config

    def __get_item__(self, name):
        return self.config[name]

    @staticmethod
    def _format_category_name(name):
        name.replace('-', ' ')
        name.replace('_', ' ')
        return name.title()

    def sub_page_key(self, page, depth):
        if page.path.rsplit('/', maxsplit=depth) == self.path:
            return True
        return False

    def included_entries(self, *args, sort_key=None,
                         force_reload=False):
        """Fetch the pages to be included with this category.
        We cache the result"""
        if not force_reload:
            try:
                return self.__dict__['_included_entries']
            except KeyError:
                pass
        try:
            pages_instance = args[0]
        except IndexError:
            raise AttributeError(
                'No cached pages were found. To load the associated entries, '
                'the CategorizedPages instance must be passed as a positional '
                'argument.'
            )
        if sort_key is None:
            def published_key(page):
                return page.meta['published']
            sort_key = published_key
        pages = []
        for depth in range(self.config['subcategory-depth']+1):
            pages += [page for page in pages_instance
                      if self.sub_page_key(page, depth)]
        pages.sort(sort_key)
        self.__dict__['_included_entries'] = pages
        return pages
