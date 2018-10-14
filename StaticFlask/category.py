"""Defines the 'Category' class, with represents a category of posts."""

from os.path import isfile, join, split
import re

from six import iteritems
from werkzeug.utils import cached_property

import yaml

def cached_result(func):
    def cache_wrapper(self, *args, **kwargs):
        name = func.__name__
        force_reload = kwargs.get('force_reload', False)
        if name in self.__dict__ and not force_reload:
            return self.__dict__[name]
        res = func(self, *args, **kwargs)
        self.__dict__[name] = res
        return res
    return cache_wrapper

class Category(object):
    
    default_config = (
        ('display_type', 'category'),
        ('subcategory-depth', '1'),
        ('paginate', False),
        ('exclude_from', "")
    )

    display_defaults = {
        'index': {
            'template': 'index.html',
            'paginate': True,
        },
        'category': {
            'template': 'category.html',
            'paginate': False
        }
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
            exclude_from = cfg.pop('exclude_from', '')
            if exclude_from:
                self.config['exclude_from'] = re.compile(exclude_from)
            for key, val in iteritems(cfg):
                config[key] = val
        for key, val in self.default_config:
            config.setdefault(key, val)
        for key, val in self.display_defaults.get(self.config['display_type'],
                                                  {}):
            self.config.setdefault(key, val)
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

    def sub_entry_key(self, entry, depth):
        if self.config['exclude_from']:
            if self.config['exclude_from'].search(entry.path):
                return False
        if entry.path.rsplit('/', maxsplit=depth) == self.path:
            return True
        return False

    def _included_entries(self, collection):
        entries = []
        for depth in range(self.config['subcategory-depth']+1):
            entries += [entry for entry in collection
                      if self.sub_entry_key(entry, depth)]
        return entries

    @cached_result
    def included_posts(self, *args, sort_key=None,
                       force_reload=False):
        """Fetch the pages to be included with this category.
        We cache the result"""
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
        pages = self._included_entries(pages_instance.iter_pages())
        pages = [page for page in pages if not page.meta.get('draft', False)]
        pages.sort(sort_key)
        return pages

    @cached_result
    def included_categories(self, *args, force_reload=False):
        try:
            pages_instance = args[0]
        except IndexError:
            raise AttributeError(
                'No cached categories were found. To load the associated entries, '
                'the CategorizedPages instance must be passed as a positional '
                'argument.'
            )
        categories = self._included_entries(pages_instance.iter_categories())
        return categories

    @cached_result
    def get_parents(self, *args, force_reload=False):
        try:
            pages_instance = args[0]
        except IndexError:
            raise AttributeError(
                'No cached categories were found. To load the associated entries, '
                'the CategorizedPages instance must be passed as a positional '
                'argument.'
            )
        parents = [pages_instance.get(parent)
                   for parent in self.config['parents']]
        return parents
