"""Tests for the StaticFlask.StaticFlask Blueprint"""

import shutil
from os.path import join

import pytest

from flask import Flask
from six import iterkeys
from StaticFlask import StaticFlask

def test_init(mocker):
    mock_super_init = mocker.patch('flask.Blueprint.__init__')
    mock_catpages = mocker.patch('StaticFlask.CategorizedPages.__init__',
                                 return_value=None)
    sflask = StaticFlask()
    assert not sflask.blueprint_root
    mock_catpages.assert_called_once_with()
    mock_super_init.assert_called_once_with('static_flask', 'StaticFlask',
                                            static_folder='templates/static',
                                            template_folder='templates')
    mock_super_init.reset_mock()
    sflask = StaticFlask(template_folder='my_templates')
    mock_super_init.assert_called_once_with('static_flask', 'StaticFlask',
                                            static_folder='my_templates/static',
                                            template_folder='my_templates')

def test_initialize_and_config():
    app = Flask(__name__)
    sflask = StaticFlask(app=app)
    assert sflask.entries.app is not None
    assert app.config['PAGINATE_STEP'] == 5
    template_conf = app.config.get_namespace('SFLASK_TEMPLATE_')
    assert template_conf == {
        'title': 'A Website',
        'foo': 'Bar'
    }

def test_route_rules():
    sflask = StaticFlask()
    sflask.setup_routes()
    assert len(sflask.deferred_functions) == 6
    assert sflask.has_static_folder

def test_registraiton():
    sflask = StaticFlask()
    app = Flask(__name__)
    app.register_blueprint(sflask)
    assert sflask.app is not None
    expected_endpoints = (
        'static',
        'static_flask.home',
        'static_flask.home_paginated',
        'static_flask.static',
        'static_flask.path',
        'static_flask.paginated',
        'static_flask.media',
        'static_flask.pygments_css'
    )
    for endpoint in iterkeys(app.view_functions):
        assert endpoint in expected_endpoints

def test_custom_blueprint_name():
    sflask = StaticFlask(name='sflask')
    app = Flask(__name__)
    app.register_blueprint(sflask)
    assert 'sflask.path' in app.view_functions

def test_root(tmpdir, test_dir):
    app = Flask(__name__)
    sflask = StaticFlask()
    sflask.app = app
    assert sflask.root == app.root_path
    app = Flask(__name__, instance_relative_config=True)
    sflask.app = app
    assert sflask.root == app.instance_path
    shutil.copyfile(
        join(test_dir, 'settings.yml'),
        tmpdir.join('settings.yml')
    )
    sflask = StaticFlask(root_path=tmpdir)
    assert sflask.root == tmpdir

def test_default_config(tmpdir, pages_root):
    shutil.copytree(pages_root, tmpdir.join("pages"))
    app = Flask(__name__, instance_relative_config=True, instance_path=tmpdir)
    app.config['FLATPAGES_ISNTANCE_FOLDER'] = True
    sflask = StaticFlask(app=app)
    assert app.config['PAGINATE_STEP'] == 10
    assert len(list(sflask.entries)) > 0
    with pytest.raises(FileNotFoundError):
        sflask = StaticFlask(app=app, cfg_filename='cfg.yml')
