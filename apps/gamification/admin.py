from django.contrib import admin
from .models import Streak, TasbihDhikr, TasbihSession, Achievement, UserAchievement


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date', 'total_active_days']
    raw_id_fields = ['user']


@admin.register(TasbihDhikr)
class TasbihDhikrAdmin(admin.ModelAdmin):
    list_display = ['text_transliteration', 'default_target', 'display_order', 'is_active']
    list_filter = ['is_active']


@admin.register(TasbihSession)
class TasbihSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'dhikr', 'count', 'target', 'completed', 'created_at']
    list_filter = ['completed']
    raw_id_fields = ['user']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'rarity', 'condition_type', 'condition_value', 'xp_reward', 'is_active']
    list_filter = ['rarity', 'condition_type', 'is_active']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    raw_id_fields = ['user']
