# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-24 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailme', '0004_message_folder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailboxfolder',
            name='uidvalidity',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
