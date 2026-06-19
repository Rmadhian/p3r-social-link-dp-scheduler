from config import DAY, TOTAL_DAYS, day_to_str
from social_link_data import SOCIAL_LINKS
from scheduler import backward_dp_reachability


def print_header():
    print("=" * 70)
    print("PERSONA 3 RELOAD - SOCIAL LINK OPTIMIZER")
    print("=" * 70)
    print(f"Total hari simulasi : {TOTAL_DAYS} hari")
    print(f"Total Social Link   : {len(SOCIAL_LINKS)}")
    print(f"Target              : Semua 22 SL mencapai Rank 10")
    print()


def print_full_schedule(schedule):
    print("=" * 70)
    print(f"SELURUH JADWAL (TOTAL {len(schedule)} SESI)")
    print("=" * 70)
    print(f"{'Tanggal':<18} {'Slot':<8} {'Social Link':<35} {'Rank'}")
    print("-" * 70)

    for entry in schedule:
        date_str = day_to_str(entry["day"])
        slot_str = "Sore" if entry["slot"] == DAY else "Malam"
        sl_name  = SOCIAL_LINKS[entry["sl_key"]]["name"]
        rank_str = f"{entry['rank_before']} → {entry['rank_after']}"
        print(f"{date_str:<18} {slot_str:<8} {sl_name:<35} {rank_str}")

    print()


def print_all_ranks(sl_ranks):
    print("=" * 70)
    print("RANK AKHIR SEMUA SOCIAL LINK")
    print("=" * 70)
    print(f"{'Arcana':<15} {'Karakter':<35} {'Status'}")
    print("-" * 70)

    for sl_key, sl in SOCIAL_LINKS.items():
        rank   = sl_ranks.get(sl_key, 0)
        status = "MAX" if rank >= 10 else f"Rank {rank}/10  ← BELUM SELESAI"
        print(f"{sl_key:<15} {sl['name']:<35} {status}")
    print()


def print_summary(sl_ranks):
    total_rank = sum(sl_ranks.values())
    max_rank   = len(SOCIAL_LINKS) * 10
    completed  = sum(1 for r in sl_ranks.values() if r >= 10)
    incomplete = [
        (sl_key, rank, SOCIAL_LINKS[sl_key]["name"])
        for sl_key, rank in sl_ranks.items()
        if rank < 10
    ]

    print("=" * 70)
    print("RINGKASAN HASIL SIMULASI")
    print("=" * 70)
    print(f"Social Link selesai (Rank 10) : {completed}/{len(SOCIAL_LINKS)}")
    print(f"Total rank tercapai           : {total_rank}/{max_rank}")
    print(f"Persentase                    : {total_rank / max_rank * 100:.1f}%")

    if incomplete:
        print(f"\nSocial Link yang belum selesai ({len(incomplete)}):")
        for _, rank, name in sorted(incomplete, key=lambda x: x[1]):
            print(f"  - {name}: Rank {rank}/10")
    else:
        print("\nSEMUA SOCIAL LINK BERHASIL DIMAKSIMALKAN!")
    print()


def print_bottleneck_analysis():
    _, counts = backward_dp_reachability()

    print("=" * 70)
    print("ANALISIS BOTTLENECK")
    print("=" * 70)
    print("Rasio = hari_tersedia / sesi_dibutuhkan")
    print("Rasio kecil = SL lebih kritis, harus diprioritaskan lebih awal")
    print()
    print(f"{'Social Link':<35} {'Hari Tersedia':>14} {'Sesi Dibutuhkan':>16} {'Rasio':>8}")
    print("-" * 75)

    sorted_sl = sorted(counts.items(), key=lambda x: x[1][0])
    for sl_key, (avail, needed) in sorted_sl:
        name  = SOCIAL_LINKS[sl_key]["name"]
        ratio = avail / max(needed, 1)
        print(f"{name:<35} {avail:>14} {needed:>16} {ratio:>8.1f}x")
    print()


