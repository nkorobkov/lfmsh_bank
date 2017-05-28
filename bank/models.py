# coding=utf-8

from django.db import models
from django.contrib.auth.models import User
import helper_functions as hf
from constants import *

# Create your models here.


class Account(models.Model):
    '''
    Extension of a user class
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    balance = models.FloatField(default=0)
    third_name = models.CharField(max_length=40, default='Not stated')

    otr = models.IntegerField(default=0)

    grade = models.IntegerField(blank=True, default=0)

    lab_passed = models.IntegerField(blank=True, default=0)
    fac_passed = models.IntegerField(blank=True, default=0)
    sem_fac_attend = models.IntegerField(blank=True, default=0)
    lec_missed = models.IntegerField(blank=True, default=0)
    sem_read = models.IntegerField(blank=True, default=0)


    def get_penalty(self):
        p = 0
        p += max(0, (self.lab_needed() - int(self.lab_passed))) * LAB_PENALTY #labs
        p += hf.sem_fac_penalty(max(0, (hf.sem_needed - int(self.sem_fac_attend)))) #semfac attend
        p += SEM_NOT_READ_PEN * max(0, 1 - int(self.sem_read))
        return p



    def __unicode__(self):
        if self.user.first_name:

            return self.user.last_name + ' ' + self.user.first_name[0] + '. ' + self.third_name[0] + '.'
        else:
            return self.user.last_name

    def long_name(self):
        return self.user.last_name + ' ' + self.user.first_name + ' ' + self.third_name

    def short_name(self):
        if self.user.first_name:

            return self.user.last_name + ' ' + self.user.first_name[0] + '. ' + self.third_name[0] + '.'
        else:
            return self.user.last_name

    def lab_needed(self):
        if self.grade < 9:
            return 3
        return 2

    def fac_needed(self):
        if self.grade < 9:
            return 0
        return 1

    def sem_att_needed(self):

        return hf.sem_needed


    def sem_att_w(self):
        print 100 * int(self.sem_fac_attend) / self.sem_att_needed()
        return (100 * int(self.sem_fac_attend) / self.sem_att_needed())

    def lab_passed_w(self):

        print 100 * int(self.lab_passed) / self.lab_needed()
        return (100 * int(self.lab_passed) / self.lab_needed())

    def fac_passed_w(self):
        if self.fac_needed():
            print 100 * int(self.fac_passed) / self.fac_needed()
            return (100 * int(self.fac_passed) / self.fac_needed())

    def sem_read_w(self):

        return int(self.sem_read) * 100


    def get_balance(self):
        if abs(self.balance) > 9.99:
            return int(self.balance)
        return round(self.balance, 1)


class TransactionType(models.Model):
    name = models.CharField(max_length=30)
    human_name = models.CharField(max_length=100, default='Other')
    group1 = models.CharField(max_length=30, blank=True, null=True)
    group2 = models.CharField(max_length=30, blank=True, null=True)
    group1_hn =  models.CharField(max_length=100, default='Other')
    group2_hn =  models.CharField(max_length=100, default='Other')
    def __unicode__(self):
        return self.human_name


class TransactionStatus(models.Model):
    name = models.CharField(max_length=30)
    human_name = models.CharField(max_length=30)
    counted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.human_name


class Transaction(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)

    recipient = models.ForeignKey(User, related_name='received_trans', on_delete=models.CASCADE,null=True)
    creator = models.ForeignKey(User, related_name='created_trans', on_delete=models.CASCADE)

    description = models.TextField(max_length=400, blank=True)
    value = models.FloatField(default=0)

    counted = models.BooleanField(default=False, editable=False)

    type = models.ForeignKey(TransactionType)
    status = models.ForeignKey(TransactionStatus)

    modifier = models.ForeignKey(User, blank=True, null=True, related_name='modified_trans')
    last_modified_date = models.DateTimeField(blank=True, null=True)


    def __unicode__(self):
        return self.creator.username + " " + str(self.value)

    @classmethod
    def create_trans(cls, recipient, value, creator, description, type, status):


        if type.group1 == 'fine' or type.group1 == 'payment':
            value = - value


        new_trans = cls(recipient=recipient, value=value, creator=creator, description=description,
                        type=type, status=status)

        if status.name == 'PR' and recipient != None:
            a = new_trans.count()
            if a:
                new_trans.do_counters(1)
        else:
            new_trans.save()

        return new_trans


    def count(self):

        if self.counted:
            return False

        if self.type.group1 != 'attend':
            a = self.recipient.account
            a.balance = a.balance + self.value
            a.save()

            a = self.creator.account
            a.balance = a.balance - self.value
            a.save()
        else:
            #return false if attend is imposible
            if Transaction.objects.filter(recipient=self.recipient).filter(value__in=[((int(self.value)//100) * 100 + a) for a in SF_IMPOSIBLE[int(self.value) % 100]]).filter(counted=True):
                return False

        self.counted = True
        self.save()
        return True


    def do_counters(self, value):

        if self.type.name == 'fac_pass':
            a = self.recipient.account
            a.fac_passed += value
            a.save()

        if self.type.group1 == 'attend' and self.type.name != 'lec_attend':
            a = self.recipient.account
            a.sem_fac_attend += value
            a.save()

        if self.type.name == 'lab_pass':
            a = self.recipient.account
            a.lab_passed += value
            a.save()

        if self.type.name == 'fine_lec':
            a = self.recipient.account
            a.lec_missed += value
            a.save()
        if self.type.name == 'sem':
            a = self.recipient.account
            a.sem_read += value
            a.save()


    def cancel(self):


        if not self.counted:
            return False



        if self.type.group1 != 'attend':
            a = self.recipient.account
            a.balance = a.balance - self.value
            a.save()

            a = self.creator.account
            a.balance = a.balance + self.value
            a.save()
        else:
            if len(Transaction.objects.filter(value=self.value).filter(recipient=self.recipient).filter(counted=True)) != 1:
                self.counted = False
                self.save()
                return False

        self.do_counters(-1)
        self.counted = False
        self.save()

        return True


    def can_be_declined(self):
        if self.status.name in ['DA', 'DC']:
            return False
        if self.type.name == 'p2p' and self.status.name == 'PR':
            return False
        print self.meta.all()
        print len(self.meta.all())
        if len(self.meta.all()) != 0:
            return False

        return True


    def get_creation_date(self):
        return self.creation_date.strftime("%d.%m.%Y %H:%M")

    def get_value(self):
        if abs(self.value) > 9.9:
            return int(self.value)
        return round(self.value, 1)

    def get_value_as_date(self):
        year = 2000 + int(self.value) // 1000000
        month = (int(self.value) // 10000) % 100
        day = (int(self.value) // 100) % 100
        block = (int(self.value) ) % 10
        if (int(self.value)//10) % 10 == SEM_IND:
            if (int(self.value)) % 10 == 0:
                return unicode('Лекция', 'utf-8')
            return unicode('{0}.{1}.{2}, {3} блок семинаров'.format(year, month, day, block), 'utf-8')
        return unicode('{0}.{1}.{2}, {3} блок факультативов'.format(year, month, day, block), 'utf-8')

class MetaTransaction(models.Model):
    creation_dict = models.CharField(max_length=20000)


    transactions = models.ManyToManyField(Transaction, default=None, blank=True, related_name='meta')
    meta = models.ForeignKey(Transaction, null=True, related_name='meta_link')
