from django.urls import path

from . import views

urlpatterns = [
    path('add', views.add, name='add'),
    path('all', views.all_recs, name='all'),
    path('delete', views.delete, name='delete'),
    path('update', views.update, name='update'),
    path('get_passed_records', views.get_passed_records, name='get_passed_records'),
    path('get_similar', views.get_similar, name='get_similar'),
    path("get_location_records", views.get_location_records, name="get_location_records"),
    path("delete_all", views.delete_all_for_user, name='delete_all')
    # path('oauth2callback', views.oauth2callback, name='oauth2callback'),
    # path("login", views.login, name='login'),
]