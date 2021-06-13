import os
import shutil
import click
from flask import Blueprint, current_app
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
    "Drop the database and remove all user files"
    db.drop_all()
    click.echo("Dropped all tables.")

    path = current_app.config["UPLOAD_FOLDER"]
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
        click.echo(f"Deleted {filename}.")
    click.echo("Deleted all files.")



command.cli.add_command(db_cli)
