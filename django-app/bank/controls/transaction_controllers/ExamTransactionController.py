import math
from django.contrib.auth.models import User

from bank.constants import MoneyTypeEnum, TransactionTypeEnum, EXAM_BUDGET
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import ExamKernelForm
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction


class ExamTransactionController(TableTransactionController):
    template_url = 'bank/add/add_exam.html'
    value_show_name = 'Баллы за экзамен'
    header = "Экзамен"

    @staticmethod
    def _get_kernel_form():
        return ExamKernelForm


    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):

        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(name =TransactionTypeEnum.exam.value),
                                                      formset_data, update_of)
        scores = list(filter(None.__ne__, [data['value'] for data in formset_data]))

        money_type = MoneyType.objects.get(name=MoneyTypeEnum.exam.value)

        for atomic_data in formset_data:
            value = atomic_data['value']
            if value:
                reward = ExamTransactionController._get_exam_reward(value,scores)
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Money.new_money(receiver, reward,
                                money_type,
                                first_form['description'],
                                new_transaction)
        return new_transaction

    @staticmethod
    def _get_exam_reward(value, scores):
        sum_normalized_score = sum([math.sqrt(max(0, s)) for s in scores])
        num_of_participants = len(scores)
        score = max(0., float(value))
        normalized_score = math.sqrt(score)
        reward = max(0., (float(EXAM_BUDGET) * num_of_participants) * normalized_score / (sum_normalized_score))
        return reward
