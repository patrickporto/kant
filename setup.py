from setuptools import setup


setup(
    name='kant',
    version='0.1.4',
    description='The CQRS and Event Sourcing framework for Python',
    url='http://github.com/patrickporto/kant',
    author='Patrick Porto',
    author_email='patrick.s.porto@gmail.com',
    license='MIT',
    packages=['kant', 'kant.events'],
    install_requires=[
        'sqlalchemy_utils',
        'python-dateutil',
        'inflection',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-pycodestyle',
        'pytest-cov',
    ],
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
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='eventsourcing cqrs eventstore',
)
