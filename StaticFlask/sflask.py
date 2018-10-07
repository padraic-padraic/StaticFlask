"""This module defines the Static Flask Blueprint.

StaticFlask is a subclass of flask.Blueprint. The subclass has some additional
funcitonality for configuring the static flask app. On registration, it
initialises a FlatPages instance, a custom static url, and creates a number of
routes for the Staticflask site.

"""

import os

from flask import Blueprint, send_from_directory, render_template
from flask_flatpages import FlatPages, pygments_style_defs
from os.path import isfile, join
from six import PY3

import yaml

# from .category import Category

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

        #TODO: How to handle a flatpages name....? 
        #TODO: Case sensitivity in config 🙄

    default_config = (
        ('FLATPAGES_MARKDOWN_EXTENSIONS',
         ['codehilite', 'toc', 'mdx_math', 'mdx_partial_gfm']),
        ('FLATPAGES_CASE_INSENSITIVE', True),
        ('FLATPAGES_INSTANCE_FOLDER', False)
    )
    debug_config = ()

    def __init__(self, *args, **kwargs):
        """Initialise the Blueprint. Takes the same arguments as the 
        Flask Blueprint class, plus one additional parameter."""
        self.cfg_path = kwargs.pop('sf_cfg', 'settings.yml')
        self.config = {}
        self.blueprint_root = False
        self.entries = FlatPages()
        self.reserved_paths = ['/cdn', '/media']
        if 'root_path' in kwargs:
            self.blueprint_root = True
        if PY3:
            super().__init__(*args, **kwargs)
        else:
            super(StaticFlask, self).__init__(*args, **kwargs)

    def _load_config(self, app, force_reload=False):
        """Load the StaticFlask config and apply the configuration to the
        flask.Flask application."""
        if not force_reload and self.config:
            return
        if self.blueprint_root:
            file_root = os.path.join(self.root_path, self.cfg_path)
        else:
            if app.instance_relative_config:
                file_root = app.instance_path
            else:
                file_root = app.root_path
        file_path = join(file_root, self.cfg_path)
        if isfile(file_path):
            with open(join(file_root, self.cfg_path), 'r') as cfg_file:
                cfg = yaml.load(cfg_file)
            app_config = cfg.pop('flask_config', {})
            template_config = cfg.pop('template_config', {})
            for key, val in app_config: #TODO: Validation? Required params?
                self.config[key.upper()] = val
            for key, val in template_config:
                self.config['SFLASK_TEMPLATE_{}'.format(key)] = val
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

    def init_app(self, app):
        self.entries.init_app(app)
        self.app = app

    def register(self, app, *args, **kwargs):
        force_config_reload = kwargs.pop('force_config_reload', False)
        self._load_config(app, force_reload=force_config_reload)
        self.init_app(app)
        self.setup_routes()
        # Category Walker
        super().register(self, app, *args, **kwargs)

    def serve_media(self, filename):
        return send_from_directory(
            '/'.join((self.app.config['FLATPAGES_ROOT'], 'media')), filename
        )

    def resolve_and_render_path(self, path):
        #Temporarily, this just uses "get or 404"
        page = self.entries.get_or_404(path)
        return render_template(
            'page.html',
            page=page,
            template_params=self.app.config.get_namespace('SFLASK_TEMPLATE')
        )

    def pygments_css(self):
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
        self.add_url_rule('/<path:path>', self.resolve_and_render_path)
        self.add_url_rule('/cdn/<path:filename>', self.serve_media)
        self.add_url_rule('/pygments.css', self.pygments_css)

    def setup_freezer(self, freezer):
        #Attach a bunch of generators to the freezer
        pass
