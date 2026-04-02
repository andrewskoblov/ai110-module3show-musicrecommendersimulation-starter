# 🎧 Model Card — Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from a 20-song catalog based on a user's preferred genre, mood, energy level, and acoustic taste. It is built for classroom exploration of how content-based recommendation systems work. It is not intended for real users or production use.

---

## 3. How It Works (Short Explanation)

Each song in the catalog has a set of attributes: its genre, mood, a number representing how energetic it is, and a number representing how acoustic (vs. produced) it sounds. The user provides their preferences — favorite genre, favorite mood, a target energy level, and whether they like acoustic sounds.

For each song, the system adds up points:
- A genre match adds the most points (2.0).
- A mood match adds slightly fewer points (1.5).
- Energy proximity adds up to 1 point — the closer the song's energy is to the user's target, the more it earns.
- Acousticness adds a small bonus depending on whether the user likes acoustic sounds or not.

All songs are ranked by their total score, and the top results are returned with a short explanation of why each one was chosen.

---

## 4. Data

- The catalog contains **20 songs** from `data/songs.csv`.
- 10 songs were added to the starter dataset to improve genre diversity.
- Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, R&B, country, latin, electronic, folk, reggae, metal, j-pop.
- Moods represented: happy, chill, intense, relaxed, moody, focused, melancholy, peaceful.
- The dataset still reflects a mostly Western, English-language taste profile. Most genres appear only once or twice, meaning any genre-matched user has very few real options.

---

## 5. Strengths

- For users who clearly prefer a specific genre and mood (e.g., "pop + happy"), the top result is immediately intuitive and well-matched.
- The energy proximity score means the system avoids extremes — it doesn't blindly favor the loudest or quietest track, just the one closest to the user's stated preference.
- The scoring logic is fully transparent: every point can be traced back to a specific attribute match, making explanations easy to generate.
- Simple enough to reason about without a machine learning background.
- Weights are parameterized, making it easy to experiment without changing the core logic.

---

## 6. Limitations and Bias

**Genre dominance is the system's biggest flaw.** When a user has a genre preference, genre match alone (2.0 points) accounts for ~40% of the maximum possible score. This means a song that perfectly matches genre and mood but has completely wrong energy can outscore a song that perfectly matches energy and mood in a different genre. In the "Conflicted Jazz" profile test (genre=jazz, energy=0.9), Coffee Shop Stories ranked #1 with a score of 4.02 — even though its energy (0.37) was 0.53 away from the user's target of 0.90. The genre+mood combination simply overrode the energy signal.

**Additional limitations discovered through testing:**
- **Exact-match genre scoring** means "indie pop" and "pop" are treated as unrelated, which fails users with broad tastes.
- **Unknown genre cold-start problem.** When the user's favorite genre is not in the catalog (tested with "classical"), the maximum achievable score drops from 5.0 to 3.0. The system still returns results, but they are driven entirely by mood and energy — the user gets folk and ambient music instead of the classical they want. This is not disclosed to the user.
- **Acousticness is a binary flag.** A user who likes "a little acoustic texture" gets the same score as someone who only listens to solo guitar.
- **No listening history.** Every session starts from scratch. The system cannot learn or adapt.
- **Single-song genres** — most genres appear once in the 20-song catalog. Any user with a niche genre preference effectively gets one guaranteed result and four fallback results.

---

## 7. Evaluation

Five user profiles were tested, including two adversarial edge cases:

| Profile | Top result | Score | Intuitive? |
|---|---|---|---|
| pop, happy, energy=0.85, not acoustic | Sunrise City [pop/happy] | 4.88 | Yes |
| lofi, chill, energy=0.38, acoustic | Library Rain [lofi/chill] | 4.90 | Yes |
| rock, intense, energy=0.92, not acoustic | Storm Runner [rock/intense] | 4.94 | Yes |
| jazz, relaxed, energy=0.90 (conflicting) | Coffee Shop Stories [jazz/relaxed] | 4.02 | Partially — genre+mood won but energy was ignored |
| classical, peaceful, energy=0.30 (unknown genre) | Mountain Echo [folk/peaceful] | 2.96 | Reasonable fallback, but not what the user asked for |

**Weight-shift experiment:** Running the "Conflicted Jazz" profile with `genre_weight=1.0, energy_weight=2.0` changed the #2 result from Quarter Past Blue (jazz/moody, low energy) to Golden Hour Drift (r&b/relaxed, medium energy). The #1 result stayed the same because Coffee Shop Stories still earned genre+mood points. The experiment confirmed that genre is the dominant driver and that doubling energy weight can shift secondary results toward more energy-appropriate songs, but genre will keep "winning" as long as there is a match in the catalog.

The automated tests (`pytest`) confirm the pop/happy profile ranks the pop song above the lofi song, and that explanations are non-empty strings.

---

## 8. Future Work

- **Fuzzy genre matching** — treat "indie pop" and "pop" as partially overlapping rather than completely separate, using a similarity table or genre embeddings.
- **Include tempo and valence** — these features are in the dataset but unused; they would add nuance to what "energetic" actually means (a fast jazz track vs. a fast metal track feel very different).
- **Diversity injection** — force the top-5 list to include at least two different genres so users aren't shown five nearly identical tracks.
- **Cold-start warning** — if the user's genre is not in the catalog, inform them that genre matching is unavailable rather than silently returning fallback results.
- **Implicit feedback loop** — track which recommendations the user skips or replays to update their profile over time.
- **Larger catalog** — 20 songs is not enough for meaningful recommendations; a real test would need hundreds of entries across more genres and cultures.

---

## 9. Personal Reflection

Building VibeFinder made it clear that a recommender is really just a structured way of measuring distance between a user's stated preferences and a song's attributes. The math is simple — addition and subtraction — but the choices about what to weight heavily and what to ignore have a huge impact on who the system serves well and who it leaves behind.

The most surprising discovery came from the "Conflicted Jazz" profile — a user who wants jazz but at high energy (0.90). The system recommended Coffee Shop Stories, a slow jazz track at energy 0.37, as the #1 result. The genre and mood match completely overrode the energy mismatch. That's not how a real listener would experience it: they'd immediately skip a slow coffee shop track when they wanted something intense. The system looked correct on paper (it matched two out of four criteria) but would have felt totally wrong in practice.

This changed how I think about real music apps. Spotify or YouTube probably have much better energy-aware models, but they still create filter bubbles — if you mostly listen to one genre, the algorithm keeps feeding you that genre and you never discover what else you might love. Human curation still matters because humans can make surprising, cross-genre recommendations that a score-based system would never generate.
