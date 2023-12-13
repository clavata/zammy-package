from django.contrib import admin

from .models import ViewCountModel, ViewLog


@admin.register(ViewCountModel)
class ViewCountModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ViewLog)
class ViewLogAdmin(admin.ModelAdmin):
    pass
