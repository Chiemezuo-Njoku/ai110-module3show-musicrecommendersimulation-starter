import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the song catalog this recommender will rank against."""
        self.songs = songs

    @staticmethod
    def _to_prefs(user: UserProfile) -> Dict:
        """Adapt a UserProfile dataclass to the dict shape score_song expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

    @staticmethod
    def _to_song_dict(song: Song) -> Dict:
        """Adapt a Song dataclass to the dict shape score_song expects."""
        return {"genre": song.genre, "mood": song.mood, "energy": song.energy}

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Score every song against the user profile and return the top-k Song
        objects, sorted from highest to lowest score. Reuses the same
        score_song recipe as the functional path so the weights stay in sync.
        """
        prefs = self._to_prefs(user)
        scored = [
            (song, score_song(prefs, self._to_song_dict(song))[0])
            for song in self.songs
        ]
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)
        return [song for song, _score in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why a song was recommended."""
        prefs = self._to_prefs(user)
        score, reasons = score_song(prefs, self._to_song_dict(song))
        if not reasons:
            return f"{song.title} scored {score:.2f} with no matching criteria."
        return f"{song.title} scored {score:.2f}: " + "; ".join(reasons)

# Column name -> conversion function. Any column not listed stays a string.
INT_FIELDS = ("id", "tempo_bpm")
FLOAT_FIELDS = ("energy", "valence", "danceability", "acousticness")


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dictionaries.

    Numeric columns are explicitly converted from strings to their proper
    types (int or float) so downstream scoring can do math on them:
      - int:   id, tempo_bpm
      - float: energy, valence, danceability, acousticness
    Any other column (title, artist, genre, mood) is kept as a string.

    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song: Dict = dict(row)
            for field in INT_FIELDS:
                if song.get(field) not in (None, ""):
                    song[field] = int(song[field])
            for field in FLOAT_FIELDS:
                if song.get(field) not in (None, ""):
                    song[field] = float(song[field])
            songs.append(song)
    return songs

# Scoring weights (see README "Algorithm Recipe"). Tunable in one place.
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences, in isolation.

    Recipe (each sub-score is 0.0-1.0, then multiplied by its weight):
      - genre match:      +2.0 if song["genre"] == user_prefs["genre"]
      - mood match:       +1.0 if song["mood"]  == user_prefs["mood"]
      - energy proximity: (1.0 - abs(song["energy"] - user_prefs["energy"])) * 1.0

    Returns (total_score, reasons) where reasons is a list of human-readable
    strings explaining each point contribution.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    # 1) Genre: exact categorical match.
    if user_prefs.get("genre") is not None and song.get("genre") == user_prefs["genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.1f})")

    # 2) Mood: exact categorical match.
    if user_prefs.get("mood") is not None and song.get("mood") == user_prefs["mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.1f})")

    # 3) Energy: proximity via inverted absolute difference (both on a 0-1 scale).
    target_energy = user_prefs.get("energy")
    song_energy = song.get("energy")
    if target_energy is not None and song_energy is not None:
        similarity = 1.0 - abs(song_energy - target_energy)
        energy_points = ENERGY_WEIGHT * similarity
        score += energy_points
        reasons.append(
            f"energy similarity: {similarity:.2f} "
            f"(target {target_energy:.2f}, song {song_energy:.2f}) (+{energy_points:.2f})"
        )

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song against the user's preferences, then returns the top-k
    as (song, score, explanation) tuples sorted from highest to lowest score.

    Scoring (per-song) and ranking (comparative) are kept as separate steps.
    Required by src/main.py
    """
    # 1) SCORE: judge each song in isolation. One tuple per song.
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no matching criteria"
        scored.append((song, score, explanation))

    # 2) RANK: sort by score, highest first. sorted() returns a NEW list and
    #    leaves the input `songs` list untouched. item[1] is the score.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    # 3) SELECT: slice off the top k.
    return ranked[:k]
