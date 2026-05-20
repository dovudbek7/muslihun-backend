from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Streak, TasbihDhikr, TasbihSession, Achievement, UserAchievement
from .serializers import (
    StreakSerializer,
    TasbihDhikrSerializer,
    TasbihSessionSerializer,
    TasbihIncrementSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
)
from .services import record_user_activity, seed_default_dhikr, seed_default_achievements


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def streak_view(request):
    if request.method == 'POST':
        streak = record_user_activity(request.user.id)
        return Response(StreakSerializer(streak).data)
    streak, _ = Streak.objects.get_or_create(user=request.user)
    return Response(StreakSerializer(streak).data)


class TasbihDhikrListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TasbihDhikrSerializer
    pagination_class = None

    def get_queryset(self):
        seed_default_dhikr()
        return TasbihDhikr.objects.filter(is_active=True)


class TasbihSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TasbihSessionSerializer

    def get_queryset(self):
        return TasbihSession.objects.filter(
            user=self.request.user
        ).select_related('dhikr')[:50]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tasbih_increment(request, session_id: int):
    try:
        session = TasbihSession.objects.get(id=session_id, user=request.user)
    except TasbihSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=404)

    serializer = TasbihIncrementSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session.increment(serializer.validated_data['amount'])

    if session.completed:
        record_user_activity(request.user.id)

    return Response({
        'count': session.count,
        'target': session.target,
        'completed': session.completed,
        'remaining': max(0, session.target - session.count),
    })


class AchievementListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AchievementSerializer
    pagination_class = None

    def get_queryset(self):
        seed_default_achievements()
        return Achievement.objects.filter(is_active=True)


class UserAchievementListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAchievementSerializer
    pagination_class = None

    def get_queryset(self):
        return UserAchievement.objects.filter(
            user=self.request.user
        ).select_related('achievement')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamification_dashboard(request):
    streak, _ = Streak.objects.get_or_create(user=request.user)
    tasbih_today = TasbihSession.objects.filter(
        user=request.user,
        created_at__date=timezone.now().date(),
        completed=True,
    ).count()
    earned_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').count()
    all_achievements = Achievement.objects.filter(is_active=True).count()

    return Response({
        'streak': StreakSerializer(streak).data,
        'tasbih_completed_today': tasbih_today,
        'achievements_earned': earned_achievements,
        'achievements_total': all_achievements,
    })
