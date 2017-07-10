import json

from django.contrib.auth.models import User
from django.db import models

from bank.constants import States
from bank.models import TransactionType, TransactionState


class Transaction(models.Model):
    creator = models.ForeignKey(User, related_name='created_transactions', on_delete=models.PROTECT, null=False)
    creation_map = models.CharField(max_length=262143)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, null=False)
    state = models.ForeignKey(TransactionState)
    update_of = models.ForeignKey("self", null=True)

    @classmethod
    def new_transaction(cls, creator, type, creation_map, update_of=None):
        create_state = TransactionState.objects.get(name=States.created.value)

        new_transaction = cls(creator=creator, type=type,
                              creation_map=json.dumps(creation_map), update_of=Transaction.objects.get(id=update_of) if update_of else None, state=create_state)
        new_transaction.save()
        return new_transaction

    def process(self):
        if self.can_be_transitioned_to(States.processed.value):
            if not self.state.counted:
                for atomic in self.get_all_atomics():
                    atomic.apply()
            self.state = TransactionState.objects.get(name=States.processed.value)
            self.save()
        else:
            raise AttributeError('process called when not expected')

    def decline(self):
        if self.can_be_transitioned_to(States.declined.value):
            self._undo()
            self.state = TransactionState.objects.get(name=States.declined.value)
            self.save()
        else:
            raise AttributeError('decline called when not expected')

    def substitute(self):
        if self.can_be_transitioned_to(States.substituted.value):
            self._undo()
            self.state = TransactionState.objects.get(name=States.substituted.value)
            self.save()
        else:
            raise AttributeError('substitute called when not expected')

    def _undo(self):
        if self.state.counted:
            for atomic in self.get_all_atomics():
                atomic.undo()
            self.save()

    def get_all_atomics(self):
        return list(self.related_attendance_atomics.all()) + list(self.related_money_atomics.all())

    def can_be_transitioned_to(self, state_name):
        return len(self.state.possible_transitions.filter(name=state_name)) > 0

    def __str__(self):
        return "{}@ для {} пионеров".format(sum([a.value for a in list(self.related_money_atomics.all())]),
                                            len(self.related_money_atomics.values_list()))

    def receivers_count(self):
        atomics = self.get_all_atomics()
        return len(set([at.receiver.username for at in atomics]))

    def money_count(self):
        return sum([a.value for a in self.related_money_atomics.all()])

