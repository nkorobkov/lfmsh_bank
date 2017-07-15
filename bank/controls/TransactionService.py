from bank.constants.TransactionTypeEnum import TransactionTypeEnum
from bank.controls.transaction_controllers.FacAttendTransactionController import FacAttendTransactionController
from bank.controls.transaction_controllers.LectureTransactionController import LectureTransactionController
from bank.controls.transaction_controllers.SeminarTransactionController import SeminarTransactionController
from bank.controls.transaction_controllers.P2PTransactionController import P2PTransactionController
from bank.controls.transaction_controllers.GeneralTransactionController import GeneralTransactionController
from bank.controls.transaction_controllers.WorkoutTransactionController import WorkoutTransactionController


class TransactionService:

    @staticmethod
    def get_controller_for(trans_type):
        if trans_type == TransactionTypeEnum.general_money.value:
            return GeneralTransactionController
        if trans_type == TransactionTypeEnum.p2p.value:
            return P2PTransactionController
        if trans_type == TransactionTypeEnum.seminar.value:
            return SeminarTransactionController
        if trans_type == TransactionTypeEnum.lecture.value:
            return LectureTransactionController
        if trans_type == TransactionTypeEnum.workout.value:
            return WorkoutTransactionController
        if trans_type == TransactionTypeEnum.fac_attend.value:
            return FacAttendTransactionController

        raise ModuleNotFoundError('no controller for this type')

