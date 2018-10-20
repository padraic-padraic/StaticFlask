"""Test for the views in the StaticFlask app"""

import pytest

from contextlib import contextmanager
from flask import Flask, template_rendered, url_for
from flask_flatpages import Page
from StaticFlask import Category, StaticFlask
from werkzeug.exceptions import NotFound

@contextmanager #Signal snippet from 'Signals' in the flask documentation
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture(scope="module")
def registered_app():
    def get_app_and_blueprint():
        app = Flask(__name__)
        sflask = StaticFlask()
        sflask.initialize(app)
        app.register_blueprint(sflask)
        return app, sflask
    return get_app_and_blueprint

def test_media(registered_app):
    app, sflask = registered_app()
    with app.test_request_context():
        url = url_for('static_flask.media', filename='Foo_was_here.jpg')
        err_url = url_for('static_flask.media', filename='Foo_isnt_here.jpg')
    with app.test_client() as test_client:
        resp = test_client.get(url)
        assert resp.status_code == 200
        assert resp.mimetype == 'image/jpeg'
        resp = test_client.get(err_url)
        assert resp.status_code == 404

def test_entry_404(registered_app):
    app, sflask = registered_app()
    with app.test_client() as client:
        resp = client.get('/false')
        assert resp.status_code == 404

def test_page_path(registered_app):
    app, sflask = registered_app()
    template_params = app.config.get_namespace('SFLASK_TEMPLATE_')
    about_page = sflask.entries.get('about')
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/about')
        assert resp.status_code == 200
        template, context = rendered_template[0]
        assert template.name == 'page.html'
        assert context['category'] == sflask.entries.get('')
        assert context['page'] == about_page
        assert context.get('template_params', None) == template_params
    custom_page_type = sflask.entries.get(
        'root_included/custom_display/post_type'
    )
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/custom_display/post_type')
        assert resp.status_code == 200
        template, context = rendered_template[0]
        assert template.name == 'big_page.html'
        assert context['page'] == custom_page_type

def test_category_path(registered_app):
    app, sflask = registered_app()
    template_params = app.config.get_namespace('SFLASK_TEMPLATE_')
    entries = sflask.entries
    default = entries.get('root_included/default_config')
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/default_config')
        assert resp.status_code == 200
        template, context = rendered_template[0]
        assert template.name == 'category.html'
        assert context['category'] == default
        assert context['posts'] == default.included_posts(entries)
        assert context['sub_categories'] == default.included_categories(entries)
        assert context['parents'] == default.get_parents(entries)
        assert context['template_params'] == template_params
    index = entries.get('')
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/')
        assert resp.status_code == 200
        template, context = rendered_template[0]
        assert template.name == 'index.html'
        assert context['category'] == index
    paginated = entries.get('root_included/lots_of_pages')
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/lots_of_pages')
        template, context = rendered_template[0]
        assert resp.status_code == 200
        assert template.name == 'index.html'
        assert context['category'] == paginated
        assert len(context['posts']) == app.config['PAGINATE_STEP']
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/custom_display')
        template, context = rendered_template[0]
        assert template.name == 'custom_category.html'

def test_paginated_errors(registered_app):
    app, sflask = registered_app()
    with app.test_client() as client:
        resp = client.get('/about/1')
        assert resp.status_code == 302
        resp = client.get('/root_included/lots_of_pages/0')
        assert resp.status_code == 302
        resp = client.get('/root_included/default_config/1')
        assert resp.status_code == 302
        resp = client.get('/0')
        assert resp.status_code == 302
        resp = client.get('/root_included/lots_of_pages/3')
        assert resp.status_code == 302
        assert 'lots_of_pages/2' in resp.headers['location']
        resp = client.get('/4')
        assert resp.status_code == 302
        assert '/3' in resp.headers['location']

def test_pagination(registered_app):
    app, sflask = registered_app()
    lots_of_pages = sflask.entries.get('root_included/lots_of_pages')
    all_posts = lots_of_pages.included_posts(sflask.entries)
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/lots_of_pages/1')
        template, context = rendered_template[0]
        assert context['posts'] == all_posts[:5]
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/lots_of_pages/2')
        template, context = rendered_template[0]
        assert context['posts'] == all_posts[5:10]
    cat = sflask.entries.get('root_included/lots_of_pages')
    cat.config['post_sort_reverse'] = False
    all_posts = all_posts[::-1]
    cat.reload()
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/lots_of_pages/1')
        template, context = rendered_template[0]
        assert context['posts'] == all_posts[:5]
    with captured_templates(app) as rendered_template:
        resp = app.test_client().get('/root_included/lots_of_pages/2')
        template, context = rendered_template[0]
        assert context['posts'] == all_posts[5:10]

def test_freezer_generators(registered_app):
    app, sflask = registered_app()
    entry_urls = (
        '/root_included/lots_of_pages/page-4'
        '/root_included/lots_of_pages/page-6'
        '/root_excluded/depth_1/foo'
        '/root_included/default_config/bar'
        '/root_included/lots_of_pages/page-1'
        '/root_excluded/foo0'
        '/about'
        '/root_included/lots_of_pages/page-5'
        '/root_excluded/depth_1/depth_2/foo2'
        '/root_included/draft'
        '/root_included/lots_of_pages/page-3'
        '/root_included/lots_of_pages/page-7'
        '/root_excluded/depth_1/depth_2/depth_3/foo3'
        '/root_included/lots_of_pages/page-2'
        '/root_included/custom_display/post_type'
    )
    paginate_urls = (
        '/1'
        '/2'
        '/3'
        '/root_included/lots_of_pages/1'
        '/root_included/lots_of_pages/2'
    )
    media_urls = (
        '/media/Foo_was_here.jpg'
    )
    other_urls = (
        '/static/style.css'
        '/pygments.css'
        '/'
    )
    for url in sflask.yield_entries():
        assert url in entry_urls
    for url in sflask.yield_paginated_pages():
        assert url in paginate_urls
    for url in sflask.yield_media():
        assert url in media_urls
    all_urls = entry_urls + paginate_urls + media_urls + other_urls
    for url in sflask.freezer.all_urls():
        assert url in all_urls