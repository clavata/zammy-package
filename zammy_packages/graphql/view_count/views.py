from zammy_packages.view_count.models import ViewCountModel


def add_view_log(query, kwargs):
    if "url" not in kwargs:
        return
    if not query.view_count:
        try:
            view_count_model = ViewCountModel.objects.create(user_uuid=query.user_uuid)
        except:
            view_count_model = ViewCountModel.objects.create()
        query.view_count = view_count_model
        query.save()
    access_url = kwargs["url"]
    query.view_count.add_logs(url=access_url)
