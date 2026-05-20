from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import PrayerTimesRequestSerializer, PrayerTimesResponseSerializer
from .services import get_prayer_times, get_next_prayer


@api_view(['GET'])
@permission_classes([AllowAny])
def prayer_times(request):
    serializer = PrayerTimesRequestSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    times = get_prayer_times(
        latitude=data['latitude'],
        longitude=data['longitude'],
        method=data.get('method', 3),
        target_date=data.get('date'),
    )
    times['next_prayer'] = get_next_prayer(times)
    return Response(times)


@api_view(['GET'])
@permission_classes([AllowAny])
def next_prayer_countdown(request):
    serializer = PrayerTimesRequestSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    times = get_prayer_times(
        latitude=data['latitude'],
        longitude=data['longitude'],
        method=data.get('method', 3),
    )
    next_prayer = get_next_prayer(times)
    return Response(next_prayer)
