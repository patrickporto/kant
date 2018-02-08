from os import path
from setuptools import setup, find_packages


BASE_DIR = path.dirname(__file__)


with open(path.join(BASE_DIR, 'README.md')) as f:
    long_description = f.read()


setup(
    name='kant',
    version='2.0.0',
    description='The CQRS and Event Sourcing framework for Python',
    url='http://github.com/patrickporto/kant',
    author='Patrick Porto',
    author_email='patrick.s.porto@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['conftest.py']),
    install_requires=[
        'python-dateutil',
        'inflection',
        'cuid.py',
        'async_generator',
        'asyncio_extras',
        'aiopg',
    ],
    long_description=long_description,
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
    keywords='eventsourcing cqrs eventstore',
)
