from setuptools import setup, find_packages
import os

version = '4.3.2'
maintainer = 'Elio Schmutz'

tests_require = [
    'zope.testing',
    'Products.PloneTestCase',
    ]

setup(name='izug.ticketbox',
      version=version,
      description="A tracker-like task management system for plone.",
      long_description=(open('README.rst').read() + '\n' + \
                            open(os.path.join('docs', 'HISTORY.txt')).read()),

      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules', ],

      keywords='ticketbox tracker ftw ',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/izug.ticketbox',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['izug', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'Products.DataGridField',
        'ftw.tabbedview',
        'ftw.table',
        'ftw.notification.base',
        'ftw.notification.email',
        'plone.principalsource',
        'BeautifulSoup'
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      test_suite='izug.ticketbox.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
