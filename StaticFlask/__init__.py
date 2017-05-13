import markdown

from flask import abort, Flask, render_template, render_template_string
from flask_flatpages import FlatPages, pygmented_markdown, pygments_style_defs
from flask_frozen import Freezer
from os import listdir, path

class Testing():
    DEBUG = True
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'mdx_math', 'mdx_partial_gfm',
                                     'headerid']
    FREEZER_DESTINATION = '../../Files'
    FREEZER_BASE_URL = 'http://localhost'
    FREEZER_REMOVE_EXTRA_FILES = True
    FLATPAGES_ROOT = '/Users/padraic/Documents/BlogPages'
    FLATPAGES_EXTENSION = '.md'
    TWITTER = 'https://twitter.com/padraic_padraic'
    GITHUB = 'https://github.com/padraic-padraic'
    MASTODON = 'https://mastodon.social/@padraic_padraic'
    APP_DIR = path.dirname(path.abspath(__file__))
    SIDEBAR_TITLE = "Padraic Calpin"
    PAGE_TITLE = 'My blog is a blog'
    CATEGORIES = ['notes', 'blog']
    # RESERVED_NAMES = CATEGORIES + ['about']

class Config(Testing):
    DEBUG = False
    FREEZER_BASE_URL = 'http://padraic.xyz'
    FLATPAGES_ROOT = '/home/pi/BlogPages/'
    FREEZER_DESTINATION = '/var/www/Static'

pages = FlatPages()
app = Flask(__name__)
conf = Config()
app.config.from_object(conf)
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


def get_from_partial_path(partial_path):
    f_path = path.join(Testing().FLATPAGES_ROOT, partial_path)
    category = [_s for _s in partial_path.split('/')][-1].capitalize()
    category_data = {'cateogry':category,
                     'sub_categories': {},
                     'posts': []}
    listings = map(lambda x: (x, path.join(Testing().FLATPAGES_ROOT, 
                                            partial_path, x)), 
                   filter(lambda x: not x.startswith('.'),
                          listdir(f_path))
                   )
    for _short, _full in listings:
        if path.isdir(_full):
            category_data['sub_categories'][_short] = []
            for _f in listdir(_full):
                if  _f.split('.')[-1]=='md':
                    p = pages.get(path.join(partial_path, _short,
                                            _f.split('.'))[0])
                    if 'published' in p.meta:
                        category_data['sub_categories'][_short].append(p)
        else:
            category_data['posts'].append(path.join(partial_path, _short))
    for category in category_data['sub_categories']:
        if 'order' in category_data['sub_categories'][cateogry][0].meta:
            category_data['sub_categories'][category] = sorted(
                category_data['subcategories'][category],
                key=lambda x: x.meta['order']
                )
        else:
            category_data['sub_categories'][category] = sorted(
                category_data['subcategories'][category],
                key=lambda x: x.meta['published'], reverse=True
                )
    if 'order' in category_data['posts']:
        category_data['posts'] = sorted(category_data['posts'],
                                        key=lambda x: x.meta['order'])
    else:
        category_data['posts'] = sorted(category_data['posts'], reverse=True,
                                        key=lambda x: x.meta['published'])
    return category_data

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
    return render_template('index.html', posts=posts, next=_next, 
                            nextpage=_page+1, prevpage=_page-1)

@app.route('/<path:_path>/')
def page(_path):
    if _page is not None:
        return render_template('page.html', page=_page)
    f_path = path.join(conf.FLATPAGES_ROOT, _path)
    if not path.isdir(f_path):
        abort(404)
    _data = get_from_partial_path(_path)
    return render_template('category_index.html', data=_data)
    #TODO: Implement partial path, think about how to handle 'topics'; is the notes category an exception?
    

@app.route('/about/')
def about():
    _page = pages.get_or_404('about')
    return render_template('page.html', page=_page)

@app.route('/notes/')
def notes():
    _pages = [p for p in pages if p.meta.get('category', None) == 'Notes']
    _pages = [p for p in _pages if p.meta.get('topic', None) is not None]
    categorized = {}
    for p in _pages:
        if not p.meta['topic'] in categorized:
            categorized[p.meta['topic']] = []
        categorized[p.meta['topic']].append(p)
    for topic in categorized.keys():
        categorized[topic] = sorted(categorized[topic],
                                    key=lambda p: p.meta['order'])
    return render_template('note_index.html', topics=categorized)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

if __name__ == '__main__':
    app.config.from_object(Testing())
    app.run(port=5003)
