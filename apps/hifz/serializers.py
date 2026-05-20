from rest_framework import serializers
from django.db.models import Count
from .models import HifzSession, HifzProgress, ErrorLog


class HifzSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HifzSession
        fields = ['id', 'surah', 'mode', 'started_at']
        read_only_fields = ['id', 'started_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HifzSessionSerializer(serializers.ModelSerializer):
    surah_name = serializers.CharField(source='surah.name_transliteration', read_only=True)
    accuracy = serializers.FloatField(read_only=True)

    class Meta:
        model = HifzSession
        fields = [
            'id', 'surah', 'surah_name', 'mode', 'started_at', 'ended_at',
            'verses_attempted', 'verses_correct', 'accuracy',
        ]


class HifzProgressSerializer(serializers.ModelSerializer):
    surah_number = serializers.IntegerField(source='verse.surah.number', read_only=True)
    verse_number = serializers.IntegerField(source='verse.number', read_only=True)
    text_arabic = serializers.CharField(source='verse.text_arabic', read_only=True)
    page_number = serializers.IntegerField(source='verse.page_number', read_only=True)
    days_until_review = serializers.SerializerMethodField()

    class Meta:
        model = HifzProgress
        fields = [
            'id', 'surah_number', 'verse_number', 'text_arabic', 'page_number',
            'status', 'ease_factor', 'interval_days', 'repetitions',
            'next_review', 'last_reviewed', 'total_reviews', 'total_errors',
            'days_until_review',
        ]

    def get_days_until_review(self, obj) -> int:
        from django.utils import timezone
        delta = obj.next_review - timezone.now().date()
        return max(0, delta.days)


class ReviewResultSerializer(serializers.Serializer):
    verse_id = serializers.IntegerField()
    quality = serializers.IntegerField(min_value=0, max_value=5)


class ErrorLogSerializer(serializers.ModelSerializer):
    surah_number = serializers.IntegerField(source='verse.surah.number', read_only=True)
    verse_number = serializers.IntegerField(source='verse.number', read_only=True)
    text_arabic = serializers.CharField(source='verse.text_arabic', read_only=True)

    class Meta:
        model = ErrorLog
        fields = [
            'id', 'surah_number', 'verse_number', 'text_arabic',
            'error_type', 'notes', 'created_at',
        ]


class ErrorLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = ['verse', 'session', 'error_type', 'notes']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        progress, _ = HifzProgress.objects.get_or_create(
            user=validated_data['user'],
            verse=validated_data['verse'],
        )
        progress.total_errors += 1
        progress.save(update_fields=['total_errors'])
        return super().create(validated_data)


class MyErrorsStatsSerializer(serializers.Serializer):
    total_red = serializers.IntegerField()
    total_yellow = serializers.IntegerField()
    most_problematic_verses = HifzProgressSerializer(many=True)
    due_for_review = serializers.IntegerField()
