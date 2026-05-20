from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .services import (
    get_surah_list,
    get_surah_detail,
    get_page_verses,
    get_juz_verses,
    get_verse_tafsir,
    get_verse,
)
from .models import Surah, Verse


VALID_LANGUAGES = {'en', 'ru', 'tr', 'uz_latin', 'uz_cyrillic'}


def get_lang(request) -> str:
    lang = request.query_params.get('lang', 'en')
    return lang if lang in VALID_LANGUAGES else 'en'


class SurahListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[OpenApiParameter('lang', str, description='Language code')],
        summary='List all 114 surahs',
    )
    def get(self, request):
        data = get_surah_list(lang=get_lang(request))
        return Response(data)


class SurahDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[OpenApiParameter('lang', str)],
        summary='Get surah with all verses',
    )
    def get(self, request, surah_number: int):
        if not 1 <= surah_number <= 114:
            return Response({'error': 'Surah number must be between 1 and 114.'}, status=400)
        data = get_surah_detail(surah_number, lang=get_lang(request))
        if data is None:
            return Response({'error': 'Surah not found.'}, status=404)
        return Response(data)


class VerseDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, surah_number: int, verse_number: int):
        data = get_verse(surah_number, verse_number, lang=get_lang(request))
        if data is None:
            return Response({'error': 'Verse not found.'}, status=404)
        return Response(data)


class PageView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[OpenApiParameter('lang', str)],
        summary='Get all verses on a mushaf page (1-604)',
    )
    def get(self, request, page_number: int):
        if not 1 <= page_number <= 604:
            return Response({'error': 'Page number must be between 1 and 604.'}, status=400)
        data = get_page_verses(page_number, lang=get_lang(request))
        return Response({'page_number': page_number, 'verses': data})


class JuzView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, juz_number: int):
        if not 1 <= juz_number <= 30:
            return Response({'error': 'Juz number must be between 1 and 30.'}, status=400)
        data = get_juz_verses(juz_number, lang=get_lang(request))
        return Response({'juz_number': juz_number, 'verses': data})


class TafsirView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, surah_number: int, verse_number: int):
        lang = get_lang(request)
        try:
            verse = Verse.objects.get(surah__number=surah_number, number=verse_number)
        except Verse.DoesNotExist:
            return Response({'error': 'Verse not found.'}, status=404)

        data = get_verse_tafsir(verse.id, lang=lang)
        if not data:
            return Response(
                {'error': f'Tafsir not available in {lang} for this verse.'},
                status=404
            )
        return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def surah_meta(request):
    surahs = Surah.objects.values(
        'number', 'name_arabic', 'name_transliteration',
        'name_en', 'total_verses', 'page_start', 'revelation_type'
    )
    return Response(list(surahs))


@api_view(['GET'])
@permission_classes([AllowAny])
def navigation_data(request):
    surahs = list(Surah.objects.values(
        'number', 'name_arabic', 'name_transliteration', 'name_en',
        'name_ru', 'name_tr', 'total_verses', 'page_start', 'page_end'
    ))
    juz_data = []
    for juz_num in range(1, 31):
        first_verse = Verse.objects.filter(juz_number=juz_num).select_related('surah').first()
        if first_verse:
            juz_data.append({
                'juz_number': juz_num,
                'surah_number': first_verse.surah.number,
                'verse_number': first_verse.number,
                'page_number': first_verse.page_number,
            })
    return Response({'surahs': surahs, 'juz': juz_data, 'total_pages': 604})
