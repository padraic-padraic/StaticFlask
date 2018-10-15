import os
import shutil

import pytest
from flask import Flask
from StaticFlask import CategorizedPages

@pytest.fixture(scope="session")
def test_dir():
	return os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope="function")
def local_catpages():
	app = Flask(__name__)
	app.config['FLATPAGES_ROOT'] = './pages'
	pages = CategorizedPages(app)
	return pages

@pytest.fixture(scope="function")
def tmp_pages(tmpdir_factory):
	tmp = tmpdir_factory.mktemp("pages")
	shutil.copy("./pages", tmp)
	app = Flask(__name__)
	app.config['FLATPAGES_ROOT'] = tmp
	pages = CategorizedPages(app)
	return pages
