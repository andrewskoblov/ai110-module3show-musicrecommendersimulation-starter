# Model Card — VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder 1.0 takes a listener's preferences — their favorite genre, mood, target energy level, acoustic taste, preferred era, and a specific mood tag — and returns the top 5 most relevant songs from a 20-song catalog. The goal is to simulate how a real content-based music recommendation engine decides what to play next.

---

## 3. Data Used

- **Catalog size:** 20 songs in `data/songs.csv`
- **Features used per song:** genre, mood, energy (0–1), acousticness (0–1), popularity (0–100), release decade, and a detailed mood tag (e.g., "euphoric", "serene", "aggressive")
- **Genre coverage:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, R&B, country, latin, electronic, folk, reggae, metal, j-pop — 16 genres total
- **Mood tag coverage:** euphoric, serene, aggressive, uplifting, nostalgic, focused, melancholic
- **Limits:** Most genres appear only once or twice. The catalog is mostly English-language and Western. No classical, Afrobeats, or K-pop (beyond j-pop). Songs were created for this classroom exercise, not sourced from real streaming data.

---

## 4. Algorithm Summary

For every song in the catalog, the system adds up points based on how well the song matches the user:

- **Genre match** earns the most points (default: 2.0). If the user likes jazz and the song is jazz, it gets the full bonus.
- **Mood match** earns a slightly smaller bonus (default: 1.5). "Happy" matches "happy."
- **Energy proximity** earns up to 1.0 points. A song with energy 0.82 earns nearly full credit for a user targeting 0.85, while a song at 0.30 earns very little. The formula is: `1.0 × (1 − |target − song_energy|)`.
- **Acousticness preference** adds up to 0.5 points depending on whether the user likes acoustic or produced sounds.
- **Popularity bonus** adds up to 0.3 points, scaled by how popular the song is (popularity/100).
- **Era match** adds 0.5 points if the song's release decade matches the user's preferred decade.
- **Mood tag match** adds 1.0 points if the detailed mood tag matches (e.g., "euphoric" vs. "serene").

All songs are scored, sorted from highest to lowest, and the top 5 are returned with a plain-language explanation for each one.

The system also supports four **scoring modes** — *balanced*, *genre-first*, *mood-first*, and *energy-focused* — which shift the weights so a different feature dominates. And an optional **diversity penalty** reduces the score of songs whose genre or artist already appears in the accepted list, so the top 5 doesn't repeat the same type of song over and over.

---

## 5. Observed Behavior and Biases

**Genre dominance is the biggest bias.** Genre match alone is worth 2.0 points, which is more than the energy score can ever earn (max 1.0) and more than the mood tag bonus (1.0). In the "Conflicted Jazz" test — a user who wanted jazz but at high energy (0.90) — the system returned Coffee Shop Stories (a slow jazz track at energy 0.37) as the #1 result. The genre + mood points together (3.5) completely overrode the fact that the song's energy was 0.53 away from what the user wanted.

**Cold-start genre failure is silent.** When the user's genre is not in the catalog (tested with "classical"), the maximum achievable score drops from ~8.0 to ~4.1. The system still returns results and presents them as recommendations without any warning. A user who wanted classical music gets folk and ambient instead, and has no way to know why.

**Popularity skews toward mainstream artists.** The 0.3 popularity weight consistently adds a small edge to more popular songs, which means niche or independent artists are slightly disadvantaged even if their song is otherwise a perfect match.

**Single-genre catalog trap.** Most genres appear only once. A rock fan will always get Storm Runner as their #1 result, regardless of which other preferences they set. Diversity mode helps, but the catalog is simply too small to provide real variety.

---

## 6. Evaluation Process

Five user profiles were tested, including two adversarial edge cases:

| Profile | Top result | Score | Matched intuition? |
|---|---|---|---|
| pop / happy / energy 0.85 / tag: euphoric | Sunrise City | 6.61 | Yes — all 4 features matched |
| lofi / chill / energy 0.38 / tag: serene | Library Rain | 6.57 | Yes — near-perfect match |
| rock / intense / energy 0.92 / tag: aggressive | Storm Runner | 6.66 | Yes — only rock song in catalog |
| jazz / relaxed / energy 0.90 (conflicting) | Coffee Shop Stories | 4.21 | Partially — energy was ignored |
| classical / peaceful / energy 0.30 (unknown genre) | Mountain Echo (folk) | 4.10 | Reasonable fallback, not ideal |

A **weight-shift experiment** ran the Conflicted Jazz profile with `genre_weight=1.0, energy_weight=2.0`. Secondary results shifted toward more energy-appropriate songs, but Coffee Shop Stories remained #1 because it still earned enough genre + mood points. This confirmed that genre bias cannot be eliminated by weight tuning alone.

A **scoring mode comparison** showed that *genre-first* mode locked in the lofi tracks even more tightly, while *energy-focused* mode produced a slightly different order but still favored the same top 2 songs because they also happened to have close energy. The modes made the biggest difference for edge-case profiles where the default weights gave a counterintuitive result.

A **diversity penalty test** showed that for the High-Energy Pop profile, the standard ranking placed two pop songs (#1 Sunrise City, #4 Gym Hero) in the top 5. With diversity enabled, Gym Hero was pushed to #5 and Rooftop Lights (indie pop) moved up to #4, adding one more distinct genre to the list.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom demonstration of how a content-based music recommender works
- Learning exercise for understanding scoring weights, feature engineering, and algorithmic bias
- Code reference for understanding functional vs. OOP design in Python

**Not intended for:**
- Real users or real music platforms
- Making decisions about which music to license or promote
- Any context where a biased or incomplete recommendation could cause harm
- Replacing human music curation or discovery

---

## 8. Ideas for Improvement

1. **Fuzzy genre matching** — instead of an all-or-nothing genre bonus, use a similarity table so that "indie pop" earns partial credit against "pop," and "metal" earns partial credit against "rock."

2. **Unknown genre warning** — when the user's requested genre is absent from the catalog, display a clear message like "Genre not found — showing closest alternatives based on mood and energy" rather than silently falling back.

3. **Tempo-based energy refinement** — `tempo_bpm` is already in the dataset but unused. Two songs at energy 0.8 can feel very different at 90 BPM vs. 140 BPM. Adding a tempo proximity score would give energy matching more real-world accuracy.

---

## 9. Personal Reflection

**Biggest learning moment:** The "Conflicted Jazz" profile was the clearest lesson. A user who wanted high-energy jazz got a coffee shop slow-jazz track as the top result. On paper the math was correct — genre and mood matched. In practice the recommendation would feel completely wrong. This made it obvious that a scoring system is not the same as understanding music. The math is just measuring labeled columns; it has no idea that "jazz" and "high energy" are in tension in this small catalog.

**How AI tools helped and when to check them:** Using Claude to generate the scoring logic, expand the dataset, and draft the mode comparison was very fast. But I had to verify every generated weight value and test with adversarial profiles to find the genre dominance problem. The AI tool didn't flag the bias — it just built what was asked. The evaluation step was where human judgment had to take over.

**What surprised me about simple algorithms:** Even a system that is just adding up points based on label matches can feel surprisingly "right" for well-matched profiles (like the lofi study user). The Chill Lofi Study profile returned Library Rain and Midnight Coding as clear #1 and #2, and those results would feel correct to a real listener. Simple math with the right features can get you a long way — until you hit an edge case.

**What I would try next:** I'd want to add a basic listening history so the system can learn that a user skips all pop songs even when they claim "pop" is their genre. Stated preferences and actual behavior often don't match, and that gap is where real recommenders earn their value.
