from django.urls import path

from .views import UserListView, SendToUsersView

urlpatterns = [
    path('', UserListView.as_view(), name='create-list'),
    path('<int:user_id>/send/', SendToUsersView.as_view(), name='send-to_users'),
]
