import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


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


@dataclass
class UserProfile:
    """Stores a listener's taste preferences used to score songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Scores and ranks Song objects against a UserProfile to produce recommendations."""

    GENRE_WEIGHT = 2.0
    MOOD_WEIGHT = 1.5
    ENERGY_WEIGHT = 1.0
    ACOUSTIC_WEIGHT = 0.5

    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a list of Song objects."""
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Compute a numeric relevance score for one song against a user profile."""
        score = 0.0

        if song.genre == user.favorite_genre:
            score += self.GENRE_WEIGHT

        if song.mood == user.favorite_mood:
            score += self.MOOD_WEIGHT

        energy_similarity = 1.0 - abs(user.target_energy - song.energy)
        score += self.ENERGY_WEIGHT * energy_similarity

        if user.likes_acoustic:
            score += self.ACOUSTIC_WEIGHT * song.acousticness
        else:
            score += self.ACOUSTIC_WEIGHT * (1.0 - song.acousticness)

        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by relevance score for the given user."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why a song was recommended."""
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")

        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({song.mood})")

        if abs(user.target_energy - song.energy) <= 0.15:
            reasons.append(
                f"energy level ({song.energy}) is close to your target ({user.target_energy})"
            )

        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"has a strong acoustic feel ({song.acousticness})")
        elif not user.likes_acoustic and song.acousticness <= 0.3:
            reasons.append(f"has a non-acoustic, produced sound ({song.acousticness})")

        if not reasons:
            reasons.append("reasonable overall match based on your profile")

        return "Recommended because: " + "; ".join(reasons) + "."


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
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dict against user preferences; return (score, list_of_reasons).

    Scoring weights:
      +2.0  genre match
      +1.5  mood match
      +1.0  scaled by energy proximity  (1 - |target - song_energy|)
      +0.5  scaled by acousticness preference
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song["mood"] == user_prefs.get("mood"):
        score += 1.5
        reasons.append("mood match (+1.5)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_points = round(1.0 * (1.0 - abs(target_energy - song["energy"])), 2)
    score += energy_points
    reasons.append(f"energy proximity (+{energy_points})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        acoustic_points = round(0.5 * song["acousticness"], 2)
        reasons.append(f"acoustic preference (+{acoustic_points})")
    else:
        acoustic_points = round(0.5 * (1.0 - song["acousticness"]), 2)
        reasons.append(f"produced-sound preference (+{acoustic_points})")
    score += acoustic_points

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Rank all songs by score and return the top-k as (song_dict, score, reasons) tuples."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
