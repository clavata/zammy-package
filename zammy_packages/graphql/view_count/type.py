import graphene
from graphene.types.generic import GenericScalar
from django.db.models import Count, DateField, F, Q
from django.db.models.functions import TruncDate
from datetime import time
from graphene import relay

from zammy_packages.graphql.core.authentication import log_authenticaion
from zammy_packages.view_count.models import ViewCountModel


def change_number_to_week_day(number):
    if number == 0:
        return "sunday"
    elif number == 1:
        return "monday"
    elif number == 2:
        return "tuesday"
    elif number == 3:
        return "wednesday"
    elif number == 4:
        return "thursday"
    elif number == 5:
        return "friday"
    elif number == 6:
        return "saturday"
    elif number == 7:
        return "sunday"


# 제거
class ViewLogType(graphene.ObjectType):
    uuid = graphene.UUID()
    access_url = graphene.String()
    access_date = graphene.DateTime()


class ViewlogConnection(relay.Connection):
    log_count = graphene.String()

    class Meta:
        node = ViewLogType

    def resolve_log_count(self, *info, **kwargs):
        return len(self.edges)


# 수정된 코드
class ViewCountLogType(graphene.ObjectType):
    uuid = graphene.UUID()
    access_url = graphene.String()
    access_date = graphene.DateTime()


class ViewCountlogConnection(relay.Connection):
    class Meta:
        node = ViewCountLogType


class ViewLogDateCount(graphene.ObjectType):
    date = graphene.Date()
    count = graphene.Int()
    logs = relay.ConnectionField(ViewCountlogConnection)


class ViewLogUrlCount(graphene.ObjectType):
    url = graphene.String()
    count = graphene.Int()


class ViewLogWeekCount(graphene.ObjectType):
    week_day = graphene.String()
    count = graphene.Int()


class ViewLogAMPMCount(graphene.ObjectType):
    time = graphene.String()
    count = graphene.Int()


class ViewLogsDataInfo(graphene.ObjectType):
    logs = relay.ConnectionField(ViewCountlogConnection)
    total_log_count = graphene.String()
    log_count_by_date = graphene.List(ViewLogDateCount)
    log_count_by_url = graphene.List(ViewLogUrlCount)
    log_count_by_week = graphene.List(ViewLogWeekCount)
    log_count_by_am_pm = graphene.List(ViewLogAMPMCount)

    def resolve_logs(self, *info, **kwargs):
        start_date = self[1]
        end_date = self[2]
        view_logs = self[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        return view_logs

    def resolve_total_log_count(self, *info, **kwargs):
        start_date = self[1]
        end_date = self[2]
        view_logs = self[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        return len(view_logs)

    def resolve_log_count_by_date(self, *info, **kwargs):
        results = []
        start_date = self[1]
        end_date = self[2]
        view_logs = self[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        view_counts_by_date = (
            view_logs.annotate(date=TruncDate("access_date", output_field=DateField()))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("-date")
        )
        for log in view_counts_by_date:
            logs = view_logs.filter(access_date__date=log["date"])
            results.append({"date": log["date"], "count": log["count"], "logs": logs})
        return results

    def resolve_log_count_by_url(self, *info, **kwargs):
        start_date = self[1]
        end_date = self[2]
        view_logs = self[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        view_counts_by_url = (
            view_logs.values("access_url")
            .annotate(url=F("access_url"), count=Count("id"))
            .values("url", "count")
        )
        return view_counts_by_url

    def resolve_log_count_by_week(self, *info, **kwargs):
        start_date = self[1]
        end_date = self[2]
        view_logs = self[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        view_counts = [
            {
                "week_day": change_number_to_week_day(week_date),
                "count": len(view_logs.filter(access_date__week_day=week_date)),
            }
            for week_date in range(0, 7)
        ]
        return view_counts

    def resolve_log_count_by_am_pm(self, *info, **kwargs):
        view_counts = []
        start_date = self[1]
        end_date = self[2]
        view_logs = self[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        am_data = view_logs.filter(
            access_date__time__lte=time(11, 59, 59),  # 오전 11:59:59까지
            access_date__time__gte=time(0, 0, 0),  # 자정부터
        )
        view_counts.append({"time": "morning", "count": len(am_data)})
        pm_data = view_logs.filter(
            Q(access_date__time__gte=time(12, 0, 0))
            | Q(access_date__time__lt=time(23, 59, 59))
        )
        view_counts.append({"time": "afternoon", "count": len(pm_data)})
        return view_counts


class LogsObjectType(graphene.ObjectType):
    date = graphene.Date()
    count = graphene.Int()
    logs = relay.ConnectionField(ViewCountlogConnection)


class LogsByUrlObjectType(graphene.ObjectType):
    url = graphene.String()
    logs = graphene.List(LogsObjectType)

    def resolve_url(self, *info, **kwargs):
        return self["url"]

    def resolve_logs(self, *info, **kwargs):
        results_list = []
        results = (
            self["logs"]
            .annotate(date=TruncDate("access_date", output_field=DateField()))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("-date")
        )
        for result in results:
            results_list.append(
                {
                    "date": result["date"],
                    "count": result["count"],
                    "logs": self["logs"].filter(access_date__date=result["date"]),
                }
            )
        return results_list


class ViewCountModelType(graphene.ObjectType):
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    view_logs = relay.ConnectionField(
        ViewlogConnection, start_date=graphene.Date(), end_date=graphene.Date()
    )
    view_count_logs = graphene.Field(
        ViewLogsDataInfo, start_date=graphene.Date(), end_date=graphene.Date()
    )
    logs_by_url = graphene.List(
        LogsByUrlObjectType, start_date=graphene.Date(), end_date=graphene.Date()
    )

    @log_authenticaion
    def resolve_view_logs(user, *info, **kwargs):
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if not info[0].view_count:
            try:
                view_count_model = ViewCountModel.objects.create(user_uuid=user.uuid)
            except:
                view_count_model = ViewCountModel.objects.create()
            info[0].view_count = view_count_model
            info[0].save()

        view_logs = info[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        return view_logs

    @log_authenticaion
    def resolve_view_count_logs(user, *info, **kwargs):
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if not info[0].view_count:
            try:
                view_count_model = ViewCountModel.objects.create(user_uuid=user.uuid)
            except:
                view_count_model = ViewCountModel.objects.create()
            info[0].view_count = view_count_model
            info[0].save()
        return [info[0], start_date, end_date]

    @log_authenticaion
    def resolve_logs_by_url(user, *info, **kwargs):
        results = []
        log_urls = []
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if not info[0].view_count:
            try:
                view_count_model = ViewCountModel.objects.create(user_uuid=user.uuid)
            except:
                view_count_model = ViewCountModel.objects.create()
            info[0].view_count = view_count_model
            info[0].save()

        view_logs = info[0].view_count.get_view_log_filter_by_date(start_date, end_date)
        for log in view_logs:
            if log.access_url not in log_urls:
                log_urls.append(log.access_url)
        for url in log_urls:
            logs = view_logs.filter(access_url=url)
            results.append({"url": url, "logs": logs})
        return results
