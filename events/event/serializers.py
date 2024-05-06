from rest_framework import serializers
from .models import Event
from django.contrib.auth.models import User
class EventSerializer(serializers.ModelSerializer):
    start_datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end_datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Event
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user