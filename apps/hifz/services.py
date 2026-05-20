from django.utils import timezone
from django.db.models import Count, Q
from .models import HifzProgress, ErrorLog


def get_due_verses(user_id: int, limit: int = 20) -> list:
    today = timezone.now().date()
    qs = (
        HifzProgress.objects.filter(user_id=user_id, next_review__lte=today)
        .select_related('verse__surah')
        .order_by('next_review', '-total_errors')[:limit]
    )
    return list(qs)


def get_weak_verses(user_id: int, limit: int = 20) -> list:
    qs = (
        HifzProgress.objects.filter(user_id=user_id)
        .filter(Q(status='weak') | Q(total_errors__gte=3))
        .select_related('verse__surah')
        .order_by('-total_errors', 'next_review')[:limit]
    )
    return list(qs)


def get_error_stats(user_id: int) -> dict:
    total_red = ErrorLog.objects.filter(user_id=user_id, error_type='RED').count()
    total_yellow = ErrorLog.objects.filter(user_id=user_id, error_type='YELLOW').count()
    today = timezone.now().date()
    due_count = HifzProgress.objects.filter(user_id=user_id, next_review__lte=today).count()

    most_problematic = (
        HifzProgress.objects.filter(user_id=user_id, total_errors__gt=0)
        .select_related('verse__surah')
        .order_by('-total_errors')[:10]
    )

    return {
        'total_red': total_red,
        'total_yellow': total_yellow,
        'due_for_review': due_count,
        'most_problematic_verses': list(most_problematic),
    }


def get_surah_progress(user_id: int, surah_number: int) -> dict:
    from apps.quran.models import Surah
    try:
        surah = Surah.objects.get(number=surah_number)
    except Surah.DoesNotExist:
        return {}

    total = surah.total_verses
    progress_qs = HifzProgress.objects.filter(
        user_id=user_id, verse__surah=surah
    )
    by_status = {
        item['status']: item['count']
        for item in progress_qs.values('status').annotate(count=Count('id'))
    }

    return {
        'surah_number': surah_number,
        'surah_name': surah.name_transliteration,
        'total_verses': total,
        'memorized': by_status.get('memorized', 0),
        'learning': by_status.get('learning', 0),
        'weak': by_status.get('weak', 0),
        'new': total - sum(by_status.values()),
        'completion_percent': round(by_status.get('memorized', 0) / total * 100, 1),
    }
