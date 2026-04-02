"""Command line runner for the Music Recommender Simulation."""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi Study": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
    # Edge case: high energy but wants a relaxed mood — conflicting signals
    "Conflicted (high energy + relaxed mood)": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    # Edge case: genre not in catalog at all
    "Unknown Genre (classical)": {
        "genre": "classical",
        "mood": "peaceful",
        "energy": 0.30,
        "likes_acoustic": True,
    },
}


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    """Print top-5 recommendations for one profile in a readable format."""
    print(f"\n{'=' * 60}")
    print(f"  Profile: {profile_name}")
    print(f"  genre={user_prefs['genre']} | mood={user_prefs['mood']} | "
          f"energy={user_prefs['energy']} | likes_acoustic={user_prefs['likes_acoustic']}")
    print(f"{'=' * 60}")

    results = recommend_songs(user_prefs, songs, k=5)
    for rank, (song, score, reasons) in enumerate(results, start=1):
        print(f"  {rank}. {song['title']}  —  {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"     Score: {score:.2f}")
        for reason in reasons:
            print(f"       • {reason}")
        print()


def run_experiment(songs: list) -> None:
    """Weight-shift experiment: compare default weights vs. energy-heavy weights."""
    profile = {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.90,
        "likes_acoustic": False,
    }

    print("\n" + "=" * 60)
    print("  EXPERIMENT: Weight Shift on 'Conflicted' Jazz Profile")
    print("  Default weights  ->  genre=2.0, mood=1.5, energy=1.0")
    print("  Shifted weights  ->  genre=1.0, mood=1.5, energy=2.0")
    print("=" * 60)

    print("\n  [Default weights]")
    default_results = recommend_songs(profile, songs, k=3)
    for rank, (song, score, reasons) in enumerate(default_results, start=1):
        print(f"    {rank}. {song['title']}  [{song['genre']} / {song['mood']}]  Score: {score:.2f}")

    print("\n  [Energy-heavy weights: genre=1.0, energy=2.0]")
    shifted_results = recommend_songs(profile, songs, k=3, genre_weight=1.0, energy_weight=2.0)
    for rank, (song, score, reasons) in enumerate(shifted_results, start=1):
        print(f"    {rank}. {song['title']}  [{song['genre']} / {song['mood']}]  Score: {score:.2f}")

    print()
    print("  Finding: with default weights, genre dominates — Coffee Shop Stories")
    print("  ranks #1 despite an energy mismatch of 0.53. Shifting energy weight")
    print("  to 2.0 promotes high-energy tracks like Storm Runner and Burning Canvas")
    print("  instead, exposing the genre bias baked into the default configuration.")
    print()


def main() -> None:
    """Load catalog, run recommendations for all test profiles, and run weight experiment."""
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs)

    run_experiment(songs)


if __name__ == "__main__":
    main()
