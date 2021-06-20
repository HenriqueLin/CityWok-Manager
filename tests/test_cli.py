import os

import pytest
from citywok_ms import db
from citywok_ms.cli import compile, create, drop, init, load_example, update
from flask.cli import shell_command
from flask.testing import FlaskCliRunner
import shutil


def test_dev_load_without_create(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    result = runner.invoke(load_example)
    assert not result.exception
    assert result.output == "Please create database first.\n"


def test_dev_load_duplicate(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    db.create_all()
    runner.invoke(load_example)
    result = runner.invoke(load_example)
    assert not result.exception
    assert result.output == "Database already loaded.\n"


def test_dev_load(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    db.create_all()
    result = runner.invoke(load_example)
    assert not result.exception
    assert result.output == "Loaded example entities.\n"


def test_dev_create(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    result = runner.invoke(create)

    assert not result.exception
    assert "Created all tables." in result.output
    assert "Created admin user." in result.output


@pytest.mark.parametrize("input, output", [("y", "Dropped"), ("n", "Abort")])
def test_dev_drop_yes(app_without_db, input, output):
    runner = FlaskCliRunner(app_without_db)
    db.create_all()
    runner.invoke(load_example)
    result = runner.invoke(drop, input=input)

    assert output in result.output


def test_shell(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    result = runner.invoke(shell_command)

    assert result.exit_code == 0
    assert app_without_db.name in result.output


def test_i18n(app_without_db):
    path = os.path.join(app_without_db.root_path, "translations/es")
    # i18n init
    runner = FlaskCliRunner(app_without_db)
    result = runner.invoke(init, "es -q")

    assert not result.exception
    assert os.path.isdir(path)
    assert os.path.isfile(os.path.join(path, "LC_MESSAGES/messages.po"))

    # i18n update
    result = runner.invoke(update, "-q")
    assert not result.exception

    # i18n compile
    result = runner.invoke(compile, "-q")
    assert not result.exception
    assert os.path.isfile(os.path.join(path, "LC_MESSAGES/messages.mo"))

    # clean up
    shutil.rmtree(path)
