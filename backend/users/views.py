from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscribtion
from .pagination import UsersPagination
from .serializers import (ChangePasswordSerializer,
                          SubscriptionSerializer,
                          SubscriptionListSerializer,
                          UserSerializer)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UsersPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return (AllowAny(),)

        return (IsAuthenticated(),)

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(subscribing__user=self.request.user)
        return User.objects.all()

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def self_user(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        if request.method == 'POST':
            data = {'user': request.user.id, 'author': pk}
            context = {'request': request}
            serializer = SubscriptionSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            user = request.user
            user_to_unsubscribe = get_object_or_404(User, id=pk)
            subscription = get_object_or_404(
                Subscribtion, user=user, author=user_to_unsubscribe
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        serializer_class=SubscriptionListSerializer,
    )
    def subscriptions(self, request):
        return super().list(request)

    @action(
        methods=('POST',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        self.object = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("current_password")
            if not self.object.check_password(old_password):
                return Response({"current_password": ["Неверный пароль"]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
