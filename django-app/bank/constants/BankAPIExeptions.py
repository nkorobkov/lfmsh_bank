class BankAPIExeption(Exception):
    """Base class for exceptions in this module."""

    def __init__(self):
        self.message = 'Bank API error occurred'
        self.code = 460


class TransactionTypeNotSupported(BankAPIExeption):
    def __init__(self, type_name):
        self.message = "Adding {} transactions through API is not supported in the moment".format(type_name)
        self.code = 461


class SelfMoneyTransfer(BankAPIExeption):
    def __init__(self):
        self.message = "Can't transfer money to yourself"
        self.code = 462


class EmptyDescriptionError(BankAPIExeption):
    def __init__(self):
        self.message = "Description can't be empty"
        self.code = 463


class CreatorDoNotMatchRequestOwner(BankAPIExeption):
    def __init__(self):
        self.message = "CreatorDoNotMatchRequestOwner"
        self.code = 464


class CantCreateThisType(BankAPIExeption):
    def __init__(self, type_name):
        self.message = "User Cant create {} transactions".format(type_name)
        self.code = 465


class TransactionTypeNotRecognized(BankAPIExeption):
    def __init__(self):
        self.message = "TransactionTypeNotRecognized"
        self.code = 466


class UserDoesNotExist(BankAPIExeption):
    def __init__(self, username):
        self.message = "User with username {} does not exist".format(username)
        self.code = 467


class P2PIllegalAmount(BankAPIExeption):
    def __init__(self, value):
        self.message = "Can't transfer {}@".format(value)
        self.code = 470
