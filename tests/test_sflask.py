"""Tests for the StaticFlask.StaticFlask Blueprint"""

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
                                            static_folder='templates/static')
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
    assert len(sflask.deferred_functions) == 4
    assert sflask.has_static_folder

def test_registraiton():
    sflask = StaticFlask()
    app = Flask(__name__)
    app.register_blueprint(sflask)
    assert sflask.app is not None
    expected_endpoints = (
        'static',
        'static_flask.static',
        'static_flask.path',
        'static_flask.paginated',
        'static_flask.media',
        'static_flask.pygments_css'
    )
    for endpoint in iterkeys(app.view_functions):
        assert endpoint in expected_endpoints