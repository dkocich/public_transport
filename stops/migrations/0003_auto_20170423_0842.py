# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-23 06:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stops', '0002_auto_20170423_0747'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stop',
            name='geom',
        ),
        migrations.RemoveField(
            model_name='stopfromoperator',
            name='geom',
        ),
    ]
