import csv
import string

from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand
from django.utils.crypto import random

from transliterate import translit

from bank.constants import UserGroups
from bank.models import Account
from main.settings import BASE_DIR


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

            self.add_users(Command.STUDENT_DATA, Command.STUDENT_DATA_OUT, UserGroups.student.value)
            self.add_users(Command.STAFF_DATA,Command.STAFF_DATA_OUT, UserGroups.staff.value)

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
            middle_name = person[2]
            if len(person) > 3:
                party = person[3]
            else:
                party = 0
            if len(person) > 4:
                grade = person[4]
            else:
                grade = 0

            login = Command.generate_login(first_name, last_name, middle_name)
            password = Command.generate_password(8)

            new_u = User.objects.create_user(first_name=first_name, last_name=last_name, username=login,
                                             password=password)
            new_u.save()
            group.user_set.add(new_u)
            new_a = Account(user=new_u, middle_name=middle_name, grade=grade, party=party)
            new_a.save()

            out.write('\n\n' + '-' * 20 + '\n')
            out.write(' '.join(person) + '\n')
            out.write('Login: ' + login + ' Password: ' + password)
            print(' '.join(person), login, password)


    @staticmethod
    def generate_password(length):
        s = ''
        for c in range(length):
            a = random.sample(string.printable[:62], 1)
            s = s + a[0]
        return s

    @staticmethod
    def generate_login(first_name, last_name, middle_name):
        login = translit(first_name[0], 'ru', reversed=True) + translit(middle_name[0], 'ru',
                                                                        reversed=True) + translit(last_name, 'ru',
                                                                                                  reversed=True)
        login = ''.join(filter(str.isalpha, login))
        return login.lower()


    @staticmethod
    def read_file_as_csv(path):
        f = open(BASE_DIR + Command.STATIC_DATA_PATH + path)
        return csv.reader(f)
