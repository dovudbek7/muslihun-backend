from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['surah', 'verse'])
    surah_number = serializers.IntegerField()
    surah_name = serializers.CharField()
    surah_name_arabic = serializers.CharField()
    ayah = serializers.IntegerField(allow_null=True)
    page = serializers.IntegerField(allow_null=True)
    juz = serializers.IntegerField(allow_null=True)
    text_arabic = serializers.CharField(allow_blank=True, required=False)
    matched_text = serializers.CharField()
    score = serializers.IntegerField()


class SearchResponseSerializer(serializers.Serializer):
    results = SearchResultSerializer(many=True)
    total = serializers.IntegerField()
    query = serializers.CharField()
    cached = serializers.BooleanField(default=False)


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=1, max_length=200)
    lang = serializers.ChoiceField(
        choices=['en', 'ru', 'tr', 'uz_latin', 'uz_cyrillic'],
        default='en',
    )
    limit = serializers.IntegerField(min_value=1, max_value=50, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)
