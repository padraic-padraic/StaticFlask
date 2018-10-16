import os
import shutil

import pytest
from flask import Flask
from StaticFlask import CategorizedPages

@pytest.fixture(scope="session")
def test_dir():
    return os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope="session")
def pages_root(test_dir):
    return os.path.join(test_dir, 'pages')

@pytest.fixture(scope="function")
def local_catpages():
    app = Flask(__name__)
    app.config['FLATPAGES_ROOT'] = 'pages'
    pages = CategorizedPages(app)
    return pages

@pytest.fixture(scope="function")
def tmp_pages(tmpdir_factory, pages_root):
    def dir_and_pages():
        tmp = tmpdir_factory.mktemp("tmp")
        shutil.copytree(pages_root, tmp.join("pages"))
        app = Flask(__name__)
        app.config['FLATPAGES_ROOT'] = tmp
        pages = CategorizedPages(app)
        return tmp, pages
    return dir_and_pages
