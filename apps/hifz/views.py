from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsOwner
from .models import HifzSession, HifzProgress, ErrorLog
from .serializers import (
    HifzSessionCreateSerializer,
    HifzSessionSerializer,
    HifzProgressSerializer,
    ReviewResultSerializer,
    ErrorLogSerializer,
    ErrorLogCreateSerializer,
    MyErrorsStatsSerializer,
)
from .services import get_due_verses, get_weak_verses, get_error_stats, get_surah_progress


class SessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HifzSessionCreateSerializer
        return HifzSessionSerializer

    def get_queryset(self):
        return HifzSession.objects.filter(user=self.request.user).select_related('surah')[:50]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id: int):
    try:
        session = HifzSession.objects.get(id=session_id, user=request.user)
    except HifzSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=404)

    verses_attempted = request.data.get('verses_attempted', 0)
    verses_correct = request.data.get('verses_correct', 0)
    session.verses_attempted = verses_attempted
    session.verses_correct = verses_correct
    session.end_session()
    return Response(HifzSessionSerializer(session).data)


class ProgressListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HifzProgressSerializer

    def get_queryset(self):
        qs = HifzProgress.objects.filter(user=self.request.user).select_related('verse__surah')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def due_verses(request):
    limit = min(int(request.query_params.get('limit', 20)), 50)
    verses = get_due_verses(request.user.id, limit)
    return Response(HifzProgressSerializer(verses, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weak_verses(request):
    limit = min(int(request.query_params.get('limit', 20)), 50)
    verses = get_weak_verses(request.user.id, limit)
    return Response(HifzProgressSerializer(verses, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request):
    serializer = ReviewResultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    verse_id = serializer.validated_data['verse_id']
    quality = serializer.validated_data['quality']

    progress, _ = HifzProgress.objects.get_or_create(
        user=request.user, verse_id=verse_id,
    )
    progress.apply_review_result(quality)
    return Response(HifzProgressSerializer(progress).data)


class ErrorLogListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ErrorLogCreateSerializer
        return ErrorLogSerializer

    def get_queryset(self):
        qs = ErrorLog.objects.filter(user=self.request.user).select_related('verse__surah')
        error_type = self.request.query_params.get('type')
        if error_type:
            qs = qs.filter(error_type=error_type.upper())
        return qs[:100]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_errors_stats(request):
    stats = get_error_stats(request.user.id)
    from .serializers import HifzProgressSerializer
    stats['most_problematic_verses'] = HifzProgressSerializer(
        stats['most_problematic_verses'], many=True
    ).data
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def surah_progress(request, surah_number: int):
    data = get_surah_progress(request.user.id, surah_number)
    if not data:
        return Response({'error': 'Surah not found.'}, status=404)
    return Response(data)
