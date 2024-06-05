from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_user, name='logout_user'),
    path('all-users', views.get_users, name='all-users'),
    path('edit-user/<id>', views.user_edit, name='edit-user'),
    path('create-user', views.create_user, name='create-user'),
    path('delete-user/<id>', views.delete_user, name='delete-user'),
    #path('activate-user/<uidb64>/<token>', views.activate_user, name='activate'),
]