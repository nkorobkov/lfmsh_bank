from django.contrib.auth.models import User
from django.db import models

from bank.constants import States
from bank.models import TransactionType, TransactionState


class Transaction(models.Model):
    creator = models.ForeignKey(User, related_name='created_transactions', on_delete=models.PROTECT, null=False)
    creation_map = models.CharField(max_length=262143)
    type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, null=False)
    state = models.ForeignKey(TransactionState)
    update_of = models.ForeignKey("self", null=True)

    @classmethod
    def new_transaction(cls, creator, type, creation_map, update_of=None):
        create_state = TransactionState.objects.get(name=States.created.value)
        new_transaction = cls(creator=creator, type=type,
                              creation_map=creation_map, update_of=update_of, state=create_state)
        new_transaction.save()
        return new_transaction

    def process(self):
        if self.can_be_transitioned_to(States.processed.value):
            for atomic in self.related_money_atomics.all():
                atomic.apply()
            self.state = TransactionState.objects.get(name=States.processed.value)
            self.save()
        else:
            raise AttributeError('processed called when not expected')

    def can_be_transitioned_to(self, state_name):
        return len(self.state.possible_transitions.filter(name=state_name)) > 0

    def __str__(self):
        return "{}@ для {} пионеров".format(sum([a.value for a in list(self.related_money_atomics.all())]), len(self.related_money_atomics.values_list()))
