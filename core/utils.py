import re
import unicodedata


ARABIC_VARIANTS = {
    'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',
    'ة': 'ه',
    'ى': 'ي',
    'ؤ': 'و',
    'ئ': 'ي',
}

LATIN_TO_ARABIC_MAP = {
    'al-fatihah': 'الفاتحة', 'al-fatiha': 'الفاتحة', 'fatiha': 'الفاتحة',
    'al-baqarah': 'البقرة', 'al-baqara': 'البقرة', 'bakara': 'البقرة',
}

UZ_CYRILLIC_TO_LATIN = {
    'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
    'Ж': 'J', 'ж': 'j', 'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k', 'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n', 'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r', 'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u', 'Ф': 'F', 'ф': 'f',
    'Х': 'X', 'х': 'x', 'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh',
    'Ъ': "'", 'ъ': "'", 'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu',
    'Я': 'Ya', 'я': 'ya', 'Ў': "O'", 'ў': "o'", 'Қ': 'Q', 'қ': 'q',
    'Ғ': "G'", 'ғ': "g'", 'Ҳ': 'H', 'ҳ': 'h',
    'Б': 'B', 'Бақара': 'Baqara', 'бақара': 'baqara',
}


def normalize_arabic(text: str) -> str:
    normalized = ''
    for char in text:
        char = ARABIC_VARIANTS.get(char, char)
        normalized += char
    return re.sub(r'[ً-ٰٟ]', '', normalized)


def cyrillic_to_latin(text: str) -> str:
    result = ''
    i = 0
    while i < len(text):
        two_char = text[i:i+2]
        if two_char in UZ_CYRILLIC_TO_LATIN:
            result += UZ_CYRILLIC_TO_LATIN[two_char]
            i += 2
        elif text[i] in UZ_CYRILLIC_TO_LATIN:
            result += UZ_CYRILLIC_TO_LATIN[text[i]]
            i += 1
        else:
            result += text[i]
            i += 1
    return result


def normalize_text(text: str) -> str:
    text = unicodedata.normalize('NFC', text.strip().lower())
    text = re.sub(r'[^\w\s؀-ۿݐ-ݿ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_arabic(text: str) -> bool:
    arabic_pattern = re.compile(r'[؀-ۿ]')
    return bool(arabic_pattern.search(text))


def is_cyrillic(text: str) -> bool:
    cyrillic_pattern = re.compile(r'[Ѐ-ӿ]')
    return bool(cyrillic_pattern.search(text))


def verse_global_index(surah_number: int, verse_number: int) -> int:
    SURAH_VERSE_COUNTS = [
        0, 7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
        123, 111, 43, 52, 99, 128, 111, 110, 98, 135, 112,
        78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73,
        54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37,
        35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29,
        22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
        44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29,
        19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11,
        8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5,
        4, 7, 3, 6, 3, 5, 4, 5, 6,
    ]
    total = 0
    for i in range(1, surah_number):
        total += SURAH_VERSE_COUNTS[i]
    return total + verse_number
