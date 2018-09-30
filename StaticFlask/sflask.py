"""This module defines the Static Flask application.

On initialisation, this class creates a Flask app instance, loads the
configuration, attaches the FrozenFlask and Flask-Flatpages extensions, and the
walks the 'pages' directory for site structure.

"""

import os

from flask import Flask, Blueprint
from flask_flatpages import FlatPages
from yaml import load

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
    default_app_config = (
        ('flatpages_markdown_extensions', ['codehilite', 'mdx_math',
                                           'mdx_partial_gfm', 'toc']),
    )
    
    required_fields = ['app_root', 'instance_path']

    def __init__(self, *args, **kwargs):
        if not any(key in kwargs for key in self.required_fields):
            raise KeyError('Could not find a required option '
                           'when initialising the blueprint. The app must '
                           'be initialized with either the application root '
                           'or an instance folder path.')
        self._instance_folder = kwargs.pop('instance_path', None)
        self._app_root = kwargs.pop('app_root', None)
        if 'root_path' in kwargs or 'static_folder' in kwargs:
            self._copy_core_files(kwargs)
        self.entries = FlatPages()
        super().__init__(self, *args, **kwargs)
        self._load_config()

    def _copy_core_files(self, kwargs):
        #For each, check if it differs, check if file exists, if not copy from
        # package, and issue an info/warning
        pass
        

    def _load_config(self):
        if self.instance_folder is not None:
            cfg_path = os.path.join(self._instance_folder, 'settings.yml')
        else:
            cfg_path = os.path.join(self._app_root, 'settings.yml')
        loaded_config = {}
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as cfg_file:
                loaded_config = load(cfg_file)
        self.app_config = loaded_config.get('app_config', {})
        self.template_config = loaded_config.get('template_config', {})
        for key, value in self.default_app_config:
            self.app_config.set_default(key, value)
        #TODO: How to handle a flatpages name....? 
        #TODO: Case sensitivity in config 🙄

    def register(self, app, *args, **kwargs):
        for key, val in self.app_config:
            app.config.set_default(key.upper(), val)
        self.entries.init_app(app)
        # Category Walker
        super().register(self, app, *args, **kwargs)

    def setup_freezer(self, freezer):
        #Attach a bunch of generators to the freezer
        pass
