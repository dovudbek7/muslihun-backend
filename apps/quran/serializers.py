from rest_framework import serializers
from .models import Surah, Verse, Translation, Tafsir, PageMapping


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['language', 'text', 'source']


class TafsirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tafsir
        fields = ['language', 'source', 'content']


class VerseSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    tafsirs = serializers.SerializerMethodField()

    class Meta:
        model = Verse
        fields = [
            'id', 'number', 'text_arabic', 'text_transliteration',
            'page_number', 'juz_number', 'hizb_quarter', 'is_sajda',
            'global_index', 'translations', 'tafsirs',
        ]

    def get_translations(self, obj):
        lang = self.context.get('lang')
        qs = obj.translations.all()
        if lang:
            qs = qs.filter(language=lang)
        return TranslationSerializer(qs, many=True).data

    def get_tafsirs(self, obj):
        if not self.context.get('include_tafsir'):
            return []
        lang = self.context.get('lang')
        qs = obj.tafsirs.all()
        if lang:
            qs = qs.filter(language=lang)
        return TafsirSerializer(qs, many=True).data


class VerseMinimalSerializer(serializers.ModelSerializer):
    translation = serializers.SerializerMethodField()

    class Meta:
        model = Verse
        fields = [
            'id', 'number', 'text_arabic', 'text_transliteration',
            'page_number', 'juz_number', 'is_sajda', 'global_index', 'translation',
        ]

    def get_translation(self, obj):
        lang = self.context.get('lang', 'en')
        translation = obj.translations.filter(language=lang).first()
        if translation:
            return translation.text
        return None


class SurahListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surah
        fields = [
            'number', 'name_arabic', 'name_transliteration',
            'name_en', 'name_ru', 'name_tr',
            'revelation_type', 'total_verses', 'page_start',
        ]


class SurahDetailSerializer(serializers.ModelSerializer):
    verses = serializers.SerializerMethodField()

    class Meta:
        model = Surah
        fields = [
            'number', 'name_arabic', 'name_transliteration',
            'name_en', 'name_ru', 'name_tr', 'revelation_type',
            'total_verses', 'page_start', 'page_end', 'verses',
        ]

    def get_verses(self, obj):
        lang = self.context.get('lang', 'en')
        verses = obj.verses.prefetch_related('translations').order_by('number')
        return VerseMinimalSerializer(verses, many=True, context={'lang': lang}).data


class PageSerializer(serializers.Serializer):
    page_number = serializers.IntegerField()
    juz_number = serializers.IntegerField()
    surah_number = serializers.IntegerField(source='surah__number')
    verses = VerseMinimalSerializer(many=True)


class TafsirDetailSerializer(serializers.ModelSerializer):
    verse_number = serializers.IntegerField(source='verse.number')
    surah_number = serializers.IntegerField(source='verse.surah.number')
    surah_name = serializers.CharField(source='verse.surah.name_transliteration')
    text_arabic = serializers.CharField(source='verse.text_arabic')

    class Meta:
        model = Tafsir
        fields = [
            'id', 'verse_number', 'surah_number', 'surah_name',
            'text_arabic', 'language', 'source', 'content',
        ]
