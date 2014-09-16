# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0003_auto_20140911_2140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='todoitem',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='title',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='todolist',
            name='collaborators',
            field=models.ManyToManyField(to=b'todo.User', blank=True),
        ),
        migrations.AlterField(
            model_name='todolist',
            name='title',
            field=models.CharField(max_length=40),
        ),
    ]
