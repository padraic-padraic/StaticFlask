"""Tests for the StaticFlask.Category class."""

import re
from os.path import join

import pytest
import yaml
from six import iteritems
from StaticFlask import Category

def test_default_conf(pages_root):
    rel_path = 'root_included/default_config'
    cat = Category(pages_root, 'root_included/default_config')
    assert cat.path == rel_path
    assert cat._cfg_file == 'settings.yml'
    assert cat._file_path == join(pages_root, 
                                  'root_included/default_config/settings.yml')
    assert cat._cache == {}
    conf = cat.config
    print(conf)
    assert conf == {
        'title': 'Default Config',
        'parents' : ['root_included', ''],
        'display_type': 'category',
        'subcategory_depth' : 1,
        'paginate': False,
        'exclude_from': '',
        'template': 'category.html',
        'post_sort_key': '',
        'post_sort_reverse': False
    }

def test_name():
    mixed_name = 'a-Long_cOmplex-name'
    assert Category._format_category_name(mixed_name) == 'A Long Complex Name'

def test_cache_and_get(pages_root):
    cat = Category(pages_root, 'root_included/default_config')
    assert 'config' not in cat.__dict__
    title = cat['title']
    assert 'config' in cat.__dict__

def test_file_finding(pages_root):
    with open(join(pages_root, 'settings.yml'), 'r') as _f:
        expected = yaml.load(_f)
    expected['exclude_from'] = [re.compile(expected['exclude_from'])]
    cat = Category(pages_root, '/')
    conf = cat.config
    for key, val in iteritems(expected):
        assert conf[key] == val
    cat = Category(pages_root, '/', 'conf.yml')
    with pytest.raises(FileNotFoundError):
        conf = cat.config

def test_type_validation(tmpdir):
    invalid = {'subcategory_depth', '1'}
    with open(tmpdir.join('settings.yml'), 'w') as _f:
        _f.write(yaml.dump(invalid))
    cat = Category(tmpdir, '')
    with pytest.raises(TypeError):
        conf = cat.config

def test_value_validation(tmpdir):
    invalid = {'display_type': 'categry'} #Typo!
    with open(tmpdir.join('settings.yml'), 'w') as _f:
        _f.write(yaml.dump(invalid))
    cat = Category(tmpdir, '')
    with pytest.raises(ValueError):
        conf = cat.config

def test_get_parents(local_catpages):
    cat = local_catpages.get('root_excluded/depth_1/depth_2/depth_3')
    parents = cat.get_parents(local_catpages)
    for parent in parents:
        assert isinstance(parent, Category)
        assert parent.path in cat['parents']

def test_cache_decorator(local_catpages):
    cat = local_catpages.get('root_excluded/depth_1/depth_2/depth_3')
    parents = cat.get_parents(local_catpages)
    assert 'get_parents' in cat._cache
    with pytest.raises(AttributeError):
        parents = cat.get_parents(force_reload=True)
    parents_copy = cat.get_parents(local_catpages, force_reload=True)

def test_included_pages_depth(local_catpages):
    cat = local_catpages.get('root_excluded')
    pages = cat.included_posts(local_catpages)
    expected = [
        'root_excluded/foo0',
        'root_excluded/depth_1/foo',
        'root_excluded/depth_1/depth_2/foo2',
        'root_excluded/depth_1/depth_2/depth_3/foo3'        
    ]
    for p in pages:
        assert p.path in expected
    for depth in range(4):
        cat.config['subcategory_depth'] = depth
        print(depth, cat['subcategory_depth'])
        pages = cat.included_posts(local_catpages, force_reload=True)
        print(pages)
        for p in pages:
            assert p.path in expected[:depth+1]

def test_exclude_from(local_catpages):
    cat = local_catpages.get('')
    pages = cat.included_posts(local_catpages)
    assert all('root_excluded' not in page.path for page in pages)
    cat.config['exclude_from'] += [re.compile('root_included')]
    pages = cat.included_posts(local_catpages, force_reload=True)
    assert len(pages) == 1

def test_sub_categories(local_catpages):
    cat = local_catpages.get('')
    sub_categories = cat.included_categories(local_catpages)
    expected = [
        'root_included',
        'root_included/custom_display',
        'root_included/default_config',
        'root_included/lots_of_pages'
    ]
    assert all(sub_cat.path in expected for sub_cat in sub_categories)
