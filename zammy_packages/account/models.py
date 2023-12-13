import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ZammyAccount(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), blank=True)
    username = models.CharField(_("username"), blank=True, max_length=100, unique=True)

    def __str__(self):
        return self.email
