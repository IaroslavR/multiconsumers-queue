SHELL = /bin/bash

.PHONY: help install build tests publish-test
.DEFAULT_GOAL = help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## install package deps locally
	poetry install

build:  ## Build package
	poetry build

tests:  ## Run tests
	poetry check
	poetry run pytest
	poetry run mypy multiconsumers_queue

publish-test: tests ## Publish package to the test.pypi.org
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi --build

publish: tests build  ## Publish package
	poetry publish
