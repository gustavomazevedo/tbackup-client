

from django.db import models


class OpLog(models.Model):
    class Meta:
        app_label = 'client'
    