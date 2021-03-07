ACT_FLAGS :=
LOG_LEVEL := INFO
MYPY_RUN_AGAINST_DEFAULT := *.py pybaseball tests
MYPY_RUN_AGAINST := $(MYPY_RUN_AGAINST_DEFAULT)
ONLY_MODIFIED := 1
TEST_RUN_AGAINST := tests
TEST_FLAGS := -n auto


ifeq ($(LOG_LEVEL), DEBUG)
	TEST_FLAGS += -v --log-cli-level=DEBUG
endif

ifeq ($(ONLY_MODIFIED), 1)
	_MODIFIED_FILES := $(shell git status | grep 'modified\|new' | xargs -n1 echo | grep -v ':' | grep [.]py$)
	_UNIQUE_MODIFIED_FILES := $(shell echo $(_MODIFIED_FILES) | sort | uniq)
	ifeq ($(MYPY_RUN_AGAINST), $(MYPY_RUN_AGAINST_DEFAULT))
		MYPY_RUN_AGAINST := $(_UNIQUE_MODIFIED_FILES)
	endif
endif

generate-team-ids:
	python -c "from pybaseball.teamid_lookup import _generate_teams; _generate_teams()"

install: upgrade-pip
	pip install -e .[test]

mypy:
	mypy --ignore-missing-imports --follow-imports silent $(MYPY_RUN_AGAINST)

test:
	pytest $(TEST_RUN_AGAINST) $(TEST_FLAGS) --doctest-modules --cov=pybaseball --cov-report term-missing

# The test-github-actions is here to allow any local developer to test the GitHub actions on their code
# before pushing and creating a PR. Just install act from https://github.com/nektos/act and run
# make test-github-actions
ACT_EXISTS := $(shell act --help 2> /dev/null)

ifeq ($(ACT_EXISTS),)
test-github-actions:
	@echo "Testing GitHub actions requires act to be installed. See: https://github.com/nektos/act"
else
test-github-actions:
	act pull_request -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 $(ACT_FLAGS)
endif

upgrade-pip:
	pip install --upgrade pip
