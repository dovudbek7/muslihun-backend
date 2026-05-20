from rest_framework import serializers
from .models import Reciter, AudioEdition


class ReciterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciter
        fields = [
            'id', 'identifier', 'name_en', 'name_ar', 'style',
            'image_url', 'bitrate', 'is_active',
        ]


class AudioEditionSerializer(serializers.ModelSerializer):
    reciter = ReciterSerializer(read_only=True)
    surah_number = serializers.IntegerField(source='surah.number', read_only=True)

    class Meta:
        model = AudioEdition
        fields = ['id', 'reciter', 'surah_number', 'audio_url', 'duration_seconds']


class VerseAudioSerializer(serializers.Serializer):
    surah_number = serializers.IntegerField()
    verse_number = serializers.IntegerField()
    reciter_id = serializers.IntegerField()
    audio_url = serializers.URLField()
    reciter_name = serializers.CharField()


class SurahAudioSerializer(serializers.Serializer):
    surah_number = serializers.IntegerField()
    reciter = ReciterSerializer()
    audio_url = serializers.URLField()
    verse_urls = serializers.ListField(child=serializers.URLField(), required=False)
