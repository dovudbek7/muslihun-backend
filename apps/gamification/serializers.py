from rest_framework import serializers
from .models import Streak, TasbihDhikr, TasbihSession, Achievement, UserAchievement


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = [
            'current_streak', 'longest_streak',
            'last_activity_date', 'total_active_days', 'freeze_count',
        ]


class TasbihDhikrSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasbihDhikr
        fields = [
            'id', 'text_arabic', 'text_transliteration',
            'text_en', 'text_ru', 'text_uz', 'default_target',
        ]


class TasbihSessionSerializer(serializers.ModelSerializer):
    dhikr = TasbihDhikrSerializer(read_only=True)
    dhikr_id = serializers.PrimaryKeyRelatedField(
        queryset=TasbihDhikr.objects.all(), source='dhikr', write_only=True
    )

    class Meta:
        model = TasbihSession
        fields = [
            'id', 'dhikr', 'dhikr_id', 'count', 'target',
            'completed', 'created_at', 'completed_at',
        ]
        read_only_fields = ['id', 'completed', 'created_at', 'completed_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TasbihIncrementSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1, max_value=100, default=1)


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = [
            'id', 'key', 'name', 'description', 'icon',
            'rarity', 'condition_type', 'condition_value', 'xp_reward',
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']
