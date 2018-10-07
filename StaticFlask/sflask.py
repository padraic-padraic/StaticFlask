"""This module defines the Static Flask Blueprint.

StaticFlask is a subclass of flask.Blueprint. The subclass has some additional
funcitonality for configuring the static flask app. On registration, it
initialises a FlatPages instance, a custom static url, and creates a number of
routes for the Staticflask site.

"""

import os

from flask import Blueprint
from flask_flatpages import FlatPages
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
        ('FLATPAGES_CASE_INSENSITIVE', True)
    )
    debug_config = ()

    def __init__(self, *args, **kwargs):
        """Initialise the Blueprint. Takes the same arguments as the 
        Flask Blueprint class, plus one additional parameter."""
        self.cfg_path = kwargs.pop('sf_cfg', 'settings.yml')
        self.config = {}
        self.blueprint_root = False
        self.entries = FlatPages()
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

    def register(self, app, *args, **kwargs):
        force_config_reload = kwargs.pop('force_config_reload', False)
        self._load_config(app, force_reload=force_config_reload)
        self.entries.init_app(app)
        # Entry walker
        # Category Walker
        super().register(self, app, *args, **kwargs)

    def setup_page_routes(self):
        """Walk through the entries in the initialized FlatPages instance
        and create routes for them. Fails in the FlatPages instance has not been"""
        pass

    def setup_freezer(self, freezer):
        #Attach a bunch of generators to the freezer
        pass
