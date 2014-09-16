# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='todoitem',
            old_name='todoList',
            new_name='todo_list',
        ),
        migrations.RemoveField(
            model_name='todoitem',
            name='isCompleted',
        ),
        migrations.AddField(
            model_name='todoitem',
            name='is_completed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
