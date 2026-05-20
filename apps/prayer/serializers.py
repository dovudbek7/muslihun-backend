from rest_framework import serializers


class PrayerTimesRequestSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    method = serializers.IntegerField(min_value=0, max_value=23, default=3)
    date = serializers.DateField(required=False)


class PrayerTimingsSerializer(serializers.Serializer):
    Fajr = serializers.CharField()
    Sunrise = serializers.CharField()
    Dhuhr = serializers.CharField()
    Asr = serializers.CharField()
    Maghrib = serializers.CharField()
    Isha = serializers.CharField()


class PrayerTimesResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    method = serializers.IntegerField()
    timings = PrayerTimingsSerializer()
    next_prayer = serializers.DictField(required=False)
    fallback = serializers.BooleanField(default=False)
