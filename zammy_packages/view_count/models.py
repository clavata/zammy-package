import uuid as _uuid
import pytz
from datetime import timedelta, datetime
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from zammy_packages.account.models import ZammyAccount


class ViewLog(models.Model):
    uuid = models.UUIDField(unique=True, default=_uuid.uuid4, editable=False)
    view_count = models.ForeignKey(
        "ViewCountModel", on_delete=models.CASCADE, related_name="view_log"
    )
    access_url = models.TextField()
    site = models.CharField(max_length=30, null=True, blank=True)
    access_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-access_date"]

    def __str__(self):
        return f"{self.access_url} / {self.access_date}"


class ViewCountModel(models.Model):
    uuid = models.UUIDField(unique=True, default=_uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_uuid = models.UUIDField(null=True, blank=True)

    def add_logs(self, url):
        ViewLog.objects.create(view_count=self, access_url=url)

    def get_view_log_filter_by_date(self, start_date, end_date):
        timezone = pytz.timezone("Asia/Seoul")
        if start_date:
            start_date = datetime.combine(start_date, datetime.min.time())
            start_date = timezone.localize(start_date)
        if end_date:
            end_date = end_date + timedelta(days=1)
            end_date = datetime.combine(end_date, datetime.min.time())
            end_date = timezone.localize(end_date)

        if start_date and end_date:
            view_logs = self.view_log.filter(access_date__range=(start_date, end_date))
        elif start_date:
            view_logs = self.view_log.filter(Q(access_date__gte=start_date))
        elif end_date:
            view_logs = self.view_log.filter(Q(access_date__lt=end_date))
        else:
            view_logs = self.view_log.all()
        return view_logs
