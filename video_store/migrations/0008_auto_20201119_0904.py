# Generated by Django 3.1.3 on 2020-11-19 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_store', '0007_remainingjobs'),
    ]

    operations = [
        migrations.AddField(
            model_name='remainingjobs',
            name='reason_for_failure',
            field=models.TextField(default='', help_text='can be used for analysis of errors'),
        ),
        migrations.AlterField(
            model_name='remainingjobs',
            name='page_token',
            field=models.CharField(help_text='storing next page token so we can continue with the paginated results', max_length=20),
        ),
    ]
