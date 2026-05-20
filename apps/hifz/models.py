from django.db import models
from django.utils import timezone
from apps.quran.models import Surah, Verse


class HifzSession(models.Model):
    MODE_CHOICES = [
        ('blind', 'Blind Mode'),
        ('hint', 'Hint Mode'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='hifz_sessions')
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='hint')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    verses_attempted = models.PositiveSmallIntegerField(default=0)
    verses_correct = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-started_at']
        indexes = [models.Index(fields=['user', '-started_at'])]

    def end_session(self):
        self.ended_at = timezone.now()
        self.save(update_fields=['ended_at'])

    @property
    def accuracy(self) -> float:
        if not self.verses_attempted:
            return 0.0
        return round(self.verses_correct / self.verses_attempted * 100, 1)


class HifzProgress(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('learning', 'Learning'),
        ('memorized', 'Memorized'),
        ('weak', 'Weak'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='hifz_progress')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='hifz_progress')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='new', db_index=True)
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.PositiveSmallIntegerField(default=1)
    repetitions = models.PositiveSmallIntegerField(default=0)
    next_review = models.DateField(default=timezone.now)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    total_reviews = models.PositiveIntegerField(default=0)
    total_errors = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [('user', 'verse')]
        ordering = ['next_review']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'next_review']),
        ]

    def apply_review_result(self, quality: int):
        """SM-2 spaced repetition algorithm. quality: 0-5"""
        self.total_reviews += 1
        self.last_reviewed = timezone.now()

        if quality < 3:
            self.repetitions = 0
            self.interval_days = 1
            self.status = 'weak'
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval_days = 1
            elif self.repetitions == 2:
                self.interval_days = 6
            else:
                self.interval_days = round(self.interval_days * self.ease_factor)

            self.ease_factor = max(
                1.3,
                self.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            )

            if self.repetitions >= 3 and quality >= 4:
                self.status = 'memorized'
            elif self.repetitions >= 1:
                self.status = 'learning'

        self.next_review = (timezone.now() + timezone.timedelta(days=self.interval_days)).date()
        self.save(update_fields=[
            'status', 'ease_factor', 'interval_days', 'repetitions',
            'next_review', 'last_reviewed', 'total_reviews',
        ])


class ErrorLog(models.Model):
    ERROR_TYPE_CHOICES = [
        ('RED', 'Major Mistake'),
        ('YELLOW', 'Minor Mistake'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='hifz_errors')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='error_logs')
    session = models.ForeignKey(
        HifzSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='errors'
    )
    error_type = models.CharField(max_length=6, choices=ERROR_TYPE_CHOICES, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'verse']),
            models.Index(fields=['user', 'error_type']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.error_type} — {self.verse} — {self.user}'
