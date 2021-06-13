from flask.testing import FlaskCliRunner
import pytest
from citywok_ms.cli import create, drop, load_example
from flask.cli import shell_command
from citywok_ms import db


def test_db_load_without_create(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    result = runner.invoke(load_example)
    assert not result.exception
    assert result.output == "Please create database first.\n"


def test_db_load_duplicate(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    db.create_all()
    runner.invoke(load_example)
    result = runner.invoke(load_example)
    assert not result.exception
    assert result.output == "Database already loaded.\n"


def test_db_load(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    db.create_all()
    result = runner.invoke(load_example)
    assert not result.exception
    assert result.output == "Loaded example entities.\n"


def test_db_create(app_without_db):
    runner = FlaskCliRunner(app_without_db)
    result = runner.invoke(create)

    assert not result.exception
    assert result.output == "Created all tables.\n"


@pytest.mark.parametrize("input, output", [("y", "Dropped"), ("n", "Abort")])
def test_db_drop_yes(app_without_db, input, output):
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
