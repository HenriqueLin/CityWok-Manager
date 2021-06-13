from flask.testing import FlaskCliRunner
import pytest
from citywok_ms.cli import create, drop
from flask.cli import shell_command


def test_db_create(client, app):
    runner = FlaskCliRunner(app)
    result = runner.invoke(create)

    assert not result.exception
    assert result.output == "Created all tables.\n"


@pytest.mark.parametrize("input, output", [("y", "Dropped"), ("n", "Abort")])
def test_db_drop_yes(client, app, input, output):
    runner = FlaskCliRunner(app)
    result = runner.invoke(drop, input=input)

    assert output in result.output


def test_shell(client, app):
    runner = FlaskCliRunner(app)
    result = runner.invoke(shell_command)

    assert result.exit_code == 0
    assert app.name in result.output
