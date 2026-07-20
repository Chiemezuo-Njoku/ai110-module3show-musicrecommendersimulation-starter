"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

Run it from the project root with:

    python -m src.main

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path
from typing import Dict, List, Tuple

from src.recommender import load_songs, recommend_songs

# Resolve the CSV relative to the project root so the script works no matter
# which directory it is launched from. main.py lives in <root>/src/, so the
# catalog is one level up in <root>/data/songs.csv.
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


# --- Evaluation profiles ---------------------------------------------------
# Each entry is (label, note, user_prefs). The note explains what the profile
# is meant to probe, so the printed output doubles as evaluation notes.

# 1) Baseline profiles: clear, self-consistent tastes the system should nail.
BASELINE_PROFILES: List[Tuple[str, str, Dict]] = [
    (
        "High-Energy Pop",
        "Coherent mainstream taste; should surface the pop/happy tracks.",
        {"genre": "pop", "mood": "happy", "energy": 0.9},
    ),
    (
        "Chill Lofi",
        "Low-energy study vibe; should favor lofi/chill, calm tracks.",
        {"genre": "lofi", "mood": "chill", "energy": 0.35},
    ),
    (
        "Deep Intense Rock",
        "High-energy aggressive taste; should surface rock/intense tracks.",
        {"genre": "rock", "mood": "intense", "energy": 0.9},
    ),
]

# 2) Adversarial profiles: designed to stress or "trick" the scoring logic.
ADVERSARIAL_PROFILES: List[Tuple[str, str, Dict]] = [
    (
        "Conflicting: high energy + sad mood",
        "No song is both high-energy AND melancholy. Tests whether energy "
        "proximity quietly overrides an impossible mood match.",
        {"genre": "pop", "mood": "melancholy", "energy": 0.95},
    ),
    (
        "Unknown genre (k-pop)",
        "Genre absent from the catalog. Genre points are impossible, so mood "
        "and energy alone should decide the ranking.",
        {"genre": "k-pop", "mood": "happy", "energy": 0.8},
    ),
    (
        "Impossible combo: angry classical",
        "Catalog's 'angry' track is metal; 'classical' is melancholy. No song "
        "can match both category fields at once.",
        {"genre": "classical", "mood": "angry", "energy": 1.0},
    ),
    (
        "Boundary energy = 0.0",
        "Extreme target at the low edge. Every song still earns some energy "
        "points; watch for near-ties among low-energy tracks.",
        {"genre": "ambient", "mood": "chill", "energy": 0.0},
    ),
    (
        "Sparse profile (energy only)",
        "Genre and mood omitted entirely. Tests the .get() guards: ranking "
        "should fall back to pure energy proximity without crashing.",
        {"energy": 0.5},
    ),
]


def print_recommendations(label: str, note: str, user_prefs: Dict, songs: List[Dict], k: int = 5) -> None:
    """Print the top-k recommendations for one profile in a copy-paste-friendly block."""
    print("=" * 60)
    print(f"  PROFILE: {label}")
    print(f"  Prefs:   {user_prefs}")
    print(f"  Probing: {note}")
    print("=" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=k)
    if not recommendations:
        print("  (no recommendations returned)\n")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} - {song['artist']} "
              f"[{song['genre']}/{song['mood']}, energy={song['energy']}]")
        print(f"   Score: {score:.2f}")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs(str(DATA_PATH))

    print("\n########## BASELINE PROFILES ##########\n")
    for label, note, prefs in BASELINE_PROFILES:
        print_recommendations(label, note, prefs, songs, k=5)

    print("\n########## ADVERSARIAL / EDGE-CASE PROFILES ##########\n")
    for label, note, prefs in ADVERSARIAL_PROFILES:
        print_recommendations(label, note, prefs, songs, k=5)


if __name__ == "__main__":
    main()
