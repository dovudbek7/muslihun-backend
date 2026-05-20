from django.db import models


class Surah(models.Model):
    REVELATION_TYPE_CHOICES = [
        ('meccan', 'Meccan'),
        ('medinan', 'Medinan'),
    ]

    number = models.PositiveSmallIntegerField(unique=True, db_index=True)
    name_arabic = models.CharField(max_length=100)
    name_transliteration = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, blank=True)
    name_tr = models.CharField(max_length=100, blank=True)
    revelation_type = models.CharField(max_length=10, choices=REVELATION_TYPE_CHOICES)
    total_verses = models.PositiveSmallIntegerField()
    page_start = models.PositiveSmallIntegerField(default=1)
    page_end = models.PositiveSmallIntegerField(default=1)
    revelation_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['number']
        verbose_name = 'Surah'
        verbose_name_plural = 'Surahs'

    def __str__(self):
        return f'{self.number}. {self.name_transliteration}'


class Verse(models.Model):
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='verses')
    number = models.PositiveSmallIntegerField()
    text_arabic = models.TextField()
    text_transliteration = models.TextField(blank=True)
    page_number = models.PositiveSmallIntegerField(db_index=True)
    juz_number = models.PositiveSmallIntegerField(db_index=True)
    hizb_quarter = models.PositiveSmallIntegerField(default=1)
    is_sajda = models.BooleanField(default=False)
    global_index = models.PositiveIntegerField(db_index=True, default=0)

    class Meta:
        ordering = ['surah__number', 'number']
        unique_together = [('surah', 'number')]
        verbose_name = 'Verse'
        verbose_name_plural = 'Verses'
        indexes = [
            models.Index(fields=['page_number']),
            models.Index(fields=['juz_number']),
            models.Index(fields=['surah', 'number']),
        ]

    def __str__(self):
        return f'{self.surah.number}:{self.number}'


class Translation(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ru', 'Русский'),
        ('tr', 'Türkçe'),
        ('uz_latin', "O'zbekcha"),
        ('uz_cyrillic', 'Ўзбекча'),
    ]
    SOURCE_CHOICES = [
        ('sahih_international', 'Sahih International'),
        ('kuliyev', 'Elmir Kuliyev'),
        ('diyanet', 'Diyanet İşleri'),
        ('uz_tashkent', 'Toshkent Mushafi'),
    ]

    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=12, choices=LANGUAGE_CHOICES, db_index=True)
    text = models.TextField()
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, blank=True)

    class Meta:
        unique_together = [('verse', 'language')]
        indexes = [models.Index(fields=['verse', 'language'])]

    def __str__(self):
        return f'{self.verse} [{self.language}]'


class Tafsir(models.Model):
    LANGUAGE_CHOICES = Translation.LANGUAGE_CHOICES

    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='tafsirs')
    language = models.CharField(max_length=12, choices=LANGUAGE_CHOICES, db_index=True)
    source = models.CharField(max_length=100, blank=True)
    content = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = [('verse', 'language')]
        indexes = [models.Index(fields=['verse', 'language'])]

    def __str__(self):
        return f'Tafsir {self.verse} [{self.language}]'


class Bookmark(models.Model):
    COLOR_CHOICES = [
        ('gold', 'Gold'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('red', 'Red'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookmarks')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='bookmarks')
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='gold')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'verse')]
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f'Bookmark {self.user} — {self.verse}'


class PageMapping(models.Model):
    page_number = models.PositiveSmallIntegerField(unique=True)
    surah_start = models.ForeignKey(
        Surah, on_delete=models.CASCADE, related_name='page_starts'
    )
    verse_start = models.PositiveSmallIntegerField()
    juz_number = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['page_number']

    def __str__(self):
        return f'Page {self.page_number}'
