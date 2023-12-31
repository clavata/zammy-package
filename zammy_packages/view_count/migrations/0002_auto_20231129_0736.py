# Generated by Django 4.0 on 2023-11-29 07:36

from django.db import migrations, models
import uuid


def change_foreign_key_to_uuid(apps, schema_editor):
    ViewCountModel = apps.get_model("view_count", "ViewCountModel")
    Account = apps.get_model("account", "ZammyAccount")
    for view_count_model in ViewCountModel.objects.all():
        try:
            user_id = view_count_model.user_id
            account = Account.objects.get(id=user_id)
            view_count_model.user_uuid = account.uuid
            view_count_model.save()
        except:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("view_count", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="viewcountmodel",
            name="user_uuid",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(change_foreign_key_to_uuid),
        migrations.RemoveField(
            model_name="viewcountmodel",
            name="user",
        ),
    ]
