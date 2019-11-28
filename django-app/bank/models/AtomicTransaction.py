from django.db import models
from django.utils.timezone import now



class AtomicTransaction(models.Model):
    update_timestamp = models.DateTimeField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)

    description = models.TextField(max_length=1023, blank=True)
    value = models.FloatField(default=0)
    counted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def _switch_counted(self, value):
        self.counted = value
        self.update_timestamp = now()
        self.save()

    def get_creation_timestamp(self):
        return self.creation_timestamp.strftime("%d.%m.%Y %H:%M")

    def full_info_as_list(self):
        return [
            self.value,
            self.description,
            self.update_timestamp.strftime("%d.%m.%Y %H:%M"),
            self.creation_timestamp.strftime("%d.%m.%Y %H:%M"),
            self.counted
        ]

    def full_info_headers_as_list(self):
        return [
            'value',
            'description',
            'update_timestamp',
            'creation_timestamp',
            'counted'
        ]

