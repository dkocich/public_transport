# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lines', '0004_remove_line_xml'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='xml',
            field=models.TextField(default='', verbose_name='XML'),
        ),
    ]
