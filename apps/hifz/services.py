from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
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


def get_hifz_dashboard(user_id: int) -> dict:
    today = timezone.now().date()

    status_counts = {
        row['status']: row['count']
        for row in HifzProgress.objects.filter(user_id=user_id)
        .values('status').annotate(count=Count('id'))
    }

    daily_reviews = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = HifzProgress.objects.filter(
            user_id=user_id, last_reviewed__date=day
        ).count()
        daily_reviews.append({'date': str(day), 'count': count, 'label': day.strftime('%a')})

    top_surahs = list(
        HifzProgress.objects.filter(user_id=user_id, status='memorized')
        .values('verse__surah__number', 'verse__surah__name_transliteration', 'verse__surah__total_verses')
        .annotate(memorized=Count('id'))
        .order_by('-memorized')[:5]
    )
    top_surahs_out = [
        {
            'surah_number': s['verse__surah__number'],
            'surah_name': s['verse__surah__name_transliteration'],
            'total_verses': s['verse__surah__total_verses'],
            'memorized': s['memorized'],
            'percent': round(s['memorized'] / s['verse__surah__total_verses'] * 100, 1)
            if s['verse__surah__total_verses'] else 0,
        }
        for s in top_surahs
    ]

    total = HifzProgress.objects.filter(user_id=user_id).count()
    due_count = HifzProgress.objects.filter(user_id=user_id, next_review__lte=today).count()

    return {
        'status_counts': {
            'memorized': status_counts.get('memorized', 0),
            'learning': status_counts.get('learning', 0),
            'weak': status_counts.get('weak', 0),
            'new': status_counts.get('new', 0),
        },
        'total_in_progress': total,
        'due_count': due_count,
        'daily_reviews': daily_reviews,
        'top_surahs': top_surahs_out,
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
