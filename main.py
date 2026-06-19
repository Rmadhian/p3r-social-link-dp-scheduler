from scheduler import run_dp_scheduler
from output import (
    print_header,
    print_full_schedule,
    print_all_ranks,
    print_summary,
    print_bottleneck_analysis,
)


def main():
    print_header()

    print("Menjalankan analisis bottleneck...")
    print_bottleneck_analysis()

    print("Menjalankan simulasi penjadwalan...")
    schedule, final_ranks, final_stats = run_dp_scheduler()
    print()

    print_full_schedule(schedule)
    print_all_ranks(final_ranks)
    print_summary(final_ranks)


if __name__ == "__main__":
    main()
