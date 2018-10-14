import re

from flask_flatpages import FlatPages
from six import iterkeys, itervalues, PY3
from werkzeug.utils import cached_property

from .category import Category

NUMERIC_REGEXP = re.compile(r'\d+')

class CategorizedPages(FlatPages):

    def __init__(self, app=None, name=None):
        FlatPages.__init__(self, app, name)

    def reload(self):
        if '_pages' in self.__dict__:
            del self.__dict__['_pages']
        if '_categories' in self.__dict__:
            del self.__dict__['_categories']

    def get(self, path, default=None):
        categories = self._categories
        pages = self._pages
        if path == '/':
            return categories['']
        if path in pages:
            return pages[path]
        if path in categories:
            return categories[path]
        return default

    def __iter__(self):
        paths = set((path for path in iterkeys(self._pages)))
        paths.union(set((path for path in iterkeys(self._categories))))
        for path in paths:
            yield self.get(path)

    def iter_pages(self):
        return itervalues(self._pages)

    def iter_categories(self):
        return itervalues(self._categories)

    @cached_property
    def _pages(self):
        if PY3:
            pages = super()._pages
        else:
            pages = super(CategorizedPages, self)._pages
        self._check_path_clashes(pages)
        return pages

    @cached_property
    def _categories(self):
        paths = set(path.rpartition('/')[0]
                    for path in iterkeys(self._pages))
        categories = {path: Category(self.root, path) for path in paths}
        self._check_path_clashes(categories)
        return categories

    def _check_path_clashes(self, collection):
        """Loops over paths, making sure none of them clash with StaticFlasks's
        pagination and would thus be hidden."""
        if any(NUMERIC_REGEXP.search(path) for path in iterkeys(collection)):
            raise ValueError(
                'StaticFlask reserves numeric names for pagination. No Category '
                'or Page my have a purely numeric name.'
            )
