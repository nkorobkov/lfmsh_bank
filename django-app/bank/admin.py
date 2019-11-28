from django.contrib import admin

# Register your models here.
from bank.models.TransactionType import TransactionType
from bank.models.AttendanceBlock import AttendanceBlock
from bank.models.Money import Money
from bank.models.TransactionState import TransactionState
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction
from bank.models.Account import Account

from django.contrib.auth.models import Permission

admin.site.register(Permission)
admin.site.register(Account)

admin.site.register(Transaction)
admin.site.register(TransactionType)
admin.site.register(TransactionState)
admin.site.register(AttendanceBlock)


admin.site.register(AttendanceType)
admin.site.register(MoneyType)
admin.site.register(Money)
admin.site.register(Attendance)
