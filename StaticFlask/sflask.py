"""This module defines the Static Flask Blueprint.

StaticFlask is a subclass of flask.Blueprint. The subclass has some additional
funcitonality for configuring the static flask app. On registration, it
initialises a FlatPages instance, a custom static url, and creates a number of
routes for the Staticflask site.

"""

from os import walk
from os.path import isfile, join

from flask import abort, Blueprint, redirect, render_template, send_from_directory, url_for
from flask_flatpages import Page, pygments_style_defs
from flask_frozen import Freezer
from six import iteritems

import yaml

from .categorized_pages import CategorizedPages

def get_n_pages(n_posts, paginate_step):
    top_page = n_posts//paginate_step
    if n_posts%paginate_step > 0:
        top_page += 1
    return top_page

class StaticFlask(Blueprint):

    default_config = (
        ('PAGINATE_STEP', 10),
    )
    debug_config = ()

    def __init__(self, **kwargs):
        """Initialise the Blueprint. Takes the same arguments as the 
        Flask Blueprint class, plus one additional parameter."""
        blueprint_name = kwargs.pop('name', 'static_flask')
        import_name = kwargs.pop('import_name', 'StaticFlask')
        self.blueprint_root = False
        self.entries = CategorizedPages()
        self.freezer = Freezer()
        self.reserved_paths = ['static','/media'] #TODO: Check for clashes?
        self.app = kwargs.pop('app', None)
        if self.app is not None:
            cfg_filename = kwargs.pop('cfg_filename', 'settings.yml')
            self.initialize(
                self.app,
                cfg_filename=cfg_filename
            )
        if 'root_path' in kwargs:
            self.blueprint_root = True
        template_folder = kwargs.get('template_folder')
        if template_folder is None:
            template_folder = 'templates'
            kwargs['template_folder'] = template_folder
        static_folder = kwargs.get('static_folder')
        if static_folder is None:
            kwargs['static_folder'] = join(template_folder, 'static')
        super(StaticFlask, self).__init__(blueprint_name, import_name,
                                          **kwargs)

    @property
    def root(self):
        if self.blueprint_root:
            file_root = self.root_path
        else:
            if self.app.config.root_path == self.app.instance_path:
                file_root = self.app.instance_path
            else:
                file_root = self.app.root_path
        return file_root

    def initialize(self, app, cfg_filename='settings.yml'):
        self.app = app
        self._load_config(cfg_filename)
        self.entries.init_app(app) #TODO: What about flatpages name?
        self.freezer.init_app(app)
        self.register_generators()

    def _load_config(self, cfg_filename):
        """Load the StaticFlask config and apply the configuration to the
        flask.Flask application."""     
        file_path = join(self.root, cfg_filename)
        if isfile(file_path):
            with open(file_path, 'r') as cfg_file:
                cfg = yaml.load(cfg_file)
            app_config = cfg.pop('flask_config', {})
            template_config = cfg.pop('template_config', {})
            debug_config = app_config.pop('debug', {})
            for key, val in iteritems(app_config): #TODO: Validation? Required params? Debug?
                self.app.config[key.upper()] = val
            if self.app.debug:
                for key, val in debug_config:
                    self.app.config[key.upper()] = val
            for key, val in iteritems(template_config):
                self.app.config['SFLASK_TEMPLATE_{}'.format(key.upper())] = val
        else:
            if cfg_filename != 'settings.yml':
                raise FileNotFoundError(
                    'StaticFlask was not able to locate the specified config '
                    'file. The path given was:\n {} \n Which I looked for at'
                    ' the absolute path:\n {}'.format(cfg_filename, file_path)
                )
        if self.app.debug:
            for key, val in self.debug_config:
                self.app.config.setdefault(key, val)
        for key, val in self.default_config:
            self.app.config.setdefault(key, val)#TODO: Default template config?

    def register(self, app, options, first_registration=False):
        if self.app is None:
            self.initialize(
                app, cfg_filename=options.pop('cfg_filename', 'settings.yml')
            )
        if not self.deferred_functions:
            self.setup_routes()
        super(StaticFlask, self).register(
            app, options, first_registration=first_registration
        )

    def serve_page_media(self, filename):
        path = join(self.root, 'media', filename)
        if not isfile(path):
            print(path)
            abort(404)
        return send_from_directory(
            join(self.root, 'media'), filename
        )

    def render_root(self):
        return self.render_path('')

    def render_path(self, path):
        entry = self.entries.get_or_404(path)
        if isinstance(entry, Page):
            category = self.entries.get(entry.path.rpartition('/')[0])
            post_type = entry.meta.get('post_type', '')
            if post_type:
                post_template = '{}_page.html'.format(post_type)
            else:
                post_template = 'page.html'
            return render_template(
                post_template,
                page=entry,
                category=category,
                template_params=self.app.config.get_namespace(
                    'SFLASK_TEMPLATE_'
                )
            )
        included_posts = entry.included_posts(self.entries)
        included_categories = entry.included_categories(self.entries)
        parents = entry.get_parents(self.entries)
        template = entry['template']
        template_data = {
            'category' : entry,
            'sub_categories' : included_categories,
            'parents': parents,
            'template_params': self.app.config.get_namespace('SFLASK_TEMPLATE_')
        }
        if entry['paginate']:
            included_posts = included_posts[:self.app.config['PAGINATE_STEP']]
            template_data['nextpage'] = 2
        template_data['posts'] = included_posts
        return render_template(template, **template_data)

    def home_paginated(self, page):
        root = self.entries.get('')
        if not root['paginate']:
            return redirect('/')
        return self.render_paginated('', page)

    def render_paginated(self, path, page):
        entry = self.entries.get_or_404(path)
        if isinstance(entry, Page):
            return redirect(url_for('static_flask.path', path=entry.path))
        if page < 1 or not entry['paginate']:
            return redirect(url_for('static_flask.path', path=entry.path))
        included_categories = entry.included_categories(self.entries)
        parents = entry.get_parents(self.entries)
        post_slice_lower = (page-1)*self.app.config['PAGINATE_STEP']
        post_slice_upper = page*self.app.config['PAGINATE_STEP']
        included_posts = entry.included_posts(self.entries)
        if len(included_posts) < post_slice_lower:
            top_page = get_n_pages(len(included_posts),
                                   self.app.config['PAGINATE_STEP'])
            return redirect(url_for('static_flask.paginated', path=entry.path,
                             page=top_page))
        included_posts = included_posts[post_slice_lower:post_slice_upper]
        print(post_slice_lower, post_slice_upper)
        print(included_posts)
        return render_template(
            entry['template'],
            category=entry,
            posts=included_posts,
            sub_categories=included_categories,
            parents=parents,
            template_params=self.app.config.get_namespace('SFLASK_TEMPLATE_')
        )

    @staticmethod
    def pygments_css():
        """Serve the Pygments CSS file for codehilite."""
        return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

    def setup_routes(self):
        """Binds url rules for the StaticFlask app."""
        self.add_url_rule('/', 'home', self.render_root)
        self.add_url_rule('/<int:page>', 'home_paginated', self.home_paginated)
        self.add_url_rule('/<path:path>', 'path', self.render_path)
        self.add_url_rule('/<path:path>/<int:page>', 'paginated',
                          self.render_paginated)
        self.add_url_rule('/media/<path:filename>', 'media',
                          self.serve_page_media)
        self.add_url_rule('/pygments.css', 'pygments_css', self.pygments_css)

    def yield_entries(self):
        for entry in self.entries:
            yield '/'+entry.path

    def yield_paginated_pages(self):
        for category in self.entries.iter_categories():
            if not category['paginate']:
                continue
            n_posts = len(category.included_posts(self.entries))
            top_page = get_n_pages(n_posts, self.app.config['PAGINATE_STEP'])
            for pagenum in range(1, top_page+1):
                if category.path == '':
                    yield '/{pagenum}'.format(pagenum=pagenum)
                else:
                    yield '/{path}/{pagenum}'.format(path=category.path,
                                                     pagenum=pagenum)

    def yield_media(self):
        for root, dirnames, filenames in walk(join(self.root, 'media')):
            filenames = [f for f in filenames if not f[0] == '.']
            dirnames = [d for d in dirnames if not d[0] == '.']
            root_dir = root.replace(self.root, '')
            if not root_dir.startswith('/'):
                root_dir = '/' + root_dir
            for file in filenames:
                yield(root_dir+'/'+file)

    def register_generators(self):
        self.freezer.register_generator(self.yield_entries)
        self.freezer.register_generator(self.yield_paginated_pages)
        self.freezer.register_generator(self.yield_media)
