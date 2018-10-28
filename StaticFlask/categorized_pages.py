import os
import re

from flask import abort
from flask_flatpages import FlatPages
from flask_flatpages.compat import string_types
from six import iterkeys, itervalues
from werkzeug.utils import cached_property

from .category import Category

NUMERIC_REGEXP = re.compile(r'/\d+')

class CategorizedPages(FlatPages):

    extra_default_config = (
        ('markdown_extensions', ['codehilite', 'toc', 'mdx_math']),
        ('case_insensitive', True),
        ('instance_folder', False),
        ('extension', '.md')
    )

    def __init__(self, app=None, name=None):
        super(CategorizedPages, self).__init__(None, name)
        if app:
            self.init_app(app)

    def reload(self):
        if '_pages' in self.__dict__:
            del self.__dict__['_pages']
        if '_categories' in self.__dict__:
            del self.__dict__['_categories']

    def get(self, path, default=None):
        categories = self._categories
        pages = self._pages
        if path in pages:
            return pages[path]
        if path in categories:
            return categories[path]
        return default

    def get_or_404(self, path):
        categories = self._categories
        pages = self._pages
        if path in pages:
            return pages[path]
        if path in categories:
            return categories[path]
        abort(404)

    def init_app(self, app):
        for key, value in self.extra_default_config:
            config_key = '_'.join((self.config_prefix, key.upper()))
            app.config.setdefault(config_key, value)
        super(CategorizedPages, self).init_app(app)

    def __iter__(self):
        paths = set((path for path in iterkeys(self._pages)))
        paths |= set((path for path in iterkeys(self._categories)))
        for path in paths:
            yield self.get(path)

    def iter_pages(self):
        return itervalues(self._pages)

    def iter_categories(self):
        return itervalues(self._categories)

    @cached_property
    def _pages(self):
        pages = super(CategorizedPages, self)._pages
        self._check_path_clashes(pages)
        return pages

    @cached_property
    def _categories(self):
        extension = self.config('extension')

        # Support for multiple extensions
        if isinstance(extension, string_types):
            if ',' in extension:
                extension = tuple(extension.split(','))
            else:
                extension = (extension, )
        elif isinstance(extension, (list, set)):
            extension = tuple(extension)
        extensions = extension + ('.yml',)
        def category_walker():
            for root_dir, dirs, files in os.walk(self.root):
                dirs = [_dir for _dir in dirs if not _dir.startswith('.')]
                if any(os.path.splitext(_file)[1] in extensions
                       for _file in files):
                    path = root_dir.replace(self.root, '').lstrip(os.sep)
                    yield path
        categories = {
            path: Category(self.root, path) for path in category_walker()
        }
        self._check_path_clashes(categories)
        return categories

    @staticmethod
    def _check_path_clashes(collection):
        """Loops over paths, making sure none of them clash with StaticFlasks's
        pagination and would thus be hidden."""
        if any(NUMERIC_REGEXP.search(path) for path in iterkeys(collection)):
            raise ValueError(
                'StaticFlask reserves numeric names for pagination. No Category '
                'or Page my have a purely numeric name.'
            )
