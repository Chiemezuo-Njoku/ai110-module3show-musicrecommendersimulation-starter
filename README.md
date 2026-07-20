# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommendation systems work by balancing two forces: **user preference** (what a
listener says or behaves like they want) and **item features** (the measurable characteristics of
the content itself). A content-based recommender bridges the two by representing each item as a set
of attributes, representing the user as a target set of those same attributes, and then scoring how
closely each item matches that target — the smaller the distance between a song and the user's
ideal, the higher its score. This simulation implements exactly that idea on a small song catalog.
For every song, it computes a **weighted match score** that combines two kinds of comparison: an
*exact-match* check on categorical fields (genre, mood) and a *proximity* check on numeric fields,
where a song is rewarded for having values **close to** the user's target rather than simply high or
low (measured with an inverted absolute difference). Each criterion is normalized to a 0–1 sub-score
and combined with tunable weights that encode relative importance, so the priorities are explicit
and adjustable. The system then separates **scoring** (judging one song in isolation) from
**ranking** (sorting all scored songs and selecting the top *k*), which keeps the matching logic
easy to test and the selection policy easy to change. Rather than optimizing for popularity or
diversity, this simulation deliberately prioritizes **transparent, feature-based preference
matching**: it favors accuracy of fit to the stated taste profile and produces a plain-language
explanation for each recommendation, so a reader can always see *why* a song was chosen.

### Algorithm Recipe

Each song is scored **in isolation** as the sum of three weighted sub-scores. Every sub-score is
normalized to the 0.0–1.0 range and multiplied by a weight that encodes its relative importance:

```
final_score = (2.0 × genre_match)        # categorical: 1.0 if song.genre == user.favorite_genre, else 0.0
            + (1.0 × mood_match)          # categorical: 1.0 if song.mood  == user.favorite_mood,  else 0.0
            + (1.0 × energy_similarity)   # proximity:   1.0 − abs(song.energy − user.target_energy)
```

| Criterion | Type | Rule | Weight | Max contribution |
|-----------|------|------|--------|------------------|
| Genre | Exact match | `1.0` if genres are equal, else `0.0` | 2.0 | **2.0** |
| Mood | Exact match | `1.0` if moods are equal, else `0.0` | 1.0 | **1.0** |
| Energy | Proximity | `1.0 − abs(song.energy − target_energy)` | 1.0 | **1.0** |

**Why proximity, not magnitude, for energy:** the system rewards a song whose energy is *closest to*
the user's `target_energy`, not simply the highest-energy song. Because `energy` and `target_energy`
both live on the same 0–1 scale, their absolute difference is already normalized (maximum possible
distance is 1.0), so `1.0 − distance` yields a clean 0–1 similarity with no further scaling required.

**Weight rationale:** the weights establish an explicit priority order of **genre > mood ≈ energy**.
Genre is weighted twice as heavily as mood because it is treated as the strongest signal of taste;
mood and energy are weighted equally so that a strong "vibe" fit can compensate for a mismatched
mood, but never override a genre mismatch. The theoretical maximum score is **4.0**, which allows
each result to be reported as a percentage match (`score / 4.0`) in its explanation. Because the
score is additive, every component contributes one line to a per-song, plain-language reason list,
so each recommendation explains itself criterion by criterion.

**Reserved for extension:** the data model also pairs `likes_acoustic` ↔ `acousticness`, but the
current recipe intentionally scores only genre, mood, and energy. `acousticness` (along with the
optional `tempo_bpm`, `valence`, and `danceability` axes) is left unscored for now so the initial
logic stays simple and easy to reason about; it can be folded in as an additional weighted sub-score
without changing the data schema.

### Bias Analysis

Because the weights are fixed and explicit, the system's biases are predictable — and worth stating
plainly:

- **Genre dominance.** Weighting genre at 2.0 means the algorithm can systematically overlook songs
  that are a *perfect* match on mood and energy but sit in a different genre. A user who loves
  "chill, low-energy" music could miss an ideal lofi track simply because it is tagged `ambient`
  instead of their stated favorite genre. The heaviest weight silently defines what "counts" as a
  good recommendation.
- **The tyranny of exact-match categories.** Genre and mood are all-or-nothing: `indie pop` earns
  zero genre credit against a `pop` preference despite being musically adjacent. The system has no
  notion of *similar* categories, so it inherits and amplifies whatever labeling choices were made
  when the catalog was tagged.
- **Continuous vs. binary accumulation.** Every song earns *some* energy points, while genre and mood
  award points only on an exact hit. Across a large catalog, small energy near-misses can accumulate
  on songs that match no category at all — a subtle bias toward "average energy" tracks.
- **Catalog and label bias.** The recommender can only surface what exists in `songs.csv`, tagged the
  way it was tagged. Any imbalance in the catalog (e.g., few classical or metal entries) or any
  subjectivity in the `mood` labels is passed directly through to the user as if it were neutral.

The takeaway for tuning: **the weights are a value judgment, not a neutral default.** Raising or
lowering `genre_weight` does not just change scores — it changes *whose* songs get seen. This is the
same dynamic that drives filter bubbles in production recommenders, reproduced here at small scale.

---

## Data Modeling

The scoring rule can only compare a `Song` against a `UserProfile` on attributes they **share**, so
the two objects are designed as mirror images: every user preference must line up with a song
feature it can be scored against.

### `Song` attributes

| Attribute | Type | Why it's necessary |
|-----------|------|--------------------|
| `id` | int | Stable identifier for tie-breaking and de-duplication during ranking. |
| `title` | str | Human-readable label for output and explanations (not scored). |
| `artist` | str | Enables diversity control (e.g., avoid recommending one artist repeatedly); not scored directly. |
| `genre` | str | **Categorical match** against `favorite_genre` — contributes a 1.0/0.0 sub-score. |
| `mood` | str | **Categorical match** against `favorite_mood` — contributes a 1.0/0.0 sub-score. |
| `energy` | float (0–1) | **Numeric proximity** to `target_energy` via inverted absolute difference; the core "vibe" axis. |
| `acousticness` | float (0–1) | Compared against the user's `likes_acoustic` flag; strong discriminator between produced and organic tracks. |
| `tempo_bpm` | float | Optional numeric axis; **must be normalized to 0–1** before use so it doesn't dominate the distance. |
| `valence` | float (0–1) | Optional numeric axis (musical positivity); pairs with `energy` to capture emotional tone. |
| `danceability` | float (0–1) | Optional numeric axis for a richer multi-feature match. |

### `UserProfile` attributes

| Attribute | Type | Why it's necessary |
|-----------|------|--------------------|
| `favorite_genre` | str | The target for the categorical genre match. |
| `favorite_mood` | str | The target for the categorical mood match. |
| `target_energy` | float (0–1) | The reference point for the numeric proximity score — the system rewards songs whose `energy` is *closest* to this value. |
| `likes_acoustic` | bool | A preference flag compared against each song's `acousticness` to reward (or avoid) acoustic tracks. |

**Why this pairing matters:** each user field exists specifically because there is a song feature it
can be scored against. `favorite_genre` ↔ `genre` and `favorite_mood` ↔ `mood` drive the
exact-match sub-scores; `target_energy` ↔ `energy` and `likes_acoustic` ↔ `acousticness` drive the
proximity sub-scores. Fields like `title`, `artist`, and `id` carry no preference target — they
support output, explanation, and ranking (tie-breaks, diversity) rather than scoring. The optional
numeric features (`tempo_bpm`, `valence`, `danceability`) are included in the `Song` model so the
scoring rule can be extended into a fuller multi-dimensional "vibe vector" later without changing the
data schema.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Running `python -m src.main` with the example profile
(`genre=pop, mood=happy, energy=0.8`) produces the following ranked output. Each
recommendation lists its total score and the specific reasons that produced it:

```text
====================================================
  TOP RECOMMENDATIONS
  For: genre=pop, mood=happy, energy=0.8
====================================================

1. Sunrise City - Neon Echo
   Score: 3.98
   Reasons:
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy similarity: 0.98 (target 0.80, song 0.82) (+0.98)

2. Gym Hero - Max Pulse
   Score: 2.87
   Reasons:
     - genre match: pop (+2.0)
     - energy similarity: 0.87 (target 0.80, song 0.93) (+0.87)

3. Rooftop Lights - Indigo Parade
   Score: 1.96
   Reasons:
     - mood match: happy (+1.0)
     - energy similarity: 0.96 (target 0.80, song 0.76) (+0.96)

4. Basement Groove - Funk Theory
   Score: 1.00
   Reasons:
     - energy similarity: 1.00 (target 0.80, song 0.80) (+1.00)

5. Concrete Bars - MC Grid
   Score: 0.98
   Reasons:
     - energy similarity: 0.98 (target 0.80, song 0.78) (+0.98)
```

**Reading the results:** *Sunrise City* scores near the 4.0 maximum by matching all
three criteria. Notice that *Gym Hero* (rank 2) outranks *Rooftop Lights* (rank 3)
despite *Rooftop Lights* being a perfect **mood** match with near-perfect energy —
because the genre weight (2.0) outweighs the mood weight (1.0). This is the
genre-dominance bias described in *How The System Works* visible in practice.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



