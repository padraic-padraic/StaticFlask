"""Defines the 'Category' class, with represents a category of posts."""

from os.path import isfile, join, split
import re

from six import iteritems
from werkzeug.utils import cached_property

import yaml

def cached_category_item(func):
    """Wraps a Category method, caching the result for quick reuse. """
    def cache_wrapper(self, *args, **kwargs):
        name = func.__name__
        force_reload = kwargs.pop('force_reload', False)
        if name in self.__dict__ and not force_reload:
            return self.__dict__[name]
        try:
            pages_instance = args[0]
        except IndexError:
            raise AttributeError(
                'No cached {} were found. To load them, '
                'the CategorizedPages instance must be passed as a positional '
                'argument.'.format(name.split('_'[1]))
            )
        res = func(self, pages_instance, **kwargs)
        self.__dict__[name] = res
        return res
    return cache_wrapper

class Category():
    
    default_config = (
        ('display_type', 'category'),
        ('subcategory_depth', 1),
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
        ('subcategory_depth', int),
        ('display_type', str),
        ('template', str),
        ('title', str)
    )

    def __init__(self, pages_root, relative_path, 
                 cfg_file='settings.yml'):
        self.path = relative_path
        self._cfg_file = cfg_file
        self._file_path = join(pages_root, relative_path.lstrip('/'), cfg_file)

    def _load_config(self):
        config = {}
        if not isfile(self._file_path):
            if self._cfg_file != 'settings.yml':
                raise FileNotFoundError(
                    'StaticFlask was not able to locate the specified config '
                    'file for the category. The path given was:\n {} \n '
                    'Which I looked for at the absolute path:\n'
                    ' {}'.format(self._cfg_file, self._file_path)
                )
        else:
            with open(self._file_path, 'r') as _f:
                loaded_cfg = yaml.load(_f)
            exclude_from = loaded_cfg.pop('exclude_from', '')
            if exclude_from:
                config['exclude_from'] = re.compile(exclude_from)
            for key, val in iteritems(loaded_cfg):
                config[key] = val
        for key, val in self.default_config:
            config.setdefault(key, val)
        template_defaults = self.display_defaults.get(config['display_type'],
                                                      {})
        for key, val in iteritems(template_defaults):
            config.setdefault(key, val)
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
        if not 'template' in config:
            raise ValueError(
                'No template specified for the Category. If using a '
                '"custom" category layout, you must also specify a '
                'template file.'
            )
        for key, val in iteritems(self.validation):
            if config[key] not in val:
                append_str = '\n'.join(v for v in val)
                raise ValueError(
                    'Setting {} should be one of:\n {}.'
                    'I found {}'.format(key, append_str, config[key])
                )
        for key, _type in self.type_validation:
            if not isinstance(config[key], _type):
                raise TypeError(
                    'Setting {} should be type {}, I found '
                    'type {}.'.format(key, _type, type(config[key]))
                )

    @cached_property
    def config(self):
        config = self._load_config()
        return config

    def __getitem__(self, name):
        return self.config[name]

    @staticmethod
    def _format_category_name(name):
        name = name.replace('-', ' ')
        name = name.replace('_', ' ')
        return name.title()

    def sub_entry_key(self, entry, depth):
        if self.config['exclude_from']:
            if self.config['exclude_from'].search(entry.path):
                return False
        if depth <= 0:
            return self.path in entry.path
        if entry.path.rsplit('/', maxsplit=depth) == self.path:
            return True
        return False

    def _included_entries(self, collection):
        entries = []
        for depth in range(self.config['subcategory_depth']+1):
            entries += [entry for entry in collection
                        if self.sub_entry_key(entry, depth)]
        return entries

    @cached_category_item
    def included_posts(self, pages_instance, sort_key=None):
        """Fetch the pages to be included with this category.
        We cache the result"""
        if sort_key is None:
            def published_key(page):
                return page.meta['published']
            sort_key = published_key
        pages = self._included_entries(pages_instance.iter_pages())
        pages = [page for page in pages if not page.meta.get('draft', False)]
        pages.sort(sort_key)
        return pages

    @cached_category_item
    def included_categories(self, pages_instance):
        categories = self._included_entries(pages_instance.iter_categories())
        return categories

    @cached_category_item
    def get_parents(self, pages_instance):
        parents = [pages_instance.get(parent)
                   for parent in self.config['parents']]
        return parents
