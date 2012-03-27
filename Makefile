#!/usr/bin/make
#
options =

.PHONY: instance cleanall test

PACKAGE_ROOT = src/collective/jekyll

GS_FILES = $(PACKAGE_ROOT)/profiles/*/*.xml $(PACKAGE_ROOT)/setuphandlers.py

BUILDOUT_FILES = buildout.cfg setup.py bin/buildout

DATA_FS = var/filestorage/Data.fs

all: instance

ifneq ($(strip $(TRAVIS_PYTHON_VERSION)),)
IS_TRAVIS = yes
endif

ifdef IS_TRAVIS
develop-eggs: bootstrap.py buildout.cfg
	python bootstrap.py
else
bin/python:
	virtualenv-2.6 --no-site-packages .

develop-eggs: bin/python bootstrap.py buildout.cfg
	./bin/python bootstrap.py
endif

buildout.cfg:
	ln -s dev.cfg buildout.cfg

bin/buildout: develop-eggs

bin/test: $(BUILDOUT_FILES)
	./bin/buildout -Nvt 5 install test
	touch $@

bin/instance: $(BUILDOUT_FILES)
	./bin/buildout -Nvt 5 install instance
	touch $@
	
$(DATA_FS): $(GS_FILES)	bin/instance
	./bin/buildout -Nvt 5 install plonesite

instance: bin/instance $(DATA_FS)
	bin/instance fg

cleanall:
	rm -fr bin develop-eggs downloads eggs parts .installed.cfg

test: bin/test	
	./bin/test

