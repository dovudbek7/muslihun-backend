from django.db import models
from apps.quran.models import Surah, Verse


class Reciter(models.Model):
    STYLE_CHOICES = [
        ('murattal', 'Murattal'),
        ('mujawwad', 'Mujawwad'),
        ('muallim', 'Muallim'),
    ]

    identifier = models.SlugField(unique=True)
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True)
    style = models.CharField(max_length=15, choices=STYLE_CHOICES, default='murattal')
    audio_base_url = models.URLField(
        help_text='CDN base URL pattern, e.g. https://cdn.islamic.network/quran/audio/128/en.alafasy'
    )
    image_url = models.URLField(blank=True)
    bitrate = models.PositiveSmallIntegerField(default=128)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name_en']

    def __str__(self):
        return self.name_en

    def get_verse_url(self, surah_number: int, verse_number: int) -> str:
        filename = f'{surah_number:03d}{verse_number:03d}.mp3'
        return f'{self.audio_base_url}/{filename}'

    def get_surah_url(self, surah_number: int) -> str:
        filename = f'{surah_number:03d}.mp3'
        return f'{self.audio_base_url}/{filename}'


class AudioEdition(models.Model):
    reciter = models.ForeignKey(Reciter, on_delete=models.CASCADE, related_name='editions')
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='audio_editions')
    audio_url = models.URLField()
    duration_seconds = models.PositiveIntegerField(default=0)
    file_size_bytes = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = [('reciter', 'surah')]

    def __str__(self):
        return f'{self.reciter.name_en} — {self.surah}'


class UserPlaybackHistory(models.Model):
    PLAYBACK_MODE_CHOICES = [
        ('single', 'Single Verse'),
        ('surah', 'Full Surah'),
        ('range', 'Verse Range'),
        ('loop', 'Loop'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='playback_history')
    reciter = models.ForeignKey(Reciter, on_delete=models.SET_NULL, null=True)
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    verse = models.ForeignKey(Verse, on_delete=models.SET_NULL, null=True, blank=True)
    mode = models.CharField(max_length=10, choices=PLAYBACK_MODE_CHOICES, default='single')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]
