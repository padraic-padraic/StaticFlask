import markdown
from flask import Flask, render_template

from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages
from flask_frozen import Freezer

# def two_tab_markdown(text, flatpages):
#     extensions = flatpages.config('markdown_extensions') if flatpages else []
#     return markdown.markdown(text, extensions, tab_length=2)

class Testing():
    DEBUG = True
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'mdx_math']
    FREEZER_DESTINATION = '../Files'
    FREEZER_BASE_URL = 'localhost://'
    FLATPAGES_EXTENSION = '.md'
#    FLATPAGES_HTML_RENDERER = two_tab_markdown

class Config(Testing):
    DEBUG = False
    FREEZER_BASE_URL = 'http://calpin.me'

pages = FlatPages()
app = Flask(__name__)
pages.init_app(app)
freezer = Freezer(app)
Bootstrap(app)
app.config.from_object(Config())

def freeze():
    freezer.freeze()
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:path>/')
def page(path):
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)
    
if __name__ == '__main__':
    app.config.from_object(Testing())
    app.run()