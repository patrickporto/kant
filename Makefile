.PHONY: build

build:
	python3 setup.py build

install:
	python3 setup.py install

publish:
	python3 setup.py sdist bdist_wheel upload

test:
	python3 setup.py test

docs-build:
	python3 setup.py build_sphinx

docs-live:
	sphinx-autobuild docs _build/html
