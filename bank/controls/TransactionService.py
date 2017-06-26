from bank.constants.TransactionTypeEnum import TransactionTypeEnum
from bank.controls.transaction_controllers.GeneralTransactionController import GeneralTransactionController


class TransactionService:

    @staticmethod
    def get_controller_for(trans_type):
        if trans_type == TransactionTypeEnum.general_money.value:
            return GeneralTransactionController
        raise ModuleNotFoundError('no controller for this type')

