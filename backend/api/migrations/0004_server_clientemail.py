# Generated by Django 5.0.1 on 2024-01-26 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_serverid_request_serverid'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='clientEmail',
            field=models.TextField(null=True),
        ),
    ]
