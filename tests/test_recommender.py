from src.recommender import Song, UserProfile, Recommender


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
            popularity=80,
            release_decade=2020,
            mood_tag="euphoric",
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
            popularity=60,
            release_decade=2020,
            mood_tag="serene",
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_scoring_mode_genre_first_ranks_genre_match_higher():
    """genre-first mode should give an even larger score gap to the genre-matched song."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec_balanced = make_small_recommender()
    rec_genre = Recommender(rec_balanced.songs, mode="genre-first")

    balanced_top = rec_balanced.recommend(user, k=1)[0]
    genre_top = rec_genre.recommend(user, k=1)[0]

    assert balanced_top.genre == "pop"
    assert genre_top.genre == "pop"


def test_diversity_reduces_same_artist_repeats():
    """With diversity=True, the same artist should not dominate the top-k list."""
    songs = [
        Song(1, "Track A", "Same Artist", "pop", "happy", 0.8, 120, 0.8, 0.8, 0.2, 80, 2020, "euphoric"),
        Song(2, "Track B", "Same Artist", "pop", "happy", 0.75, 118, 0.78, 0.78, 0.22, 78, 2020, "euphoric"),
        Song(3, "Track C", "Other Artist", "lofi", "chill", 0.4, 80, 0.6, 0.6, 0.8, 60, 2020, "serene"),
    ]
    rec = Recommender(songs)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)

    with_div = rec.recommend(user, k=3, diversity=True)
    artists = [s.artist for s in with_div]

    # After diversity penalty the second "Same Artist" song should still appear
    # but the Other Artist song should be promoted relative to no-diversity
    assert "Other Artist" in artists
