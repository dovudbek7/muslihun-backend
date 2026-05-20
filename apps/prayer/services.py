import requests
import logging
from typing import Optional
from datetime import date, datetime, timezone
from django.core.cache import cache
from core.cache import PrayerCacheKeys

logger = logging.getLogger(__name__)

ALADHAN_API = 'https://api.aladhan.com/v1/timings'
CACHE_TIMEOUT = 3600 * 6

PRAYER_NAMES = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
PRAYER_NAMES_RU = {
    'Fajr': 'Бомдод', 'Sunrise': 'Қуёш чиқиши', 'Dhuhr': 'Пешин',
    'Asr': 'Аср', 'Maghrib': 'Шом', 'Isha': 'Хуфтон',
}
PRAYER_NAMES_UZ = {
    'Fajr': 'Bomdod', 'Sunrise': 'Quyosh chiqishi', 'Dhuhr': 'Peshin',
    'Asr': 'Asr', 'Maghrib': 'Shom', 'Isha': 'Xufton',
}


def get_prayer_times(
    latitude: float,
    longitude: float,
    method: int = 3,
    target_date: Optional[date] = None,
) -> dict:
    if target_date is None:
        target_date = date.today()

    cache_key = PrayerCacheKeys.format(
        str(target_date), latitude, longitude, method
    )
    cached = cache.get(cache_key)
    if cached:
        return cached

    timestamp = int(datetime(target_date.year, target_date.month, target_date.day).timestamp())
    url = f'{ALADHAN_API}/{timestamp}'
    params = {'latitude': latitude, 'longitude': longitude, 'method': method}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()['data']['timings']
    except Exception as exc:
        logger.error('Prayer times API error: %s', exc)
        return _fallback_times()

    result = {
        'date': str(target_date),
        'latitude': latitude,
        'longitude': longitude,
        'method': method,
        'timings': {
            name: data[name]
            for name in PRAYER_NAMES
            if name in data
        },
    }
    cache.set(cache_key, result, CACHE_TIMEOUT)
    return result


def get_next_prayer(prayer_times: dict) -> dict:
    now = datetime.now()
    timings = prayer_times.get('timings', {})

    for prayer_name in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
        time_str = timings.get(prayer_name)
        if not time_str:
            continue
        try:
            hour, minute = map(int, time_str.split(':'))
            prayer_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if prayer_dt > now:
                seconds_remaining = int((prayer_dt - now).total_seconds())
                return {
                    'name': prayer_name,
                    'time': time_str,
                    'seconds_remaining': seconds_remaining,
                }
        except (ValueError, AttributeError):
            continue

    fajr_time = timings.get('Fajr', '05:00')
    hour, minute = map(int, fajr_time.split(':'))
    from datetime import timedelta
    tomorrow_fajr = (now + timedelta(days=1)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    return {
        'name': 'Fajr',
        'time': fajr_time,
        'seconds_remaining': int((tomorrow_fajr - now).total_seconds()),
    }


def _fallback_times() -> dict:
    return {
        'date': str(date.today()),
        'timings': {
            'Fajr': '05:30', 'Sunrise': '07:00', 'Dhuhr': '12:30',
            'Asr': '15:30', 'Maghrib': '18:00', 'Isha': '19:30',
        },
        'fallback': True,
    }
