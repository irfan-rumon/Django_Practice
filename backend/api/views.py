from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Like, Notification
from .serializers import (UserSerializer, ProfileSerializer, PostSerializer,
                         CommentSerializer, LikeSerializer, NotificationSerializer)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if the object has an author field
        if hasattr(obj, 'author'):
            return obj.author == request.user
        # For profile
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj.user == request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']