from django.urls import path

from .views import UserListView, SendToUsersView

app_name = 'users'

urlpatterns = [
    path('', UserListView.as_view(), name='create-list'),
    path('<int:user_id>/send/', SendToUsersView.as_view(), name='send-to-users'),
]
