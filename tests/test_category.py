"""Tests for the StaticFlask.Category class."""

import pytest
import re
import yaml

from os.path import join
from six import iteritems
from StaticFlask import Category

@pytest.fixture(scope="session")
def pages_root(test_dir):
    return join(test_dir, 'pages')

def test_default_conf(pages_root):
    rel_path = '/root_included/default_config'
    cat = Category(pages_root, '/root_included/default_config')
    assert cat.path == rel_path
    assert cat._cfg_file == 'settings.yml'
    assert cat._file_path == join(pages_root, 
                                  'root_included/default_config/settings.yml')
    conf = cat.config
    print(conf)
    assert conf == {
        'title': 'Default Config',
        'parents' : ['/root_included'],
        'display_type': 'category',
        'subcategory_depth' : 1,
        'paginate': False,
        'exclude_from': '',
        'template': 'category.html'
    }

def test_name():
    mixed_name = 'a-Long_cOmplex-name'
    assert Category._format_category_name(mixed_name) == 'A Long Complex Name'

def test_cache_and_get(pages_root):
    cat = Category(pages_root, '/root_included/default_config')
    assert 'config' not in cat.__dict__
    title = cat['title']
    assert 'config' in cat.__dict__

def test_file_finding(pages_root):
    with open(join(pages_root, 'settings.yml'), 'r') as _f:
        expected = yaml.load(_f)
    expected['exclude_from'] = re.compile(expected['exclude_from'])
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
