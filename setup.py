"""
Setup module for StaticFlask
"""
from setuptools import find_packages, setup

setup(
    name='StaticFlask',
    version='1.0.0-dev',
    description='A Flask blueprint for static site generation.',
    url='https://github.com/padraic-padraic/StaticFlask',
    classifiers=[
        'Framework :: Flask',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=['StaticFlask'],
    package_data={
        'StaticFlask': [
            'templates/base.html',
            'templates/index.html',
            'templates/page.html',
            'templates/category.html'
        ]
    },
    install_requires=[
        'Flask>=1.0',
        'Flask-Flatpages>=0.7.0',
        'Frozen-Flask',
        'Pygments',
        'python-markdown-math',
        'six'
    ],
    python_requires='>=2.7, !=3.0, !=3.1, !=3.2, !=3.3, !=3.4',
)