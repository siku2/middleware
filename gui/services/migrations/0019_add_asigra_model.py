# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-13 13:38
from __future__ import unicode_literals

from django.db import migrations, models


def add_asigra(apps, schema_editor):
    Asigra = apps.get_model('services', 'asigra')
    Asigra.objects.create()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0018_add_asigra_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asigra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filesystem', models.CharField(blank=True, max_length=255, verbose_name='Base Filesystem')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(add_asigra, reverse_code=migrations.RunPython.noop)
    ]