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


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        profile = self.get_object()
        user = request.user
        
        if profile.user == user:
            return Response({"detail": "You cannot follow yourself."},
                           status=status.HTTP_400_BAD_REQUEST)
        
        if profile.followers.filter(id=user.id).exists():
            profile.followers.remove(user)
            return Response({"status": "unfollowed"})
        else:
            profile.followers.add(user)
            # Create notification
            Notification.objects.create(
                recipient=profile.user,
                sender=user,
                notification_type='follow'
            )
            return Response({"status": "following"})
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'author__username']
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        user = request.user
        # Get posts from people the user follows and their own posts
        following_users = user.following.values_list('user', flat=True)
        posts = Post.objects.filter(author__in=following_users) | Post.objects.filter(author=user)
        posts = posts.order_by('-created_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        like, created = Like.objects.get_or_create(user=user, post=post)
        
        if created:
            # Create notification for the post author if not self-like
            if post.author != user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=user,
                    notification_type='like',
                    post=post
                )
            return Response({"status": "liked"})
        else:
            like.delete()
            return Response({"status": "unliked"})
        

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        comment = serializer.save()
        post = comment.post
        
        # Create notification for the post author if not self-comment
        if post.author != self.request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=self.request.user,
                notification_type='comment',
                post=post,
                comment=comment
            )