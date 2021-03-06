# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-02 02:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailboxFolder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Folder name')),
                ('uidvalidity', models.BigIntegerField()),
                ('highestmodseq', models.BigIntegerField(blank=True, null=True)),
                ('uidnext', models.PositiveIntegerField(blank=True, null=True)),
                ('mailbox', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='mailme.Mailbox')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='uid',
            field=models.BigIntegerField(db_index=True, default=1),
            preserve_default=False,
        ),
    ]
