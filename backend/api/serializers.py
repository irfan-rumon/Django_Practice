from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Like, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'location', 'birth_date', 'profile_picture',
                 'cover_photo', 'followers_count', 'following_count', 'is_following']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False