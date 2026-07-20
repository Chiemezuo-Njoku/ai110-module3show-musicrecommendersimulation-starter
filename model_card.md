# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0** — a taste-based music recommender that matches songs to a listener's mood and energy.

---

## 2. Intended Use  

**Goal.** VibeMatch suggests songs from a small catalog that fit a listener's stated taste. A user
describes what they want — a favorite genre, a mood, and an energy level — and the system returns a
short, ranked list of matching songs, each with a plain-language reason.

**Who it is for.** This is a classroom simulation, built to explore how recommenders turn data into
suggestions. It assumes the user can describe their taste directly. It is not connected to real
listening history or a music service.

**What it is designed for:**

- Learning how content-based scoring and ranking work.
- Experimenting with how scoring weights change results.
- Producing transparent, explainable recommendations on a tiny catalog.

**What it should *not* be used for:**

- Real product recommendations or anything users rely on.
- Judging the quality or popularity of any artist or song.
- Any setting where the catalog's known biases (see §6) could cause harm or unfairness.

---

## 3. How the Model Works  

VibeMatch scores every song against the listener's request, then ranks them from best to worst match.

Each song earns points on three things:

- **Genre** — if the song's genre matches the listener's favorite, it earns the most points (the
  strongest signal of taste).
- **Mood** — if the song's mood matches, it earns a moderate number of points.
- **Energy** — the song earns points based on how close its energy level is to what the listener
  wants. A perfect match earns full points; the further apart, the fewer points.

The points are added into one total score. The songs with the highest totals rise to the top of the
list. Because the score is just a sum, the system can explain each pick line by line — "matched your
genre," "close to your energy," and so on. We kept genre weighted twice as heavily as mood and
energy, so genre has the biggest say in the results.

---

## 4. Data  

The catalog is a single file of **20 songs**. Each song has 10 fields: a title and artist, two
category tags (**genre** and **mood**), and six numeric "vibe" measures on a 0–1 scale (**energy**,
**valence**, **danceability**, **acousticness**, plus tempo in BPM).

The dataset covers **17 genres** and **16 moods**, but the coverage is uneven: lofi (3 songs) and pop
(2 songs) appear more than once, while every other genre has only a single song. Energy also skews
high — no song is very quiet (the lowest energy is 0.28). We used the starter catalog as provided.
Large parts of real musical taste are missing: there is no play history, no lyrics, no listening
context (time of day, activity), and only one example of most genres.

---

## 5. Strengths  

- **Clear, mainstream tastes work well.** For coherent profiles (e.g. happy pop or chill lofi), the
  ideal song reliably lands at or near the top score.
- **Every pick is explainable.** The system shows exactly why each song was chosen, which made
  testing and debugging easy.
- **Behavior matched intuition on the energy axis.** Low-energy profiles returned calm songs and
  high-energy profiles returned energetic ones, as expected.
- **It fails gracefully.** Unknown genres or partial profiles do not crash the system; it simply
  falls back to the signals it does have.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

**Profiles tested.** We evaluated the recommender against three coherent "baseline"
profiles — **High-Energy Pop** (pop / happy / energy 0.9), **Chill Lofi**
(lofi / chill / energy 0.35), and **Deep Intense Rock** (rock / intense / energy 0.9) —
plus five adversarial profiles designed to stress the scoring logic, including a
self-contradictory "high energy but melancholy mood" user, an unknown genre (k-pop)
absent from the catalog, an "angry classical" combination no song can satisfy, and a
sparse profile specifying energy only. For the baseline profiles the system behaved as
intended: each put the ideal song at or near the maximum score of 4.0 (Chill Lofi
returned *Library Rain* at an exact 4.00; Deep Intense Rock returned *Storm Runner* at
3.99).

**Surprising results.** Two findings stood out. First, the contradictory "high energy +
sad mood" profile did **not** surface the catalog's one genuinely sad song near the top —
*Moonlight Sonatina* fell to third place because its low energy was penalized more
heavily than the correct mood match rewarded it, so the user asking for "sad" was served
upbeat pop instead. Second, a small group of high-energy songs (*Gym Hero*, *Neon Pulse*,
*Storm Runner*) reappeared across every high-energy list, revealing that once genre and
mood are exhausted, the ranking collapses toward whichever songs simply sit closest on the
energy scale.

**Comparative analysis.**

- **High-Energy Pop vs. Chill Lofi** — The pop profile gravitated toward bright, upbeat,
  high-energy tracks (*Sunrise City*, *Gym Hero*), while the lofi profile shifted entirely
  toward calm, low-energy study music (*Library Rain*, *Midnight Coding*). The lists share
  almost no songs, which makes sense: the two profiles sit at opposite ends of both the
  genre space and the energy scale, so nearly every scoring signal pushes them apart.
- **High-Energy Pop vs. Deep Intense Rock** — Both are high-energy profiles, so they
  *overlapped* in their lower ranks (*Gym Hero*, *Storm Runner*, *Neon Pulse* appear for
  both) even though their top slots differed by genre. This is expected — they agree on the
  energy axis and disagree only on genre and mood, so the energy component draws the same
  pool of energetic songs into both lists.
- **Chill Lofi vs. Deep Intense Rock** — The starkest contrast: the lofi profile favored
  quiet, acoustic-leaning tracks around 0.35 energy, whereas the rock profile favored
  aggressive tracks near 0.9 energy. The two lists are essentially mirror images, which is
  exactly what we'd want from a system that treats energy as a core "vibe" axis.

**Why the same song keeps appearing (plain-language explanation).**

> **Why does "Gym Hero" keep showing up for people who like Happy Pop?**
>
> Think of the recommender as a matchmaker that scores every song on three things: whether
> it's the *style* of music you asked for, whether it has the *feeling* you asked for, and
> whether it has the right *energy level* — calm, moderate, or high.
>
> When someone asks for happy pop with high energy, "Gym Hero" scores well on two of those
> three. It's tagged as **pop**, which is exactly the style they wanted, and it's a
> **high-energy** track, which matches the energetic vibe they're after. The only box it
> *doesn't* tick is the mood: it's labeled "intense" rather than "happy." But because it
> wins on style and energy — two out of three — it still earns a high overall score and
> lands near the top of the list.
>
> In short, "Gym Hero" keeps appearing not because it's a perfect match, but because it
> shares the most important tags with what these listeners asked for. It's the equivalent
> of a friend recommending a song by saying, "It's not quite the mood you described, but
> it's the right genre and it's got the energy you love." That's usually a reasonable pick —
> but it also shows how a song can rise to the top by matching the *labels* a listener cares
> about most, even when the overall feel isn't a bullseye.

---

## 8. Future Work  

If development continued, three improvements would matter most:

1. **Balance the catalog.** Adding more songs, with even coverage across genres and a wider energy
   range, would fix the biggest source of unfair results (see §6).
2. **Score more features.** The data already includes acousticness, valence, and danceability. Using
   them would give the system more ways to tell songs apart and reduce repetitive results.
3. **Add variety controls.** A simple rule at ranking time — such as limiting how many songs by one
   artist or in one mood can appear — would make the top list feel less repetitive.

A further step would be handling more complex tastes, such as "energetic but not aggressive," which
the current single-mood, single-genre input cannot express.

---

## 9. Personal Reflection  

*(Draft — edit this into your own words.)*

Building VibeMatch showed me that a recommender is really just a scoring rule applied over and over.
The interesting part was not the code but the weights: small choices about what "counts" most quietly
decided which songs users saw. The most surprising moment was watching a request for "sad" music
return upbeat pop, because the energy score outweighed the mood match. It made me realize how easily
a system can look neutral while carrying strong hidden preferences — and how much the data itself, not
just the algorithm, shapes what people are shown.
