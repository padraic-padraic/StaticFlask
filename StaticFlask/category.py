"""Defines the 'Category' class, with represents a category of posts."""

from os.path import isfile, join, split
import re

from flask_flatpages import Page
from six import iteritems, iterkeys, PY3
from werkzeug.utils import cached_property

import yaml

def cached_category_item(func):
    """Wraps a Category method, caching the result for quick reuse. """
    def cache_wrapper(self, *args, **kwargs):
        name = func.__name__
        force_reload = kwargs.pop('force_reload', False)
        if force_reload:
            try:
                del self._cache[name]
            except KeyError:
                pass
        if name in self._cache:
            return self._cache[name]
        try:
            pages_instance = args[0]
        except IndexError:
            raise AttributeError(
                'No cached {} were found. To load them, '
                'the CategorizedPages instance must be passed as a positional '
                'argument.'.format(name.split('_')[1])
            )
        res = func(self, pages_instance, **kwargs)
        self._cache[name] = res
        return res
    return cache_wrapper

class Category():
    
    default_config = (
        ('display_type', 'category'),
        ('subcategory_depth', 1),
        ('exclude_from', ''),
        ('post_sort_key',''),
        ('post_sort_reverse',False)
    )

    display_defaults = {
        'index': {
            'template': 'index.html',
            'paginate': True,
        },
        'category': {
            'template': 'category.html',
            'paginate': False
        },
        'custom': {
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
        self._cache = {}

    def __repr__(self):
        return '<Category {path}'.format(path=self.path)

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
                if isinstance(exclude_from, list):
                    config['exclude_from'] = [re.compile(regex)
                                              for regex in exclude_from]
                else:
                    config['exclude_from'] = [re.compile(exclude_from)]
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
        parent = self.path.rpartition('/', )[0]
        while parent:
            config['parents'].append(parent)
            parent = parent.rpartition('/')[0]
        else:
            config['parents'].append('')
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
        if self['exclude_from']:
            if any(regex.search(entry.path) for regex in self['exclude_from']):
                return False
        if depth < 0:
            return self.path in entry.path and self.path != entry.path
        if isinstance(entry, Page):
            depth += 1
        relative_path = entry.path.replace(self.path, '')
        return (relative_path and relative_path.count('/') == depth and 
            self.path in entry.path)
    
    def _included_entries(self, collection):
        entries = []
        if self['subcategory_depth'] == -1:
            entries = [entry for entry in collection()
                       if self.sub_entry_key(entry, -1)]
        else:
            for depth in range(self['subcategory_depth']+1):
                entries += [entry for entry in collection()
                            if self.sub_entry_key(entry, depth)]
        return entries

    @cached_category_item
    def included_posts(self, pages_instance):
        """Fetch the pages to be included with this category.
        We cache the result"""
        pages = self._included_entries(pages_instance.iter_pages)
        if self['post_sort_key']:
            post_key = self['post_sort_key']
            post_reverse = self['post_sort_reverse']
            pages.sort(key=lambda x: x.meta.get(post_key), reverse=post_reverse)
        return pages

    @cached_category_item
    def included_categories(self, pages_instance):
        categories = self._included_entries(pages_instance.iter_categories)
        return categories

    @cached_category_item
    def get_parents(self, pages_instance):
        parents = [pages_instance.get(parent)
                   for parent in self.config['parents']]
        return parents

    def reload(self):
        keys = list(iterkeys(self._cache))
        for key in keys:
            del self._cache[key]
