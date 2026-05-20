from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirm', 'preferred_language']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            preferred_language=validated_data.get('preferred_language', 'en'),
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'avatar', 'preferred_language',
            'reading_mode', 'font_size', 'tajweed_mode', 'arabic_only',
            'zen_mode', 'show_transliteration', 'last_read_surah',
            'last_read_verse', 'last_read_page', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'preferred_language', 'reading_mode', 'font_size',
            'tajweed_mode', 'arabic_only', 'zen_mode', 'show_transliteration',
        ]

    def validate_font_size(self, value):
        if value < 12 or value > 48:
            raise serializers.ValidationError('Font size must be between 12 and 48.')
        return value


class LastReadUpdateSerializer(serializers.Serializer):
    surah = serializers.IntegerField(min_value=1, max_value=114)
    verse = serializers.IntegerField(min_value=1)
    page = serializers.IntegerField(min_value=1, max_value=604)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        token['preferred_language'] = user.preferred_language
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserProfileSerializer(self.user).data
        return data
