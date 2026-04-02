# 🎧 Model Card — Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from a small 10-song catalog based on a user's preferred genre, mood, energy level, and acoustic taste. It is built for classroom exploration of how content-based recommendation systems work. It is not intended for real users or production use.

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

- The catalog contains **10 songs** from `data/songs.csv`.
- No songs were added or removed from the starter dataset.
- Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop.
- Moods represented: happy, chill, intense, relaxed, moody, focused.
- The dataset reflects a Western, English-language taste profile skewed toward electronic and indie music. No classical, hip-hop, R&B, country, or non-English music is present.

---

## 5. Strengths

- For users who clearly prefer a specific genre and mood (e.g., "pop + happy"), the top result is immediately intuitive and well-matched.
- The energy proximity score means the system avoids extremes — it doesn't blindly favor the loudest or quietest track, just the one closest to the user's stated preference.
- The scoring logic is fully transparent: every point can be traced back to a specific attribute match, making explanations easy to generate.
- Simple enough to reason about without a machine learning background.

---

## 6. Limitations and Bias

- **Exact genre and mood matching** means "indie pop" and "pop" are treated as completely unrelated, even though a pop fan might enjoy indie pop songs.
- **Small catalog** means a user whose favorite genre appears only once (e.g., synthwave) will always get that one song ranked first regardless of other attributes.
- **Genre and mood dominate the score.** A song that matches both genre and mood but has the wrong energy will often beat a song with perfect energy but no genre match. This may not reflect how people actually experience music.
- **No listening history.** Every user session starts from scratch. The system cannot learn or adapt.
- **Western genre bias.** The catalog has no representation of hip-hop, R&B, country, classical, or any non-English musical tradition. Users whose taste falls outside this set receive poor recommendations.
- **Acousticness binary.** The `likes_acoustic` preference is a true/false flag, which flattens a nuanced preference into two buckets.

---

## 7. Evaluation

Three user profiles were tested manually:

| Profile | Expected top result | Actual top result | Match? |
|---|---|---|---|
| pop, happy, energy=0.8, not acoustic | Sunrise City (pop/happy/0.82) | Sunrise City | Yes |
| lofi, chill, energy=0.4, acoustic | Library Rain (lofi/chill/0.35) | Library Rain | Yes |
| rock, intense, energy=0.9, not acoustic | Storm Runner (rock/intense/0.91) | Storm Runner | Yes |

All three profiles returned an intuitive first recommendation. The automated tests (`pytest`) also confirm that the pop/happy profile ranks the pop song above the lofi song, and that explanations are non-empty strings.

---

## 8. Future Work

- **Fuzzy genre matching** — treat "indie pop" and "pop" as partially overlapping rather than entirely separate categories.
- **Include tempo and valence** — these features are in the dataset but unused; they could improve energy-feel matching.
- **Diversity injection** — force the top-5 list to include at least two different genres so users aren't shown five nearly identical tracks.
- **Implicit feedback loop** — track which recommendations the user skips or replays to update their profile over time.
- **Larger catalog** — 10 songs is too few for meaningful recommendations; a real test would need hundreds of entries across more genres and cultures.

---

## 9. Personal Reflection

Building VibeFinder made it clear that a recommender is really just a structured way of measuring distance between a user's stated preferences and a song's attributes. The math itself is simple — addition and subtraction — but the choices about what to weight heavily and what to ignore have a huge impact on who the system serves well and who it leaves behind.

The most surprising discovery was how quickly genre dominance kicked in with a small catalog. A user whose favorite genre had only one or two songs in the dataset would get those songs recommended no matter what, even if the energy or mood was wrong. At scale, this could create "filter bubbles" where users are never exposed to music outside the genres already well-represented in the platform's catalog. Human judgment still matters here — someone needs to decide what goes into the catalog in the first place, and that curatorial decision shapes every recommendation the model will ever make.
