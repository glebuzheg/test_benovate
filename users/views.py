from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny

from .serializers import UserSerializer, SendToUsersSerializer

User = get_user_model()


class UserListView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)


class SendToUsersView(UpdateAPIView):
    serializer_class = SendToUsersSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    lookup_url_kwarg = 'user_id'
