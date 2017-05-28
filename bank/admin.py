from django.contrib import admin

# Register your models here.
from bank.models import Account, Transaction, TransactionType, TransactionStatus, MetaTransaction
from django.contrib.auth.models import Permission

admin.site.register(Permission)
admin.site.register(Account)

admin.site.register(Transaction)
admin.site.register(TransactionType)
admin.site.register(TransactionStatus)
admin.site.register(MetaTransaction)
