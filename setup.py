# -*- coding: utf-8 -*-
"""
This module contains the tool of izug.ticketbox
"""
from setuptools import setup, find_packages


def read(*rnames):
    return open('/'.join(rnames)).read()

version = open('izug/ticketbox/version.txt').read().strip()
maintainer = 'Elio Schmutz'


long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs/HISTORY.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('izug', 'ticketbox', 'README.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='izug.ticketbox',
      version=version,
      maintainer=maintainer,
      description="A tracker-like task management system (Maintainer: %s)"
        % maintainer,
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Elio Schmutz, 4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='http://www.4teamwork.ch',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['izug', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Products.DataGridField',
                        'ftw.tabbedview',
                        'ftw.table',
                        'ftw.notification.base',
                        'ftw.notification.email',
                        'izug.utils',
                        'ftw.sendmail',
                        # -*- Extra requirements: -*-
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
