# References 
# http://code.djangoproject.com/browser/django/trunk/setup.py 
#!/usr/bin/env python
from mailsync import __version__
import os

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
mailsync_dir = 'mailsync'

for dirpath, dirnames, filenames in os.walk(mailsync_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

sdict = {
    'name' : 'mailsync',
    'version' : __version__,
    'description' : 'Syncs web apps with Mailsync and Campaign Monitor',
    'long_description' : 'Syncs user data directly from MySQL and PostgreSQL to Mailchimp and Campaign Monitor.',
    'url': 'http://mailsync.github.io/',
    'author' : 'Mailsync',
    'author_email' : 'team at mailsync dot li',
    'keywords' : ['Mailsync'],
    'license' : 'GPL',
    'packages' : packages,
    'data_files' : data_files,
    'install_requires': 
    [
        'tornado==2.4',
        'formencode==1.2.4',
        'Jinja2==2.6',
        'MySQL-python==1.2.3',
        'createsend==1.1.1',
        'mailsnake==1.6.0',
        'psycopg2==2.4.5',
        'SQLAlchemy==0.7.9',
		'pip',
        'pytz==2012j'
    ]
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)