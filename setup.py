#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: setup.py
# @time: 2018/7/23 15:24
# @Software: PyCharm


import pathlib

from setuptools import find_packages, setup
from django.conf import settings

settings.configure()

from djangohelper import __version__


def load_install_requires(filepath='requirements.txt', encoding='utf-8'):
    """Read ``requirements.txt`` and return a list of install requirements.

    Lines starting with ``#`` or ``-`` (e.g. ``-r``) are ignored. Inline
    comments (``#``) are stripped. This replaces the previous
    ``astartool.setuptool.load_install_requires`` helper.
    """
    file = pathlib.Path(filepath)
    if not file.exists():
        raise FileNotFoundError('file not found: {}'.format(filepath))
    with file.open('r', encoding=encoding) as f:
        lines = f.readlines()
    requirements = (
        line.split('#')[0].strip()
        for line in lines
        if not line.strip().startswith('#') and not line.startswith('-')
    )
    return [req for req in requirements if req]


setup(
    name='snowland-djangohelper',
    version=__version__,
    description=(
        'django helper, toolkit for django.'
    ),
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='A.Star',
    author_email='astar@snowland.ltd',
    maintainer='A.Star',
    maintainer_email='astar@snowland.ltd',
    license='BSD-3-Clause',
    packages=find_packages(),
    package_data={
        'djangohelper/templetes/': ['*.html'],
        'views/templetes/': ['*.html']
    },

    platforms=["all"],
    url='https://gitee.com/snowlandltd/snowland-djangohelper',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    install_requires=load_install_requires(),
    extras_require={
        'bcrypt': ['bcrypt'],
    },
)
