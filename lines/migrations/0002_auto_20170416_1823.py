# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-16 16:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lines', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Variation',
            new_name='Itinerary',
        ),
    ]
