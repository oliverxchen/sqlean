# Run the tests and linters
test:
	poetry run pytest \
		--black \
		--flake8 \
		--pylint \
		--cov=sqlean --cov-fail-under=80 --cov-report html \
		--mypy

# Run the tests in watch mode
test-watch:
	poetry run ptw -- --testmon


##############################################################################
# The commands below are just for people who are not familiar with poetry. If
# you are familiar with poetry, go ahead and use the poetry commands
##############################################################################

# Installs all dependencies, including dev dependencies.
# Equivalent to: `pip install -e .`
install:
	poetry install

# Install only the non-dev dependencies.
install-prod:
	poetry install --no-dev

# Update the poetry.lock with the latest dependencies that fall within the
# constraints of pyproject.toml
update:
	poetry update

# source the virtual environment that has been setup for this project
# to exit: `exit`
venv:
	poetry shell
