import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import models


class ZammyAccount(models.Model):
    LOGIN_TYPE = [
        ("EMAIL", "email"),
        ("GOOGLE", "google"),
        ("LINE", "line"),
    ]
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), blank=True, null=True)
    username = models.CharField(_("username"), blank=True, max_length=100)
    login_type = models.CharField(max_length=50, choices=LOGIN_TYPE, default="EMAIL")

    class Meta:
        unique_together = ["email", "login_type"]

    def __str__(self):
        return self.email
