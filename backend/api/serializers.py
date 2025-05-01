from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Like, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']