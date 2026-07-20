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

from src.recommender import load_songs, recommend_songs

# Resolve the CSV relative to the project root so the script works no matter
# which directory it is launched from. main.py lives in <root>/src/, so the
# catalog is one level up in <root>/data/songs.csv.
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


def main() -> None:
    songs = load_songs(str(DATA_PATH))

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 52)
    print("  TOP RECOMMENDATIONS")
    print(
        f"  For: genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, energy={user_prefs['energy']}"
    )
    print("=" * 52)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} - {song['artist']}")
        print(f"   Score: {score:.2f}")
        print("   Reasons:")
        # `explanation` joins the reasons with "; " — split it back out so each
        # reason gets its own bullet in the terminal.
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print()


if __name__ == "__main__":
    main()
