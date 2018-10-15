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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=['StaticFlask'],
    install_requires=[
        'Flask>=1.0',
        'Flask-Flatpages>=0.7.0.dev0',
        'Frozen-Flask',
        'six',
        'python-markdown-math'
    ],
    python_requires='>=2.7, !=3.0, !=3.1, !=3.2, !=3.3',
    dependency_links=[
        'https://github.com/padraic-padraic/Flask-FlatPages.git@markdown-3#egg=Flask-Flatpages-0.7.0.dev0'
    ]
)