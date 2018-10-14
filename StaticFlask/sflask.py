"""This module defines the Static Flask Blueprint.

StaticFlask is a subclass of flask.Blueprint. The subclass has some additional
funcitonality for configuring the static flask app. On registration, it
initialises a FlatPages instance, a custom static url, and creates a number of
routes for the Staticflask site.

"""

from os.path import isfile, join

from flask import Blueprint, send_from_directory, redirect, render_template, url_for
from flask_flatpages import Page, pygments_style_defs
from six import iteritems, PY3
from werkzeug.utils import cached_property

import yaml

from .category import Category
from .categorized_pages import CategorizedPages

class StaticFlask(Blueprint):
    # Static Flask app
    # Subclass blueprint
    # Register routes etc
    # App config from file, or else expect it to be in the app
    # Overload 'register', enforce default required config in the app, then call super
    # 'Entries' are the pages
    # 'Categories' are category objects
    #  Indexed with path
    # 'Render Entry' and 'Render Category' functions
    # Accesses category template or page template, and fills path with template dir from config
    # Also handles checking clashing names (reserve names feature?)
    # Register freezer generators too

    default_config = (
        ('FLATPAGES_MARKDOWN_EXTENSIONS',
         ['codehilite', 'toc', 'mdx_math', 'mdx_partial_gfm']),
        ('FLATPAGES_CASE_INSENSITIVE', True),
        ('FLATPAGES_INSTANCE_FOLDER', False),
        ('PAGINATE_STEP', 10)
    )
    debug_config = ()

    def __init__(self, **kwargs):
        """Initialise the Blueprint. Takes the same arguments as the 
        Flask Blueprint class, plus one additional parameter."""
        self.cfg_path = kwargs.pop('config_file', 'settings.yml')
        self.config = {}
        self.blueprint_root = False
        self.entries = CategorizedPages()
        self.reserved_paths = ['/cdn', '/media']
        self.app = None
        if 'root_path' in kwargs:
            self.blueprint_root = True
        if 'static_folder' not in kwargs:
            template_folder = kwargs.get('template_folder', 'templates')
            kwargs['static_folder'] = join(template_folder, 'static')
        if PY3:
            super().__init__('static_flask', 'StaticFlask', **kwargs)
        else:
            super(StaticFlask, self).__init__('static_flask', 'StaticFlask', **kwargs)

    @property
    def root(self):
        if self.blueprint_root:
            file_root = self.root_path
        else:
            if self.app.instance_relative_config:
                file_root = self.app.instance_path
            else:
                file_root = self.app.root_path
        return file_root
    
    def load_config(self, app, force_reload=False):
        """Load the StaticFlask config and apply the configuration to the
        flask.Flask application."""
        self.app = app
        if not force_reload and self.config:
            return
        file_path = join(self.root, self.cfg_path)
        if isfile(file_path):
            with open(file_path, 'r') as cfg_file:
                cfg = yaml.load(cfg_file)
            app_config = cfg.pop('flask_config', {})
            template_config = cfg.pop('template_config', {})
            for key, val in iteritems(app_config): #TODO: Validation? Required params?
                self.config[key.upper()] = val
            for key, val in iteritems(template_config):
                self.config['SFLASK_TEMPLATE_{}'.format(key.upper())] = val
        else:
            if self.cfg_path != 'settings.yml':
                raise FileNotFoundError(
                    'StaticFlask was not able to locate the specified config '
                    'file. The path given was:\n {} \n Which I looked for at'
                    ' the absolute path:\n {}'.format(self.cfg_path, file_path)
                )
        if app.debug:
            for key, val in self.debug_config:
                self.config.setdefault(key, val)
        for key, val in self.default_config:
            self.config.setdefault(key, val)#TODO: Default template config?
        app.config.from_mapping(self.config)

    def load_entries(self):
        if self.app is None:
            raise AttributeError(
                'Static Flask needs to be configured before we initialize '
                'extensions and load the content. Please call '
                'StaticFlask.load_config.'
            )
        self.entries.init_app(self.app)

    def register(self, app, *args, **kwargs):
        force_config_reload = kwargs.pop('force_config_reload', False)
        self.load_config(app, force_reload=force_config_reload)
        self.load_entries()
        self.setup_routes()
        if PY3:
            super().register(self, app, *args, **kwargs)
        else:
            super(StaticFlask, self).register(self, app, *args, **kwargs)

    def serve_page_media(self, filename):
        return send_from_directory(
            join((self.root, 'media')), filename
        )

    def render_path(self, path):
        entry = self.entries.get(path)
        if isinstance(entry, Page):
            post_type = entry.meta.get('post_type', '')
            if post_type:
                post_template = '{}_page.html'.format(post_type)
            else:
                post_template = 'page.html'
            return render_template(
                post_template,
                page=entry,
                template_params=self.app.config.get_namespace('SFLASK_TEMPLATE')
            )
        included_posts = entry.included_posts(self.entries)
        included_categories = entry.included_categories(self.entries)
        parents = entry.get_parents(self.entries)
        template = entry['template']
        template_data = {
            'category' : entry,
            'sub_categories' : included_categories,
            'parents': parents,
            'template_params': self.app.config.get_namespace('SFLASK_TEMPLATE')
        }
        if entry['paginate']:
            included_posts = included_posts[:self.config['PAGINATE_STEP']]
            template_data['nextpage'] = 2
        template_data['posts'] = included_posts
        return render_template(template, **template_data)

    def render_paginated(self, path, page):
        entry = self.entries.get(path)
        if isinstance(entry, Page):
            redirect(url_for('static_flask.path', path=entry.path))
        if page < 1 or not entry['paginate']:
            redirect(url_for('static_flask.path', path=entry.path))
        included_categories = entry.included_categories(self.entries)
        parents = entry.get_parents(self.entries)
        post_slice_lower = (page-1)*self.app.config['PAGINATE_STEP']
        post_slice_upper = (page-1)*self.app.config['PAGINATE_STEP']
        included_posts = entry.included_posts(self.entries)
        if len(included_posts) < post_slice_lower:
            top_page = len(included_posts)//self.app.config['PAGINATE_STEP']
            redirect(url_for('static_flask.paginate', path=entry.path,
                             page=top_page))
        included_posts = included_posts[post_slice_lower:post_slice_upper]
        return render_template(
            entry['template'],
            category=entry,
            posts=included_posts,
            sub_categories=included_categories,
            parents=parents
        )

    @staticmethod
    def pygments_css():
        """Serve the Pygments CSS file for codehilite."""
        return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

    def setup_routes(self):
        """Walk through the entries in the initialized FlatPages instance
        and create routes for them. Fails in the FlatPages instance has not been"""
        if not hasattr(self.entries, 'app'):
            raise ValueError(
                'The FlatPages instance at `StaticFlask.entries` must be '
                'initialised with the application before the Blueprint creates '
                'routes.'
                )
        self.add_url_rule('/<path:path>', 'path', self.render_path)
        self.add_url_rule('/<path:path>/<int:page>', 'paginated', self.render_paginated)
        self.add_url_rule('/media/<path:filename>', 'media', self.serve_page_media)
        self.add_url_rule('/pygments.css', 'pygments_css', self.pygments_css)
