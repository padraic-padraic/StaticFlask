"""Tests for the StaticFlask.CategorizedPages class."""

import pytest
from flask import Flask
from six import iterkeys, itervalues
from StaticFlask import CategorizedPages

@pytest.fixture(scope='session')
def expected_pages():
    return set((
        'about',
        'root_excluded/foo0',
        'root_excluded/depth_1/foo',
        'root_excluded/depth_1/depth_2/foo2',
        'root_excluded/depth_1/depth_2/depth_3/foo3',
        'root_included/draft',
        'root_included/custom_display/post_type',
        'root_included/default_config/bar',
        'root_included/lots_of_pages/page-1',
        'root_included/lots_of_pages/page-2',
        'root_included/lots_of_pages/page-3',
        'root_included/lots_of_pages/page-4',
        'root_included/lots_of_pages/page-5',
        'root_included/lots_of_pages/page-6',
        'root_included/lots_of_pages/page-7'
    ))

@pytest.fixture(scope='session')
def expected_categories():
    return set((
        '/',
        '/root_included',
        '/root_included/default_config',
        '/root_included/custom_display',
        '/root_included/lots_of_pages'
        '/root_excluded',
        '/root_excluded/depth_1',
        '/root_excluded/depth_1/depth_2',
        '/root_excluded/depth_1/depth_2/depth_3'
    ))

def test_init(mocker):
    catpages = CategorizedPages()
    assert catpages.name is None
    mock_super_init_app = mocker.patch('flask_flatpages.FlatPages.init_app')
    app = Flask(__name__)
    catpages = CategorizedPages(app)
    mock_super_init_app.assert_called_once_with(app)

def test_init_app(mocker):
    mock_super_init_app = mocker.patch('flask_flatpages.FlatPages.init_app')
    app = Flask(__name__)
    catpages = CategorizedPages()
    mock_super_init_app.assert_not_called()
    catpages.init_app(app)
    mock_super_init_app.assert_called_once_with(app)
    #Test config

def test_page_finding(local_catpages, expected_pages):
    pages = local_catpages._pages
    print(local_catpages.root)
    for page in itervalues(pages):
        print(page.path)
    assert set((page.path for page in itervalues(pages))) == expected_pages

def test_path_exclusion(tmp_pages):
    tmp_dir, tmp_catpages = tmp_pages()
    with open(tmp_dir.join('pages','42.md'), 'w') as _f:
        _f.write(
            """
            title: Test

            I should cause an error
            """
        )
    with pytest.raises(ValueError):
        pages = tmp_catpages._pages
