from django.db import models
from django.core import serializers
import json


class User(models.Model):
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=40)

    def to_json(self):
        return json.dumps({
            'id': self.pk,
            'username': self.username
        })

    def __str__(self):
        return self.username


class TodoList(models.Model):
    title = models.CharField(max_length=40)
    owner = models.ForeignKey(User, related_name='owner_of')
    collaborators = models.ManyToManyField(User, blank=True)

    def to_json(self):
        collaborators = []
        for user in self.collaborators.all():
            collaborators.append(json.loads(user.to_json()))

        todos = []
        for todo in self.todos.all():
            todos.append(json.loads(todo.to_json()))

        return json.dumps({
            'id': self.pk,
            'title': self.title,
            'owner': json.loads(self.owner.to_json()),
            'collaborators': collaborators,
            'items': todos
        })

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']


class TodoItem(models.Model):
    title = models.CharField(max_length=60)
    is_completed = models.BooleanField(default=False)
    todo_list = models.ForeignKey(TodoList, related_name='todos')

    def to_json(self):
        return json.dumps({
            'id': self.pk,
            'title': self.title,
            'is_completed': self.is_completed
        })

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']
    



