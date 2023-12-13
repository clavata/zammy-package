"""
import graphene, datetime
from graphene_django import DjangoObjectType
from graphene import relay
from django.db.models import Count, DateField, F
from django.db.models.functions import TruncDate

from zammy_packages.graphql.core.authentication import log_authenticaion
from zammy_packages.view_count.models import ViewCountModel

def check_and_create_view_count(query, user):
    if not query.view_count:
        if user:
            view_count_model = ViewCountModel.objects.create(user=user)
        else:
            view_count_model = ViewCountModel.objects.create()
        query.view_count = view_count_model
        query.save()

class ViewLogType(graphene.ObjectType):
    uuid = graphene.UUID()
    access_url = graphene.String()
    access_date = graphene.DateTime()

class ViewlogConnection(relay.Connection):
    class Meta:
        node = ViewLogType

class ViewLogsByDateObjectType(graphene.ObjectType):
    date = graphene.Date()
    count = graphene.Int()
    logs = relay.ConnectionField(ViewlogConnection)

class ViewLogsByDateObjectType(graphene.ObjectType):
    date = graphene.Date()
    count = graphene.Int()
    logs = relay.ConnectionField(ViewlogConnection)

class ViewLogsByDateInfoType(graphene.ObjectType):
    count = graphene.Int()
    views = graphene.List(
        ViewLogsByDateObjectType, start_date=graphene.Date(), end_date=graphene.Date()
    )

class ViewCountModelObjectType(graphene.ObjectType):
    log_by_date = graphene.Field(
        ViewLogsByDateInfoType, start_date=graphene.Date(), end_date=graphene.Date()
    )

    @log_authenticaion
    def resolve_log_by_date(user, *info, **kwargs):
        check_and_create_view_count(info[0], user)
        views = []
        total_count = 0
        view_count = info[0].view_count
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if not start_date:
            start_date = view_count.view_log.order_by('access_date').first().access_date.date()
        if not end_date:
            end_date = view_count.view_log.order_by('access_date').last().access_date.date()

        for date in range((end_date - start_date).days + 1):
            current_date = start_date + datetime.timedelta(date)
            logs = view_count.view_log.filter(access_date__date=current_date)
            count = len(logs)
            total_count += count
            views.append(
                {
                    "date": current_date,
                    "count": count,
                    "logs": logs
                 }
            )
        return {"count": total_count, "views": views}

class ViewCountModelObjectType(DjangoObjectType):
    class Meta:
        model = ViewCountModel
        fields = (
            "uuid", "created_at", "updated_at"
        )
"""
