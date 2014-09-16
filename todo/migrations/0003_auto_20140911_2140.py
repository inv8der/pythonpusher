# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_auto_20140910_2042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='todoitem',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='todolist',
            old_name='name',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='todo_list',
            field=models.ForeignKey(to='todo.TodoList', related_name='todos'),
        ),
        migrations.AlterField(
            model_name='todolist',
            name='owner',
            field=models.ForeignKey(to='todo.User', related_name='owner_of'),
        ),
    ]
