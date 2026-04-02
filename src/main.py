"""Command line runner for the Music Recommender Simulation."""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    """Load the song catalog, score every track against the user profile, and print the top results."""
    songs = load_songs("data/songs.csv")

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    print(f"\nUser profile: genre={user_prefs['genre']} | mood={user_prefs['mood']} "
          f"| energy={user_prefs['energy']} | likes_acoustic={user_prefs['likes_acoustic']}")
    print("=" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop 5 Recommendations\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"  {rank}. {song['title']}  —  {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"     Score: {score:.2f}")
        for reason in reasons:
            print(f"       • {reason}")
        print()


if __name__ == "__main__":
    main()
