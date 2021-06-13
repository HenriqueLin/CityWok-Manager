from flask import Blueprint
from flask.cli import AppGroup
from citywok_ms import db

command = Blueprint("command", __name__, cli_group=None)


db_cli = AppGroup("db")


@db_cli.command("create")
def create():
    "Create the database"
    print("Creating all tables")
    db.create_all()

    print("Success.")


@db_cli.command("drop")
def drop():
    "Drop the database"
    msg = "Drop All"
    i = input(f'Please type "{msg}" to confirm the operation\n')
    if i == msg:
        print("Droping all tables")
        db.drop_all()
        print("Success.")
    else:
        print("Wrong input, exit.")


command.cli.add_command(db_cli)
