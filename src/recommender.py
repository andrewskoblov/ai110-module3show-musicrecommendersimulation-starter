import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Scoring mode presets
# Each mode shifts weight emphasis to favour a different matching dimension.
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre_weight": 2.0,
        "mood_weight": 1.5,
        "energy_weight": 1.0,
        "acoustic_weight": 0.5,
        "popularity_weight": 0.3,
        "decade_weight": 0.5,
        "mood_tag_weight": 1.0,
    },
    "genre-first": {
        "genre_weight": 4.0,
        "mood_weight": 0.8,
        "energy_weight": 0.5,
        "acoustic_weight": 0.2,
        "popularity_weight": 0.3,
        "decade_weight": 0.2,
        "mood_tag_weight": 0.5,
    },
    "mood-first": {
        "genre_weight": 0.8,
        "mood_weight": 3.5,
        "energy_weight": 0.8,
        "acoustic_weight": 0.3,
        "popularity_weight": 0.3,
        "decade_weight": 0.3,
        "mood_tag_weight": 1.5,
    },
    "energy-focused": {
        "genre_weight": 0.5,
        "mood_weight": 0.5,
        "energy_weight": 3.5,
        "acoustic_weight": 0.3,
        "popularity_weight": 0.2,
        "decade_weight": 0.2,
        "mood_tag_weight": 0.5,
    },
}


@dataclass
class Song:
    """Represents a song and its audio attributes loaded from the catalog."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int
    release_decade: int
    mood_tag: str


@dataclass
class UserProfile:
    """Stores a listener's taste preferences used to score songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decade: Optional[int] = None
    preferred_mood_tag: Optional[str] = None
    min_popularity: int = 0


class Recommender:
    """Scores and ranks Song objects against a UserProfile to produce recommendations."""

    def __init__(self, songs: List[Song], mode: str = "balanced"):
        """Initialize the recommender with a list of Song objects and an optional scoring mode."""
        self.songs = songs
        self.weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])

    def _score(self, user: UserProfile, song: Song) -> float:
        """Compute a numeric relevance score for one song against a user profile."""
        w = self.weights
        score = 0.0

        if song.genre == user.favorite_genre:
            score += w["genre_weight"]
        if song.mood == user.favorite_mood:
            score += w["mood_weight"]

        energy_similarity = 1.0 - abs(user.target_energy - song.energy)
        score += w["energy_weight"] * energy_similarity

        if user.likes_acoustic:
            score += w["acoustic_weight"] * song.acousticness
        else:
            score += w["acoustic_weight"] * (1.0 - song.acousticness)

        score += w["popularity_weight"] * (song.popularity / 100)

        if user.preferred_decade and song.release_decade == user.preferred_decade:
            score += w["decade_weight"]

        if user.preferred_mood_tag and song.mood_tag == user.preferred_mood_tag:
            score += w["mood_tag_weight"]

        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5, diversity: bool = False) -> List[Song]:
        """Return the top-k Song objects ranked by relevance, with optional diversity re-ranking."""
        scored = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        if not diversity:
            return scored[:k]
        return _apply_diversity_penalty(
            [(s, self._score(user, s)) for s in scored], k
        )

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why a song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({song.mood})")
        if abs(user.target_energy - song.energy) <= 0.15:
            reasons.append(f"energy ({song.energy}) is close to your target ({user.target_energy})")
        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"strong acoustic feel ({song.acousticness})")
        elif not user.likes_acoustic and song.acousticness <= 0.3:
            reasons.append(f"produced sound matches preference ({song.acousticness})")
        if user.preferred_decade and song.release_decade == user.preferred_decade:
            reasons.append(f"from your preferred era ({song.release_decade}s)")
        if user.preferred_mood_tag and song.mood_tag == user.preferred_mood_tag:
            reasons.append(f"mood tag matches ({song.mood_tag})")
        if not reasons:
            reasons.append("reasonable overall match based on your profile")
        return "Recommended because: " + "; ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Diversity penalty helper (Challenge 3)
# ---------------------------------------------------------------------------

def _apply_diversity_penalty(
    scored_songs: List[Tuple["Song | Dict", float]],
    k: int,
    genre_penalty: float = 0.7,
    artist_penalty: float = 0.6,
) -> List:
    """Re-rank candidates so the top-k list avoids repeating the same genre or artist.

    Songs whose genre or artist already appears in the accepted list have their
    effective score multiplied by a penalty factor before the next pick is made.
    """
    accepted = []
    seen_genres: Dict[str, int] = {}
    seen_artists: Dict[str, int] = {}

    # Work on a mutable copy of (song, score)
    remaining = list(scored_songs)

    while len(accepted) < k and remaining:
        # Apply penalties to remaining candidates based on already-accepted set
        penalised = []
        for song, score in remaining:
            key_genre = song.genre if hasattr(song, "genre") else song["genre"]
            key_artist = song.artist if hasattr(song, "artist") else song["artist"]
            effective = score
            if seen_genres.get(key_genre, 0) >= 1:
                effective *= genre_penalty
            if seen_artists.get(key_artist, 0) >= 1:
                effective *= artist_penalty
            penalised.append((song, score, effective))

        # Pick the candidate with the highest effective score
        penalised.sort(key=lambda x: x[2], reverse=True)
        best_song, best_score, _ = penalised[0]

        accepted.append(best_song)
        key_genre = best_song.genre if hasattr(best_song, "genre") else best_song["genre"]
        key_artist = best_song.artist if hasattr(best_song, "artist") else best_song["artist"]
        seen_genres[key_genre] = seen_genres.get(key_genre, 0) + 1
        seen_artists[key_artist] = seen_artists.get(key_artist, 0) + 1

        # Remove picked song from remaining
        remaining = [(s, sc) for s, sc in remaining if s is not best_song]

    return accepted


# ---------------------------------------------------------------------------
# Functional API used by src/main.py
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a tab-separated CSV file, converting numeric fields to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row["popularity"]),
                "release_decade": int(row["release_decade"]),
                "mood_tag": row["mood_tag"],
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    genre_weight: float = 2.0,
    mood_weight: float = 1.5,
    energy_weight: float = 1.0,
    acoustic_weight: float = 0.5,
    popularity_weight: float = 0.3,
    decade_weight: float = 0.5,
    mood_tag_weight: float = 1.0,
) -> Tuple[float, List[str]]:
    """Score one song dict against user preferences; return (score, list_of_reasons).

    Default weights (balanced mode):
      +2.0  genre match
      +1.5  mood match
      +1.0  scaled energy proximity
      +0.5  acousticness preference
      +0.3  scaled popularity bonus
      +0.5  release decade match (optional)
      +1.0  mood tag match (optional)
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight})")

    if song["mood"] == user_prefs.get("mood"):
        score += mood_weight
        reasons.append(f"mood match (+{mood_weight})")

    target_energy = user_prefs.get("energy", 0.5)
    energy_points = round(energy_weight * (1.0 - abs(target_energy - song["energy"])), 2)
    score += energy_points
    reasons.append(f"energy proximity (+{energy_points})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        acoustic_points = round(acoustic_weight * song["acousticness"], 2)
        reasons.append(f"acoustic preference (+{acoustic_points})")
    else:
        acoustic_points = round(acoustic_weight * (1.0 - song["acousticness"]), 2)
        reasons.append(f"produced-sound preference (+{acoustic_points})")
    score += acoustic_points

    pop_points = round(popularity_weight * (song["popularity"] / 100), 2)
    score += pop_points
    reasons.append(f"popularity bonus (+{pop_points})")

    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade and song["release_decade"] == preferred_decade:
        score += decade_weight
        reasons.append(f"era match: {song['release_decade']}s (+{decade_weight})")

    preferred_mood_tag = user_prefs.get("preferred_mood_tag")
    if preferred_mood_tag and song["mood_tag"] == preferred_mood_tag:
        score += mood_tag_weight
        reasons.append(f"mood tag match: {song['mood_tag']} (+{mood_tag_weight})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversity: bool = False,
) -> List[Tuple[Dict, float, List[str]]]:
    """Rank all songs using the chosen scoring mode and return the top-k results.

    Args:
        user_prefs: User taste preferences dict.
        songs: List of song dicts from load_songs.
        k: Number of results to return.
        mode: Scoring mode — 'balanced', 'genre-first', 'mood-first', 'energy-focused'.
        diversity: If True, apply a genre/artist diversity penalty to avoid repetitive results.
    """
    weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    scored = [
        (song, *score_song(user_prefs, song, **weights))
        for song in songs
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    if not diversity:
        return scored[:k]

    # Re-rank with diversity penalty
    song_score_pairs = [(s, sc) for s, sc, _ in scored]
    diverse_songs = _apply_diversity_penalty(song_score_pairs, k)

    # Re-attach reasons for the diversity-selected songs
    song_to_reasons = {id(s): r for s, _, r in scored}
    song_to_score = {id(s): sc for s, sc, _ in scored}
    return [(s, song_to_score[id(s)], song_to_reasons[id(s)]) for s in diverse_songs]
