"""Tests for the StaticFlask.CategorizedPages class."""

import pytest
from flask import Flask
from flask_flatpages import Page
from six import iterkeys, itervalues
from StaticFlask import CategorizedPages, Category
from werkzeug.exceptions import NotFound

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
        '',
        'root_included',
        'root_included/default_config',
        'root_included/custom_display',
        'root_included/lots_of_pages',
        'root_excluded',
        'root_excluded/depth_1',
        'root_excluded/depth_1/depth_2',
        'root_excluded/depth_1/depth_2/depth_3'
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

def test_category_finding(local_catpages, expected_categories):
    categories = local_catpages._categories
    assert set(
        (category.path for category in itervalues(categories))
    ) == expected_categories

def test_iterators(local_catpages, expected_pages, expected_categories):
    assert set(
        (page.path for page in local_catpages.iter_pages())
    ) == expected_pages
    assert set(
        (category.path for category in local_catpages.iter_categories())
    ) == expected_categories
    all_items = set()
    all_items |= expected_pages
    all_items |= expected_categories
    assert set(
        (entry.path for entry in local_catpages)
    ).difference(all_items) == set()

def test_get(local_catpages):
    page = local_catpages.get('about')
    assert isinstance(page, Page)
    category = local_catpages.get('')
    assert isinstance(category, Category)
    default = local_catpages.get('nonexistant')
    assert default is None

def test_get_or_404(local_catpages):
    with pytest.raises(NotFound):
        local_catpages.get_or_404('nonexistant')

def test_reload(local_catpages):
    local_catpages.get('')
    assert '_categories' in local_catpages.__dict__
    assert '_pages' in local_catpages.__dict__
    local_catpages.reload()
    assert '_categories' not in local_catpages.__dict__
    assert '_pages' not in local_catpages.__dict__
