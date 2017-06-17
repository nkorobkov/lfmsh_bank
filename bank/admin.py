from django.contrib import admin

# Register your models here.
from bank.models import *
from django.contrib.auth.models import Permission

admin.site.register(Permission)
admin.site.register(Account)

admin.site.register(Transaction)
admin.site.register(TransactionType)
admin.site.register(TransactionState)

admin.site.register(AttendanceType)
admin.site.register(MoneyType)
admin.site.register(Money)
admin.site.register(Attendance)
