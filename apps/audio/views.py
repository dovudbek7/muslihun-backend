from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from apps.quran.models import Surah, Verse
from .models import Reciter, AudioEdition
from .serializers import ReciterSerializer, VerseAudioSerializer, SurahAudioSerializer


DEFAULT_RECITERS = [
    {
        'identifier': 'en.alafasy',
        'name_en': 'Mishary Rashid Alafasy',
        'name_ar': 'مشاري راشد العفاسي',
        'style': 'murattal',
        'bitrate': 128,
        'display_order': 1,
    },
    {
        'identifier': 'ar.luhaidan',
        'name_en': 'Muhammad Al-Luhaidan',
        'name_ar': 'محمد اللحيدان',
        'style': 'mujawwad',
        'bitrate': 128,
        'display_order': 2,
    },
]

CDN_BASE = 'https://cdn.islamic.network/quran/audio'


def get_or_seed_reciters():
    if not Reciter.objects.exists():
        for r in DEFAULT_RECITERS:
            Reciter.objects.get_or_create(
                identifier=r['identifier'],
                defaults={
                    **r,
                    'audio_base_url': f"{CDN_BASE}/{r['bitrate']}/{r['identifier']}",
                }
            )
    return Reciter.objects.filter(is_active=True)


class ReciterListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ReciterSerializer

    def get_queryset(self):
        return get_or_seed_reciters()


@api_view(['GET'])
@permission_classes([AllowAny])
def verse_audio(request, surah_number: int, verse_number: int):
    if not 1 <= surah_number <= 114:
        return Response({'error': 'Invalid surah number.'}, status=400)

    reciter_id = request.query_params.get('reciter')
    reciters = get_or_seed_reciters()

    if reciter_id:
        try:
            reciter = reciters.get(id=reciter_id)
        except Reciter.DoesNotExist:
            return Response({'error': 'Reciter not found.'}, status=404)
    else:
        reciter = reciters.first()

    if not reciter:
        return Response({'error': 'No reciters available.'}, status=404)

    try:
        verse = Verse.objects.get(surah__number=surah_number, number=verse_number)
    except Verse.DoesNotExist:
        return Response({'error': 'Verse not found.'}, status=404)

    audio_url = reciter.get_verse_url(surah_number, verse_number)

    return Response({
        'surah_number': surah_number,
        'verse_number': verse_number,
        'reciter_id': reciter.id,
        'reciter_name': reciter.name_en,
        'audio_url': audio_url,
        'global_index': verse.global_index,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def surah_audio(request, surah_number: int):
    if not 1 <= surah_number <= 114:
        return Response({'error': 'Invalid surah number.'}, status=400)

    include_verses = request.query_params.get('include_verses', 'false').lower() == 'true'
    reciter_id = request.query_params.get('reciter')
    reciters = get_or_seed_reciters()

    if reciter_id:
        try:
            reciter = reciters.get(id=reciter_id)
        except Reciter.DoesNotExist:
            return Response({'error': 'Reciter not found.'}, status=404)
    else:
        reciter = reciters.first()

    if not reciter:
        return Response({'error': 'No reciters available.'}, status=404)

    try:
        surah = Surah.objects.get(number=surah_number)
    except Surah.DoesNotExist:
        return Response({'error': 'Surah not found.'}, status=404)

    data = {
        'surah_number': surah_number,
        'surah_name': surah.name_transliteration,
        'reciter': ReciterSerializer(reciter).data,
        'audio_url': reciter.get_surah_url(surah_number),
    }

    if include_verses:
        data['verse_urls'] = [
            reciter.get_verse_url(surah_number, v)
            for v in range(1, surah.total_verses + 1)
        ]

    return Response(data)
