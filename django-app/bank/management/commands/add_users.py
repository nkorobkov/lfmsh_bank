import csv
import string

from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand
from django.utils.crypto import random

from transliterate import translit

from bank.constants import UserGroups, BANKIR_USERNAME, TransactionTypeEnum, MoneyTypeEnum, INITIAL_MONEY, \
    INITIAL_MONEY_DESC
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction
from bank.models.Account import Account

from main.settings import BASE_DIR
from django.db.utils import IntegrityError

class Command(BaseCommand):
    args = 'No args'
    help = 'will add student and staff users to db'

    # all file adreses should be in constants here
    STATIC_DATA_PATH = '/meta_files/users_data/'
    STAFF_DATA = 'staff.csv'
    STUDENT_DATA = 'student.csv'
    STAFF_DATA_OUT = 'staff_out.txt'
    STUDENT_DATA_OUT = 'student_out.txt'

    def handle(self, *args, **options):
        if options.get("student", "none") != "none":
            Command.STUDENT_DATA = options.get("student")
        if options.get("staff", "none") != "none":
            Command.STAFF_DATA = options.get("staff")
        if options.get("student_out", "none") != "none":
            Command.STUDENT_DATA_OUT = options.get("student_out")
        if options.get("staff_out", "none") != "none":
            Command.STAFF_DATA_OUT = options.get("staff_out")

        if self.flush_all_users():

            self.add_bank_user()
            self.add_users(Command.STAFF_DATA, Command.STAFF_DATA_OUT, UserGroups.staff.value)
            self.add_users(Command.STUDENT_DATA, Command.STUDENT_DATA_OUT, UserGroups.student.value)
            self.add_initial_money(UserGroups.student.value)

    @staticmethod
    def flush_all_users():

        a = input("this command will delete all existing users and transactions info and create new ones"
              "are you sure you want to continue ? (print yes to proceed)")
        if a == "yes":
            Account.objects.all().delete()
            User.objects.all().delete()
            return True
        return False

    @staticmethod
    def add_users(data_path, out_path, group):
        data = Command.read_file_as_csv(data_path)
        out = open(BASE_DIR + Command.STATIC_DATA_PATH + out_path, 'w')

        group = Group.objects.get(name=group)
        for person in data:
            print(person)
            last_name = person[0]
            first_name = person[1]
            if len(person)>2:
                middle_name = person[2]
            else:
                middle_name=''
            if len(person) > 3:
                party = person[3]
            else:
                party = 0
            if len(person) > 4:
                grade = person[4]
            else:
                grade = 0

            password = Command.generate_password(8)
            user_created = False
            need_unique_login = False 

            while not user_created:
                try:
                    login = Command.generate_login(first_name, last_name, middle_name, need_unique_login)
    
                    new_u = User.objects.create_user(first_name=first_name, last_name=last_name, username=login,
                                                 password=password)
                    new_u.save()
                    group.user_set.add(new_u)
                    new_a = Account(user=new_u, middle_name=middle_name, grade=grade, party=party)
                    new_a.save()
                    user_created = True
                except IntegrityError as e:
                    need_unique_login = True


            out.write('\n\n' + '-' * 20 + '\n')
            out.write(' '.join(person) + '\n')
            out.write('Login: ' + login + ' Password: ' + password)
            print(' '.join(person), login, password)


    @staticmethod
    def add_bank_user():
        login = BANKIR_USERNAME
        password = Command.generate_password(8)
        new_u = User.objects.create_user(first_name="Банкир", last_name="ЛФМШ", username=login,
                                             password=password)
        new_u.save()
        new_a = Account(user=new_u, middle_name="Ф", grade=0, party=0)
        new_a.save()
        group = Group.objects.get(name='admin')
        group.user_set.add(new_u)

        
        out = open(BASE_DIR + Command.STATIC_DATA_PATH + "bankir.txt", 'w')
        out.write(' Банкир ЛФМШ \n')
        out.write('Login: ' + login + ' Password: ' + password)
        print("admin:   ", login, password)

    @staticmethod
    def add_initial_money(group_name):
        creator = User.objects.get(username=BANKIR_USERNAME)
        t_type = TransactionType.objects.get(name=TransactionTypeEnum.general_money.value)
        money_type = MoneyType.objects.get(name=MoneyTypeEnum.initial.value)
        new_transaction = Transaction.new_transaction(creator, t_type, {})
        for student in User.objects.filter(groups__name=group_name):
            Money.new_money(student, INITIAL_MONEY, money_type, INITIAL_MONEY_DESC, new_transaction)
        new_transaction.process()



    @staticmethod
    def generate_password(length):
        s = ''
        for c in range(length):
            a = random.sample(string.printable[:62].replace("l","").replace("1",'').replace('I','').replace('i',''), 1)
            s = s + a[0]
        return s

    @staticmethod
    def generate_login(first_name, last_name, middle_name='', need_unique=False):
        middle_name_repr = '.'+translit(middle_name[0], 'ru',reversed=True).lower()+'.' if  middle_name  else ''

        first_name_processed = ''.join(filter(str.isalpha, translit(first_name, 'ru', reversed=True))).lower()
        last_name_processed = ''.join(filter(str.isalpha, translit(last_name, 'ru', reversed=True))).lower()

        if need_unique:
            return last_name_processed+middle_name_repr+first_name_processed
        else:
            return last_name_processed


    @staticmethod
    def read_file_as_csv(path):
        f = open(BASE_DIR + Command.STATIC_DATA_PATH + path)
        return csv.reader(f)
