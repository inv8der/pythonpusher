from django.contrib import admin

from todo.models import User, TodoList, TodoItem

admin.site.register(User)
admin.site.register(TodoList)
admin.site.register(TodoItem)
