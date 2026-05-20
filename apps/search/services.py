from typing import Optional
import logging
import re
from django.core.cache import cache
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from rapidfuzz import fuzz, process
from apps.quran.models import Surah, Verse, Translation
from core.utils import normalize_text, normalize_arabic, cyrillic_to_latin, is_arabic, is_cyrillic
from core.cache import SearchCacheKeys

logger = logging.getLogger(__name__)

SURAH_ALIASES = {
    'fatiha': 1, 'al-fatiha': 1, 'al-fatihah': 1, 'фатиха': 1, 'fatih': 1,
    'baqara': 2, 'bakara': 2, 'al-baqara': 2, 'al-baqarah': 2, 'бакара': 2, 'бақара': 2,
    'imran': 3, 'al-imran': 3, "ali imran": 3, 'аль имран': 3,
    'nisa': 4, 'an-nisa': 4, 'ниса': 4,
    'maida': 5, 'al-maida': 5, 'маида': 5,
    'ikhlas': 112, 'al-ikhlas': 112, 'ихлас': 112,
    'falaq': 113, 'al-falaq': 113, 'фалак': 113,
    'nas': 114, 'an-nas': 114, 'нас': 114,
    'yasin': 36, 'ya-sin': 36, 'ясин': 36, 'yaseen': 36,
    'rahman': 55, 'ar-rahman': 55, 'рахман': 55,
    'waqia': 56, 'al-waqia': 56, 'вакиа': 56, 'waqi\'a': 56,
    'mulk': 67, 'al-mulk': 67, 'мульк': 67,
    'kahf': 18, 'al-kahf': 18, 'кахф': 18,
}

SEARCH_CACHE_TIMEOUT = 300


def search(
    query: str,
    lang: str = 'en',
    limit: int = 20,
    offset: int = 0,
) -> dict:
    if not query or not query.strip():
        return {'results': [], 'total': 0, 'query': query}

    query = query.strip()
    cache_key = SearchCacheKeys.for_query(query, lang)
    cached = cache.get(cache_key)
    if cached:
        results = cached
        return {
            'results': results[offset:offset + limit],
            'total': len(results),
            'query': query,
            'cached': True,
        }

    results = []

    surah_match = _try_surah_search(query)
    if surah_match:
        results = surah_match
    elif is_arabic(query):
        results = _search_arabic(query, lang)
    elif is_cyrillic(query):
        latin_query = cyrillic_to_latin(query)
        results = _search_text(latin_query, lang) or _search_text(query, lang)
    else:
        results = _search_text(query, lang)

    cache.set(cache_key, results, SEARCH_CACHE_TIMEOUT)
    return {
        'results': results[offset:offset + limit],
        'total': len(results),
        'query': query,
    }


def _try_surah_search(query: str) -> Optional[list]:
    normalized = normalize_text(query)

    if normalized in SURAH_ALIASES:
        surah_num = SURAH_ALIASES[normalized]
        try:
            surah = Surah.objects.get(number=surah_num)
            return [_surah_result(surah)]
        except Surah.DoesNotExist:
            return None

    all_surahs = list(Surah.objects.all())
    candidates = {}
    for s in all_surahs:
        candidates[s.name_transliteration.lower()] = s
        candidates[s.name_en.lower()] = s
        if s.name_ru:
            candidates[s.name_ru.lower()] = s
        if s.name_tr:
            candidates[s.name_tr.lower()] = s

    matches = process.extract(
        normalized,
        list(candidates.keys()),
        scorer=fuzz.WRatio,
        limit=3,
        score_cutoff=70,
    )

    if matches:
        best_match = matches[0]
        matched_surah = candidates[best_match[0]]
        return [_surah_result(matched_surah)]

    return None


def _surah_result(surah: Surah) -> dict:
    return {
        'type': 'surah',
        'surah_number': surah.number,
        'surah_name': surah.name_transliteration,
        'surah_name_arabic': surah.name_arabic,
        'page': surah.page_start,
        'juz': None,
        'ayah': None,
        'matched_text': surah.name_transliteration,
        'score': 100,
    }


def _search_arabic(query: str, lang: str) -> list:
    normalized = normalize_arabic(query)
    qs = (
        Verse.objects.filter(text_arabic__contains=normalized)
        .select_related('surah')
        [:50]
    )
    return [_verse_result(v, lang, query) for v in qs]


def _search_text(query: str, lang: str) -> list:
    normalized = normalize_text(query)
    words = normalized.split()
    if not words:
        return []

    q_filter = Q()
    for word in words:
        if len(word) >= 3:
            q_filter &= Q(text__icontains=word)

    if not q_filter:
        q_filter = Q(text__icontains=normalized)

    translations = (
        Translation.objects.filter(language=lang)
        .filter(q_filter)
        .select_related('verse__surah')
        [:50]
    )

    results = []
    seen = set()
    for t in translations:
        v = t.verse
        key = (v.surah.number, v.number)
        if key in seen:
            continue
        seen.add(key)
        score = fuzz.partial_ratio(normalized, normalize_text(t.text))
        results.append({
            **_verse_result(v, lang, query),
            'matched_text': t.text[:200],
            'score': score,
        })

    results.sort(key=lambda x: -x['score'])

    if not results:
        results = _fuzzy_surah_name_search(normalized, lang)

    return results


def _fuzzy_surah_name_search(query: str, lang: str) -> list:
    surahs = Surah.objects.all()
    results = []
    for s in surahs:
        fields = [s.name_en, s.name_transliteration, s.name_ru or '', s.name_tr or '']
        best_score = max(fuzz.WRatio(query, normalize_text(f)) for f in fields if f)
        if best_score >= 65:
            results.append({**_surah_result(s), 'score': best_score})
    results.sort(key=lambda x: -x['score'])
    return results[:10]


def _verse_result(verse: Verse, lang: str, query: str) -> dict:
    translation = verse.translations.filter(language=lang).values('text').first()
    return {
        'type': 'verse',
        'surah_number': verse.surah.number,
        'surah_name': verse.surah.name_transliteration,
        'surah_name_arabic': verse.surah.name_arabic,
        'ayah': verse.number,
        'page': verse.page_number,
        'juz': verse.juz_number,
        'text_arabic': verse.text_arabic,
        'matched_text': (translation['text'][:200] if translation else ''),
        'score': 80,
    }
