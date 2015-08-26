# -*- coding: utf-8 -*-

import re
from setuptools import setup
from setuptools import find_packages


REQUIRES = [
    # 'smore==0.0.0',
    # 'marshmallow-sqlalchemy==0.3.0.dev0',
]


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='marshmallow-pagination',
    version=find_version('marshmallow_pagination/__init__.py'),
    description='Pagination helpers for Marshmallow',
    long_description=read('README.rst'),
    author='Joshua Carp',
    author_email='jm.carp@gmail.com',
    url='https://github.com/jmcarp/marshmallow-pagination',
    packages=find_packages(exclude=('test*', )),
    package_dir={'marshmallow_pagination': 'marshmallow_pagination'},
    include_package_data=True,
    install_requires=REQUIRES,
    license=read('LICENSE'),
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests'
)
