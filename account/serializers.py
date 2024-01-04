from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from account.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginResponceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','profile','email', 'first_name','full_name')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email', 'first_name','full_name')

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ('id','from_user','to_user', 'status')

class ConnectionResponceSerializer(serializers.ModelSerializer):
    from_user_card = UserSerializer(source='from_user', read_only=True)
    to_user_card = UserSerializer(source='to_user', read_only=True)

    class Meta:
        model = Connection
        fields = ('id','from_user','to_user', 'status','from_user_card','to_user_card')
