from bank.constants.TransactionTypeEnum import TransactionTypeEnum
from bank.controls.transaction_controllers.P2PTransactionController import P2PTransactionController
from bank.controls.transaction_controllers.GeneralTransactionController import GeneralTransactionController


class TransactionService:

    @staticmethod
    def get_controller_for(trans_type):
        if trans_type == TransactionTypeEnum.general_money.value:
            return GeneralTransactionController
        if trans_type == TransactionTypeEnum.p2p.value:
            return P2PTransactionController
        raise ModuleNotFoundError('no controller for this type')

