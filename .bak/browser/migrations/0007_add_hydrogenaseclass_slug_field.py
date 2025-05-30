# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-13 09:42
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.text import slugify


def set_slug(apps, schema_editor):
    HydrogenaseClass = apps.get_model('browser', 'HydrogenaseClass')
    for obj in HydrogenaseClass.objects.all():
        obj.slug = slugify(obj.name)
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('browser', '0006_auto_20160607_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='hydrogenaseclass',
            name='slug',
            field=models.SlugField(null=True),
        ),
        migrations.RunPython(set_slug),
    ]
