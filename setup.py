from os import path
from io import open
from setuptools import setup, find_packages
try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    BuildDoc = None
#==============================================================================
# INTERFACE
#==============================================================================

NAME = 'Kant'
VERSION = '3.0'
RELEASE = '3.0.0'

#==============================================================================
# IMPLEMENTATION
#==============================================================================

BASE_DIR = path.dirname(__file__)

command_options = {}
cmdclass = {}

if BuildDoc is not None:
    command_options['build_sphinx'] = {
        'project': ('setup.py', NAME),
        # 'author': ('setup.py', AUTHOR),
        'version': ('setup.py', VERSION),
        'release': ('setup.py', RELEASE),
        'source_dir': ('setup.py', 'docs'),
        'builder': ('setup.py', 'html')
    }

    cmdclass['build_sphinx'] = BuildDoc

with open(path.join(BASE_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=NAME,
    version=RELEASE,
    description='A CQRS and Event Sourcing framework for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://github.com/patrickporto/kant',
    author='Patrick Porto',
    author_email='patrick.s.porto@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['conftest.py', 'docs', 'tests']),
    install_requires=[
        'python-dateutil',
        'inflection',
        'cuid.py',
        'async_generator',
        'asyncio_extras',
        'aiopg',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-pycodestyle',
        'pytest-cov',
        'pytest-asyncio',
        'sqlalchemy',
    ],
    extras_require={
        'SQLAlchemy-Projections': ['sqlalchemy'],
    },
    zip_safe=False,
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    python_requires='~=3.5',
    keywords='eventsourcing cqrs eventstore',
    cmdclass=cmdclass,
    command_options=command_options,
)
