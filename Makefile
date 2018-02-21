.PHONY: clean deps develop docs clean-build lint test coverage coverage-html tox migrate runserver
COVER := mailme
APP := src/

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "develop - install all packages required for development"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "coverage - generate test coverage report"
	@echo "coverage-html - generate test coverage report, html output"
	@echo "tox - Run all tests in a tox container"


clean: clean-build clean-pyc


deps:
	@echo "--> Installing python dependencies"
	pip install --upgrade pip setuptools wheel
	pip install --use-wheel --upgrade -r requirements.txt
	@echo ""


develop: deps

docs: clean-build
	pip install --use-wheel "file://`pwd`#egg=mailme[docs]"
	$(MAKE) -C docs clean
	$(MAKE) -C docs html


clean-build:
	@rm -fr build/ src/build
	@rm -fr dist/ src/dist
	@rm -fr *.egg-info src/*.egg-info
	@rm -fr htmlcov/
	$(MAKE) -C docs clean


i18n:
	@python manage.py babel makemessages -d django -l de
	@python manage.py babel compilemessages -d django -l de
	@python manage.py babel makemessages -d djangojs -l de
	@python manage.py babel compilemessages -d djangojs -l de
	@python manage.py compilejsi18n -d djangojs -l de


test: lint
	docker-compose exec web pytest $(APP) $(ARGS)

lint:
	docker-compose exec web flake8 src/

coverage:
	docker-compose exec web pytest --cov=${COVER} --cov-report=term-missing ${APP}

coverage-html:
	docker-compose exec web pytest --cov=${COVER} --cov-report=html ${APP}

tdd:
	docker-compose exec web pytest -x --pdb $(ARGS) $(APP)

test_failed:
	docker-compose exec web pytest --lf $(ARGS) $(APP)

update_docker:
	docker-compose exec web make develop

initialize_docker: update_docker
	docker-compose exec web ./manage.py migrate

shell:
	docker-compose exec web bash

djshell:
	docker-compose exec web ./manage.py shell

dbshell:
	docker-compose exec web ./manage.py dbshell
