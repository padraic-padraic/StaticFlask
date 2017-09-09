"""Helper functions for resoloving a path in StaticFlask. 
We use os.walk to build a collection of all subcategories and all posts under a 
given category, ignoring any special 'reserved names' defined in the install."""


def delete_occurances(_list, search_items):
    indices = []
    for i, d in enumerate(_list):
        if d in search_items:
            indices.append(i)
    indices = sorted(indices, reverse=True)
    for i in indices:
        _list.pop(i)
    return _list


def skip_reserved_names(dirs, files, reserved_names):
    delete_occurances(dirs, reserved_names)
    delete_occurances(files, reserved_names)
    return dirs, files

def get_from_partial_path(partial_path):
    #TODO: Fix the fact that max depth is currently 1, using os.walk and pruning
    #Maybe break this up in to functions
    #Remove dependence on config class and use app instead?
    # Could this be an extension to flatpages?
    reserved = app.config['RESERVED_NAMES']
    root = os.path.join(app.config['FLATOAGES_ROOT'], partial_path)
    category_data = {}
    for path, dirs, files in os.walk(root):
        dir_data = {}
        dirs, files = skip_reserved_names(dirs, files, reserved)
        stem = os.path.relpath(path, root)
        if stem != '.': #More than 1 level deep
            dir_data['files'] = []
            for f in files:
                dir_data['files'].append(pages.get(os.path.join(root, stem, f)))