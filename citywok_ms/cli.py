import click
from flask import Blueprint
from flask.cli import AppGroup
from citywok_ms import db

command = Blueprint("command", __name__, cli_group=None)


db_cli = AppGroup("db")


@db_cli.command("create")
def create():
    "Create the database"
    db.create_all()
    click.echo("Created all tables.")


@db_cli.command("drop")
@click.confirmation_option(prompt="Are you sure you want to drop the db?")
def drop():
    "Drop the database"
    db.drop_all()
    click.echo("Dropped all tables.")


command.cli.add_command(db_cli)
