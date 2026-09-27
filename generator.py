#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generator.py — MEGA dashboard v3.
Погода, космос, новости, инструменты, трекеры, самолёты, живая карта МКС.
"""
import os
import re
import json
import html
import random
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from math import radians, cos, sin, asin, sqrt

import requests

DOCS = Path('docs')
UA = 'Mozilla/5.0 (compatible; Dashboard/3.0)'
NALCHIK_LAT = 43.4981
NALCHIK_LON = 43.6189
NALCHIK_NAME = 'Нальчик'

WEEKDAYS_SHORT = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
WEEKDAYS_FULL = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
MONTHS_GEN = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
MONTHS_NOM = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

HOLIDAYS = {
    (1, 1): "🎄 Новый год", (1, 7): "🌟 Рождество",
    (1, 14): "🎊 Старый Новый год",
    (2, 23): "🎖 День защитника Отечества",
    (3, 8): "💐 8 Марта",
    (4, 12): "🚀 День космонавтики",
    (5, 1): "🌷 Праздник Весны и Труда",
    (5, 9): "🎗 День Победы",
    (6, 1): "👶 День защиты детей",
    (6, 12): "🇷🇺 День России",
    (9, 1): "📚 День знаний",
    (11, 4): "🕊 День народного единства",
    (12, 31): "🥂 Канун Нового года",
}

QUOTES = [
    ("Жизнь — это то, что происходит, пока ты строишь планы.", "Джон Леннон"),
    ("Единственный способ делать великую работу — любить то, что делаешь.", "Стив Джобс"),
    ("Не бойся медленно идти, бойся стоять на месте.", "Китайская пословица"),
    ("Дорогу осилит идущий.", "Латинская пословица"),
    ("Всё гениальное — просто.", "Исаак Ньютон"),
    ("Кто хочет — ищет возможности, кто не хочет — ищет причины.", "Сократ"),
    ("Самый тёмный час — перед рассветом.", "Пауло Коэльо"),
    ("Меняй свою жизнь, а не мир вокруг.", "Лев Толстой"),
    ("Будь тем изменением, которое ты хочешь видеть в мире.", "Махатма Ганди"),
    ("Цель без плана — просто желание.", "Антуан де Сент-Экзюпери"),
    ("Мы то, что мы делаем постоянно. Совершенство — не действие, а привычка.", "Аристотель"),
    ("Победа над собой — величайшая из побед.", "Платон"),
    ("Если хочешь идти быстро — иди один. Если хочешь идти далеко — иди вместе.", "Африканская пословица"),
    ("Лучший способ предсказать будущее — создать его.", "Питер Друкер"),
    ("Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма.", "Уинстон Черчилль"),
]

MOOD_TRACKS = {
    'sun': [('Here Comes the Sun', 'The Beatles'), ('Walking on Sunshine', 'Katrina & The Waves'), ('Good Vibrations', 'The Beach Boys')],
    'cloud': [('Mad World', 'Gary Jules'), ('Boulevard of Broken Dreams', 'Green Day'), ('Fix You', 'Coldplay')],
    'rain': [('Riders on the Storm', 'The Doors'), ('Set Fire to the Rain', 'Adele'), ('Purple Rain', 'Prince')],
    'snow': [('White Winter Hymnal', 'Fleet Foxes'), ('Winter Song', 'Sara Bareilles'), ('Let It Snow', 'Frank Sinatra')],
    'storm': [('Thunderstruck', 'AC/DC'), ('Storm', 'Godspeed You! Black Emperor'), ('Lightning Crashes', 'Live')],
    'fog': [('Fog', 'Radiohead'), ('Clint Eastwood', 'Gorillaz'), ('Silent Lucidity', 'Queensrÿche')],
}

FACTS = [
    "Мёд не портится. Археологи находили в египетских гробницах 3000-летний мёд — он был съедобен.",
    "Осьминоги имеют три сердца. Два качают кровь через жабры, третье — к остальному телу.",
    "Бананы радиоактивны из-за калия-40. Но чтобы получить опасную дозу, нужно съесть ~10 миллионов.",
    "Отпечаток языка — уникален, как отпечаток пальца. Нет двух людей с одинаковым.",
    "Между Марсом и Юпитером больше миллиона астероидов, но их общая масса меньше массы Луны.",
    "Средняя продолжительность молнии — 30 микросекунд. Но её видно — глаз цепляет кадр.",
    "В человеческом теле 37 триллионов клеток и 30 триллионов бактерий — почти пополам.",
    "Земля вращается со скоростью 1670 км/ч на экваторе — мы не замечаем.",
    "Венера вращается в обратную сторону. Солнце там восходит на западе.",
    "Твоё тело содержит ~7 000 000 000 000 000 000 000 000 000 атомов.",
    "Вода в облаке размером с кубический километр весит ~500 тонн.",
    "Первое фото Луны сделал Джон Адамс Уиппл в 1851 году.",
    "Сердце за жизнь делает около 2,5 миллиардов ударов.",
    "Стрекозы существовали до динозавров. Они старше на 100 млн лет.",
    "Через 5 миллиардов лет Солнце станет красным гигантом и поглотит Меркурий и Венеру.",
]


def log(m): print(m, flush=True)


def get(url, timeout=12, json_=False, headers=None):
    try:
        h = {'User-Agent': UA}
        if headers: h.update(headers)
        r = requests.get(url, timeout=timeout, headers=h)
        r.raise_for_status()
        return r.json() if json_ else r
    except Exception as e:
        log(f"⚠️  {url}: {e}")
        return None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return round(2 * R * asin(sqrt(a)))


def weather_icon(code):
    try: code = int(code)
    except: return '🌡️'
    if code == 0: return '☀️'
    if code <= 3: return '⛅'
    if code <= 48: return '🌫️'
    if code <= 57: return '🌦️'
    if code <= 67: return '🌧️'
    if code <= 77: return '❄️'
    if code <= 82: return '🌧️'
    if code <= 86: return '❄️'
    return '⛈️'


def weather_kind(code):
    if code == 0: return 'sun'
    if code <= 3: return 'cloud'
    if code <= 48: return 'fog'
    if code <= 67: return 'rain'
    if code <= 77: return 'snow'
    if code <= 82: return 'rain'
    if code <= 86: return 'snow'
    return 'storm'


def fetch_weather():
    r = get('https://wttr.in/Nalchik?format=j1', json_=True)
    if not r: return None
    try:
        cur = r['current_condition'][0]
        today = r['weather'][0]
        astro = today['astronomy'][0]
        return {
            'temp': cur['temp_C'], 'feels': cur['FeelsLikeC'],
            'code': int(cur.get('weatherCode', 0)),
            'kind': weather_kind(int(cur.get('weatherCode', 0))),
            'humidity': cur.get('humidity', '—'),
            'wind': cur.get('windspeedKmph', '—'),
            'pressure': cur.get('pressure', '—'),
            'sunrise': astro.get('sunrise', ''),
            'sunset': astro.get('sunset', ''),
            'forecast': [
                {'date': d['date'], 'max': d['maxtempC'], 'min': d['mintempC'],
                 'code': int(d['hourly'][4].get('weatherCode', 0))}
                for d in r['weather'][:3]
            ],
        }
    except Exception as e:
        log(f"weather: {e}"); return None


def golden_hour(weather):
    if not weather or not weather.get('sunrise') or not weather.get('sunset'):
        return None
    def parse_t(s):
        try: return int(s.split(':')[0]), int(s.split(':')[1])
        except: return None, None
    sr_h, sr_m = parse_t(weather['sunrise']); ss_h, ss_m = parse_t(weather['sunset'])
    if sr_h is None or ss_h is None: return None
    sr_min = sr_h * 60 + sr_m; ss_min = ss_h * 60 + ss_m
    return {
        'morning_start': f"{(sr_min-60)//60:02d}:{(sr_min-60)%60:02d}",
        'morning_end':   f"{(sr_min+30)//60:02d}:{(sr_min+30)%60:02d}",
        'evening_start': f"{(ss_min-45)//60:02d}:{(ss_min-45)%60:02d}",
        'evening_end':   f"{(ss_min+30)//60:02d}:{(ss_min+30)%60:02d}",
    }


def fetch_currency():
    r = get('https://www.cbr-xml-daily.ru/daily_json.js', json_=True)
    if r:
        try:
            v = r['Valute']
            return {'usd': round(v['USD']['Value'], 2), 'eur': round(v['EUR']['Value'], 2), 'cny': round(v['CNY']['Value'], 2)}
        except: pass
    r = get('https://www.cbr.ru/scripts/XML_daily.asp', timeout=15)
    if r:
        try:
            r.encoding = 'windows-1251'
            root = ET.fromstring(r.text)
            out = {}
            for val in root.findall('Valute'):
                code = val.findtext('CharCode'); value = val.findtext('Value')
                if code in ('USD', 'EUR', 'CNY') and value:
                    out[code.lower()] = round(float(value.replace(',', '.')) / int(val.findtext('Nominal') or '1'), 2)
            if all(k in out for k in ('usd', 'eur', 'cny')): return out
        except: pass
    return None


def fetch_crypto():
    r = get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,the-open-network&vs_currencies=usd&include_24hr_change=true', json_=True)
    if not r: return None
    out = {}
    try:
        if 'bitcoin' in r: out['btc'] = {'usd': round(r['bitcoin']['usd']), 'chg': round(r['bitcoin'].get('usd_24h_change', 0), 2)}
        if 'ethereum' in r: out['eth'] = {'usd': round(r['ethereum']['usd']), 'chg': round(r['ethereum'].get('usd_24h_change', 0), 2)}
        if 'the-open-network' in r: out['ton'] = {'usd': round(r['the-open-network']['usd'], 2), 'chg': round(r['the-open-network'].get('usd_24h_change', 0), 2)}
    except: pass
    return out or None


def parse_rss(xml_bytes, source_name, limit=5):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
        for item in root.iter('item'):
            t = item.find('title'); l = item.find('link'); p = item.find('pubDate'); d = item.find('description')
            if t is None or not t.text: continue
            desc = ''
            if d is not None and d.text:
                desc = re.sub(r'<[^>]+>', '', d.text)
                desc = html.unescape(desc).strip()
                if len(desc) > 130: desc = desc[:127] + '...'
            items.append({'title': t.text.strip(),
                          'link': (l.text or '').strip() if l is not None else '',
                          'date': (p.text or '').strip() if p is not None else '',
                          'desc': desc, 'source': source_name})
            if len(items) >= limit: break
    except Exception as e:
        log(f"RSS {source_name}: {e}")
    return items


NEWS_SOURCES = [
    ('Lenta', 'https://lenta.ru/rss/news'),
    ('RBC', 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss'),
    ('TASS', 'https://tass.ru/rss/v2.xml'),
    ('Habr', 'https://habr.com/ru/rss/news/?fl=ru'),
    ('Известия', 'https://iz.ru/xml/rss/all.xml'),
]


def fetch_news():
    all_items = []
    for name, url in NEWS_SOURCES:
        r = get(url, timeout=12)
        if not r: continue
        all_items.extend(parse_rss(r.content, name, limit=5))
    def parse_date(s):
        for fmt in ('%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S'):
            try:
                dt = datetime.datetime.strptime(s, fmt)
                if dt.tzinfo is not None:
                    dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                return dt
            except: continue
        return datetime.datetime.min
    for it in all_items: it['dt'] = parse_date(it['date'])
    all_items.sort(key=lambda x: x['dt'], reverse=True)
    return all_items[:12]


def fetch_iss():
    r = get('https://api.wheretheiss.at/v1/satellites/25544', json_=True)
    if not r: return None
    try:
        lat = float(r['latitude']); lon = float(r['longitude'])
        return {'lat': round(lat, 2), 'lon': round(lon, 2),
                'alt': round(float(r['altitude'])),
                'velocity': round(float(r['velocity'])),
                'visibility': r.get('visibility', '?'),
                'dist': haversine(NALCHIK_LAT, NALCHIK_LON, lat, lon)}
    except: return None


def fetch_kp_index():
    candidates = [
        'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json',
        'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json',
    ]
    for url in candidates:
        r = get(url, json_=True, timeout=10)
        if not r or not isinstance(r, list) or len(r) < 2: continue
        vals = []
        for item in r:
            if isinstance(item, dict):
                v = item.get('estimated_kp') or item.get('kp_index') or item.get('kp')
                if v is not None:
                    try: vals.append(float(v))
                    except: pass
            elif isinstance(item, list) and len(item) >= 2:
                try: vals.append(float(item[1]))
                except: pass
        if vals:
            kp = vals[-1]
            return {'kp': kp, 'level': kp_to_level(kp), 'aurora_possible': kp >= 6, 'forecast': vals[-8:]}
    return None


def kp_to_level(kp):
    if kp < 4: return ('Спокойно', '#4ade80')
    if kp < 5: return ('Возмущено', '#facc15')
    if kp < 6: return ('Слабая буря G1', '#fb923c')
    if kp < 7: return ('Умеренная G2', '#f87171')
    if kp < 8: return ('Сильная G3', '#f87171')
    return ('Очень сильная G4+', '#dc2626')


def fetch_air_quality():
    r = get(f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={NALCHIK_LAT}&longitude={NALCHIK_LON}&current=pm10,pm2_5,european_aqi,us_aqi', json_=True)
    if not r: return None
    try:
        c = r.get('current', {}); aqi = c.get('european_aqi') or c.get('us_aqi')
        return {'aqi': round(aqi) if aqi is not None else None, 'pm25': c.get('pm2_5'), 'pm10': c.get('pm10'), 'level': aqi_level(aqi)}
    except: return None


def aqi_level(aqi):
    if aqi is None: return ('—', '#8a8f98')
    if aqi <= 20: return ('Отличный', '#4ade80')
    if aqi <= 40: return ('Хороший', '#86efac')
    if aqi <= 60: return ('Средний', '#facc15')
    if aqi <= 80: return ('Плохой', '#fb923c')
    if aqi <= 100: return ('Очень плохой', '#f87171')
    return ('Опасный', '#dc2626')


def fetch_uv_index():
    r = get(f'https://api.open-meteo.com/v1/forecast?latitude={NALCHIK_LAT}&longitude={NALCHIK_LON}&current=uv_index&daily=uv_index_max&timezone=Europe%2FMoscow', json_=True)
    if not r: return None
    try:
        cur = r.get('current', {}); daily = r.get('daily', {})
        return {'uv': cur.get('uv_index'), 'uv_max': (daily.get('uv_index_max') or [None])[0], 'level': uv_level(cur.get('uv_index'))}
    except: return None


def uv_level(uv):
    if uv is None: return ('—', '#8a8f98')
    try: uv = float(uv)
    except: return ('—', '#8a8f98')
    if uv < 3: return ('Низкий', '#4ade80')
    if uv < 6: return ('Умеренный', '#facc15')
    if uv < 8: return ('Высокий', '#fb923c')
    if uv < 11: return ('Очень высокий', '#f87171')
    return ('Экстремальный', '#dc2626')


def fetch_earthquakes():
    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude={NALCHIK_LAT}&longitude={NALCHIK_LON}&maxradiuskm=1500&limit=5&orderby=time&minmagnitude=3.5'
    r = get(url, json_=True)
    if not r: return []
    try:
        out = []
        for f in r.get('features', [])[:5]:
            p = f.get('properties', {}); g = f.get('geometry', {}).get('coordinates', [None, None])
            lon, lat = g[0], g[1]
            out.append({'mag': p.get('mag'), 'place': p.get('place'), 'time': p.get('time'),
                        'dist': haversine(NALCHIK_LAT, NALCHIK_LON, lat, lon) if lat and lon else None})
        return out
    except: return []


def time_ago_from_ts(ms):
    if not ms: return ''
    try:
        dt = datetime.datetime.fromtimestamp(ms / 1000)
        s = int((datetime.datetime.now() - dt).total_seconds())
        if s < 60: return 'только что'
        if s < 3600: return f'{s // 60} мин'
        if s < 86400: return f'{s // 3600} ч'
        return f'{s // 86400} дн'
    except: return ''


def fetch_planes():
    delta = 1.5
    url = f'https://opensky-network.org/api/states/all?lamin={NALCHIK_LAT-delta}&lomin={NALCHIK_LON-delta}&lamax={NALCHIK_LAT+delta}&lomax={NALCHIK_LON+delta}'
    r = get(url, json_=True, timeout=15)
    if not r: return []
    try:
        out = []
        for s in (r.get('states') or [])[:8]:
            try:
                callsign = (s[1] or '').strip()
                if not callsign: continue
                lon, lat = s[5], s[6]; alt = s[7] or s[13]; speed = s[9]; country = s[2]
                if lat is None or lon is None: continue
                out.append({'callsign': callsign, 'country': country,
                            'alt': round(alt) if alt else 0,
                            'speed': round(speed * 3.6) if speed else 0,
                            'dist': haversine(NALCHIK_LAT, NALCHIK_LON, lat, lon)})
            except: continue
        out.sort(key=lambda x: x['dist'])
        return out
    except: return []


def fetch_on_this_day():
    today = datetime.date.today()
    r = get(f'https://api.wikimedia.org/feed/v1/wikipedia/ru/onthisday/selected/{today.month:02d}/{today.day:02d}', json_=True, timeout=10)
    if not r: return []
    try:
        return [{'year': e.get('year', ''), 'text': e.get('text', ''),
                 'link': (e.get('pages') or [{}])[0].get('content_urls', {}).get('desktop', {}).get('page', '')}
                for e in r.get('selected', [])[:5]]
    except: return []


def fetch_article_of_day():
    try:
        r = get(f'https://ru.wikipedia.org/api/rest_v1/page/random/summary', json_=True, timeout=10)
        if not r: return None
        return {'title': r.get('title', ''),
                'extract': (r.get('extract', '') or '')[:400] + '...',
                'url': (r.get('content_urls', {}).get('desktop', {}) or {}).get('page', ''),
                'thumb': (r.get('thumbnail', {}) or {}).get('source', '')}
    except: return None


def moon_phase():
    today = datetime.date.today()
    days = (today - datetime.date(2000, 1, 6)).days
    phase = (days % 29.530588853) / 29.530588853
    if phase < 0.03 or phase > 0.97: return '🌑', 'Новолуние'
    if phase < 0.22: return '🌒', 'Молодая луна'
    if phase < 0.28: return '🌓', 'Первая четверть'
    if phase < 0.47: return '🌔', 'Растущая луна'
    if phase < 0.53: return '🌕', 'Полнолуние'
    if phase < 0.72: return '🌖', 'Убывающая луна'
    if phase < 0.78: return '🌗', 'Последняя четверть'
    return '🌘', 'Старая луна'


def quote_of_day():
    today = datetime.date.today()
    return QUOTES[(today.year * 366 + today.timetuple().tm_yday) % len(QUOTES)]


def days_to_new_year():
    today = datetime.date.today()
    return (datetime.date(today.year + 1, 1, 1) - today).days


def calendar_html(today):
    y, m = today.year, today.month
    first = datetime.date(y, m, 1); start = first.weekday()
    nm = datetime.date(y + 1, 1, 1) if m == 12 else datetime.date(y, m + 1, 1)
    days_in = (nm - first).days
    cells = ['<div class="cal-cell cal-empty"></div>'] * start
    for d in range(1, days_in + 1):
        date = datetime.date(y, m, d); cls = 'cal-cell'
        if d == today.day: cls += ' cal-today'
        elif date.weekday() >= 5: cls += ' cal-weekend'
        hol = HOLIDAYS.get((m, d)); title = f' title="{hol}"' if hol else ''
        dot = '<span class="cal-hol">•</span>' if hol else ''
        cells.append(f'<div class="{cls}"{title}>{d}{dot}</div>')
    heads = ''.join(f'<div class="cal-head">{w}</div>' for w in WEEKDAYS_SHORT)
    return f'<div class="cal-month">{MONTHS_NOM[m-1]} {y}</div><div class="cal-grid">{heads}{"".join(cells)}</div>'


def generate_svg_art(kind='cloud'):
    random.seed(datetime.datetime.now().strftime('%Y%m%d%H') + kind)
    hour = datetime.datetime.now().hour
    if 6 <= hour < 10: palettes = [('#f6d365', '#fda085', '#fbc2eb'), ('#ffecd2', '#fcb69f', '#ff8177')]
    elif 10 <= hour < 17: palettes = [('#4facfe', '#00f2fe', '#43e97b'), ('#43e97b', '#38f9d7', '#4facfe')]
    elif 17 <= hour < 21: palettes = [('#fa709a', '#fee140', '#fda085'), ('#ff6b6b', '#fecfef', '#f6d365')]
    else: palettes = [('#30cfd0', '#330867', '#a8edea'), ('#5ee7df', '#b490ca', '#7b68ee')]
    c1, c2, c3 = random.choice(palettes)
    blobs = ''.join(f'<circle cx="{random.randint(0,400)}" cy="{random.randint(0,240)}" r="{random.randint(60,160)}" fill="{random.choice([c1,c2,c3])}" opacity="{random.uniform(0.3,0.7):.2f}"/>' for _ in range(7))
    lines = ''.join(f'<line x1="{random.randint(0,400)}" y1="{random.randint(0,240)}" x2="{random.randint(0,400)}" y2="{random.randint(0,240)}" stroke="white" stroke-width="{random.uniform(0.3,1):.1f}" opacity="{random.uniform(0.1,0.3):.2f}"/>' for _ in range(10))
    parts = ''.join(f'<circle cx="{random.randint(0,400)}" cy="{random.randint(0,240)}" r="{random.uniform(0.5,2):.1f}" fill="white" opacity="{random.uniform(0.2,0.7):.2f}"/>' for _ in range(50))
    seed = random.randint(0, 999999)
    return f'<svg viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><filter id="b{seed}"><feGaussianBlur stdDeviation="26"/></filter><radialGradient id="v{seed}" cx="50%" cy="50%" r="70%"><stop offset="60%" stop-color="rgba(0,0,0,0)"/><stop offset="100%" stop-color="rgba(0,0,0,0.55)"/></radialGradient></defs><rect width="400" height="240" fill="#0a0e1a"/><g filter="url(#b{seed})">{blobs}</g>{lines}{parts}<rect width="400" height="240" fill="url(#v{seed})"/></svg>'


def track_of_day(kind):
    today = datetime.date.today()
    tracks = MOOD_TRACKS.get(kind, MOOD_TRACKS['cloud'])
    idx = today.timetuple().tm_yday % len(tracks)
    name, artist = tracks[idx]
    return {'name': name, 'artist': artist, 'url': f'https://www.youtube.com/results?search_query={artist.replace(" ", "+")}+{name.replace(" ", "+")}'}


def solar_image_url():
    return {'visible': 'https://sdo.gsfc.nasa.gov/assets/img/latest/latest_256_HMIIF.jpg',
            'corona':  'https://sdo.gsfc.nasa.gov/assets/img/latest/latest_256_0171.jpg',
            'atmo':    'https://sdo.gsfc.nasa.gov/assets/img/latest/latest_256_0304.jpg'}


def fetch_apod():
    r = get('https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY', json_=True, timeout=15)
    if not r: return None
    try:
        return {'url': r.get('hdurl') or r.get('url'), 'thumb': r.get('url'),
                'title': r.get('title', ''), 'explanation': (r.get('explanation', '') or '')[:250] + '...',
                'media_type': r.get('media_type', 'image'), 'date': r.get('date', '')}
    except: return None


def fetch_asteroids():
    today = datetime.date.today(); end = today + datetime.timedelta(days=7)
    r = get(f'https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={end}&api_key=DEMO_KEY', json_=True, timeout=15)
    if not r: return []
    try:
        items = []
        for date, list_ in r.get('near_earth_objects', {}).items():
            for ast in list_:
                d = ast.get('estimated_diameter', {}).get('meters', {})
                size = round((d.get('estimated_diameter_min', 0) + d.get('estimated_diameter_max', 0)) / 2)
                approach = ast.get('close_approach_data', [{}])[0]
                items.append({'name': ast.get('name', '').replace('(', '').replace(')', ''),
                              'size': size, 'hazardous': ast.get('is_potentially_hazardous_asteroid', False),
                              'date': approach.get('close_approach_date', ''),
                              'velocity': round(float(approach.get('relative_velocity', {}).get('kilometers_per_hour', 0))),
                              'distance': round(float(approach.get('miss_distance', {}).get('kilometers', 0)))})
        items.sort(key=lambda x: x['date'])
        return items[:5]
    except: return []


def fetch_rocket_launch():
    r = get('https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=1&mode=list', json_=True, timeout=15)
    if not r: return None
    try:
        results = r.get('results', [])
        if not results: return None
        item = results[0]
        def safe_dict(x): return x if isinstance(x, dict) else {}
        pad = safe_dict(item.get('pad')); loc = safe_dict(pad.get('location')); provider = safe_dict(item.get('launch_service_provider'))
        net = item.get('net', '')
        try:
            dt = datetime.datetime.fromisoformat(net.replace('Z', '+00:00'))
            dt_naive = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        except: dt_naive = None
        return {'name': item.get('name') or '?', 'provider': provider.get('name') or '?',
                'location': loc.get('name') or pad.get('name') or '?', 'net_str': net, 'dt': dt_naive}
    except Exception as e:
        log(f"Launch: {e}"); return None


def fetch_art_of_day():
    today = datetime.date.today(); idx = today.timetuple().tm_yday
    for offset in range(20):
        oid = 436535 + ((idx * 97 + offset * 13) % 40000)
        r = get(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}', json_=True, timeout=8)
        if not r: continue
        if r.get('primaryImageSmall') and r.get('isPublicDomain'):
            return {'url': r['primaryImageSmall'], 'title': r.get('title', '') or 'Без названия',
                    'artist': r.get('artistDisplayName', '') or 'Неизвестный',
                    'year': r.get('objectDate', ''), 'link': r.get('objectURL', '')}
    return None


def fetch_cat():
    r = get('https://api.thecatapi.com/v1/images/search?size=med', json_=True, timeout=10)
    if not r or not isinstance(r, list) or not r: return None
    try: return {'url': r[0]['url']}
    except: return None


def fact_of_day():
    today = datetime.date.today()
    return FACTS[(today.year * 366 + today.timetuple().tm_yday) % len(FACTS)]


def time_ago(dt):
    if dt == datetime.datetime.min: return ''
    try:
        s = int((datetime.datetime.now() - dt).total_seconds())
        if s < 60: return 'только что'
        if s < 3600: return f'{s // 60} мин'
        if s < 86400: return f'{s // 3600} ч'
        return f'{s // 86400} дн'
    except: return ''


def render_news():
    items = fetch_news()
    if not items: return '<div class="empty">Новости недоступны</div>'
    cards = []
    for n in items:
        ago = time_ago(n.get('dt', datetime.datetime.min))
        ago_html = f'<span class="news-ago">{ago}</span>' if ago else ''
        desc = f'<div class="news-desc">{html.escape(n["desc"])}</div>' if n['desc'] else ''
        cards.append(f'<a class="news-card" href="{html.escape(n["link"])}" target="_blank" rel="noopener"><div class="news-head"><span class="news-source">{html.escape(n["source"])}</span>{ago_html}</div><div class="news-title">{html.escape(n["title"])}</div>{desc}</a>')
    return ''.join(cards)


def render_weather(w):
    if not w: return '<div class="empty">Погода недоступна</div>'
    fc = ''.join(f'<div class="fc-day"><div class="fc-date">{d["date"][5:].replace("-", ".")}</div><div class="fc-icon">{weather_icon(d["code"])}</div><div class="fc-temps"><span class="fc-max">↑{d["max"]}°</span><span class="fc-min">↓{d["min"]}°</span></div></div>' for d in w['forecast'])
    return f'<div class="wx-hero"><div class="wx-icon">{weather_icon(w["code"])}</div><div><div class="wx-temp">{w["temp"]}°</div><div class="wx-feels">ощущается {w["feels"]}°</div></div></div><div class="wx-meta"><div class="wx-item"><span>💧</span><b>{w["humidity"]}%</b></div><div class="wx-item"><span>💨</span><b>{w["wind"]}</b><small>км/ч</small></div><div class="wx-item"><span>🔽</span><b>{w["pressure"]}</b><small>мм</small></div></div><div class="wx-sun"><div><span>🌅</span> {w["sunrise"]}</div><div><span>🌇</span> {w["sunset"]}</div></div><div class="wx-forecast">{fc}</div>'


def render_currency(c):
    if not c: return '<div class="empty">—</div>'
    return f'<div class="cur-row"><span class="cur-flag">🇺🇸</span><span class="cur-code">USD</span><span class="cur-val">{c["usd"]} ₽</span></div><div class="cur-row"><span class="cur-flag">🇪🇺</span><span class="cur-code">EUR</span><span class="cur-val">{c["eur"]} ₽</span></div><div class="cur-row"><span class="cur-flag">🇨🇳</span><span class="cur-code">CNY</span><span class="cur-val">{c["cny"]} ₽</span></div>'


def render_crypto(c):
    if not c: return '<div class="empty">—</div>'
    rows = []
    for key, icon, label in [('btc', '₿', 'BTC'), ('eth', 'Ξ', 'ETH'), ('ton', '💎', 'TON')]:
        if key not in c: continue
        d = c[key]; chg = d['chg']
        color = 'var(--good)' if chg >= 0 else 'var(--bad)'
        arrow = '▲' if chg >= 0 else '▼'
        rows.append(f'<div class="cur-row"><span class="cur-flag">{icon}</span><span class="cur-code">{label}</span><span class="cur-val">${d["usd"]:,}</span><span class="cur-chg" style="color:{color}">{arrow} {abs(chg):.1f}%</span></div>')
    return ''.join(rows) or '<div class="empty">—</div>'


def render_iss(iss):
    if not iss: return '<div class="empty">—</div>'
    return f'<div class="iss-hero"><div class="iss-icon">🛰</div><div><div class="iss-dist">{iss["dist"]} <span class="iss-dist-unit">км от тебя</span></div><div class="iss-sub">высота {iss["alt"]} км · {iss["velocity"]} км/ч</div></div></div><div class="iss-meta"><span>📍 {iss["lat"]}°, {iss["lon"]}°</span><span>👁 {iss["visibility"]}</span></div>'


def render_kp(kp):
    if not kp: return '<div class="empty">—</div>'
    name, color = kp['level']
    bars = ''.join(f'<div class="kp-bar" style="height:{min(100, int((v / 9) * 100))}%" title="Kp={v}"></div>' for v in kp['forecast'][-6:])
    return f'<div class="kp-hero"><div class="kp-value" style="color:{color}">{kp["kp"]:.1f}</div><div class="kp-label">Kp-индекс</div></div><div class="kp-level" style="color:{color}">{name}</div><div class="kp-bars">{bars}</div><div class="kp-axis"><span>6ч назад</span><span>сейчас</span></div>'


def render_air(aq):
    if not aq: return '<div class="empty">—</div>'
    name, color = aq['level']
    pm25 = f'{aq["pm25"]:.1f}' if aq.get('pm25') is not None else '—'
    pm10 = f'{aq["pm10"]:.1f}' if aq.get('pm10') is not None else '—'
    return f'<div class="aq-hero"><div class="aq-value" style="color:{color}">{aq["aqi"] if aq["aqi"] is not None else "—"}</div><div class="aq-label">AQI</div></div><div class="aq-level" style="color:{color}">{name}</div><div class="aq-meta"><div><b>PM2.5</b> {pm25}</div><div><b>PM10</b> {pm10}</div></div>'


def render_uv(uv):
    if not uv: return '<div class="empty">—</div>'
    name, color = uv['level']
    v = uv['uv']; v_max = uv.get('uv_max')
    return f'<div class="aq-hero"><div class="aq-value" style="color:{color}">{f"{v:.1f}" if v is not None else "—"}</div><div class="aq-label">УФ</div></div><div class="aq-level" style="color:{color}">{name}</div><div class="aq-meta"><div><b>Макс.</b> {f"{v_max:.0f}" if v_max is not None else "—"}</div></div>'


def render_earthquakes(eqs):
    if not eqs: return '<div class="empty">За 30 дней рядом нет землетрясений M≥3.5 ✅</div>'
    rows = []
    for e in eqs[:3]:
        mag = e.get('mag', '—')
        color = '#facc15' if mag < 4.5 else ('#fb923c' if mag < 5.5 else '#f87171')
        place = e.get('place', '?')
        if place and len(place) > 40: place = place[:37] + '...'
        ago = time_ago_from_ts(e.get('time'))
        dist = f'{e["dist"]} км' if e.get('dist') else '—'
        rows.append(f'<div class="eq-row"><span class="eq-mag" style="color:{color}">M{mag}</span><span class="eq-place">{html.escape(place)}</span><span class="eq-meta">{dist} · {ago}</span></div>')
    return ''.join(rows)


def render_planes(planes):
    if not planes: return '<div class="empty">Сейчас в небе над тобой никого ✈️</div>'
    rows = []
    for p in planes[:6]:
        rows.append(f'<div class="plane-row"><span class="plane-icon">✈️</span><div class="plane-info"><div class="plane-name">{html.escape(p["callsign"])}</div><div class="plane-meta">{p["alt"]} м · {p["speed"]} км/ч · {p["dist"]} км</div></div><span class="plane-country">{html.escape(p["country"])}</span></div>')
    return ''.join(rows)


def render_history(events):
    if not events: return '<div class="empty">—</div>'
    rows = []
    for e in events[:5]:
        text = e.get('text', '')
        if len(text) > 110: text = text[:107] + '...'
        link = e.get('link', '')
        if link:
            rows.append(f'<a class="hist-row" href="{html.escape(link)}" target="_blank" rel="noopener"><span class="hist-year">{e.get("year", "")}</span><span class="hist-text">{html.escape(text)}</span></a>')
        else:
            rows.append(f'<div class="hist-row"><span class="hist-year">{e.get("year", "")}</span><span class="hist-text">{html.escape(text)}</span></div>')
    return ''.join(rows)


def render_golden_hour(gh):
    if not gh: return ''
    return f'<div class="gh-block"><div class="gh-title">📸 Золотой час</div><div class="gh-row"><span>Утро:</span> <b>{gh["morning_start"]}–{gh["morning_end"]}</b></div><div class="gh-row"><span>Вечер:</span> <b>{gh["evening_start"]}–{gh["evening_end"]}</b></div></div>'


def render_track(track):
    if not track: return ''
    return f'<a class="track-card" href="{track["url"]}" target="_blank" rel="noopener"><div class="track-icon">🎵</div><div class="track-info"><div class="track-name">{html.escape(track["name"])}</div><div class="track-artist">{html.escape(track["artist"])}</div></div></a>'


def render_solar():
    urls = solar_image_url()
    return f'<div class="space-grid"><a class="space-img" href="https://sdo.gsfc.nasa.gov/data/" target="_blank"><img src="{urls["visible"]}" loading="lazy"><span class="space-label">Видимое</span></a><a class="space-img" href="https://sdo.gsfc.nasa.gov/data/" target="_blank"><img src="{urls["corona"]}" loading="lazy"><span class="space-label">Корона</span></a><a class="space-img" href="https://sdo.gsfc.nasa.gov/data/" target="_blank"><img src="{urls["atmo"]}" loading="lazy"><span class="space-label">Атмосфера</span></a></div><div class="space-note">📸 NASA SDO · каждые 15 мин</div>'


def render_apod(apod):
    if not apod: return '<div class="empty">—</div>'
    img = ''
    if apod['media_type'] == 'image':
        img = f'<img class="apod-img" src="{apod.get("thumb") or apod["url"]}" loading="lazy" onerror="this.style.display=\'none\'">'
    return f'<a class="apod-card" href="{apod["url"]}" target="_blank"><div>{img}</div><div class="apod-title">{html.escape(apod["title"])}</div><div class="apod-date">{apod["date"]}</div><div class="apod-desc">{html.escape(apod["explanation"])}</div></a>'


def render_asteroids(items):
    if not items: return '<div class="empty">—</div>'
    rows = []
    for a in items[:4]:
        icon = '⚠️' if a['hazardous'] else '☄️'
        color = 'var(--bad)' if a['hazardous'] else 'var(--accent2)'
        rows.append(f'<div class="ast-row"><span class="ast-icon" style="color:{color}">{icon}</span><div class="ast-info"><div class="ast-name">{html.escape(a["name"])}</div><div class="ast-meta">{a["date"][5:]} · {a["size"]} м · {a["velocity"]:,} км/ч</div></div></div>')
    return ''.join(rows)


def render_launch(launch):
    if not launch: return '<div class="empty">—</div>'
    if launch.get('dt'):
        s = int((launch['dt'] - datetime.datetime.utcnow()).total_seconds())
        if s > 0:
            days = s // 86400; hours = (s % 86400) // 3600; mins = (s % 3600) // 60
            countdown = f'{days}д {hours}ч {mins}м' if days > 0 else (f'{hours}ч {mins}м' if hours > 0 else f'{mins}м')
        else: countdown = 'уже летит 🚀'
    else: countdown = '—'
    return f'<div class="launch-card"><div class="launch-icon">🚀</div><div class="launch-info"><div class="launch-name">{html.escape(launch["name"])}</div><div class="launch-provider">{html.escape(launch["provider"])}</div><div class="launch-loc">{html.escape(launch["location"])}</div><div class="launch-countdown">⏱ {countdown}</div></div></div>'


def render_art(art):
    if not art: return '<div class="empty">—</div>'
    return f'<a class="art-card-museum" href="{art["link"]}" target="_blank"><img class="museum-img" src="{art["url"]}" loading="lazy" onerror="this.style.display=\'none\'"><div class="museum-title">{html.escape(art["title"])}</div><div class="museum-artist">{html.escape(art["artist"])}, {art["year"]}</div><div class="museum-museum">🏛 The Met</div></a>'


def render_cat(cat):
    if not cat: return '<div class="empty">—</div>'
    return f'<a class="cat-card" href="{cat["url"]}" target="_blank"><img src="{cat["url"]}" loading="lazy"></a>'


def render_fact():
    return f'<div class="fact-text">{html.escape(fact_of_day())}</div>'


def render_article(article):
    if not article: return '<div class="empty">—</div>'
    thumb = f'<img class="article-thumb" src="{article["thumb"]}" loading="lazy" onerror="this.style.display=\'none\'">' if article.get('thumb') else ''
    return f'<a class="article-card" href="{article["url"]}" target="_blank">{thumb}<div class="article-title">{html.escape(article["title"])}</div><div class="article-desc">{html.escape(article["extract"])}</div><div class="article-source">📖 Wikipedia RU</div></a>'


def generate():
    log("📄 Генерирую dashboard v3...")
    DOCS.mkdir(exist_ok=True)

    now = datetime.datetime.now(); today = now.date()
    weekday = WEEKDAYS_FULL[now.weekday()]
    month_name = MONTHS_NOM[now.month - 1]; year = now.year
    date_str = f"{now.day} {MONTHS_GEN[now.month - 1]}"
    holiday = HOLIDAYS.get((today.month, today.day))
    holiday_html = f'<div class="holiday">{holiday}</div>' if holiday else ''

    weather = fetch_weather()
    kind = weather['kind'] if weather else 'cloud'
    gh = golden_hour(weather)
    cur = fetch_currency()
    crypto = fetch_crypto()
    iss = fetch_iss()
    kp = fetch_kp_index()
    aq = fetch_air_quality()
    uv = fetch_uv_index()
    eqs = fetch_earthquakes()
    history = fetch_on_this_day()
    moon_icon, moon_name = moon_phase()
    quote, author = quote_of_day()
    days_ny = days_to_new_year()
    track = track_of_day(kind)
    apod = fetch_apod()
    asteroids = fetch_asteroids()
    launch = fetch_rocket_launch()
    art = fetch_art_of_day()
    cat = fetch_cat()
    planes = fetch_planes()
    article = fetch_article_of_day()

    aurora_class = ' aurora' if kp and kp['aurora_possible'] else ''

    news_block = render_news()
    calendar_block = calendar_html(today)
    svg_art = generate_svg_art(kind)

    html_out = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✨</text></svg>">
<meta name="theme-color" content="#0a0e1a">
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>window.QRCode||document.write('<script src="https://unpkg.com/qrcodejs@1.0.0/qrcode.min.js"><\\/script>')</script>
<style>
{get_css()}
</style>
</head>
<body class="kind-{kind}{aurora_class}">

<div class="splash">✨</div>
<canvas id="bgCanvas"></canvas>

<div class="wrap">

<div class="header">
  <div class="header-left">
    <h1>Dashboard</h1>
    <div class="date-line"><span class="wd">{weekday}</span>, {date_str} · {year}</div>
  </div>
  <div class="header-right">
    <button class="icon-btn" id="soundBtn" title="Звук часов">🔇</button>
    <button class="icon-btn" id="themeBtn" title="Тема">☀</button>
  </div>
</div>

<div class="bento">

{holiday_html}

  <div class="card card-clock">
    <div class="clock"><span id="h1">-</span><span id="h2">-</span><span class="colon">:</span><span id="m1">-</span><span id="m2">-</span><span class="sec" id="ss">--</span></div>
    <div class="tz">Московское время · UTC+3</div>
    <div class="counters">
      <div class="cnt"><span id="cnt-day">0</span><small>секунд с начала дня</small></div>
      <div class="cnt"><span id="cnt-year">0</span><small>дней с начала года</small></div>
      <div class="cnt"><span id="cnt-left">0</span><small>дней до конца года</small></div>
    </div>
  </div>

  <div class="card card-weather"><h3>🌤 Погода · {NALCHIK_NAME}</h3>{render_weather(weather)}</div>
  <div class="card card-iss"><h3>🛰 МКС</h3>{render_iss(iss)}</div>
  <div class="card card-kp"><h3>🌌 Магнитное поле</h3>{render_kp(kp)}</div>
  <div class="card card-aq"><h3>🌬 Воздух</h3>{render_air(aq)}</div>
  <div class="card card-uv"><h3>🌡 УФ</h3>{render_uv(uv)}</div>
  <div class="card card-currency"><h3>💱 Курсы ЦБ</h3>{render_currency(cur)}</div>
  <div class="card card-crypto"><h3>💰 Крипта</h3>{render_crypto(crypto)}</div>
  <div class="card card-news"><h3>📰 Новости · 5 источников</h3><div class="news-grid">{news_block}</div></div>
  <div class="card card-calendar"><h3>📅 {month_name} {year}</h3>{calendar_block}</div>
  <div class="card card-art">{svg_art}<div class="art-label">🎨 по погоде</div></div>
  <div class="card card-gh">{render_golden_hour(gh)}</div>
  <div class="card card-moon"><h3>🌕 Луна</h3><span class="moon-icon">{moon_icon}</span><div class="moon-name">{moon_name}</div></div>
  <div class="card card-ny"><h3>🎄 До НГ</h3><div class="ny-num">{days_ny}</div><div class="ny-label">дней</div></div>
  <div class="card card-track"><h3>🎵 Атмосфера дня</h3>{render_track(track)}</div>
  <div class="card card-eq"><h3>🌍 Землетрясения</h3>{render_earthquakes(eqs)}</div>
  <div class="card card-history"><h3>📖 В истории</h3>{render_history(history)}</div>
  <div class="card card-quote"><h3>💭 Цитата дня</h3><div class="quote-text">«{quote}»</div><div class="quote-author">{author}</div></div>

  <div class="card card-solar"><h3>🌞 Солнце прямо сейчас</h3>{render_solar()}</div>
  <div class="card card-apod"><h3>🌌 Фото дня · NASA</h3>{render_apod(apod)}</div>
  <div class="card card-asteroids"><h3>☄️ Астероиды недели</h3>{render_asteroids(asteroids)}</div>
  <div class="card card-launch"><h3>🚀 Запуск ракеты</h3>{render_launch(launch)}</div>
  <div class="card card-museum"><h3>🎨 Картина дня</h3>{render_art(art)}</div>
  <div class="card card-cat"><h3>🐱 Кот дня</h3>{render_cat(cat)}</div>

  <div class="card card-planes"><h3>✈️ Самолёты над Нальчиком</h3>{render_planes(planes)}</div>
  <div class="card card-article"><h3>📖 Статья дня</h3>{render_article(article)}</div>

  <div class="card card-habits">
    <h3>🎯 Мои привычки</h3>
    <div id="habits"></div>
    <div class="tool-input-row">
      <input type="text" id="habitInput" placeholder="Новая привычка..." maxlength="30">
      <button class="tool-btn" onclick="addHabit()">+</button>
    </div>
  </div>

  <div class="card card-todo">
    <h3>✅ Задачи</h3>
    <div id="todoList"></div>
    <div class="tool-input-row">
      <input type="text" id="todoInput" placeholder="Что сделать?" maxlength="100">
      <button class="tool-btn" onclick="addTodo()">+</button>
    </div>
  </div>

  <div class="card card-notes">
    <h3>📝 Заметки</h3>
    <textarea id="notesArea" placeholder="Пиши сюда — сохранится автоматически..."></textarea>
    <div class="notes-status" id="notesStatus">сохранено</div>
  </div>

  <div class="card card-pomo">
    <h3>🍅 Помодоро</h3>
    <div class="pomo-timer" id="pomoTime">25:00</div>
    <div class="pomo-buttons">
      <button class="dice-btn" id="pomoStart" onclick="pomoToggle()">▶ Старт</button>
      <button class="dice-btn" onclick="pomoReset()">⟲ Сброс</button>
    </div>
    <div class="pomo-count" id="pomoCount">🍅 сегодня: 0</div>
  </div>

  <div class="card card-mood">
    <h3>😊 Настроение</h3>
    <div class="mood-buttons">
      <button class="mood-btn" onclick="setMood('good')" title="Отлично">😄</button>
      <button class="mood-btn" onclick="setMood('ok')" title="Норм">😐</button>
      <button class="mood-btn" onclick="setMood('bad')" title="Плохо">😞</button>
    </div>
    <div class="mood-status" id="moodStatus">Сегодня: —</div>
  </div>

  <div class="card card-water">
    <h3>💧 Вода</h3>
    <div class="water-glass" id="waterGlass">0 / 8</div>
    <div class="mood-buttons">
      <button class="dice-btn" onclick="addWater()">+ стакан</button>
      <button class="dice-btn" onclick="resetWater()">⟲</button>
    </div>
  </div>

  <div class="card card-conv">
    <h3>🧮 Конвертеры</h3>
    <div class="conv-row"><input type="number" id="convC" placeholder="°C" oninput="convTemp()"> <span>→</span> <span id="convF">°F</span></div>
    <div class="conv-row"><input type="number" id="convKm" placeholder="км" oninput="convDist()"> <span>→</span> <span id="convMi">миль</span></div>
    <div class="conv-row"><input type="number" id="convKg" placeholder="кг" oninput="convWeight()"> <span>→</span> <span id="convLb">фунт</span></div>
    <div class="conv-row"><input type="number" id="convRub" placeholder="₽" oninput="convMoney()"> <span>→</span> <span id="convUsd">$</span></div>
  </div>

  <div class="card card-tools">
    <h3>🔐 Пароль / QR</h3>
    <div class="pwd-out" id="pwdOut">———</div>
    <button class="dice-btn" style="width:100%;margin-top:8px" onclick="genPwd()">🎲 Новый пароль (20)</button>
    <button class="dice-btn" style="width:100%;margin-top:6px" onclick="genQR()">📱 QR для этой страницы</button>
    <div id="qrBox" style="margin-top:10px;text-align:center"></div>
  </div>

  <div class="card card-dates">
    <h3>⏳ Счётчики дат</h3>
    <div id="dateCounters"></div>
    <div class="tool-input-row">
      <input type="date" id="dateInput">
      <input type="text" id="dateLabel" placeholder="Название" maxlength="20" style="max-width:100px">
      <button class="tool-btn" onclick="addDateCounter()">+</button>
    </div>
  </div>

  <div class="card card-issmap">
    <h3>🗺 МКС на карте мира</h3>
    <div class="issmap-wrap">
      <svg class="issmap" viewBox="0 0 360 180" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <rect width="360" height="180" fill="#0a1628"/>
        <line x1="0" y1="45" x2="360" y2="45" stroke="#1e3a5f" stroke-width="0.5"/>
        <line x1="0" y1="90" x2="360" y2="90" stroke="#1e3a5f" stroke-width="0.5"/>
        <line x1="0" y1="135" x2="360" y2="135" stroke="#1e3a5f" stroke-width="0.5"/>
        <line x1="90" y1="0" x2="90" y2="180" stroke="#1e3a5f" stroke-width="0.5"/>
        <line x1="180" y1="0" x2="180" y2="180" stroke="#1e3a5f" stroke-width="0.5"/>
        <line x1="270" y1="0" x2="270" y2="180" stroke="#1e3a5f" stroke-width="0.5"/>
        <line x1="0" y1="90" x2="360" y2="90" stroke="#60a5fa" stroke-width="0.8" stroke-dasharray="3,3"/>
        <circle id="issDot2" cx="180" cy="90" r="12" fill="none" stroke="#facc15" stroke-width="1" opacity="0.5">
          <animate attributeName="r" values="5;15;5" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle id="issDot" cx="180" cy="90" r="5" fill="#facc15" stroke="#fff" stroke-width="1"/>
        <circle cx="{round((NALCHIK_LON + 180))}" cy="{round(90 - NALCHIK_LAT)}" r="3" fill="#f87171"/>
      </svg>
    </div>
    <div class="issmap-info">
      <span id="issMapCoords">—</span>
      <span id="issMapDist">—</span>
    </div>
  </div>

  <div class="card card-sleep">
    <h3>💤 Фаза сна</h3>
    <div class="sleep-block">
      <div class="sleep-row"><span>Встать в</span> <b>06:00</b> → лечь в <b id="sleep-6">--:--</b></div>
      <div class="sleep-row"><span>Встать в</span> <b>07:00</b> → лечь в <b id="sleep-7">--:--</b></div>
      <div class="sleep-row"><span>Встать в</span> <b>08:00</b> → лечь в <b id="sleep-8">--:--</b></div>
      <div class="sleep-note">💡 90-минутные циклы сна</div>
    </div>
  </div>

  <div class="card card-dice">
    <h3>🎲 Кубик / Монетка</h3>
    <div class="dice-wrap">
      <div class="dice-result" id="diceResult">🎲</div>
      <div class="dice-buttons">
        <button class="dice-btn" onclick="rollDice()">Кубик</button>
        <button class="dice-btn" onclick="flipCoin()">Монетка</button>
      </div>
    </div>
  </div>

  <div class="card card-fact">
    <h3>🧠 Факт дня</h3>
    {render_fact()}
  </div>

</div>

<div class="footer">
  Обновлено {now.strftime('%H:%M')} МСК · обновляется каждый час
</div>

</div>

<script>
const EXCH = {{usd: {cur["usd"] if cur else 100}, eur: {cur["eur"] if cur else 110}, cny: {cur["cny"] if cur else 14}}};
{get_js(kind)}
</script>

</body>
</html>'''

    (DOCS / 'index.html').write_text(html_out, encoding='utf-8')
    log(f"✅ {DOCS / 'index.html'} ({len(html_out)} байт)")


def get_css():
    return '''
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0e1a;--panel:rgba(22,27,42,0.72);--panel2:rgba(30,36,55,0.55);--border:rgba(148,163,184,0.12);--text:#e8eaf0;--muted:#8892a6;--accent:#60a5fa;--accent2:#a78bfa;--good:#4ade80;--bad:#f87171;--warn:#facc15}
[data-theme="light"]{--bg:#f4f6fa;--panel:rgba(255,255,255,0.75);--panel2:rgba(255,255,255,0.6);--border:rgba(15,23,42,0.08);--text:#0f172a;--muted:#64748b;--accent:#2563eb;--accent2:#7c3aed}
html,body{overflow-x:hidden}
body{font-family:-apple-system,'Inter','Segoe UI',Roboto,sans-serif;color:var(--text);background:var(--bg);min-height:100vh;padding:20px;transition:background-color .5s,color .5s;position:relative;line-height:1.4}
body::before{content:'';position:fixed;inset:0;z-index:-1;background:radial-gradient(circle at 15% -5%, rgba(96,165,250,0.14), transparent 45%),radial-gradient(circle at 85% 100%, rgba(167,139,250,0.10), transparent 45%);background-attachment:fixed;transition:background 1.5s}
body.kind-sun::before{background:radial-gradient(circle at 20% -5%, rgba(251,191,36,0.18), transparent 45%),radial-gradient(circle at 80% 100%, rgba(96,165,250,0.08), transparent 45%);background-attachment:fixed}
body.kind-rain::before{background:radial-gradient(circle at 20% -5%, rgba(96,165,250,0.18), transparent 45%),radial-gradient(circle at 80% 100%, rgba(51,65,85,0.2), transparent 45%);background-attachment:fixed}
body.kind-snow::before{background:radial-gradient(circle at 20% -5%, rgba(200,220,255,0.2), transparent 45%),radial-gradient(circle at 80% 100%, rgba(167,139,250,0.1), transparent 45%);background-attachment:fixed}
body.kind-storm::before{background:radial-gradient(circle at 20% -5%, rgba(120,53,15,0.25), transparent 45%),radial-gradient(circle at 80% 100%, rgba(96,165,250,0.15), transparent 45%);background-attachment:fixed}
body.aurora::after{content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;background:linear-gradient(180deg, rgba(74,222,128,0.08) 0%, transparent 40%);animation:auroraShift 8s ease-in-out infinite}
@keyframes auroraShift{0%,100%{opacity:0.4}50%{opacity:0.9}}
[data-theme="light"] body::before{background:radial-gradient(circle at 15% -5%, rgba(37,99,235,0.10), transparent 45%),radial-gradient(circle at 85% 100%, rgba(124,58,237,0.07), transparent 45%);background-attachment:fixed}
#bgCanvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;pointer-events:none;opacity:0.55}
.wrap{max-width:1400px;margin:0 auto;position:relative;z-index:1}
.header{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:20px;flex-wrap:wrap}
.header-left h1{font-size:28px;font-weight:600;letter-spacing:-0.02em;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.header-left .date-line{color:var(--muted);font-size:14px;margin-top:4px}
.header-left .date-line .wd{color:var(--accent);font-weight:500}
.header-right{display:flex;gap:8px}
.icon-btn{background:var(--panel);border:1px solid var(--border);color:var(--text);width:44px;height:44px;border-radius:12px;cursor:pointer;font-size:17px;backdrop-filter:blur(20px);transition:transform .2s}
.icon-btn:hover{transform:scale(1.08) rotate(8deg)}
.bento{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-bottom:20px}
@media(max-width:1000px){.bento{grid-template-columns:repeat(6,1fr)}}
@media(max-width:640px){.bento{grid-template-columns:1fr}.bento>*{grid-column:1!important}}
.card{background:var(--panel);border:1px solid var(--border);border-radius:20px;padding:20px;backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);position:relative;overflow:hidden;transition:border-color .2s,transform .2s;animation:fadeInUp .5s ease-out both}
.card:hover{border-color:rgba(96,165,250,0.3);transform:translateY(-2px)}
.card h3{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;font-weight:600;display:flex;align-items:center;gap:6px}
@keyframes fadeInUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.empty{color:var(--muted);font-size:13px;text-align:center;padding:12px}
.card-clock{grid-column:span 4;min-height:220px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:30px 24px}
.card-weather{grid-column:span 4}.card-iss{grid-column:span 4}.card-kp{grid-column:span 4}.card-aq{grid-column:span 4}.card-uv{grid-column:span 4}
.card-currency{grid-column:span 3}.card-crypto{grid-column:span 3}
.card-news{grid-column:span 6;grid-row:span 2}
.card-calendar{grid-column:span 3}.card-art{grid-column:span 3;padding:0;min-height:220px}.card-gh{grid-column:span 3}
.card-moon{grid-column:span 3;text-align:center}.card-ny{grid-column:span 3;text-align:center}.card-track{grid-column:span 3}
.card-eq{grid-column:span 6}.card-history{grid-column:span 6}.card-quote{grid-column:span 12}
.card-solar{grid-column:span 6}.card-apod{grid-column:span 6}.card-asteroids{grid-column:span 4}.card-launch{grid-column:span 4}.card-museum{grid-column:span 4}
.card-cat{grid-column:span 3;padding:0;overflow:hidden}.card-sleep{grid-column:span 3}.card-dice{grid-column:span 3;text-align:center}.card-fact{grid-column:span 3}
.card-planes{grid-column:span 6}.card-article{grid-column:span 6}
.card-habits{grid-column:span 4}.card-todo{grid-column:span 4}.card-notes{grid-column:span 4}
.card-pomo{grid-column:span 3;text-align:center}.card-mood{grid-column:span 3;text-align:center}.card-water{grid-column:span 3;text-align:center}.card-conv{grid-column:span 3}
.card-tools{grid-column:span 4}.card-dates{grid-column:span 4}.card-issmap{grid-column:span 4}
@media(max-width:1000px){
  .card-clock,.card-weather,.card-iss,.card-kp,.card-aq,.card-uv{grid-column:span 6}
  .card-currency,.card-crypto,.card-calendar,.card-art,.card-gh,.card-moon,.card-ny,.card-track{grid-column:span 3}
  .card-news,.card-eq,.card-history,.card-quote{grid-column:span 6}
  .card-solar,.card-apod,.card-asteroids,.card-launch,.card-museum,.card-planes,.card-article{grid-column:span 6}
  .card-cat,.card-sleep,.card-dice,.card-fact{grid-column:span 3}
  .card-habits,.card-todo,.card-notes,.card-tools,.card-dates,.card-issmap{grid-column:span 6}
  .card-pomo,.card-mood,.card-water,.card-conv{grid-column:span 3}
}
.clock{font-size:clamp(56px,10vw,88px);font-weight:200;letter-spacing:-0.05em;line-height:0.95;font-variant-numeric:tabular-nums;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.clock .colon{animation:blink 1s steps(1) infinite;opacity:0.7}
@keyframes blink{50%{opacity:0.25}}
.clock .sec{font-size:0.42em;color:var(--accent);-webkit-text-fill-color:var(--accent);margin-left:8px;opacity:0.75;font-variant-numeric:tabular-nums}
.tz{font-size:12px;color:var(--muted);margin-top:6px;letter-spacing:0.4px}
.counters{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:16px;padding-top:14px;border-top:1px solid var(--border);width:100%}
.cnt{text-align:center;font-size:11px}
.cnt span{display:block;font-size:18px;font-weight:500;color:var(--accent);font-variant-numeric:tabular-nums;margin-bottom:2px}
.cnt small{color:var(--muted);font-size:9px}
.wx-hero{display:flex;align-items:center;gap:16px;margin-bottom:14px}
.wx-icon{font-size:52px;line-height:1;filter:drop-shadow(0 4px 16px rgba(96,165,250,0.25))}
.wx-temp{font-size:38px;font-weight:200;letter-spacing:-0.02em;line-height:1}
.wx-feels{font-size:12px;color:var(--muted);margin-top:2px}
.wx-meta{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:12px;border-top:1px solid var(--border)}
.wx-item{text-align:center;font-size:12px}
.wx-item span{display:block;font-size:16px;margin-bottom:2px}
.wx-item b{font-weight:500}
.wx-item small{color:var(--muted);font-size:10px;display:block}
.wx-sun{display:flex;justify-content:space-around;padding:10px 0;margin-top:10px;border-top:1px solid var(--border);font-size:12px;color:var(--muted)}
.wx-forecast{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px;padding-top:10px;border-top:1px solid var(--border)}
.fc-day{text-align:center}.fc-date{font-size:10px;color:var(--muted);margin-bottom:4px}.fc-icon{font-size:22px;margin-bottom:4px}
.fc-temps{font-size:11px;display:flex;flex-direction:column;gap:2px}.fc-max{font-weight:500}.fc-min{color:var(--muted);font-size:10px}
.cur-row{display:flex;align-items:center;gap:8px;padding:7px 0;font-size:13px}
.cur-row + .cur-row{border-top:1px solid var(--border)}
.cur-flag{font-size:18px;flex-shrink:0}.cur-code{font-size:11px;color:var(--muted);font-weight:600;letter-spacing:0.5px;min-width:32px}
.cur-val{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:500}.cur-chg{font-size:10px;font-variant-numeric:tabular-nums}
.news-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:600px){.news-grid{grid-template-columns:1fr}}
.news-card{display:block;padding:12px 14px;background:var(--panel2);border:1px solid var(--border);border-radius:12px;color:var(--text);text-decoration:none;transition:transform .15s,border-color .15s}
.news-card:hover{transform:translateY(-2px);border-color:var(--accent)}
.news-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.news-source{font-size:10px;font-weight:600;color:var(--accent);letter-spacing:0.6px;text-transform:uppercase}
.news-ago{font-size:10px;color:var(--muted)}
.news-title{font-size:14px;font-weight:500;line-height:1.35;margin-bottom:4px}
.news-desc{font-size:11px;color:var(--muted);line-height:1.45;margin-top:4px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.cal-month{font-size:14px;font-weight:500;text-align:center;margin-bottom:10px}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.cal-head{font-size:10px;color:var(--muted);text-align:center;padding:3px 0;font-weight:600}
.cal-cell{aspect-ratio:1;display:flex;align-items:center;justify-content:center;font-size:11px;border-radius:6px;font-variant-numeric:tabular-nums;position:relative}
.cal-empty{opacity:0.2}.cal-weekend{color:var(--muted)}
.cal-today{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-weight:600;box-shadow:0 0 14px rgba(96,165,250,0.35)}
.cal-hol{position:absolute;top:1px;right:3px;font-size:8px;color:var(--bad);line-height:1}
.card-art svg{width:100%;height:100%;display:block}
.art-label{position:absolute;bottom:10px;right:12px;font-size:10px;color:rgba(255,255,255,0.6);background:rgba(0,0,0,0.35);padding:4px 10px;border-radius:12px;backdrop-filter:blur(8px)}
.moon-icon{font-size:52px;line-height:1;display:block;margin-bottom:8px;filter:drop-shadow(0 0 20px rgba(167,139,250,0.5))}
.moon-name{font-size:11px;color:var(--muted)}
.ny-num{font-size:44px;font-weight:200;letter-spacing:-0.03em;background:linear-gradient(135deg,#f87171,#facc15);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;line-height:1}
.ny-label{font-size:11px;color:var(--muted);margin-top:6px}
.quote-text{font-size:15px;font-style:italic;line-height:1.5;margin-bottom:8px}
.quote-author{font-size:12px;color:var(--muted);text-align:right}
.quote-author::before{content:'— '}
.iss-hero{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.iss-icon{font-size:44px;line-height:1;filter:drop-shadow(0 4px 16px rgba(96,165,250,0.4));animation:issFloat 4s ease-in-out infinite}
@keyframes issFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.iss-dist{font-size:22px;font-weight:300;color:var(--accent);font-variant-numeric:tabular-nums}
.iss-dist-unit{font-size:12px;color:var(--muted)}.iss-sub{font-size:11px;color:var(--muted);margin-top:2px}
.iss-meta{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);padding-top:10px;border-top:1px solid var(--border)}
.kp-hero,.aq-hero{text-align:center;margin-bottom:10px}
.kp-value,.aq-value{font-size:44px;font-weight:200;letter-spacing:-0.03em;line-height:1;font-variant-numeric:tabular-nums}
.kp-label,.aq-label{font-size:11px;color:var(--muted);margin-top:2px}
.kp-level,.aq-level{text-align:center;font-size:13px;font-weight:500;margin-bottom:10px}
.kp-bars{display:flex;gap:3px;align-items:flex-end;height:40px;padding:6px;background:var(--panel2);border-radius:8px}
.kp-bar{flex:1;background:linear-gradient(180deg,var(--accent),var(--accent2));border-radius:3px;min-height:4px;opacity:0.7}
.kp-axis{display:flex;justify-content:space-between;font-size:9px;color:var(--muted);margin-top:4px}
.aq-meta{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding-top:12px;border-top:1px solid var(--border);font-size:12px;text-align:center}
.aq-meta b{display:block;color:var(--muted);font-size:10px;font-weight:600;letter-spacing:0.5px;margin-bottom:2px}
.eq-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:12px}
.eq-row:last-child{border-bottom:none}
.eq-mag{font-weight:600;font-size:14px;min-width:36px;font-variant-numeric:tabular-nums}
.eq-place{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.eq-meta{color:var(--muted);font-size:11px;white-space:nowrap}
.hist-row{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid var(--border);text-decoration:none;color:var(--text);transition:transform .15s}
.hist-row:last-child{border-bottom:none}.hist-row:hover{transform:translateX(4px)}.hist-row:hover .hist-text{color:var(--accent)}
.hist-year{font-weight:600;color:var(--accent2);font-size:13px;min-width:46px;font-variant-numeric:tabular-nums}
.hist-text{flex:1;font-size:12px;line-height:1.4}
.gh-block{text-align:center}.gh-title{font-size:12px;font-weight:600;color:var(--accent);margin-bottom:10px;letter-spacing:0.5px}
.gh-row{font-size:13px;color:var(--muted);padding:4px 0}.gh-row b{color:var(--text);font-variant-numeric:tabular-nums;font-weight:500}
.track-card{display:flex;align-items:center;gap:12px;padding:10px;background:var(--panel2);border:1px solid var(--border);border-radius:12px;text-decoration:none;color:var(--text);transition:transform .15s,border-color .15s}
.track-card:hover{transform:translateY(-2px);border-color:var(--accent)}
.track-icon{font-size:28px;line-height:1}.track-info{flex:1;min-width:0}
.track-name{font-size:13px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.track-artist{font-size:11px;color:var(--muted);margin-top:2px}
.holiday{grid-column:span 12;text-align:center;padding:12px 20px;background:linear-gradient(135deg,rgba(255,193,7,0.15),rgba(255,87,34,0.12));border:1px solid rgba(255,193,7,0.3);border-radius:16px;font-size:15px;font-weight:500;animation:holidayPulse 3s ease-in-out infinite}
@keyframes holidayPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,193,7,0.3)}50%{box-shadow:0 0 30px 4px rgba(255,193,7,0.18)}}
.space-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:10px}
.space-img{position:relative;border-radius:10px;overflow:hidden;text-decoration:none;display:block;background:#000}
.space-img img{width:100%;height:auto;display:block;transition:transform .3s}.space-img:hover img{transform:scale(1.05)}
.space-label{position:absolute;bottom:4px;left:6px;font-size:9px;color:#fff;background:rgba(0,0,0,0.6);padding:2px 6px;border-radius:6px;font-weight:500}
.space-note{text-align:center;font-size:10px;color:var(--muted)}
.apod-card{display:block;text-decoration:none;color:var(--text)}
.apod-img{width:100%;height:200px;object-fit:cover;border-radius:12px;margin-bottom:10px;background:var(--panel2)}
.apod-title{font-size:14px;font-weight:500;margin-bottom:4px;line-height:1.3}.apod-card:hover .apod-title{color:var(--accent)}
.apod-date{font-size:10px;color:var(--muted);margin-bottom:6px;letter-spacing:0.4px}
.apod-desc{font-size:11px;color:var(--muted);line-height:1.45;overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical}
.ast-row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)}.ast-row:last-child{border-bottom:none}
.ast-icon{font-size:20px;line-height:1}.ast-info{flex:1;min-width:0}
.ast-name{font-size:12px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ast-meta{font-size:10px;color:var(--muted);margin-top:2px}
.launch-card{display:flex;gap:12px;align-items:flex-start}.launch-icon{font-size:36px;line-height:1;filter:drop-shadow(0 4px 12px rgba(96,165,250,0.4))}
.launch-info{flex:1;min-width:0}.launch-name{font-size:13px;font-weight:500;line-height:1.3;margin-bottom:4px}
.launch-provider{font-size:11px;color:var(--accent);margin-bottom:2px}.launch-loc{font-size:10px;color:var(--muted);margin-bottom:6px}
.launch-countdown{font-size:14px;font-weight:600;color:var(--accent2);font-variant-numeric:tabular-nums}
.art-card-museum{display:block;text-decoration:none;color:var(--text)}
.museum-img{width:100%;height:200px;object-fit:cover;border-radius:12px;margin-bottom:10px;background:var(--panel2)}
.museum-title{font-size:13px;font-weight:500;margin-bottom:2px}.art-card-museum:hover .museum-title{color:var(--accent)}
.museum-artist{font-size:11px;color:var(--muted)}.museum-museum{font-size:10px;color:var(--muted);margin-top:6px;opacity:0.7}
.cat-card{display:block}.cat-card img{width:100%;height:100%;min-height:180px;object-fit:cover;display:block}
.plane-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)}
.plane-row:last-child{border-bottom:none}
.plane-icon{font-size:20px}.plane-info{flex:1;min-width:0}
.plane-name{font-size:13px;font-weight:500;font-family:ui-monospace,monospace}
.plane-meta{font-size:10px;color:var(--muted);margin-top:2px}
.plane-country{font-size:10px;color:var(--muted)}
.article-card{display:block;text-decoration:none;color:var(--text)}
.article-thumb{width:100%;max-height:200px;object-fit:cover;border-radius:12px;margin-bottom:10px;background:var(--panel2)}
.article-title{font-size:15px;font-weight:600;margin-bottom:8px;line-height:1.3}.article-card:hover .article-title{color:var(--accent)}
.article-desc{font-size:12px;color:var(--muted);line-height:1.5;margin-bottom:8px}
.article-source{font-size:10px;color:var(--muted);opacity:0.7}

/* ISS map */
.issmap-wrap{width:100%;border-radius:12px;overflow:hidden;background:#0a1628;margin-bottom:10px}
.issmap{width:100%;height:auto;display:block;aspect-ratio:2/1}
.issmap-info{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);font-family:ui-monospace,monospace}

/* Tools */
.tool-input-row{display:flex;gap:6px;margin-top:10px}
.tool-input-row input{flex:1;background:var(--panel2);border:1px solid var(--border);color:var(--text);padding:8px 12px;border-radius:10px;font-size:13px;font-family:inherit}
.tool-input-row input:focus{outline:none;border-color:var(--accent)}
.tool-btn{background:var(--accent);border:none;color:#fff;padding:8px 14px;border-radius:10px;cursor:pointer;font-size:16px;font-weight:600}
.tool-btn:hover{filter:brightness(1.1)}
.habit-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)}
.habit-row:last-child{border-bottom:none}
.habit-name{flex:1;font-size:13px;cursor:pointer}
.habit-name.done{text-decoration:line-through;color:var(--muted)}
.habit-check{width:22px;height:22px;border:2px solid var(--border);border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.habit-check.done{background:var(--good);border-color:var(--good);color:#0a0e1a}
.habit-streak{font-size:10px;color:var(--warn);font-variant-numeric:tabular-nums}
.habit-del{background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:16px;padding:0 4px}
.habit-del:hover{color:var(--bad)}
.todo-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)}
.todo-row:last-child{border-bottom:none}
.todo-check{width:22px;height:22px;border:2px solid var(--border);border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.todo-check.done{background:var(--good);border-color:var(--good);color:#0a0e1a}
.todo-text{flex:1;font-size:13px}
.todo-text.done{text-decoration:line-through;color:var(--muted)}
#notesArea{width:100%;min-height:140px;background:var(--panel2);border:1px solid var(--border);color:var(--text);padding:12px;border-radius:12px;font-size:13px;font-family:inherit;resize:vertical;line-height:1.5}
#notesArea:focus{outline:none;border-color:var(--accent)}
.notes-status{text-align:right;font-size:10px;color:var(--muted);margin-top:6px}
.pomo-timer{font-size:56px;font-weight:200;letter-spacing:-0.03em;font-variant-numeric:tabular-nums;line-height:1;margin:14px 0}
.pomo-buttons{display:flex;gap:8px;justify-content:center;margin-top:14px}
.pomo-count{font-size:11px;color:var(--muted);margin-top:12px}
.mood-buttons{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:8px}
.mood-btn{background:var(--panel2);border:1px solid var(--border);padding:10px 16px;border-radius:12px;cursor:pointer;font-size:24px;transition:transform .15s}
.mood-btn:hover{transform:scale(1.1);border-color:var(--accent)}
.mood-btn.active{background:var(--accent);border-color:var(--accent)}
.mood-status{font-size:12px;color:var(--muted);margin-top:12px}
.water-glass{font-size:36px;font-weight:200;color:var(--accent);font-variant-numeric:tabular-nums;margin:14px 0}
.conv-row{display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13px}
.conv-row input{width:100px;background:var(--panel2);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:8px;font-size:13px;font-family:inherit}
.conv-row input:focus{outline:none;border-color:var(--accent)}
.conv-row span:last-child{color:var(--accent);font-weight:500;font-variant-numeric:tabular-nums}
.pwd-out{font-family:ui-monospace,monospace;font-size:16px;font-weight:500;text-align:center;padding:14px;background:var(--panel2);border-radius:12px;letter-spacing:1px;color:var(--accent);word-break:break-all;cursor:pointer}
.date-row{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border);font-size:12px}
.date-row:last-child{border-bottom:none}
.date-label-txt{flex:1}.date-days{font-weight:600;color:var(--accent2);font-variant-numeric:tabular-nums}
.date-del{background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:14px;padding:0 4px}
.sleep-block{font-size:12px}
.sleep-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border);color:var(--muted);flex-wrap:wrap;gap:4px}
.sleep-row:last-of-type{border-bottom:none}
.sleep-row b{color:var(--text);font-variant-numeric:tabular-nums;font-weight:500}
.sleep-note{font-size:10px;color:var(--muted);margin-top:10px;text-align:center;opacity:0.7}
.dice-result{font-size:60px;line-height:1;margin:10px 0;min-height:70px;display:flex;align-items:center;justify-content:center;transition:transform .3s}
.dice-result.rolling{animation:shake .5s}
@keyframes shake{0%,100%{transform:rotate(0)}25%{transform:rotate(-15deg)}75%{transform:rotate(15deg)}}
.dice-buttons{display:flex;gap:8px;justify-content:center;margin-top:10px}
.dice-btn{background:var(--panel2);border:1px solid var(--border);color:var(--text);padding:8px 14px;border-radius:10px;cursor:pointer;font-size:12px;font-family:inherit;transition:border-color .15s}
.dice-btn:hover{border-color:var(--accent)}
.fact-text{font-size:13px;line-height:1.5;font-style:italic}
.footer{text-align:center;font-size:11px;color:var(--muted);padding:24px 0 8px}
.splash{position:fixed;inset:0;background:var(--bg);z-index:1000;display:flex;align-items:center;justify-content:center;font-size:52px;animation:splashOut 0.9s ease-out 1s forwards;pointer-events:none}
@keyframes splashOut{to{opacity:0;visibility:hidden}}
'''


def get_js(weather_kind):
    return f'''
(function(){{
  function tick(){{
    const now = new Date();
    const msk = new Date(now.toLocaleString('en-US', {{timeZone:'Europe/Moscow'}}));
    const hh = String(msk.getHours()).padStart(2, '0');
    const mm = String(msk.getMinutes()).padStart(2, '0');
    const ss = String(msk.getSeconds()).padStart(2, '0');
    document.getElementById('h1').textContent = hh[0];
    document.getElementById('h2').textContent = hh[1];
    document.getElementById('m1').textContent = mm[0];
    document.getElementById('m2').textContent = mm[1];
    document.getElementById('ss').textContent = ss;
  }}
  tick(); setInterval(tick, 1000);
  function counters(){{
    const msk = new Date(new Date().toLocaleString('en-US', {{timeZone:'Europe/Moscow'}}));
    const daySec = msk.getHours()*3600 + msk.getMinutes()*60 + msk.getSeconds();
    document.getElementById('cnt-day').textContent = daySec.toLocaleString('ru-RU');
    const start = new Date(msk.getFullYear(), 0, 1);
    document.getElementById('cnt-year').textContent = Math.floor((msk - start) / 86400000).toLocaleString('ru-RU');
    const end = new Date(msk.getFullYear(), 11, 31);
    document.getElementById('cnt-left').textContent = Math.floor((end - msk) / 86400000) + 1;
  }}
  counters(); setInterval(counters, 1000);
  let saved = localStorage.getItem('theme') || 'dark';
  if (!['dark','light'].includes(saved)) saved = 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('themeBtn');
  btn.textContent = saved === 'dark' ? '☀' : '🌙';
  btn.addEventListener('click', function(){{
    const cur = document.documentElement.getAttribute('data-theme') || 'dark';
    const nxt = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nxt);
    localStorage.setItem('theme', nxt);
    btn.textContent = nxt === 'dark' ? '☀' : '🌙';
  }});
  let soundOn = localStorage.getItem('clockSound') === 'on';
  const sBtn = document.getElementById('soundBtn');
  sBtn.textContent = soundOn ? '🔊' : '🔇';
  let audioCtx = null;
  function beep(){{
    if (!audioCtx) {{ try {{ audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }} catch(e){{ return; }} }}
    const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
    osc.frequency.value = 880; osc.type = 'sine';
    gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
    osc.connect(gain).connect(audioCtx.destination);
    osc.start(); osc.stop(audioCtx.currentTime + 0.06);
  }}
  sBtn.addEventListener('click', function(){{
    soundOn = !soundOn;
    localStorage.setItem('clockSound', soundOn ? 'on' : 'off');
    sBtn.textContent = soundOn ? '🔊' : '🔇';
  }});
  setInterval(() => {{ if(soundOn) beep(); }}, 1000);
  const kind = '{weather_kind}';
  const canvas = document.getElementById('bgCanvas');
  if(canvas){{
    const ctx = canvas.getContext('2d');
    let W, H, particles = [];
    function resize(){{
      W = canvas.width = window.innerWidth * devicePixelRatio;
      H = canvas.height = window.innerHeight * devicePixelRatio;
      canvas.style.width = window.innerWidth + 'px'; canvas.style.height = window.innerHeight + 'px';
    }}
    resize(); window.addEventListener('resize', resize);
    let count = 0;
    if(kind === 'rain' || kind === 'storm') count = 110;
    else if(kind === 'snow') count = 80;
    else if(kind === 'sun') count = 45;
    else if(kind === 'fog') count = 30;
    else count = 25;
    for(let i = 0; i < count; i++){{
      particles.push({{x: Math.random() * W, y: Math.random() * H,
        vx: kind === 'rain' ? 0.5 : (Math.random() - 0.5) * 0.6,
        vy: kind === 'rain' ? 4 + Math.random() * 6 : kind === 'snow' ? 0.4 + Math.random() * 1 : (Math.random() - 0.5) * 0.5,
        r: kind === 'rain' ? 1 + Math.random() * 1.5 : kind === 'snow' ? 2 + Math.random() * 3 : 1 + Math.random() * 2.5,
        a: 0.15 + Math.random() * 0.5}});
    }}
    function draw(){{
      ctx.clearRect(0, 0, W, H);
      for(const p of particles){{
        if(kind === 'rain' || kind === 'storm'){{
          ctx.strokeStyle = 'rgba(150,200,255,' + p.a + ')'; ctx.lineWidth = p.r;
          ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x + p.vx * 3, p.y + 20 + p.vy * 2); ctx.stroke();
        }} else if(kind === 'snow'){{
          ctx.fillStyle = 'rgba(255,255,255,' + p.a + ')';
          ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
        }} else if(kind === 'sun'){{
          ctx.fillStyle = 'rgba(255,220,120,' + (p.a * 0.8) + ')';
          ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
        }} else {{
          ctx.fillStyle = 'rgba(200,220,255,' + (p.a * 0.6) + ')';
          ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
        }}
        p.x += p.vx; p.y += p.vy;
        if(p.y > H + 20){{ p.y = -20; p.x = Math.random() * W; }}
        if(p.x > W + 20) p.x = -20;
        if(p.x < -20) p.x = W + 20;
      }}
      requestAnimationFrame(draw);
    }}
    draw();
  }}
  function sleepCalc(){{
    const msk = new Date(new Date().toLocaleString('en-US', {{timeZone:'Europe/Moscow'}}));
    [6, 7, 8].forEach(target => {{
      const wake = new Date(msk); wake.setHours(target, 0, 0, 0);
      if (wake <= msk) wake.setDate(wake.getDate() + 1);
      const sleepMs = wake.getTime() - (15 * 60 * 1000) - (5 * 90 * 60 * 1000);
      const s = new Date(sleepMs);
      const el = document.getElementById('sleep-' + target);
      if (el) el.textContent = String(s.getHours()).padStart(2, '0') + ':' + String(s.getMinutes()).padStart(2, '0');
    }});
  }}
  sleepCalc(); setInterval(sleepCalc, 60000);
  window.rollDice = function(){{
    const el = document.getElementById('diceResult'); if (!el) return;
    el.classList.add('rolling');
    const faces = ['⚀','⚁','⚂','⚃','⚄','⚅'];
    let n = 0;
    const iv = setInterval(() => {{ el.textContent = faces[Math.floor(Math.random() * 6)]; n++; if (n > 10) {{ clearInterval(iv); el.classList.remove('rolling'); }} }}, 60);
  }};
  window.flipCoin = function(){{
    const el = document.getElementById('diceResult'); if (!el) return;
    el.classList.add('rolling');
    let n = 0;
    const iv = setInterval(() => {{ el.textContent = Math.random() < 0.5 ? '🪙 Орёл' : '🪙 Решка'; n++; if (n > 8) {{ clearInterval(iv); el.classList.remove('rolling'); }} }}, 80);
  }};

  // ============ КАРТА МКС (LIVE) ============
  let issLat = 0, issLon = 0;
  function updateIssMap(){{
    const dot = document.getElementById('issDot');
    const dot2 = document.getElementById('issDot2');
    if (!dot) return;
    const x = issLon + 180;
    const y = 90 - issLat;
    dot.setAttribute('cx', x);
    dot.setAttribute('cy', y);
    if (dot2) {{
      dot2.setAttribute('cx', x);
      dot2.setAttribute('cy', y);
    }}
    const coordsEl = document.getElementById('issMapCoords');
    if (coordsEl) coordsEl.textContent = issLat.toFixed(1) + '°, ' + issLon.toFixed(1) + '°';
    const lat1 = 43.4981, lon1 = 43.6189;
    const R = 6371;
    const dLat = (issLat - lat1) * Math.PI / 180;
    const dLon = (issLon - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180) * Math.cos(issLat*Math.PI/180) * Math.sin(dLon/2)**2;
    const dist = Math.round(2 * R * Math.asin(Math.sqrt(a)));
    const distEl = document.getElementById('issMapDist');
    if (distEl) distEl.textContent = dist.toLocaleString('ru-RU') + ' км до Нальчика';
  }}
  async function fetchIssLive(){{
    try {{
      const r = await fetch('https://api.wheretheiss.at/v1/satellites/25544');
      if (!r.ok) return;
      const d = await r.json();
      issLat = d.latitude;
      issLon = d.longitude;
      updateIssMap();
    }} catch(e){{}}
  }}
  fetchIssLive();
  setInterval(fetchIssLive, 5000);

  // ============ ПРИВЫЧКИ ============
  function todayKey() {{ const d = new Date(); return d.getFullYear() + '-' + (d.getMonth()+1) + '-' + d.getDate(); }}
  function loadHabits() {{ try {{ return JSON.parse(localStorage.getItem('habits') || '[]'); }} catch(e) {{ return []; }} }}
  function saveHabits(h) {{ localStorage.setItem('habits', JSON.stringify(h)); }}
  window.addHabit = function(){{
    const inp = document.getElementById('habitInput');
    const name = inp.value.trim(); if (!name) return;
    const h = loadHabits(); h.push({{name: name, dates: [], streak: 0}});
    saveHabits(h); inp.value = ''; renderHabits();
  }};
  window.toggleHabit = function(i){{
    const h = loadHabits(); const key = todayKey();
    const idx = h[i].dates.indexOf(key);
    if (idx >= 0) h[i].dates.splice(idx, 1); else h[i].dates.push(key);
    let streak = 0; let d = new Date();
    while (true) {{
      const k = d.getFullYear() + '-' + (d.getMonth()+1) + '-' + d.getDate();
      if (h[i].dates.includes(k)) {{ streak++; d.setDate(d.getDate() - 1); }} else break;
    }}
    h[i].streak = streak;
    saveHabits(h); renderHabits();
  }};
  window.delHabit = function(i){{ const h = loadHabits(); h.splice(i, 1); saveHabits(h); renderHabits(); }};
  function renderHabits(){{
    const el = document.getElementById('habits'); if (!el) return;
    const h = loadHabits(); const key = todayKey();
    if (!h.length) {{ el.innerHTML = '<div class="empty">Пока нет привычек</div>'; return; }}
    el.innerHTML = h.map((x, i) => {{
      const done = x.dates.includes(key);
      const streak = x.streak || 0;
      return '<div class="habit-row">' +
        '<div class="habit-check ' + (done ? 'done' : '') + '" onclick="toggleHabit(' + i + ')">' + (done ? '✓' : '') + '</div>' +
        '<span class="habit-name ' + (done ? 'done' : '') + '" onclick="toggleHabit(' + i + ')">' + x.name.replace(/</g,'&lt;') + '</span>' +
        (streak > 1 ? '<span class="habit-streak">🔥' + streak + '</span>' : '') +
        '<button class="habit-del" onclick="delHabit(' + i + ')">×</button></div>';
    }}).join('');
  }}
  renderHabits();

  // ============ TODO ============
  function loadTodo() {{ try {{ return JSON.parse(localStorage.getItem('todo') || '[]'); }} catch(e) {{ return []; }} }}
  function saveTodo(t) {{ localStorage.setItem('todo', JSON.stringify(t)); }}
  window.addTodo = function(){{
    const inp = document.getElementById('todoInput');
    const txt = inp.value.trim(); if (!txt) return;
    const t = loadTodo(); t.push({{text: txt, done: false, ts: Date.now()}});
    saveTodo(t); inp.value = ''; renderTodo();
  }};
  window.toggleTodo = function(i){{ const t = loadTodo(); t[i].done = !t[i].done; saveTodo(t); renderTodo(); }};
  window.delTodo = function(i){{ const t = loadTodo(); t.splice(i, 1); saveTodo(t); renderTodo(); }};
  function renderTodo(){{
    const el = document.getElementById('todoList'); if (!el) return;
    const t = loadTodo();
    if (!t.length) {{ el.innerHTML = '<div class="empty">Все задачи сделаны ✨</div>'; return; }}
    el.innerHTML = t.map((x, i) =>
      '<div class="todo-row">' +
      '<div class="todo-check ' + (x.done ? 'done' : '') + '" onclick="toggleTodo(' + i + ')">' + (x.done ? '✓' : '') + '</div>' +
      '<span class="todo-text ' + (x.done ? 'done' : '') + '" onclick="toggleTodo(' + i + ')">' + x.text.replace(/</g,'&lt;') + '</span>' +
      '<button class="habit-del" onclick="delTodo(' + i + ')">×</button></div>'
    ).join('');
  }}
  renderTodo();

  // ============ ЗАМЕТКИ ============
  const notesArea = document.getElementById('notesArea');
  const notesStatus = document.getElementById('notesStatus');
  if (notesArea) {{
    notesArea.value = localStorage.getItem('notes') || '';
    let notesTimer = null;
    notesArea.addEventListener('input', () => {{
      notesStatus.textContent = 'сохраняю...';
      clearTimeout(notesTimer);
      notesTimer = setTimeout(() => {{
        localStorage.setItem('notes', notesArea.value);
        notesStatus.textContent = '✓ сохранено ' + new Date().toLocaleTimeString('ru-RU', {{hour:'2-digit',minute:'2-digit'}});
      }}, 600);
    }});
  }}

  // ============ ПОМОДОРО ============
  let pomoSeconds = 25 * 60;
  let pomoRunning = false;
  let pomoInterval = null;
  let pomoMode = 'work';
  const pomoCountKey = 'pomo-' + todayKey();
  let pomoCount = parseInt(localStorage.getItem(pomoCountKey) || '0');
  const pomoTimeEl = document.getElementById('pomoTime');
  const pomoStartBtn = document.getElementById('pomoStart');
  const pomoCountEl = document.getElementById('pomoCount');
  function pomoUpdate(){{
    if (!pomoTimeEl) return;
    const m = Math.floor(pomoSeconds / 60); const s = pomoSeconds % 60;
    pomoTimeEl.textContent = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
    pomoTimeEl.style.color = pomoMode === 'work' ? 'var(--accent)' : 'var(--good)';
  }}
  window.pomoToggle = function(){{
    if (pomoRunning) {{
      clearInterval(pomoInterval); pomoRunning = false;
      if (pomoStartBtn) pomoStartBtn.textContent = '▶ Старт';
    }} else {{
      pomoRunning = true;
      if (pomoStartBtn) pomoStartBtn.textContent = '⏸ Пауза';
      pomoInterval = setInterval(() => {{
        pomoSeconds--;
        if (pomoSeconds <= 0) {{
          clearInterval(pomoInterval); pomoRunning = false;
          if (pomoStartBtn) pomoStartBtn.textContent = '▶ Старт';
          if (pomoMode === 'work') {{
            pomoCount++; localStorage.setItem(pomoCountKey, pomoCount);
            if (pomoCountEl) pomoCountEl.textContent = '🍅 сегодня: ' + pomoCount;
            pomoMode = 'break'; pomoSeconds = 5 * 60;
          }} else {{
            pomoMode = 'work'; pomoSeconds = 25 * 60;
          }}
          if (audioCtx) {{ try {{ beep(); beep(); }} catch(e){{}} }}
        }}
        pomoUpdate();
      }}, 1000);
    }}
  }};
  window.pomoReset = function(){{
    clearInterval(pomoInterval); pomoRunning = false;
    pomoMode = 'work'; pomoSeconds = 25 * 60;
    if (pomoStartBtn) pomoStartBtn.textContent = '▶ Старт';
    pomoUpdate();
  }};
  pomoUpdate();
  if (pomoCountEl) pomoCountEl.textContent = '🍅 сегодня: ' + pomoCount;

  // ============ НАСТРОЕНИЕ ============
  const moodKey = 'mood-' + todayKey();
  function renderMood(){{
    const cur = localStorage.getItem(moodKey);
    const st = document.getElementById('moodStatus');
    if (st) {{
      const map = {{'good':'😄 Отлично','ok':'😐 Норм','bad':'😞 Плохо'}};
      st.textContent = 'Сегодня: ' + (cur ? map[cur] : '—');
    }}
    document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
    if (cur) {{
      const el = document.querySelector('.mood-btn[onclick*="' + cur + '"]');
      if (el) el.classList.add('active');
    }}
  }}
  window.setMood = function(m){{ localStorage.setItem(moodKey, m); renderMood(); }};
  renderMood();

  // ============ ВОДА ============
  const waterKey = 'water-' + todayKey();
  function renderWater(){{
    const v = parseInt(localStorage.getItem(waterKey) || '0');
    const el = document.getElementById('waterGlass');
    if (el) {{
      const cups = '💧'.repeat(Math.min(v, 8));
      el.textContent = v + ' / 8 ' + cups;
    }}
  }}
  window.addWater = function(){{
    const v = parseInt(localStorage.getItem(waterKey) || '0') + 1;
    localStorage.setItem(waterKey, v); renderWater();
  }};
  window.resetWater = function(){{ localStorage.setItem(waterKey, '0'); renderWater(); }};
  renderWater();

  // ============ КОНВЕРТЕРЫ ============
  window.convTemp = function(){{
    const c = parseFloat(document.getElementById('convC').value);
    document.getElementById('convF').textContent = isNaN(c) ? '°F' : (c * 9 / 5 + 32).toFixed(1) + '°F';
  }};
  window.convDist = function(){{
    const km = parseFloat(document.getElementById('convKm').value);
    document.getElementById('convMi').textContent = isNaN(km) ? 'миль' : (km * 0.621371).toFixed(2) + ' миль';
  }};
  window.convWeight = function(){{
    const kg = parseFloat(document.getElementById('convKg').value);
    document.getElementById('convLb').textContent = isNaN(kg) ? 'фунт' : (kg * 2.20462).toFixed(2) + ' фунт';
  }};
  window.convMoney = function(){{
    const r = parseFloat(document.getElementById('convRub').value);
    const el = document.getElementById('convUsd');
    if (isNaN(r)) {{ el.textContent = '$'; return; }}
    el.textContent = '$' + (r / EXCH.usd).toFixed(2) + ' / €' + (r / EXCH.eur).toFixed(2);
  }};

  // ============ ПАРОЛЬ / QR ============
  window.genPwd = function(){{
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%^&*';
    let s = '';
    for (let i = 0; i < 20; i++) s += chars[Math.floor(Math.random() * chars.length)];
    const el = document.getElementById('pwdOut');
    el.textContent = s;
    el.onclick = () => {{ navigator.clipboard.writeText(s); el.textContent = '✓ скопировано'; setTimeout(() => el.textContent = s, 1000); }};
  }};
  window.genQR = function(){{
    const box = document.getElementById('qrBox');
    box.innerHTML = '';
    if (!window.QRCode) {{ box.textContent = 'QR-библиотека не загрузилась'; return; }}
    new QRCode(box, {{text: location.href, width: 180, height: 180, colorDark: '#000', colorLight: '#fff'}});
  }};

  // ============ СЧЁТЧИКИ ДАТ ============
  function loadDates() {{ try {{ return JSON.parse(localStorage.getItem('dates') || '[]'); }} catch(e) {{ return []; }} }}
  function saveDates(d) {{ localStorage.setItem('dates', JSON.stringify(d)); }}
  window.addDateCounter = function(){{
    const inp = document.getElementById('dateInput');
    const lbl = document.getElementById('dateLabel');
    if (!inp.value) return;
    const d = loadDates();
    d.push({{date: inp.value, label: lbl.value.trim() || inp.value}});
    saveDates(d); inp.value = ''; lbl.value = ''; renderDates();
  }};
  window.delDateCounter = function(i){{ const d = loadDates(); d.splice(i, 1); saveDates(d); renderDates(); }};
  function renderDates(){{
    const el = document.getElementById('dateCounters'); if (!el) return;
    const d = loadDates();
    if (!d.length) {{ el.innerHTML = '<div class="empty">Добавь важную дату</div>'; return; }}
    const now = new Date(); now.setHours(0,0,0,0);
    el.innerHTML = d.map((x, i) => {{
      const target = new Date(x.date); target.setHours(0,0,0,0);
      const days = Math.round((target - now) / 86400000);
      const label = days > 0 ? 'через ' + days + ' дн.' : (days < 0 ? Math.abs(days) + ' дн. назад' : 'сегодня 🎉');
      const emoji = days === 0 ? '🎉' : (days > 0 ? '⏳' : '📅');
      return '<div class="date-row">' +
        '<span class="date-label-txt">' + emoji + ' ' + x.label.replace(/</g,'&lt;') + '</span>' +
        '<span class="date-days">' + label + '</span>' +
        '<button class="date-del" onclick="delDateCounter(' + i + ')">×</button></div>';
    }}).join('');
  }}
  renderDates();
}})();
'''


if __name__ == '__main__':
    generate()
