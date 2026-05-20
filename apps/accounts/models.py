from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ru', 'Русский'),
        ('tr', 'Türkçe'),
        ('uz_latin', "O'zbekcha"),
        ('uz_cyrillic', 'Ўзбекча'),
    ]
    READING_MODE_CHOICES = [
        ('scroll', 'Scroll Mode'),
        ('mushaf', 'Mushaf Mode'),
    ]

    email = models.EmailField(unique=True)
    avatar = models.URLField(blank=True, default='')
    preferred_language = models.CharField(
        max_length=12, choices=LANGUAGE_CHOICES, default='en'
    )
    reading_mode = models.CharField(
        max_length=10, choices=READING_MODE_CHOICES, default='scroll'
    )
    font_size = models.PositiveSmallIntegerField(default=18)
    tajweed_mode = models.BooleanField(default=False)
    arabic_only = models.BooleanField(default=False)
    zen_mode = models.BooleanField(default=False)
    show_transliteration = models.BooleanField(default=False)
    last_read_surah = models.PositiveSmallIntegerField(null=True, blank=True)
    last_read_verse = models.PositiveSmallIntegerField(null=True, blank=True)
    last_read_page = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def update_last_read(self, surah: int, verse: int, page: int):
        self.last_read_surah = surah
        self.last_read_verse = verse
        self.last_read_page = page
        self.save(update_fields=['last_read_surah', 'last_read_verse', 'last_read_page', 'updated_at'])
