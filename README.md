Static Flask [![Build Status](https://travis-ci.org/padraic-padraic/StaticFlask.svg?branch=master)](https://travis-ci.org/padraic-padraic/StaticFlask)
===========

This is a small project to create a Jekyll-like blogging tool using markdown formatted pages and Flask, to be run as a personal blog. As such it also includes `py-markdown-math` for escaping LaTeX commands in Markdown.

StaticFlask is a configurable, 'batteries included' Blueprint. It's core is based on [`Flask-Flatpages`](https://github.com/Flask-FlatPages/Flask-FlatPages/), an extension that provides flat page markdown support to Flask. 

StaticFlask pages are categorized using the file system. Each folder defines a category, and each sub-folder is a subcategory. Each category can be simply configured using a small yaml file, defining the template, and what subcategories/posts to display.

The Blueprint itself can also be configured with a small yaml file. This is used to set the pages and media folder, configure the FlatPages instance, and set other config values in the `Flask` application.

On registration, StaticFlask sets up the categories and pages, and registers routes:
    - `/<path>`: Load the category or page at the path
    - `/<path>/<page_number>`: Load the paginated pages in the category at `path`
    - `/media/<path>`: Serve images and other media
    - `/static/`: Serve CSS and JS and other static files.

StaticFlask also sets up an instance of `flask_frozen.Freezer` provided by the [FrozenFlask](https://github.com/Frozen-Flask/Frozen-Flask) extension, and registers generators for building a static site from the resulting application.

## Possible Extensions / Refinements

The core refinement I would like is to package StaticFlask and create a simple command-wrapper. This would initialize a directly with config and (skeleton) template files and (optionally) the raw site code, to enable others to create websites with Static Flask.
