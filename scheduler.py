from collections import defaultdict
from config import (
    TOTAL_DAYS, HOLIDAYS, HERMIT_HOLIDAYS, STAT_SCHEDULE,
    AUTO_SL, DAY, NIGHT, SUN,
    date_to_day, day_of_week, is_school_restricted
)
from social_link_data import SOCIAL_LINKS


# Fungsi mengecek ketersediaan SL pada hari tertentu.

def is_sl_available(sl_key, day_idx, stats, sl_ranks):
    sl = SOCIAL_LINKS[sl_key]

    # SL otomatis tidak perlu dijadwalkan
    if sl.get("auto_rank", False):
        return False

    # Cek unlock date
    if day_idx < sl["unlock_day"]:
        return False

    # Cek end date
    if day_idx > sl["end_day"]:
        return False

    # Cek rank sudah max
    if sl_ranks.get(sl_key, 0) >= 10:
        return False

    # Cek stat requirements
    for stat, min_val in sl.get("stat_req", {}).items():
        if stats.get(stat, 0) < min_val:
            return False

    # Cek prereq SL
    for prereq_key, min_rank in sl.get("prereq_sl", {}).items():
        if sl_ranks.get(prereq_key, 0) < min_rank:
            return False

    # Cek hari dalam minggu
    dow = day_of_week(day_idx)
    available_days = sl["available_days"]

    # Hermit (Maya): hanya Minggu + holiday khusus
    if sl_key == "Hermit":
        if dow != SUN and day_idx not in HERMIT_HOLIDAYS:
            return False
    else:
        if dow not in available_days:
            return False

    # Empress: Mon & Fri hanya tersedia sampai 24 Desember
    if sl_key == "Empress":
        from config import MON, FRI
        if dow in {MON, FRI} and day_idx > date_to_day(12, 24):
            return False

    # Cek school restriction (ujian & holiday)
    if sl.get("school_restricted", False):
        if is_school_restricted(day_idx):
            return False

    return True


# Fungsi perhitungan urgency SL.

def sessions_still_needed(sl_key, sl_ranks):
    current_rank = sl_ranks.get(sl_key, 0)
    ranks_needed = SOCIAL_LINKS[sl_key]["ranks_needed"]
    return sum(ranks_needed[current_rank:])


def count_available_future_days(sl_key, from_day, stats, sl_ranks):
    count = 0
    for d in range(from_day, TOTAL_DAYS):
        if is_sl_available(sl_key, d, stats, sl_ranks):
            count += 1
    return count


def compute_urgency(sl_key, day_idx, stats, sl_ranks):
    needed = sessions_still_needed(sl_key, sl_ranks)
    if needed == 0:
        return -1  # Sudah max rank

    future_days = count_available_future_days(sl_key, day_idx + 1, stats, sl_ranks)
    if future_days == 0:
        return float('inf')  # Tidak ada hari lagi = sangat kritis

    return needed / future_days


# Fungsi pembaruan rank SL.

def try_update_rank(sl_key, sl_ranks, sessions_done):
    sl = SOCIAL_LINKS[sl_key]
    total_done = sessions_done[sl_key]
    cumulative = 0
    new_rank = 0

    for r in range(1, 11):
        idx = r - 1
        cumulative += sl["ranks_needed"][idx] if idx < len(sl["ranks_needed"]) else 1
        if total_done >= cumulative:
            new_rank = r
        else:
            break

    if new_rank > sl_ranks.get(sl_key, 0):
        sl_ranks[sl_key] = new_rank

    return sl_ranks.get(sl_key, 0)


# Algoritma penjadwalan utama.

def run_dp_scheduler():
    # Inisialisasi state
    stats = {"academics": 1, "charm": 1, "courage": 1}
    sl_ranks = {sl_key: 0 for sl_key in SOCIAL_LINKS}
    sessions_done = defaultdict(int)

    # SL otomatis langsung dianggap selesai
    for sl_key in AUTO_SL:
        sl_ranks[sl_key] = 10

    schedule = []

    for day_idx in range(TOTAL_DAYS):

        # Update stat protagonis sesuai jadwal
        if day_idx in STAT_SCHEDULE:
            for stat, val in STAT_SCHEDULE[day_idx].items():
                stats[stat] = max(stats[stat], val)

        # Kumpulkan SL yang tersedia hari ini beserta urgency-nya
        available_day   = []
        available_night = []

        for sl_key in SOCIAL_LINKS:
            if sl_key in AUTO_SL:
                continue
            if not is_sl_available(sl_key, day_idx, stats, sl_ranks):
                continue

            urgency = compute_urgency(sl_key, day_idx, stats, sl_ranks)
            sl = SOCIAL_LINKS[sl_key]

            if sl["slot"] == DAY:
                available_day.append((urgency, sl_key))
            else:
                available_night.append((urgency, sl_key))

        # Pilih SL paling urgent untuk slot DAY
        for slot_list, slot_name in [
            (available_day, DAY),
            (available_night, NIGHT)
        ]:
            if not slot_list:
                continue

            slot_list.sort(key=lambda x: -x[0])
            chosen_urgency, chosen_sl = slot_list[0]

            if chosen_urgency <= 0:
                continue  # Tidak ada yang perlu dikunjungi

            rank_before = sl_ranks.get(chosen_sl, 0)
            sessions_done[chosen_sl] += 1
            rank_after = try_update_rank(chosen_sl, sl_ranks, sessions_done)

            schedule.append({
                "day":         day_idx,
                "slot":        slot_name,
                "sl_key":      chosen_sl,
                "rank_before": rank_before,
                "rank_after":  rank_after,
                "urgency":     round(chosen_urgency, 3),
            })

    return schedule, sl_ranks, stats


# Analisis bottleneck reachability SL.

def backward_dp_reachability():
    # Asumsi stat sudah max di akhir game (untuk hitung hari tersedia maksimal)
    stats_max = {"academics": 6, "charm": 6, "courage": 6}
    sl_ranks_zero = {sl_key: 0 for sl_key in SOCIAL_LINKS}

    reachable = {}
    for day_idx in range(TOTAL_DAYS - 1, -1, -1):
        reachable[day_idx] = {}
        dow = day_of_week(day_idx)

        for sl_key in SOCIAL_LINKS:
            if sl_key in AUTO_SL:
                reachable[day_idx][sl_key] = True
                continue

            sl = SOCIAL_LINKS[sl_key]
            can_visit = (
                day_idx >= sl["unlock_day"] and
                day_idx <= sl["end_day"] and
                (not sl.get("school_restricted", False) or
                 not is_school_restricted(day_idx))
            )

            if sl_key == "Hermit":
                can_visit = can_visit and (dow == SUN or day_idx in HERMIT_HOLIDAYS)
            else:
                can_visit = can_visit and (dow in sl["available_days"])

            if sl_key == "Empress":
                from config import MON, FRI
                if dow in {MON, FRI} and day_idx > date_to_day(12, 24):
                    can_visit = False

            reachable[day_idx][sl_key] = can_visit

    # Hitung total hari tersedia per SL
    counts = {}
    for sl_key in SOCIAL_LINKS:
        if sl_key in AUTO_SL:
            continue
        avail = sum(1 for d in range(TOTAL_DAYS) if reachable[d].get(sl_key, False))
        needed = sum(SOCIAL_LINKS[sl_key]["ranks_needed"])
        counts[sl_key] = (avail, needed)

    return reachable, counts
