from bank.management.commands.add_static_data import Command


def seed_db():
    command = Command()
    command.add_static_data(silent=True)
