from typing import Optional
import logging
from django.core.cache import cache
from django.db.models import Prefetch
from core.cache import QuranCacheKeys
from .models import Surah, Verse, Translation, Tafsir

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 3600 * 24


def get_surah_list(lang: str = 'en') -> list:
    key = QuranCacheKeys.format(QuranCacheKeys.SURAH_LIST, lang=lang)
    cached = cache.get(key)
    if cached:
        return cached

    from .serializers import SurahListSerializer
    surahs = Surah.objects.all()
    data = SurahListSerializer(surahs, many=True).data
    cache.set(key, data, CACHE_TIMEOUT)
    return data


def get_surah_detail(surah_number: int, lang: str = 'en') -> Optional[dict]:
    key = QuranCacheKeys.format(QuranCacheKeys.SURAH_DETAIL, surah_number=surah_number, lang=lang)
    cached = cache.get(key)
    if cached:
        return cached

    try:
        surah = Surah.objects.get(number=surah_number)
    except Surah.DoesNotExist:
        return None

    from .serializers import SurahDetailSerializer
    data = SurahDetailSerializer(surah, context={'lang': lang}).data
    cache.set(key, data, CACHE_TIMEOUT)
    return data


def get_page_verses(page_number: int, lang: str = 'en') -> list:
    key = QuranCacheKeys.format(QuranCacheKeys.PAGE_VERSES, page_number=page_number, lang=lang)
    cached = cache.get(key)
    if cached:
        return cached

    translation_qs = Translation.objects.filter(language=lang)
    verses = (
        Verse.objects.filter(page_number=page_number)
        .select_related('surah')
        .prefetch_related(Prefetch('translations', queryset=translation_qs))
        .order_by('surah__number', 'number')
    )

    from .serializers import VerseMinimalSerializer
    data = VerseMinimalSerializer(verses, many=True, context={'lang': lang}).data
    cache.set(key, data, CACHE_TIMEOUT)
    return data


def get_juz_verses(juz_number: int, lang: str = 'en') -> list:
    key = QuranCacheKeys.format(QuranCacheKeys.JUZ_VERSES, juz_number=juz_number, lang=lang)
    cached = cache.get(key)
    if cached:
        return cached

    translation_qs = Translation.objects.filter(language=lang)
    verses = (
        Verse.objects.filter(juz_number=juz_number)
        .select_related('surah')
        .prefetch_related(Prefetch('translations', queryset=translation_qs))
        .order_by('surah__number', 'number')
    )

    from .serializers import VerseMinimalSerializer
    data = VerseMinimalSerializer(verses, many=True, context={'lang': lang}).data
    cache.set(key, data, CACHE_TIMEOUT)
    return data


def get_verse_tafsir(verse_id: int, lang: str = 'en') -> Optional[dict]:
    key = QuranCacheKeys.format(QuranCacheKeys.TAFSIR, verse_id=verse_id, lang=lang)
    cached = cache.get(key)
    if cached is not None:
        return cached

    try:
        tafsir = Tafsir.objects.select_related('verse__surah').get(
            verse_id=verse_id, language=lang
        )
    except Tafsir.DoesNotExist:
        cache.set(key, {}, 3600)
        return {}

    from .serializers import TafsirDetailSerializer
    data = TafsirDetailSerializer(tafsir).data
    cache.set(key, data, CACHE_TIMEOUT)
    return data


def get_verse(surah_number: int, verse_number: int, lang: str = 'en') -> Optional[dict]:
    try:
        translation_qs = Translation.objects.filter(language=lang)
        verse = (
            Verse.objects.filter(surah__number=surah_number, number=verse_number)
            .select_related('surah')
            .prefetch_related(Prefetch('translations', queryset=translation_qs))
            .first()
        )
        if not verse:
            return None

        from .serializers import VerseSerializer
        return VerseSerializer(verse, context={'lang': lang}).data
    except Exception as exc:
        logger.error('get_verse error: %s', exc)
        return None
