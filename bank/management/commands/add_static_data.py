import datetime
import json

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from bank.constants import UserGroups, Actions
from bank.models import TransactionState, MoneyType, AttendanceType, TransactionType, AttendanceBlock
from main.settings import BASE_DIR


class Command(BaseCommand):
    args = 'No args'
    help = 'will add all needed types groups and states to db'

    # all file adreses should be in constants here
    STATIC_DATA_PATH = '/meta_files/static_data/'
    MONEY_TYPES_DATA = 'money_types.json'
    ATTENDANCE_TYPES_DATA = 'attendance_types_json.json'
    TRANSACTION_STATES_DATA = 'transaction_states.json'
    TRANSACTION_TYPES_DATA = 'transaction_types.json'
    GROUPS_DATA = 'user_groups.json'
    BLOCKS_DATA = 'attendance_blocks.json'

    def handle(self, *args, **options):
        self.add_static_data()

    def add_static_data(self):
        self.add_transaction_states()
        self.add_atomic_types(MoneyType, Command.MONEY_TYPES_DATA)
        self.add_atomic_types(AttendanceType, Command.ATTENDANCE_TYPES_DATA)
        self.add_transaction_types()
        self.add_user_groups()

        self.add_transaction_permissions()
        self.add_groups_permissions()
        self.add_permissions_to_groups()

        self.add_attendance_blocks()

    @staticmethod
    def add_transaction_states():
        states = Command.read_file_as_json(Command.TRANSACTION_STATES_DATA)

        for state in states:
            s, created = TransactionState.objects.get_or_create(name=state['name'],
                                                                readable_name=state['readable_name'],
                                                                counted=state['counted'])
            s.save()

        for state in states:
            s = TransactionState.objects.get(name=state['name'])
            for trans_name in state['possible_transitions']:
                t = TransactionState.objects.get(name=trans_name)
                s.possible_transitions.add(t)
            s.save()

    @staticmethod
    def add_atomic_types(model, path):

        types = Command.read_file_as_json(path)

        for general_group_name, general_group_value in types.items():
            general_group_readable_name = general_group_value['readable_general']

            for local_group_name, local_group_value in general_group_value.items():
                if local_group_name == 'readable_general':
                    continue
                local_group_readable_name = local_group_value['readable_local']

                for type_name, type_readable_name in local_group_value.items():
                    if type_name == 'readable_local':
                        continue

                    atomic_type, created = model.objects.get_or_create(group_general=general_group_name,
                                                                       group_local=local_group_name,
                                                                       readable_group_local=local_group_readable_name,
                                                                       readable_group_general=general_group_readable_name,
                                                                       name=type_name, readable_name=type_readable_name)
                    atomic_type.save()

    @staticmethod
    def add_transaction_types():
        types = Command.read_file_as_json(Command.TRANSACTION_TYPES_DATA)

        for trans_type in types:
            new_type, created = TransactionType.objects.get_or_create(name=trans_type['name'],
                                                                      readable_name=trans_type['readable_name'])
            new_type.save()

            Command.add_type_to_atomic_type(trans_type['money'], new_type, MoneyType)
            Command.add_type_to_atomic_type(trans_type['attendance'], new_type, AttendanceType)

    @staticmethod
    def add_user_groups():
        for group in UserGroups:
            Group.objects.get_or_create(name=group.value)

    @staticmethod
    def add_transaction_permissions():
        per_trans_type_permissions = [Actions.create, Actions.decline, Actions.process, Actions.update]
        types = Command.read_file_as_json(Command.TRANSACTION_TYPES_DATA)
        for trans_type in types:
            for perm in per_trans_type_permissions:
                name = Command.make_perm_name(perm.value, 'self', trans_type['name'])
                print(name)
                content_type = ContentType.objects.get_for_model(TransactionType)
                new_perm = Permission.objects.get_or_create(codename=name, name=name, content_type=content_type)[0]
                new_perm.save()

    @staticmethod
    def add_groups_permissions():
        per_group_permissions = [Actions.see, Actions.process, Actions.decline]
        targets = [u.value for u in UserGroups] + ['self']
        for target in targets:
            for perm in per_group_permissions:
                direction_modificators = ['created']
                if perm.value == 'see':
                    direction_modificators += ['received']
                for direction in direction_modificators:
                    name = Command.make_perm_name(perm.value, target, direction, 'transactions')
                    content_type = ContentType.objects.get_for_model(TransactionType)
                    new_perm = Permission.objects.get_or_create(codename=name, name=name, content_type=content_type)[0]
                    new_perm.save()
            for info in ['balance', 'attendance']:
                name = Command.make_perm_name(Actions.see.value, target, info)
                content_type = ContentType.objects.get_for_model(TransactionType)
                new_perm = Permission.objects.get_or_create(codename=name, name=name, content_type=content_type)[0]
                new_perm.save()

    @staticmethod
    def add_permissions_to_groups():
        groups = Command.read_file_as_json(Command.GROUPS_DATA)
        for group in groups:
            name = group['name']
            permissions = group['permissions']
            group_model = Group.objects.get(name=name)
            for action, per_action_perm in permissions.items():
                for target, perm_list in per_action_perm.items():
                    for perm in perm_list:
                        print(Command.make_perm_name(action, target, perm))

                        p = Permission.objects.get(name=Command.make_perm_name(action, target, perm))
                        group_model.permissions.add(p)

            group_model.save()

    @staticmethod
    def add_attendance_blocks():
        blocks_data = Command.read_file_as_json(Command.BLOCKS_DATA)
        for block_data in blocks_data:

            block, created = AttendanceBlock.objects.get_or_create(name=block_data['name'],
                                                                   readable_name=block_data['readable_name'],
                                                                   start_time=Command.time_from_string(
                                                                       block_data['start_time']),
                                                                   end_time=Command.time_from_string(
                                                                       block_data['end_time']))

            for att_type_name in block_data['related_attendance_types']:
                att_type = AttendanceType.objects.get(name=att_type_name)
                block.related_attendance_types.add(att_type)
            block.save()

    @staticmethod
    def read_file_as_json(path):
        f = open(BASE_DIR + Command.STATIC_DATA_PATH + path)
        return json.JSONDecoder().decode(f.read())

    @staticmethod
    def add_type_to_atomic_type(name_list, new_type, model):
        for atomic_type_name in name_list:
            atomic_type = model.objects.get(name=atomic_type_name)
            atomic_type.related_transaction_type = new_type
            atomic_type.save()

    @staticmethod
    def make_perm_name(*args):
        args = map(str, args)
        return '_'.join(args)

    @staticmethod
    def time_from_string(time_string):
        triple = time_string.split(':')
        ints = map(int, triple)
        return datetime.time(*ints)
