import markdown

from flask import Flask, render_template, render_template_string
from flask_flatpages import FlatPages, pygmented_markdown, pygments_style_defs
from flask_frozen import Freezer
from os import listdir, path

class Testing():
    DEBUG = True
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'mdx_math', 'mdx_gfm',
                                     'headerid']
    FREEZER_DESTINATION = '../../Files'
    FREEZER_BASE_URL = 'http://localhost'
    FREEZER_REMOVE_EXTRA_FILES = True
    FLATPAGES_ROOT = '/Users/padraic/Documents/BlogPages'
    FLATPAGES_EXTENSION = '.md'
    TWITTER = 'https://twitter.com/padraic_padraic'
    GITHUB = 'https://github.com/padraic-padraic'
    APP_DIR = path.dirname(path.abspath(__file__))
    SIDEBAR_TITLE = "Padraic Calpin"
    PAGE_TITLE = 'My blog is a blog'

class Config(Testing):
    DEBUG = False
    FREEZER_BASE_URL = 'http://padraic.xyz'
    FLATPAGES_ROOT = '/home/pi/BlogPages/'
    FREEZER_DESTINATION = '/var/www/Static'

pages = FlatPages()
app = Flask(__name__)
app.config.from_object(Config())
pages.init_app(app)
freezer = Freezer(app)

@freezer.register_generator
def archive():
    posts = [p for p in pages if p.path != 'about']
    _pages= int(len(posts)/10)
    if _pages == 0:
        yield {'_page': 1}
    else:
        for n in range(1,_pages):
            yield {'_page': n}

@freezer.register_generator
def page():
    for filename in listdir(app.config['APP_DIR']+'/pages'):
        if filename != 'about' or filename.split('.')[1] != 'md':
            yield{'path':filename.split('.')[0]}


@app.route('/')
@app.route('/<int:_page>/')
def archive(_page=1):
    _pages = [p for p in pages if p.meta.get('category', None) == 'Blog']
    _pages = sorted((p for p in _pages if 'published' in p.meta),
                    reverse=True, key=lambda p: p.meta['published'])
    posts = _pages[(_page-1)*10:_page*10]
    for post in posts:
        bits = post.body.split('\n')
        if bits == bits[:3]:
            post.meta['read_more'] = False
        else:
            post.meta['read_more'] = True
        for index, bit in enumerate(bits):
            if not bit:
                bits[index] = "\n"
        post.meta['extract'] = pygmented_markdown("\n".join(bits[:3]))
    _next = len(_pages[_page*10:(_page+1)*10])>0
    return render_template('index.html', posts=posts, next=_next, nextpage=_page+1,
                           prevpage=_page-1)

@app.route('/<path:path>/')
def page(path):
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)

@app.route('/about/')
def about():
    _page = pages.get_or_404('about')
    return render_template('page.html', page=_page)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

if __name__ == '__main__':
    app.config.from_object(Testing())
    app.run(port=5003)
