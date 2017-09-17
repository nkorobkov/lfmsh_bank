from django.db import models


class AbstractType(models.Model):
    name = models.CharField(max_length=127, unique=True)
    readable_name = models.CharField(max_length=511)

    def full_info_as_list(self):
        return [
            self.readable_name
        ]

    def full_info_headers_as_list(self):
        return [
            'type_readable_name'
        ]

    def __str__(self):
        return self.readable_name

    class Meta:
        abstract = True
