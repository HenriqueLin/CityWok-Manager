# CityWok Manager

[![Tests](https://github.com/HenriqueLin/CityWok-Manager/actions/workflows/tests.yml/badge.svg)](https://github.com/HenriqueLin/CityWok-Manager/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/HenriqueLin/CityWok-Manager/branch/develop/graph/badge.svg?token=PCSK7B85XY)](https://codecov.io/gh/HenriqueLin/CityWok-Manager)
![license](https://img.shields.io/github/license/HenriqueLin/CityWok-Manager)
![Uptime Robot status](https://img.shields.io/uptimerobot/status/m788531133-9727a88c922e36fa09bd5a3a)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Introduction
A website base management system for a restaurante.

## Usage
### Prepare
Create a `.env` file under root directory with following context
```
SECRET_KEY=...
ADMIN_NAME=...
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
MAIL_USERNAME=...
MAIL_PASSWORD=...
DATABASE_URL=...
```
Change the `FLASK_ENV` in `.flaskenv` in production
```
...
FLASK_ENV=production
```
### Install
```sh
$ sudo apt install ghostscript redis-server

# Upgrade pip
$ python -m pip install --upgrade pip

# Install libraries
$ if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```
### Launch
```
$ flask run
```
### Test
```sh
# Test all files
$ python -m pytest

# Test with output
$ python -m pytest -s

# Test with coverage report
$ python -m pytest --cov-report term-missing
```
### Database Migration
Commands provided by `flask-migrate`
```sh
# Generate a migration
flask db migrate
# Apply the migration to the database
flask db upgrade
```

### Utils
Some utils commands created using `click`
```sh
# Create the database
$ flask dev create
# Load some example data
$ flask dev load_example
# Drop the database and filse
$ flask dev drop
# Add a new user
$ flask dev add_user USERNAME EMAIL PASSWORD ROLE [CONFIRMED]

# Initialize translation file for a language
$ flask i18n init LANG
# Update the translation file
$ flask i18n update
# Compile the translation file
$ flask i18n compile
```

## Tools
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite3](https://www.sqlite.org/)
- [SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io/en/latest/)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)
- [Flask-Babel](https://flask-babel.tkte.ch/#)
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- [Flask-Principal](https://pythonhosted.org/Flask-Principal/)
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/0.15.x/)
- [WTForms](https://wtforms.readthedocs.io/en/2.3.x/)
- [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- [Flask-Moment](https://flask-moment.readthedocs.io/en/latest/)
- [Click](https://click.palletsprojects.com/en/8.0.x/)
- [Pytest](https://docs.pytest.org/en/6.2.x/)
- [Pytest-Mock](https://github.com/pytest-dev/pytest-mock/)
- [Pytest-Cov](https://github.com/pytest-dev/pytest-cov)
- [Pytest-flask](https://pytest-flask.readthedocs.io/en/latest/)
- [Sentry.io](https://docs.sentry.io/platforms/python/guides/flask/)

## References
- Miguel Grinberg's [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- Corey Schafer's [Python Flask Tutorial](https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)

## Changelog
[Here](CHANGELOG.md)

## License
[MIT](LICENSE.txt)
