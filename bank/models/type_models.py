# coding=utf-8

from django.db import models


class TransactionType(models.Model):
    name = models.CharField(max_length=31)
    human_name = models.CharField(max_length=127, default='Other')
    group1 = models.CharField(max_length=31, blank=True, null=True)
    group2 = models.CharField(max_length=31, blank=True, null=True)
    group1_hn = models.CharField(max_length=127, default='Other')
    group2_hn = models.CharField(max_length=127, default='Other')
    has_custom_form = models.BooleanField(default=False)

    def __unicode__(self):
        return self.human_name


class TransactionStatus(models.Model):
    name = models.CharField(max_length=31)
    human_name = models.CharField(max_length=127)
    counted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.human_name
