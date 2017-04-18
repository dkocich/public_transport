# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 21:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lines', '0005_line_xml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='line',
            name='ref',
            field=models.CharField(max_length=20, unique=True, verbose_name='Internal line number of operator'),
        ),
    ]
