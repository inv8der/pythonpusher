# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TodoItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('isCompleted', models.BooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TodoList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('username', models.CharField(max_length=40, unique=True)),
                ('password', models.CharField(max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='todolist',
            name='collaborators',
            field=models.ManyToManyField(to='todo.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolist',
            name='owner',
            field=models.ForeignKey(related_name='ownerOf', to='todo.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todoitem',
            name='todoList',
            field=models.ForeignKey(to='todo.TodoList'),
            preserve_default=True,
        ),
    ]
