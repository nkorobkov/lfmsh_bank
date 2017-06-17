from django.db import models


class AbstractType(models.Model):
    name = models.CharField(max_length=127)
    readable_name = models.CharField(max_length=511)

    def __str__(self):
        return self.readable_name

    class Meta:
        abstract = True
