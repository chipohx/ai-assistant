from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('all', views.all_recs, name='all'),
    path('delete', views.delete, name='delete'),
    path('get_similar', views.get_similar, name='get_similar'),
]