# Generated by Django 4.2.3 on 2023-08-04 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="serverId",
            field=models.TextField(default=700082073372721172),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="request",
            name="serverID",
            field=models.TextField(default=700082073372721172),
            preserve_default=False,
        ),
    ]
