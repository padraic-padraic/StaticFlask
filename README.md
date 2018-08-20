Static Flask
===========

This is a small project to create a Jekyll-like blogging tool using markdown formatted pages and Flask, to be run as a personal blog. As such it also includes MathJax support for rendering Latex. 

Eventually, I would like to make it extensible to work like a little Flask-based CMS, but we'll see how much time I have.

## '0.5' Plans

StaticFlask took a significant step forward with my idea to use the filesystem to incremenent a CMS-like post categories and sub-categories system. However, the core hasn't changed since its original implementation, and this is still very rough.

The plan is to rewrite StaticFlask to be more flexible, and eventually packagable into a command line tool. 

### Case Insenstive Path Resolution
This is a small extension to Flask-Flatpages that I plan to propose. Simply, we add a config flag, and we wrap
the `pages.get()` methods and the `pages` init functions with calls to `string.lower`.

### Simpler Path Resolution

The current directory-walking funciton is a bit of a mess, and is poorly bolted on to the existing code.

The core of the app is a single URL resolver, `@app.route('/<path:path>'). The resolver will proceed as:
1. Checking if the path if a page, using `pages.get()`.
    + If it's a page, grab the page template and render
    + If not, continue to step 2.
2. Checking if the path is a directory
    + If not, 404
    + If yes, proceed to step 3.
3. Check for the existence of the file `_config.yml`
    + This file will handle how the category is rendered, including:
        - Which template to use
        - How many 'sub categories' to fetch
    + If the file doesn't exist, we fall back on defaults

An additional resolvers with be added for `@app.route('/')`, to control the index. This will look to a special file, 
`/home.yml` for controlling the main page index.
#### Additional considerations

We might also want to consider
+ Wrapping the `FlatPages` initialiser to catch any filenames that would clash with this system
+ Some kind of pagination for indexes. It *could* rely on query strings, but this adds additional complexity to the `freezer` generators

### Seperate Config File
Currently, all config is hand-coded in `__init__.py`. This will be replaced with a YAML-loader, which will have 3 distinct blocks
1. 'Internal Data': `FLATPAGES_ROOT` etc...
2. 'Template Options': A dict, that will be passed to every page
3. 'Site data': Arbitrary config vals that will be passed to Jinja

## Possible Extensions / Refinements

The core refinement I would like is to package StaticFlask and create a simple command-wrapper. This would initialize a directly with config and (skeleton) template files and (optionally) the raw site code, to enable others to create websites with Static Flask.