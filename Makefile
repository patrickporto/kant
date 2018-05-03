.PHONY: build

build:
	python3 setup.py build

install:
	python3 setup.py install

publish:
	python3 setup.py sdist bdist_wheel upload

test:
	python3 setup.py test
