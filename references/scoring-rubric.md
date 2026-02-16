# Segment Scoring Rubric

When analyzing a transcript for shortform candidates, score each segment on these 5 dimensions. Each dimension is scored 0-100, then weighted to produce a final score.

## Dimensions

### 1. Hook Strength (Weight: 0.30)

The first 3 seconds determine whether a viewer scrolls past or stays. Score based on which hook archetype is present:

| Archetype | Example | Score Range |
|-----------|---------|-------------|
| Bold/Contrarian | "Everything you know about X is wrong" | 80-100 |
| Curiosity Gap | "There's one thing nobody tells you about..." | 75-95 |
| Value Promise | "Here's the exact framework I used to..." | 70-90 |
| Pattern Interrupt | "Wait, let me show you something weird" | 70-90 |
| Payoff Preview | "By the end of this you'll know how to..." | 65-85 |
| Mid-Action Start | [Starts mid-sentence with energy] | 60-80 |
| Hidden Knowledge | "The secret that [authority figures] don't share" | 60-80 |
| Weak/Generic | "So today I want to talk about..." | 10-40 |

**Boosters** (+5-10 each):
- Contains a specific number ("3 steps", "$50K", "in 30 days")
- Names a recognizable entity (person, company, tool)
- Implies personal experience ("I tested", "I spent 6 months")

### 2. Standalone Coherence (Weight: 0.25)

The segment must make complete sense to someone who hasn't seen the rest of the video.

| Criteria | Score |
|----------|-------|
| Complete self-contained narrative arc (setup → development → resolution) | 85-100 |
| Complete idea with minor context gaps (viewer can infer) | 65-84 |
| Mostly standalone but references earlier content ("as I said before") | 40-64 |
| Requires prior context to understand ("so going back to that point") | 10-39 |
| Fragment — starts or ends mid-thought | 0-9 |

**Red flags** (automatic low score):
- "As I mentioned earlier..."
- "Going back to what we discussed..."
- Pronouns without clear referents ("he said that...")
- Cuts off mid-sentence at the end

### 3. Emotional Intensity (Weight: 0.20)

Strong emotions drive shares and comments.

| Signal | Score Range |
|--------|-------------|
| Passionate rant / strong opinion with conviction | 80-100 |
| Surprise reveal / unexpected twist | 75-95 |
| Genuine humor / laughter | 70-90 |
| Personal vulnerability / honest failure story | 70-90 |
| Enthusiastic explanation of something fascinating | 60-80 |
| Calm but insightful observation | 40-60 |
| Monotone recitation of facts | 10-30 |

### 4. Value Density (Weight: 0.15)

How much actionable content is packed per second.

| Content Type | Score Range |
|--------------|-------------|
| Step-by-step process / exact method | 80-100 |
| Framework / mental model with examples | 75-95 |
| Specific data points / research findings | 70-90 |
| Counter-intuitive insight with explanation | 65-85 |
| General advice with some specifics | 40-60 |
| Vague platitudes ("work harder", "be consistent") | 10-30 |

**Duration adjustment**: Penalize segments where >30% of time is filler, repetition, or tangents.

### 5. Payoff Quality (Weight: 0.10)

How satisfying the ending feels.

| Ending Type | Score Range |
|-------------|-------------|
| Punchline / satisfying reveal | 85-100 |
| Clear call-to-action with specific next step | 75-90 |
| Complete thought — natural stopping point | 65-80 |
| Fades into next topic (can be cut cleanly) | 40-60 |
| Cuts off mid-thought / no resolution | 10-30 |

## Scoring Formula

```
final_score = (hook * 0.30) + (coherence * 0.25) + (emotion * 0.20) + (value * 0.15) + (payoff * 0.10)
```

## Candidate Selection Guidelines

1. **Target 8-12 candidates** from a typical 30-60 minute video
2. **Duration sweet spot**: 15-55 seconds (peak engagement at 25-40s)
3. **Minimum score threshold**: 60 (below this, skip the segment)
4. **Diversity**: Don't select 5 segments about the same subtopic
5. **Spacing**: Prefer segments at least 2 minutes apart in source
6. **Natural boundaries**: Align start/end with sentence boundaries, not mid-word

## Hook Text Generation

For each selected segment, write a hook overlay:
- **Line 1**: 4-8 words, the attention-grabbing statement (white, large)
- **Line 2**: 3-6 words, context or subtitle (cyan, smaller)
- Lines should NOT duplicate the first spoken words — they complement the audio
