# Evaluation Reflection

## Profile Comparisons

---

### High-Energy Pop vs. Chill Lofi Study

**Pop profile:** genre=pop, mood=happy, energy=0.85, likes_acoustic=False
**Lofi profile:** genre=lofi, mood=chill, energy=0.38, likes_acoustic=True

Top results:
- Pop: Sunrise City (4.88), Gym Hero (3.39)
- Lofi: Library Rain (4.90), Midnight Coding (4.81)

These two profiles are almost mirror opposites and the recommendations reflect that perfectly. The pop profile surfaces high-energy, produced tracks with upbeat moods. The lofi profile surfaces quiet, acoustic-leaning tracks designed for studying or relaxing. What is interesting is that the lofi results are actually *more confident* — both top lofi songs score around 4.8–4.9, while the pop profile has a large gap between #1 (4.88) and #2 (3.39). This happens because there are two lofi/chill songs in the catalog that closely match, but only one pop/happy song that also gets the acousticness bonus right.

**Why it makes sense:** The lofi listener gets two near-perfect matches. The pop listener gets one perfect match and then the next-best options are just "kinda close." This reveals that the *distribution of the catalog* shapes what any given user can actually discover.

---

### Deep Intense Rock vs. Conflicted (High Energy + Relaxed Mood)

**Rock profile:** genre=rock, mood=intense, energy=0.92, likes_acoustic=False
**Conflicted profile:** genre=jazz, mood=relaxed, energy=0.90, likes_acoustic=False

Top results:
- Rock: Storm Runner (4.94) by a wide margin
- Conflicted: Coffee Shop Stories (4.02) — a slow jazz track despite the user wanting high energy

The rock profile works almost perfectly: Storm Runner matches on all four dimensions and no other song comes close (next best is 2.96). The system behaves well when preferences are internally consistent.

The conflicted profile exposes the biggest weakness. The user says they want jazz with a relaxed mood but high energy (0.90) — those preferences contradict each other because jazz songs in the catalog that are labeled "relaxed" all have low energy. The system picked the genre+mood match (Coffee Shop Stories, energy 0.37) and ignored that the user's actual energy preference was nearly 0.53 points away. In plain English: the system gave this person a coffee shop slow jazz song when they asked for something intense. The genre label "won" even though it was the wrong vibe.

**Why it makes sense:** The scoring weights mean a genre match (2.0) + mood match (1.5) = 3.5 points before energy is even counted. No energy-only song can beat that. This is not a bug in the math — it is a deliberate design choice — but it shows that the weights encode assumptions about what matters most to a listener. Those assumptions are sometimes wrong.

---

### Unknown Genre (Classical) vs. Any Matched Profile

**Classical profile:** genre=classical, mood=peaceful, energy=0.30, likes_acoustic=True
Top result: Mountain Echo [folk/peaceful] — Score: 2.96

Every profile with a genre that exists in the catalog scores 4.0+ on its top result. The classical profile's top result is only 2.96. That is a dramatic drop, and the user has no idea it happened — the system still prints a result and says it is "recommended." There is no warning that the genre was not found.

Mountain Echo (folk, peaceful, low energy, high acousticness) is actually a reasonable fallback for a classical listener — it is quiet, acoustic, and peaceful. The system found the right *vibe* even without a genre match. But a real user would probably expect to see a note like: "We don't have classical in our catalog; here are the closest alternatives."

**Why it makes sense:** Without genre points, the system can only earn up to 3.0 total (mood 1.5 + energy 1.0 + acousticness 0.5). It falls back to mood and energy matching, which are weaker but still meaningful signals. The system degrades gracefully but silently.

---

## Weight Experiment: Genre=1.0, Energy=2.0 on Conflicted Jazz Profile

Default top 3: Coffee Shop Stories (jazz/relaxed), Quarter Past Blue (jazz/moody), Golden Hour Drift (r&b/relaxed)
Shifted top 3: Coffee Shop Stories (jazz/relaxed), Golden Hour Drift (r&b/relaxed), Pressure Drop (reggae/relaxed)

Halving the genre weight and doubling the energy weight moved Quarter Past Blue (jazz, energy 0.46) out of the top 3 and replaced it with Golden Hour Drift (r&b, energy 0.55) and Pressure Drop (reggae, energy 0.58). These are slightly closer to the target energy of 0.90 — but they are still far off. Coffee Shop Stories stayed #1 because it still earns genre + mood points even at the lower genre weight.

**What this tells us:** The genre bias cannot be eliminated just by lowering its weight — it can only be reduced. To truly break out of the genre filter bubble, the system would need a fundamentally different approach, such as clustering songs by audio similarity rather than by label matching.
