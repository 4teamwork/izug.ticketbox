from setuptools import setup, find_packages
import os

version = '4.9.0'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'unittest2',
    'ftw.testing',
    'plone.app.testing',
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.zipexport',
    'collective.MockMailHost',
    'xlrd',
]

setup(
    name='izug.ticketbox',
    version=version,
    description="A tracker-like task management system for plone.",
    long_description=(open('README.rst').read() + '\n' + \
                      open(os.path.join('docs', 'HISTORY.txt')).read()),

    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers

    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    keywords='ticketbox tracker ftw ',
    author='4teamwork AG',
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
        'AccessControl',
        'Acquisition',
        'Plone',
        'Products.ATContentTypes',
        'Products.ATReferenceBrowserWidget',
        'Products.Archetypes',
        'Products.CMFCore',
        'Products.CMFPlone',
        'Products.DataGridField',
        'Products.statusmessages',
        'ZODB3',
        'Zope2',
        'ftw.calendarwidget',
        'ftw.notification.base',
        'ftw.notification.email',
        'ftw.tabbedview',
        'ftw.table',
        'ftw.upgrade >= 1.14.0',
        'plone.principalsource',
        'zope.annotation',
        'zope.app.component',
        'zope.app.container',
        'zope.app.pagetemplate',
        'zope.cachedescriptors',
        'zope.component',
        'zope.contentprovider',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        'zope.viewlet',
        'XlsxWriter',
    ],

    tests_require=tests_require,
    extras_require=dict(tests=tests_require,
                        workspace=['ftw.workspace'],
                        zip_export=['ftw.zipexport']),

    test_suite='izug.ticketbox.tests.test_docs.test_suite',
    entry_points="""
    # -*- entry_points -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
