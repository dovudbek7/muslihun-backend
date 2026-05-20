from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import SearchQuerySerializer, SearchResponseSerializer
from .services import search


class SearchRateThrottle(AnonRateThrottle):
    rate = '100/minute'


@extend_schema(
    parameters=[
        OpenApiParameter('q', str, required=True, description='Search query'),
        OpenApiParameter('lang', str, description='Language: en, ru, tr, uz_latin, uz_cyrillic'),
        OpenApiParameter('limit', int, description='Results per page (max 50)'),
        OpenApiParameter('offset', int, description='Pagination offset'),
    ],
    responses=SearchResponseSerializer,
    summary='Fuzzy search across Quran text, surah names, and translations',
)
@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([SearchRateThrottle])
def search_view(request):
    serializer = SearchQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    results = search(
        query=data['q'],
        lang=data['lang'],
        limit=data['limit'],
        offset=data['offset'],
    )
    return Response(results)
