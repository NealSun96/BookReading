from django.conf import settings
from django.db import models


class ReadingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    private = models.BooleanField(default=True)
