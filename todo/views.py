from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound
from django.middleware import csrf
from django.core.exceptions import ValidationError

from todo.forms import LoginForm
from todo.models import User, TodoList, TodoItem

import json, pusher, config

p = pusher.Pusher(
    app_id=config.app_id, 
    key=config.app_key, 
    secret=config.app_secret
)


def index(request):
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect('/todo/login/')

    return render(request, 'todo/dashboard.html', {
        'me': user,
        'csrf_token': csrf.get_token(request)
    })


def login(request):
    # User has already logged in, so redirect to the dashboard
    if request.session.get('user_id') is not None:
        return HttpResponseRedirect('/todo/')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username, password=password)
                request.session['user_id'] = user.id
                request.session.set_expiry(0);
                return HttpResponseRedirect('/todo/')
            except User.DoesNotExist:
                error_msg = 'Incorrect username or password'
        else:
            error_msg = 'Invalid login'   

        return render(request, 'todo/login.html', {
            'errorMsg': error_msg,
            'loginForm': form
        })
    else:
        form = LoginForm()

    return render(request, 'todo/login.html', {'loginForm': form})


def listHandler(request, list_id=None):
    if request.method == 'POST':
        if list_id is None:
            response = createTodoList(request)
        else:
            response = editTodoList(request, list_id)
        return response
        
    elif request.method == 'GET' and list_id is not None:
        todo_list = get_object_or_404(TodoList, pk=list_id)
        
        # Redirect to login page if user is not signed in. If signed in, make
        # make sure they have permission to view/edit the requested list
        user_id = request.session.get('user_id')
        if user_id is None:
            return HttpResponseRedirect('/todo/login/')
        elif not todo_list.collaborators.filter(pk=user_id).exists():
            return HttpResponseForbidden()

        context = {
            'todo_list': todo_list, 
            'app_key': config.app_key,
            'csrf_token': csrf.get_token(request)
        }

        return render(request, 'todo/list.html', context)


def listItemHandler(request, list_id, item_id=None):
    if request.method == 'POST':
        if item_id is None:
            response = createTodoItem(request, list_id)
        else:
            response = editTodoItem(request, list_id, item_id)
        return response

    elif request.method == 'DELETE' and item_id is not None:
        response = deleteTodoItem(request, list_id, item_id)
        return response


def authenticate(request):
    channel_name = request.POST.get('channel_name')
    socket_id = request.POST.get('socket_id')
    user_id = request.session.get('user_id')

    user = get_object_or_404(User, pk=user_id)

    channel_data = {
        'user_id': user.id,
        'socket_id': socket_id,
        'user_info': {'name': user.username}
    }

    auth = p[channel_name].authenticate(socket_id, channel_data)
    json_data = json.dumps(auth)

    return HttpResponse(json_data)


################################################################
# Helper functions - not intended to be used as route handlers #
################################################################

def createTodoList(request):
    user_id = request.session.get('user_id')
    title = request.POST.get('title')
    
    try:
        if title is None:
            return HttpResponseBadRequest()

        user = User.objects.get(pk=user_id)
        todo_list = TodoList(title=title, owner=user)
        todo_list.full_clean()
        todo_list.save()

        # Add the user as a collaborator
        todo_list.collaborators.add(user)
        todo_list.save()

    except User.DoesNotExist:
        return HttpResponse(status=401)

    except ValidationError as e:
        return HttpResponse(status=400, content=e.message)

    return HttpResponse(content=todo_list.to_json(), content_type='application/json')


def editTodoList(request, list_id):
    user_id = request.session.get('user_id')
    title = request.POST.get('title')
    collaborators = request.POST.getlist('collaborators[]', default=[])

    try:
        todo_list = TodoList.objects.get(pk=list_id)

        # Make sure the user is authorized to make modifications to this list
        # (i.e. they are a collaborator on the document)
        if not todo_list.collaborators.filter(pk=user_id).exists():
            return HttpResponseForbidden()

        if title is not None:
            todo_list.title = title

        try:
            for username in collaborators:
                # Username is unique, so we can use get to retrieve a single user
                user = User.objects.get(username=username)
                if not todo_list.collaborators.filter(username=username).exists():
                    todo_list.collaborators.add(user)
        
        except User.DoesNotExist:
            error_msg = 'User with username "{0}" does not exist'.format(username)
            return HttpResponseBadRequest(content=error_msg)

        todo_list.full_clean()
        todo_list.save()

        # If the request was accepted and successfully processed, broadcast a 
        # 'list-updated' message on the pusher channel for this list
        channel_name = 'presence-todoList' + list_id
        p[channel_name].trigger('list-updated', todo_list.to_json())

    except TodoList.DoesNotExist:
        return HttpResponseNotFound()

    except ValidationError as e:
        return HttpResponseBadRequest(content=e.message)

    return HttpResponse(content=todo_list.to_json(), content_type='application/json')


def createTodoItem(request, list_id):
    user_id = request.session.get('user_id')
    title = request.POST.get('title')
        
    try:
        if title is None:
            return HttpResponseBadRequest()

        # Make sure the user is authorized to make modifications to this list
        todo_list = TodoList.objects.get(pk=list_id)
        if not todo_list.collaborators.filter(pk=user_id).exists():
            return HttpResponseForbidden()

        todo = TodoItem(title=title, todo_list=todo_list)
        todo.full_clean()
        todo.save()

        # If the request was accepted and successfully processed, broadcast a 
        # 'item-added' message on the pusher channel for this list
        channel_name = 'presence-todoList' + list_id
        p[channel_name].trigger('item-added', todo.to_json())

    except TodoList.DoesNotExist:
        return HttpResponseNotFound()    

    except ValidationError as e:
        return HttpResponseBadRequest(content=e.message)

    return HttpResponse(content=todo_list.to_json(), content_type='application/json')


def editTodoItem(request, list_id, item_id):
    user_id = request.session.get('user_id')
    title = request.POST.get('title')
    is_completed = request.POST.get('is_completed')
        
    try:
        # Make sure the user is authorized to make modifications to this list
        todo_list = TodoList.objects.get(pk=list_id)
        if not todo_list.collaborators.filter(pk=user_id).exists():
            return HttpResponseForbidden()

        todo = TodoItem.objects.get(pk=item_id)
            
        if title is not None: 
            todo.title = title

        if is_completed is not None:
            is_completed = is_completed.lower()
            if (is_completed == 'true'):
                todo.is_completed = True
            elif (is_completed == 'false'):
                todo.is_completed = False
            else:
                return HttpResponseBadRequest()
        
        todo.full_clean()
        todo.save()

        # If the request was accepted and successfully processed, broadcast a 
        # 'item-updated' message on the pusher channel for this list
        channel_name = 'presence-todoList' + list_id
        p[channel_name].trigger('item-updated', todo.to_json())
    
    except TodoItem.DoesNotExist, TodoList.DoesNotExist:
        return HttpResponseNotFound()    

    except ValidationError as e:
        return HttpResponseBadRequest(content=e.message)

    return HttpResponse(content=todo_list.to_json(), content_type='application/json')


def deleteTodoItem(request, list_id, item_id):
    user_id = request.session.get('user_id')
        
    try:
        # Make sure the user is authorized to make modifications to this list
        todo_list = TodoList.objects.get(pk=list_id)
        if not todo_list.collaborators.filter(pk=user_id).exists():
            return HttpResponseForbidden()

        todo = TodoItem.objects.get(pk=item_id)
        todo.delete()

        # If the request was accepted and successfully processed, broadcast a 
        # 'list-removed' message on the pusher channel for this list
        channel_name = 'presence-todoList' + list_id
        p[channel_name].trigger('item-removed', todo.to_json())

    except TodoItem.DoesNotExist, TodoList.DoesNotExist:
        return HttpResponseNotFound()    

    return HttpResponse(content=todo_list.to_json(), content_type='application/json')
