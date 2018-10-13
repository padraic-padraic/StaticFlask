from flask_flatpages import FlatPages
from six import iterkeys
from werkzeug.utils import cached_property

from .category import Category

class CategorizedPages(FlatPages):

    def __init__(self, app=None, name=None):
        FlatPages.__init__(self, app, name)

    def reload(self):
        if '_pages' in self.__dict__:
            del self.__dict__['_pages']
        if '_categories' in self.__dict__:
            del self.__dict__['_categories']

    def get(self, path, default=None):
        categories = self.categories
        pages = self.pages
        if path == '/':
            return categories['']
        if path in pages:
            return pages[path]
        if path in categories:
            return categories[path]
        return default

    @cached_property
    def _categories(self):
        paths = set(path.rpartition('/')[0]
                    for path in iterkeys(self.pages))
        categories = {path: Category(self.root, path) for path in paths}
        return categories

    #TODO: Think about pagination masking pages?

    @property
    def pages(self):
        return self._pages

    @property
    def categories(self):
        return self._categories

