# Generated by Django 3.1.3 on 2020-11-19 21:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('video_store', '0008_auto_20201119_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='last_used',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 19, 21, 14, 35, 953133, tzinfo=utc)),
        ),
    ]
