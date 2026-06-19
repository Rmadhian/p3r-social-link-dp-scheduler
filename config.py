# Konstanta hari dalam seminggu.
MON, TUE, WED, THU, FRI, SAT, SUN = 0, 1, 2, 3, 4, 5, 6
DAY_NAMES = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

# Slot waktu
DAY   = "day"
NIGHT = "night"

# Konversi tanggal in-game (mulai 7 April 2009).

MONTH_STARTS = {
    4: 0,    # April
    5: 30,
    6: 61,
    7: 91,
    8: 122,
    9: 153,
    10: 183,
    11: 214,
    12: 244,
    1: 275   # Januari tahun berikutnya
}

START_OFFSET = 6  # Mulai dari tanggal 7 April, bukan tanggal 1


def date_to_day(month, day):
    return MONTH_STARTS[month] + day - 1 - START_OFFSET


def day_of_week(day_idx):
    return (day_idx + 1) % 7


def day_to_str(day_idx):
    # Tabel bulan dengan tanggal mulai tiap bulan (dalam indeks hari)
    month_list = [
        (date_to_day(4,  1),  "Apr", 4),
        (date_to_day(5,  1),  "Mei", 5),
        (date_to_day(6,  1),  "Jun", 6),
        (date_to_day(7,  1),  "Jul", 7),
        (date_to_day(8,  1),  "Agu", 8),
        (date_to_day(9,  1),  "Sep", 9),
        (date_to_day(10, 1),  "Okt", 10),
        (date_to_day(11, 1),  "Nov", 11),
        (date_to_day(12, 1),  "Des", 12),
        (date_to_day(1,  1),  "Jan", 1),
    ]

    month_name  = "Apr"
    month_start = date_to_day(4, 1)

    for ms, mn, _ in month_list:
        if day_idx >= ms:
            month_start = ms
            month_name  = mn

    day_num = day_idx - month_start + 1
    dow = DAY_NAMES[day_of_week(day_idx)]
    return f"{month_name} {day_num:2d} ({dow})"


# Total hari simulasi hingga 31 Januari.
TOTAL_DAYS = date_to_day(1, 31) + 1


# Daftar hari libur.
HOLIDAYS = set([
    date_to_day(4, 29),   # Showa Day
    date_to_day(5, 3),    # Constitution Day
    date_to_day(5, 4),    # Greenery Day
    date_to_day(5, 5),    # Children's Day
    date_to_day(9, 21),   # Respect for the Aged Day
    date_to_day(9, 22),   # National Holiday
    date_to_day(9, 23),   # Autumnal Equinox
    date_to_day(10, 12),  # Health and Sports Day
    date_to_day(11, 3),   # Culture Day
    date_to_day(11, 23),  # Labor Thanksgiving Day
    date_to_day(12, 23),  # Emperor's Birthday
    date_to_day(1, 1),    # New Year
    date_to_day(1, 2),    # New Year holiday
    date_to_day(1, 3),    # New Year holiday
    date_to_day(1, 11),   # Coming of Age Day
])

# Hari libur khusus untuk Hermit (Maya) - bermain MMORPG
HERMIT_HOLIDAYS = set([
    date_to_day(4, 29),
    date_to_day(5, 4),
    date_to_day(5, 5),
    date_to_day(9, 21),
    date_to_day(9, 22),
    date_to_day(9, 23),
    date_to_day(10, 12),
    date_to_day(11, 23),
    date_to_day(12, 23),
    date_to_day(1, 11),
])

# Minggu ujian tidak memungkinkan untuk Social Link sekolah.
EXAM_WEEKS = set()
exam_dates = [
    (5, 20), (5, 21), (5, 22), (5, 23), (5, 24),
    (7, 14), (7, 15), (7, 16), (7, 17), (7, 18),
    (10, 6), (10, 7), (10, 8), (10, 9), (10, 10),
    (12, 8), (12, 9), (12, 10), (12, 11), (12, 12),
]
for _m, _d in exam_dates:
    EXAM_WEEKS.add(date_to_day(_m, _d))


def is_school_restricted(day_idx):
    return day_idx in HOLIDAYS or day_idx in EXAM_WEEKS


# Estimasi peningkatan stat berdasarkan aktivitas harian.
STAT_SCHEDULE = {
    date_to_day(4, 28): {"charm": 2},    # Charm Lv.2 - unlock Moon
    date_to_day(5, 7):  {"charm": 3},
    date_to_day(5, 8):  {"academics": 2},  # Academics Lv.2 - unlock Temperance
    date_to_day(5, 15): {"courage": 2},   # Courage Lv.2 - unlock Tower
    date_to_day(5, 16): {"charm": 4},     # Charm Lv.4 - unlock Devil
    date_to_day(6, 1):  {"courage": 6},   # Courage Lv.6 - unlock Priestess
    date_to_day(7, 1):  {"courage": 4},
    date_to_day(7, 15): {"academics": 4}, # Academics Lv.4 - unlock Sun
    date_to_day(7, 20): {"charm": 6},     # Charm Lv.6 - unlock Lovers
    date_to_day(10, 1): {"academics": 6}, # Academics Lv.6 - unlock Empress
}

# SL yang naik rank secara otomatis (tidak perlu dijadwalkan)
AUTO_SL = {"Fool", "Death", "Judgement"}
