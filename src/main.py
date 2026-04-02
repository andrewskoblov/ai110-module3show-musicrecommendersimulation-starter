"""Command line runner for the Music Recommender Simulation."""

from tabulate import tabulate
from src.recommender import load_songs, recommend_songs, SCORING_MODES


# ---------------------------------------------------------------------------
# Test profiles
# ---------------------------------------------------------------------------
PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
        "preferred_decade": 2020,
        "preferred_mood_tag": "euphoric",
    },
    "Chill Lofi Study": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
        "preferred_decade": 2020,
        "preferred_mood_tag": "serene",
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
        "preferred_decade": 2010,
        "preferred_mood_tag": "aggressive",
    },
    "Conflicted Jazz (high energy + relaxed mood)": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    "Unknown Genre: Classical": {
        "genre": "classical",
        "mood": "peaceful",
        "energy": 0.30,
        "likes_acoustic": True,
        "preferred_mood_tag": "serene",
    },
}


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(profile_name: str, user_prefs: dict, results: list, mode: str = "balanced") -> None:
    """Print a tabulate table of recommendations for one profile."""
    print(f"\n{'=' * 70}")
    print(f"  Profile : {profile_name}")
    print(f"  Mode    : {mode}")
    print(f"  Prefs   : genre={user_prefs.get('genre')} | mood={user_prefs.get('mood')} | "
          f"energy={user_prefs.get('energy')} | decade={user_prefs.get('preferred_decade', 'any')} | "
          f"tag={user_prefs.get('preferred_mood_tag', 'any')}")
    print(f"{'=' * 70}\n")

    rows = []
    for rank, (song, score, reasons) in enumerate(results, start=1):
        rows.append([
            rank,
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            song["mood_tag"],
            song["release_decade"],
            song["popularity"],
            f"{score:.2f}",
            "\n".join(f"• {r}" for r in reasons),
        ])

    headers = ["#", "Title", "Artist", "Genre / Mood", "Tag", "Era", "Pop", "Score", "Reasons"]
    print(tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=[None]*8 + [40]))
    print()


# ---------------------------------------------------------------------------
# Experiment helpers
# ---------------------------------------------------------------------------

def run_mode_comparison(songs: list) -> None:
    """Challenge 2: Compare all four scoring modes on the same Chill Lofi profile."""
    profile = PROFILES["Chill Lofi Study"]

    print(f"\n{'=' * 70}")
    print("  CHALLENGE 2: Scoring Mode Comparison — Chill Lofi Profile")
    print(f"{'=' * 70}\n")

    rows = []
    for mode in SCORING_MODES:
        results = recommend_songs(profile, songs, k=3, mode=mode)
        top3 = " / ".join(f"{s['title']} ({sc:.2f})" for s, sc, _ in results)
        rows.append([mode, top3])

    print(tabulate(rows, headers=["Mode", "Top 3 results (score)"], tablefmt="grid"))
    print()


def run_diversity_demo(songs: list) -> None:
    """Challenge 3: Show before/after diversity penalty on the High-Energy Pop profile."""
    profile = PROFILES["High-Energy Pop"]

    print(f"\n{'=' * 70}")
    print("  CHALLENGE 3: Diversity Penalty Demo — High-Energy Pop Profile")
    print(f"{'=' * 70}\n")

    no_div = recommend_songs(profile, songs, k=5, diversity=False)
    with_div = recommend_songs(profile, songs, k=5, diversity=True)

    rows = []
    for rank, ((s1, sc1, _), (s2, sc2, _)) in enumerate(zip(no_div, with_div), start=1):
        rows.append([
            rank,
            f"{s1['title']} [{s1['genre']}]",
            f"{sc1:.2f}",
            f"{s2['title']} [{s2['genre']}]",
            f"{sc2:.2f}",
        ])

    headers = ["#", "Without Diversity", "Score", "With Diversity", "Score"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print("  Diversity penalty: genre repeat x0.7, artist repeat x0.6\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Load catalog and run all profile evaluations, mode comparisons, and diversity demo."""
    songs = load_songs("data/songs.csv")

    # Phase 4 profiles — balanced mode
    for profile_name, user_prefs in PROFILES.items():
        results = recommend_songs(user_prefs, songs, k=5, mode="balanced")
        print_table(profile_name, user_prefs, results, mode="balanced")

    # Challenge 2: mode comparison
    run_mode_comparison(songs)

    # Challenge 3: diversity penalty
    run_diversity_demo(songs)


if __name__ == "__main__":
    main()
