import markdown

from flask import Flask, render_template
from flask_flatpages import FlatPages, pygmented_markdown
from flask_frozen import Freezer
from os import listdir, path

# def two_tab_markdown(text, _pages=None):
#     extensions = _pages.config('markdown_extensions') if _pages else []
#     return markdown.markdown(text, extensions=extensions, tab_length=4)

class Testing():
    DEBUG = True
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'mdx_math', 'sane_lists']
    FREEZER_DESTINATION = '../../Files'
    FREEZER_BASE_URL = 'http://localhost'
    FREEZER_REMOVE_EXTRA_FILES = True
    FLATPAGES_EXTENSION = '.md'
    APP_DIR = path.dirname(path.abspath(__file__))
#    FLATPAGES_HTML_RENDERER = two_tab_markdown

class Config(Testing):
    DEBUG = False
    FREEZER_BASE_URL = 'http://calpin.me'

pages = FlatPages()
app = Flask(__name__)
app.config.from_object(Config())
pages.init_app(app)
freezer = Freezer(app)

@freezer.register_generator
def archive():
    posts = pages._pages
    _pages= int(len(posts)/10)
    if _pages == 0:
        yield {'_page': 1}
    else:
        for n in range(1,_pages):
            yield {'_page': 1}

@freezer.register_generator
def page():
    for filename  in listdir(app.config['APP_DIR']+'/pages'):
        yield{'path':filename.split('.')[0]}
    
@app.route('/')
@app.route('/<int:_page>/')
def archive(_page=1):
    _pages = sorted((p for p in pages if 'published' in p.meta),
                    reverse=True, key=lambda p: p.meta['published'])
    posts = _pages[(_page-1)*10:_page*10]
    for post in posts:
        bits = post.body.split('\n')[:10]
        for index, bit in enumerate(bits):
            if not bit:
                bits[index] = "\n"
        post.meta['extract'] = pygmented_markdown("\n".join(bits))
    _next = len(_pages[_page*10:(_page+1)*10])>0
    return render_template('index.html', posts=posts, next=_next,
                            page=(_page+1))

@app.route('/<path:path>/')
def page(path):
    _page = pages.get_or_404(path)
 #   _page.html_renderer = pages._smart_html_renderer(two_tab_markdown)
    return render_template('page.html', page=_page)

if __name__ == '__main__':
    app.config.from_object(Testing())
    freezer.freeze()
    #app.run()
