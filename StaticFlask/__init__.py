from .category import Category
from .categorized_pages import CategorizedPages
from .sflask import StaticFlask

# # import markdown
# import os
# import sys

# from flask import abort, Flask, render_template, render_template_string
# from flask_flatpages import FlatPages, pygmented_markdown, pygments_style_defs
# from flask_frozen import Freezer

# class Testing():
#     DEBUG = True
#     FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'mdx_math', 'mdx_partial_gfm',
#                                      'headerid']
#     FREEZER_DESTINATION = '../../Files'
#     FREEZER_BASE_URL = 'http://localhost'
#     FLATPAGES_ROOT = '/Users/padraic/Documents/BlogPages'
#     FLATPAGES_EXTENSION = '.md'
#     TWITTER = 'https://twitter.com/padraic_padraic'
#     GITHUB = 'https://github.com/padraic-padraic'
#     # MASTODON = 'https://mastodon.social/@padraic_padraic'
#     APP_DIR = os.path.dirname(os.path.abspath(__file__))
#     SIDEBAR_TITLE = "Padraic Calpin"
#     PAGE_TITLE = 'My blog is a blog'
#     # CATEGORIES = ['notes', 'blog']
#     RESERVED_NAMES = ['about', 'static', 'images']
#     IGNORED_NAMES = ['.git', '.gitignore', '.DS_Store']

# class Config(Testing):
#     DEBUG = False
#     FREEZER_BASE_URL = 'http://padraic.xyz'
#     FLATPAGES_ROOT = '/home/pi/BlogPages/'
#     FREEZER_DESTINATION = '/var/www/Static'
#     FREEZER_REMOVE_EXTRA_FILES = False

# app = Flask(__name__)
# pages = FlatPages()
# conf = Config()
# app.config.from_object(conf)
# pages.init_app(app)
# freezer = Freezer(app)

# # def init_app(app, config=Config()):
# #     app.config.from_object(config)
# #     pages.init_app(app)

# @freezer.register_generator
# def archive():
#     posts = [p for p in pages if 'Blog' in p.path]
#     _pages= int(len(posts)/10)
#     if _pages == 0:
#         yield {'_page': 1}
#     else:
#         for n in range(1,_pages):
#             yield {'_page': n}

# @freezer.register_generator
# def page():
#     reserved = app.config['RESERVED_NAMES'] + app.config['IGNORED_NAMES']
#     for path, dirs, files in os.walk(app.config['FLATPAGES_ROOT']):
#         dirs, files = skip_reserved_names(dirs, files, reserved)
#         stem = os.path.relpath(path, app.config['FLATPAGES_ROOT'])
#         if '\\' in stem:
#             stem = stem.replace('\\', '/')
#         if stem !='.':
#             yield{'path':stem.strip('/')}
#     for p in pages:
#         yield{'path':p.path}


# def delete_occurances(_list, search_items):
#     indices = []
#     for i, d in enumerate(_list):
#         if d in search_items:
#             indices.append(i)
#     indices = sorted(indices, reverse=True)
#     for i in indices:
#         _list.pop(i)
#     return _list


# def skip_reserved_names(dirs, files, reserved_names):
#     delete_occurances(dirs, reserved_names)
#     delete_occurances(files, reserved_names)
#     return dirs, files

# def get_from_partial_path(partial_path):
#     #TODO: Fix the failure if we're in the bottom of the stack
#     reserved = app.config['RESERVED_NAMES'] + app.config['IGNORED_NAMES']
#     if partial_path != '/':
#         root = os.path.join(app.config['FLATPAGES_ROOT'], partial_path)
#     else:
#         root = app.config['FLATPAGES_ROOT']
#     # reserved = Testing().RESERVED_NAMES
#     # root = os.path.join(Testing().FLATPAGES_ROOT, partial_path)
#     category_data = {'category':partial_path}
#     for path, dirs, files in os.walk(root):
#         dir_data = {}
#         dirs, files = skip_reserved_names(dirs, files, reserved)
#         stem = os.path.relpath(path, root)
#         if '\\' in stem:
#             stem = '/'.join(split_path(stem))
#         dir_data['files'] = []
#         for f in files:
#             if stem != '.':
#                 p_path = '/'.join([partial_path, stem, 
#                                    os.path.splitext(f)[0]]).strip('/')
#             else:
#                 p_path = '/'.join([partial_path, 
#                                    os.path.splitext(f)[0]]).strip('/')
#             p = pages.get(p_path)
#             if p is not None:
#                 dir_data['files'].append(p)
#         if all([p.meta.get('order', False) for p in dir_data['files']]):
#             dir_data['files'] = sorted(dir_data['files'], 
#                                        key=lambda x: x.meta['order'])
#         if stem == '.':
#             dir_data['categories'] = []
#             for d in dirs:
#                 dir_data['categories'].append(d)
#         category_data[stem] = dir_data
#     return category_data

# @app.template_filter('split_path')
# def split_path(path):
#     if sys.platform.startswith('win'):
#         sep = '\\'
#     else:
#         sep = '/'
#     return path.split(sep)

# @app.template_filter('uscore_to_space')
# def us_to_space(_object):
#     if type(_object)==list:
#         return [el.replace('_', ' ') for el in _object]
#     else:
#         return _object.replace('_', ' ')

# @app.template_filter('echo_split_path')
# def echo_path(_split_path):
#     return(' > '.join(_split_path))

# @app.route('/')
# @app.route('/<int:_page>/')
# def archive(_page=1):
#     post_data = get_from_partial_path('/')
#     blog_posts = []
#     root_categories = post_data['.']['categories']
#     blog_pages = []
#     for key in post_data:
#         if key=='.' or key == 'category':
#             continue
#         if 'Blog' in key:
#             [blog_pages.append(p) for p in post_data[key]['files']]
#     blog_pages = [p for p in blog_pages if p.meta.get('published', None) is not None]
#     _pages = sorted(blog_pages, key=lambda x: x.meta['published'], reverse=True)
#     posts = _pages[(_page-1)*10:_page*10]
#     for post in posts:
#         bits = post.body.split('\n')
#         if bits == bits[:3]:
#             post.meta['read_more'] = False
#         else:
#             post.meta['read_more'] = True
#         for index, bit in enumerate(bits):
#             if not bit:
#                 bits[index] = "\n"
#         post.meta['extract'] = pygmented_markdown("\n".join(bits[:3]))
#     _next = len(_pages[_page*10:(_page+1)*10])>0
#     return render_template('index.html',
#                             root_categories = root_categories,
#                             posts=posts, next=_next,
#                             nextpage=_page+1, prevpage=_page-1)

# @app.route('/<path:path>/')
# def page(path):
#     root_categories = get_from_partial_path('/')['.']['categories']
#     _page = pages.get(path)
#     if _page is not None:
#         return render_template('page.html', page=_page, 
#                                root_categories=root_categories)
#     if sys.platform.startswith('win'):
#         f_path = path.replace('/', '\\')
#     else:
#         f_path = path
#     f_path = os.path.join(app.config['FLATPAGES_ROOT'], f_path)
#     if not os.path.isdir(f_path):
#         abort(404)
#     _data = get_from_partial_path(path)
#     return render_template('category_index.html', data=_data,
#         root_categories=root_categories)
#     #TODO: Implement the category index template.

# # @app.route('/about/')
# # def about():
# #     _page = pages.get_or_404('about')
# #     return render_template('page.html', page=_page)

# @app.route('/pygments.css')
# def pygments_css():
#     return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

# if __name__ == '__main__':
#     app.config.from_object(Testing())
#     app.run(port=5003)
