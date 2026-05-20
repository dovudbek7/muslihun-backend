from django.db import models
from django.utils import timezone


class Streak(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_active_days = models.PositiveIntegerField(default=0)
    freeze_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Streak'

    def __str__(self):
        return f'{self.user.email} — {self.current_streak} day streak'

    def record_activity(self):
        today = timezone.now().date()
        if self.last_activity_date == today:
            return

        if self.last_activity_date is None:
            self.current_streak = 1
        else:
            delta = (today - self.last_activity_date).days
            if delta == 1:
                self.current_streak += 1
            elif delta == 2 and self.freeze_count > 0:
                self.current_streak += 1
                self.freeze_count -= 1
            else:
                self.current_streak = 1

        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_activity_date = today
        self.total_active_days += 1
        self.save()


class TasbihDhikr(models.Model):
    text_arabic = models.CharField(max_length=200)
    text_transliteration = models.CharField(max_length=200)
    text_en = models.CharField(max_length=300, blank=True)
    text_ru = models.CharField(max_length=300, blank=True)
    text_uz = models.CharField(max_length=300, blank=True)
    default_target = models.PositiveSmallIntegerField(default=33)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.text_transliteration


class TasbihSession(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='tasbih_sessions')
    dhikr = models.ForeignKey(TasbihDhikr, on_delete=models.CASCADE, related_name='sessions')
    count = models.PositiveIntegerField(default=0)
    target = models.PositiveSmallIntegerField(default=33)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

    def increment(self, amount: int = 1):
        self.count = min(self.count + amount, self.target * 10)
        if self.count >= self.target and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
        self.save(update_fields=['count', 'completed', 'completed_at'])


class Achievement(models.Model):
    CONDITION_CHOICES = [
        ('streak_days', 'Streak Days'),
        ('verses_memorized', 'Verses Memorized'),
        ('tasbih_sessions', 'Tasbih Sessions'),
        ('tasbih_total', 'Total Tasbih Count'),
        ('reading_pages', 'Pages Read'),
        ('hifz_sessions', 'Hifz Sessions'),
    ]
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]

    key = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏅')
    rarity = models.CharField(max_length=10, choices=RARITY_CHOICES, default='common')
    condition_type = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    condition_value = models.PositiveIntegerField()
    xp_reward = models.PositiveSmallIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['condition_value']

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'achievement')]
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user.email} — {self.achievement.name}'
