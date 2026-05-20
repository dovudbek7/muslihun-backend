import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from apps.quran.models import Surah, Verse, Translation, PageMapping

JUZ_BOUNDARIES = [
    (1, 1, 1), (2, 2, 142), (3, 2, 253), (4, 3, 93), (5, 4, 24),
    (6, 4, 148), (7, 5, 82), (8, 6, 111), (9, 7, 88), (10, 8, 41),
    (11, 9, 93), (12, 11, 6), (13, 12, 53), (14, 15, 1), (15, 17, 1),
    (16, 18, 75), (17, 21, 1), (18, 23, 1), (19, 25, 21), (20, 27, 56),
    (21, 29, 46), (22, 33, 31), (23, 36, 28), (24, 39, 32), (25, 41, 47),
    (26, 46, 1), (27, 51, 31), (28, 58, 1), (29, 67, 1), (30, 78, 1),
]

SURAH_PAGE_START = {
    1: 1, 2: 2, 3: 50, 4: 77, 5: 106, 6: 128, 7: 151, 8: 177, 9: 187, 10: 208,
    11: 221, 12: 235, 13: 249, 14: 255, 15: 262, 16: 267, 17: 282, 18: 293,
    19: 305, 20: 312, 21: 322, 22: 333, 23: 342, 24: 350, 25: 359, 26: 367,
    27: 377, 28: 385, 29: 396, 30: 404, 31: 411, 32: 415, 33: 418, 34: 428,
    35: 434, 36: 440, 37: 446, 38: 453, 39: 458, 40: 467, 41: 477, 42: 483,
    43: 489, 44: 496, 45: 499, 46: 502, 47: 507, 48: 511, 49: 515, 50: 518,
    51: 520, 52: 523, 53: 526, 54: 528, 55: 531, 56: 534, 57: 537, 58: 542,
    59: 545, 60: 549, 61: 551, 62: 553, 63: 554, 64: 556, 65: 558, 66: 560,
    67: 562, 68: 564, 69: 566, 70: 568, 71: 570, 72: 572, 73: 574, 74: 575,
    75: 577, 76: 578, 77: 580, 78: 582, 79: 583, 80: 585, 81: 586, 82: 587,
    83: 587, 84: 589, 85: 590, 86: 591, 87: 591, 88: 592, 89: 593, 90: 594,
    91: 595, 92: 595, 93: 596, 94: 596, 95: 597, 96: 597, 97: 598, 98: 598,
    99: 599, 100: 599, 101: 600, 102: 600, 103: 601, 104: 601, 105: 601,
    106: 602, 107: 602, 108: 602, 109: 603, 110: 603, 111: 603, 112: 604,
    113: 604, 114: 604,
}

SAJDA_VERSES = {
    (7, 206), (13, 15), (16, 50), (17, 109), (19, 58), (22, 18), (22, 77),
    (25, 60), (27, 26), (32, 15), (38, 24), (41, 38), (53, 62), (84, 21),
    (96, 19),
}


def build_juz_map() -> dict:
    juz_map = {}
    boundaries = sorted(JUZ_BOUNDARIES, key=lambda x: (x[1], x[2]))
    for i, (juz_num, surah_num, verse_num) in enumerate(boundaries):
        if i + 1 < len(boundaries):
            next_surah, next_verse = boundaries[i + 1][1], boundaries[i + 1][2]
        else:
            next_surah, next_verse = 115, 0
        juz_map[(surah_num, verse_num)] = (juz_num, next_surah, next_verse)
    return juz_map


def get_juz_for_verse(surah_num: int, verse_num: int, juz_boundaries: list) -> int:
    juz = 1
    for (j, s, v) in juz_boundaries:
        if (surah_num, verse_num) >= (s, v):
            juz = j
        else:
            break
    return juz


def get_page_for_verse(surah_num: int, verse_num: int, verse_pages: dict) -> int:
    key = (surah_num, verse_num)
    if key in verse_pages:
        return verse_pages[key]
    surah_start_page = SURAH_PAGE_START.get(surah_num, 1)
    return surah_start_page


class Command(BaseCommand):
    help = 'Import Quran text, translations, and metadata from JSON data files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-path',
            type=str,
            default=None,
            help='Path to quran-json data directory',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import',
        )

    def handle(self, *args, **options):
        data_path = options['data_path'] or settings.QURAN_DATA_PATH
        if not os.path.exists(data_path):
            raise CommandError(f'Data path not found: {data_path}')

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Translation.objects.all().delete()
            Verse.objects.all().delete()
            Surah.objects.all().delete()

        self.stdout.write('Loading JSON files...')
        arabic = self._load_json(data_path, 'quran.json')
        en_trans = self._load_json(data_path, 'editions/en.json')
        ru_trans = self._load_json(data_path, 'editions/ru.json')
        tr_trans = self._load_json(data_path, 'editions/tr.json')
        transliteration = self._load_json(data_path, 'editions/transliteration.json')
        chapters_en = self._load_json(data_path, 'chapters/en.json')
        chapters_ru = self._load_json(data_path, 'chapters/ru.json')
        chapters_tr = self._load_json(data_path, 'chapters/tr.json')

        chapters_ru_map = {ch['id']: ch for ch in chapters_ru}
        chapters_tr_map = {ch['id']: ch for ch in chapters_tr}

        self.stdout.write('Importing Surahs...')
        with transaction.atomic():
            self._import_surahs(chapters_en, chapters_ru_map, chapters_tr_map)

        self.stdout.write('Importing Verses and Translations...')
        with transaction.atomic():
            self._import_verses(
                arabic, en_trans, ru_trans, tr_trans, transliteration
            )

        self.stdout.write(self.style.SUCCESS('Import complete.'))

    def _load_json(self, data_path: str, filename: str) -> dict | list:
        filepath = os.path.join(data_path, filename)
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return {}
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)

    def _import_surahs(self, chapters_en, chapters_ru_map, chapters_tr_map):
        surahs_to_create = []
        surahs_to_update = []
        existing = {s.number: s for s in Surah.objects.all()}

        for ch in chapters_en:
            num = ch['id']
            page_start = SURAH_PAGE_START.get(num, 1)
            next_surah_page = SURAH_PAGE_START.get(num + 1, 605)
            page_end = next_surah_page - 1 if num < 114 else 604

            data = dict(
                number=num,
                name_arabic=ch['name'],
                name_transliteration=ch['transliteration'],
                name_en=ch['translation'],
                name_ru=chapters_ru_map.get(num, {}).get('translation', ''),
                name_tr=chapters_tr_map.get(num, {}).get('translation', ''),
                revelation_type=ch.get('type', 'meccan'),
                total_verses=ch['total_verses'],
                page_start=page_start,
                page_end=page_end,
            )

            if num in existing:
                surah = existing[num]
                for field, val in data.items():
                    setattr(surah, field, val)
                surahs_to_update.append(surah)
            else:
                surahs_to_create.append(Surah(**data))

        if surahs_to_create:
            Surah.objects.bulk_create(surahs_to_create, batch_size=50)
        if surahs_to_update:
            Surah.objects.bulk_update(
                surahs_to_update,
                fields=[
                    'name_arabic', 'name_transliteration', 'name_en',
                    'name_ru', 'name_tr', 'revelation_type', 'total_verses',
                    'page_start', 'page_end',
                ],
                batch_size=50,
            )
        self.stdout.write(f'  Surahs: {len(surahs_to_create)} created, {len(surahs_to_update)} updated')

    def _import_verses(self, arabic, en_trans, ru_trans, tr_trans, transliteration):
        surah_map = {s.number: s for s in Surah.objects.all()}
        juz_boundaries = sorted(JUZ_BOUNDARIES, key=lambda x: (x[1], x[2]))
        existing_verses = {
            (v.surah_id, v.number): v
            for v in Verse.objects.all()
        }

        verses_to_create = []
        verses_to_update = []
        translations_to_create = []
        global_index = 0

        for surah_num_str, verses in arabic.items():
            surah_num = int(surah_num_str)
            surah = surah_map.get(surah_num)
            if not surah:
                continue

            en_verses = en_trans.get(str(surah_num), en_trans.get(surah_num, []))
            ru_verses = ru_trans.get(str(surah_num), ru_trans.get(surah_num, []))
            tr_verses = tr_trans.get(str(surah_num), tr_trans.get(surah_num, []))
            tr_verses_list = tr_trans.get(str(surah_num), tr_trans.get(surah_num, []))
            tl_verses = transliteration.get(str(surah_num), transliteration.get(surah_num, []))

            en_map = {v['verse']: v['text'] for v in en_verses} if isinstance(en_verses, list) else {}
            ru_map = {v['verse']: v['text'] for v in ru_verses} if isinstance(ru_verses, list) else {}
            tr_map = {v['verse']: v['text'] for v in tr_verses_list} if isinstance(tr_verses_list, list) else {}
            tl_map = {v['verse']: v['text'] for v in tl_verses} if isinstance(tl_verses, list) else {}

            for verse_data in verses:
                verse_num = verse_data['verse']
                global_index += 1
                juz_num = get_juz_for_verse(surah_num, verse_num, juz_boundaries)
                page_num = self._compute_page(surah_num, verse_num)
                is_sajda = (surah_num, verse_num) in SAJDA_VERSES

                key = (surah.id, verse_num)
                verse_fields = dict(
                    surah=surah,
                    number=verse_num,
                    text_arabic=verse_data['text'],
                    text_transliteration=tl_map.get(verse_num, ''),
                    page_number=page_num,
                    juz_number=juz_num,
                    is_sajda=is_sajda,
                    global_index=global_index,
                )

                if key in existing_verses:
                    verse = existing_verses[key]
                    for f, v in verse_fields.items():
                        setattr(verse, f, v)
                    verses_to_update.append(verse)
                else:
                    verse_obj = Verse(**verse_fields)
                    verse_obj._en_text = en_map.get(verse_num, '')
                    verse_obj._ru_text = ru_map.get(verse_num, '')
                    verse_obj._tr_text = tr_map.get(verse_num, '')
                    verses_to_create.append(verse_obj)

        if verses_to_create:
            created = Verse.objects.bulk_create(verses_to_create, batch_size=200)
            for verse in created:
                if verse._en_text:
                    translations_to_create.append(
                        Translation(verse=verse, language='en', text=verse._en_text, source='sahih_international')
                    )
                if verse._ru_text:
                    translations_to_create.append(
                        Translation(verse=verse, language='ru', text=verse._ru_text, source='kuliyev')
                    )
                if verse._tr_text:
                    translations_to_create.append(
                        Translation(verse=verse, language='tr', text=verse._tr_text, source='diyanet')
                    )

        if verses_to_update:
            Verse.objects.bulk_update(
                verses_to_update,
                fields=['text_arabic', 'text_transliteration', 'page_number', 'juz_number', 'is_sajda', 'global_index'],
                batch_size=200,
            )

        if translations_to_create:
            Translation.objects.bulk_create(
                translations_to_create,
                ignore_conflicts=True,
                batch_size=500,
            )

        self.stdout.write(
            f'  Verses: {len(verses_to_create)} created, {len(verses_to_update)} updated'
        )
        self.stdout.write(f'  Translations: {len(translations_to_create)} created')

    def _compute_page(self, surah_num: int, verse_num: int) -> int:
        base_page = SURAH_PAGE_START.get(surah_num, 1)
        if surah_num >= 114:
            return base_page
        next_surah_page = SURAH_PAGE_START.get(surah_num + 1, base_page + 10)
        surah_obj = Surah.objects.filter(number=surah_num).values('total_verses').first()
        if not surah_obj:
            return base_page
        total_verses = surah_obj['total_verses']
        total_pages = max(1, next_surah_page - base_page)
        verse_fraction = (verse_num - 1) / total_verses
        return min(base_page + int(verse_fraction * total_pages), next_surah_page - 1)
