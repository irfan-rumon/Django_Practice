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
    
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at', 'parent', 'replies']
        read_only_fields = ['author', 'replies']
    
    def get_replies(self, obj):
        if obj.parent is None:  # Only get replies for top-level comments
            replies = Comment.objects.filter(parent=obj)
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)