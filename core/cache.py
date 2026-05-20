import hashlib
import json
from functools import wraps
from django.core.cache import cache


def make_cache_key(prefix: str, *args, **kwargs) -> str:
    raw = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f'{prefix}:{digest}'


def cached_result(prefix: str, timeout: int = 3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = make_cache_key(prefix, *args[1:], **kwargs)
            result = cache.get(key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator


class QuranCacheKeys:
    SURAH_LIST = 'quran:surah_list:{lang}'
    SURAH_DETAIL = 'quran:surah:{surah_number}:{lang}'
    VERSE_LIST = 'quran:verses:{surah_number}:{lang}'
    PAGE_VERSES = 'quran:page:{page_number}:{lang}'
    JUZ_VERSES = 'quran:juz:{juz_number}:{lang}'
    TAFSIR = 'quran:tafsir:{verse_id}:{lang}'

    @staticmethod
    def format(template: str, **kwargs) -> str:
        return template.format(**kwargs)


class SearchCacheKeys:
    SEARCH_RESULTS = 'search:results:{query_hash}:{lang}'

    @staticmethod
    def for_query(query: str, lang: str) -> str:
        digest = hashlib.md5(query.lower().encode()).hexdigest()[:10]
        return f'search:results:{digest}:{lang}'


class PrayerCacheKeys:
    TIMES = 'prayer:times:{date}:{lat}:{lon}:{method}'

    @staticmethod
    def format(date: str, lat: float, lon: float, method: int) -> str:
        return f'prayer:times:{date}:{lat:.4f}:{lon:.4f}:{method}'
