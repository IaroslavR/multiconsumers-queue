SHELL = /bin/bash

.PHONY: help install build tests publish-test
.DEFAULT_GOAL = help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## Install package deps locally
	poetry install

build:  ## Build package
	poetry build

bootstrap:  install ## Init tools
	poetry run pre-commit install


test-annotations:  # mypy, pytest etc.
	poetry run mypy multiconsumers_queue
	pytest --typeguard-packages=multiconsumers_queue
	poetry run pytype --disable=import-error multiconsumers_queue

test:  ## Run tests
	poetry check
	poetry run pytest
	poetry run flake8
	poetry export --dev --format=requirements.txt --without-hashes --output=requirements.txt
	poetry run safety check --full-report --file=requirements.txt
	rm requirements.txt

coverage:
	poetry run coverage run -m pytest
	poetry run coverage report

publish-test: test build ## Publish package to the test.pypi.org
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

publish: test build  ## Publish package
	poetry publish
