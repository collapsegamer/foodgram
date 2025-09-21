from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from .models import Subscription
from .serializers import (
    UserSerializer, UserCreateSerializer, UserWithRecipesSerializer,
    SetPasswordSerializer, SetAvatarSerializer, SetAvatarResponseSerializer
)

User = get_user_model()


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all().order_by('id')
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return UserWithRecipesSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """Регистрация пользователя с корректным JSON-ответом."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='me')
    def me(self, request):
        return Response(UserSerializer(
            request.user, context={'request': request}).data)

    @action(detail=False,
            methods=['post'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='set_password')
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(
                serializer.validated_data['current_password']):
            return Response({'current_password': ['Неверный пароль.']},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['put'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='me/avatar')
    def set_avatar(self, request):
        serializer = SetAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.avatar = serializer.validated_data['avatar']
        request.user.save(update_fields=['avatar'])
        response = SetAvatarResponseSerializer({'avatar': request.user.avatar})
        return Response(response.data, status=status.HTTP_200_OK)

    @set_avatar.mapping.delete
    def delete_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='subscriptions')
    def subscriptions(self, request):
        subs = Subscription.objects.filter(user=request.user).select_related(
            'author').order_by('author__id')
        authors = [s.author for s in subs]
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='subscribe')
    def subscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user
        if request.method == 'POST':
            if author == user:
                return Response({'detail': 'Нельзя подписаться на себя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            created = Subscription.objects.get_or_create(
                user=user, author=author)[1]
            if not created:
                return Response({'detail': 'Уже подписаны.'},
                                status=status.HTTP_400_BAD_REQUEST)
            data = UserWithRecipesSerializer(
                author, context={'request': request}).data
            return Response(data, status=status.HTTP_201_CREATED)
        deleted, _ = Subscription.objects.filter(
            user=user, author=author).delete()
        if not deleted:
            return Response({'detail': 'Не были подписаны.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
