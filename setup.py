#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.0.2'
LONG_DESC = """\
DagCategory aims to be a query efficient solution to categories
"""

setup(name='django-dagcategory',
      version=VERSION,
      description="A simple library for creating tree like categories",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='django category',
      maintainer = 'Jason Kraus',
      maintainer_email = 'zbyte64@gmail.com',
      url='http://github.com/cuker/django-dagcategory',
      license='New BSD License',
      packages=find_packages(exclude=['test_settings.py']),
      zip_safe=True,
      install_requires=[
      ],
      test_suite='setuptest.SetupTestSuite',
      tests_require=(
        'django-setuptest',
      ),
      include_package_data = True,
)

