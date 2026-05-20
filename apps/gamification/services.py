from django.db import transaction
from .models import Streak, Achievement, UserAchievement


def record_user_activity(user_id: int) -> Streak:
    streak, _ = Streak.objects.get_or_create(user_id=user_id)
    streak.record_activity()
    _check_streak_achievements(user_id, streak.current_streak)
    return streak


def _check_streak_achievements(user_id: int, current_streak: int):
    eligible = Achievement.objects.filter(
        condition_type='streak_days',
        condition_value__lte=current_streak,
        is_active=True,
    )
    existing = set(
        UserAchievement.objects.filter(user_id=user_id)
        .values_list('achievement_id', flat=True)
    )
    new_achievements = [
        UserAchievement(user_id=user_id, achievement=a)
        for a in eligible
        if a.id not in existing
    ]
    if new_achievements:
        UserAchievement.objects.bulk_create(new_achievements, ignore_conflicts=True)


def seed_default_dhikr():
    from .models import TasbihDhikr
    defaults = [
        {
            'text_arabic': 'سُبْحَانَ اللَّهِ',
            'text_transliteration': 'Subhanallah',
            'text_en': 'Glory be to Allah',
            'text_ru': 'Слава Аллаху',
            'text_uz': 'Allohni ulug\'layman',
            'default_target': 33,
            'display_order': 1,
        },
        {
            'text_arabic': 'الْحَمْدُ لِلَّهِ',
            'text_transliteration': 'Alhamdulillah',
            'text_en': 'All praise is due to Allah',
            'text_ru': 'Хвала Аллаху',
            'text_uz': 'Allohga hamdu sanolar bo\'lsin',
            'default_target': 33,
            'display_order': 2,
        },
        {
            'text_arabic': 'اللَّهُ أَكْبَرُ',
            'text_transliteration': 'Allahu Akbar',
            'text_en': 'Allah is the Greatest',
            'text_ru': 'Аллах Велик',
            'text_uz': 'Alloh eng Ulug\'dir',
            'default_target': 34,
            'display_order': 3,
        },
        {
            'text_arabic': 'لَا إِلَهَ إِلَّا اللَّهُ',
            'text_transliteration': 'La ilaha illallah',
            'text_en': 'There is no god but Allah',
            'text_ru': 'Нет бога, кроме Аллаха',
            'text_uz': 'Allohdan boshqa iloh yo\'q',
            'default_target': 100,
            'display_order': 4,
        },
        {
            'text_arabic': 'أَسْتَغْفِرُ اللَّهَ',
            'text_transliteration': 'Astaghfirullah',
            'text_en': 'I seek forgiveness from Allah',
            'text_ru': 'Прошу прощения у Аллаха',
            'text_uz': 'Allohdan mag\'firat so\'rayman',
            'default_target': 100,
            'display_order': 5,
        },
    ]
    for dhikr_data in defaults:
        TasbihDhikr.objects.get_or_create(
            text_transliteration=dhikr_data['text_transliteration'],
            defaults=dhikr_data,
        )


def seed_default_achievements():
    defaults = [
        {'key': 'streak_3', 'name': '3-Day Streak', 'description': 'Read Quran 3 days in a row', 'icon': '🔥', 'rarity': 'common', 'condition_type': 'streak_days', 'condition_value': 3, 'xp_reward': 30},
        {'key': 'streak_7', 'name': '1-Week Streak', 'description': 'Read Quran 7 days in a row', 'icon': '⚡', 'rarity': 'common', 'condition_type': 'streak_days', 'condition_value': 7, 'xp_reward': 70},
        {'key': 'streak_30', 'name': '30-Day Streak', 'description': 'Read Quran 30 days in a row', 'icon': '🏆', 'rarity': 'rare', 'condition_type': 'streak_days', 'condition_value': 30, 'xp_reward': 300},
        {'key': 'streak_100', 'name': 'Century', 'description': '100-day reading streak', 'icon': '💎', 'rarity': 'epic', 'condition_type': 'streak_days', 'condition_value': 100, 'xp_reward': 1000},
        {'key': 'streak_365', 'name': 'Year of Devotion', 'description': '365-day reading streak', 'icon': '🌟', 'rarity': 'legendary', 'condition_type': 'streak_days', 'condition_value': 365, 'xp_reward': 5000},
    ]
    for data in defaults:
        Achievement.objects.get_or_create(key=data['key'], defaults=data)
