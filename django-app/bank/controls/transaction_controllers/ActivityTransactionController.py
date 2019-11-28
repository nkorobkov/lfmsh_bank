from django.contrib.auth.models import User

from bank.constants import TransactionTypeEnum, MoneyTypeEnum, ACTIVITY_REWARD, BOOK_CERTIFICATE_VALUE, \
    AttendanceTypeEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import ActivityKernelForm
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class ActivityTransactionController(TableTransactionController):
    template_url = 'bank/add/add_activity.html'
    value_show_name = 'Место'
    header = "Мероприятия"

    @staticmethod
    def _get_kernel_form():
        return ActivityKernelForm

    @staticmethod
    def get_initial_form_data(creator_username):
        initial = super(ActivityTransactionController, ActivityTransactionController).get_initial_form_data(
            creator_username)
        for in_data in initial:
            in_data['money_type'] = MoneyTypeEnum.evening_activity.value
        return initial

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])
        money_type = MoneyType.objects.get(name=first_form['money_type'])
        print(money_type)
        print(first_form)

        new_transaction = Transaction.new_transaction(creator,
                                                      TransactionType.objects.get(name=TransactionTypeEnum.activity.value),
                                                      formset_data, update_of)

        places = {key: list(filter(lambda t: t['place'] == str(key), formset_data)) for key in range(1, 5)}
        for place in places:
            if not places[place]:
                continue
            reward = ActivityTransactionController._get_reward_for_place(place, money_type, len(places[place]))
            for form in places[place]:
                receiver = User.objects.get(username=form['receiver_username'])
                if reward:
                    Money.new_money(receiver, reward,
                                    money_type,
                                    first_form['description'],
                                    new_transaction)

                    if form['cert'] and place == 1:
                        Attendance.new_attendance(receiver, BOOK_CERTIFICATE_VALUE,
                                                  AttendanceType.objects.get(name=AttendanceTypeEnum.book_certificate.value), first_form['description'],
                                                  form['date'], new_transaction)

        return new_transaction

    @staticmethod
    def _get_reward_for_place(place, money_type, num_of_att):
        if money_type.name == MoneyTypeEnum.sport_activity.value:
            return ActivityTransactionController._get_sport_reward(place)
        else:
            if place in [1, 2, 3]:
                if num_of_att == 1:
                    return ACTIVITY_REWARD[money_type.name].get('single')[place - 1]
                else:
                    return ACTIVITY_REWARD[money_type.name].get('team')[place - 1] / num_of_att

    @staticmethod
    def _get_sport_reward(place):
        if place in [1, 2, 3, 4]:
            return ACTIVITY_REWARD[MoneyTypeEnum.sport_activity.value].get('single')[place - 1]
