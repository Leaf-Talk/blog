#-*- codeing = utf-8 -*-
from django.urls import path
from home.views import IndexView, WriteBlogView, DetailView

app_name = 'home'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('write/', WriteBlogView.as_view(), name='write'),
    path('index/', DetailView.as_view(), name='detail'),

]