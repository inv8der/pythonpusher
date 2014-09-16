from django.conf.urls import patterns, url

from todo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^list/$', views.listHandler),
    url(r'^list/(?P<list_id>\d+)/$', views.listHandler),
    url(r'^list/(?P<list_id>\d+)/item/$', views.listItemHandler),
    url(r'^list/(?P<list_id>\d+)/item/(?P<item_id>\d+)/$', views.listItemHandler),
    url(r'^pusher/auth/$', views.authenticate, name='authenticate'),
)