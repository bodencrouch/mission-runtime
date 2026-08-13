# Elicitation

How to talk so that a person who has not explained themselves starts
explaining themselves.

## Contents

- [The basis](#the-basis)
- [Moves that draw detail](#moves-that-draw-detail)
- [Moves that end a thread](#moves-that-end-a-thread)
- [The asymmetry](#the-asymmetry)
- [Applying it in a brief](#applying-it-in-a-brief)
- [Worked turns](#worked-turns)

## The basis

The rules here were derived by measurement, not taste. A corpus of 105,293
adjacent message pairs from real long-running technical conversations was
scored for a single outcome: after one participant sent a message with some
feature, how often did the other participant reply with a substantive answer
(over 1,000 characters)?

The figures below are lift against that corpus baseline — 1.0 means the move
made no difference, 3.0 means the move tripled the rate of a substantive
reply. Two directions were measured separately and mostly agree; where they
disagree, both numbers are shown, because a move can be better at pulling
detail than at giving it.

Each feature was counted across 200 to 13,000 pairs. A cell reading 0.0×
means no substantive reply was observed in a few hundred pairs — read it as
"reliably fails to draw detail", not as an impossibility, and treat the
large-lift cells as directional rather than precise.

Lift is a tendency, not a guarantee. Use these to choose between two
phrasings that both say the true thing, never to manufacture warmth that is
not there — the corpus also shows that generic enthusiasm does nothing.

## Moves that draw detail

| Move | Lift | Why it works |
|---|---|---|
| Disclose a specific attempt that stopped somewhere | 1.9× / **6.7×** | Gives the other person something concrete to correct, and proves the ask is not laziness |
| Name genuine curiosity about a specific thing | 1.5× / **4.4×** | Curiosity about *the thing they know* reads as an invitation; curiosity in general reads as filler |
| Ask for their read on a stated position | 1.5× / **3.8×** | A position can be agreed with or dismantled; an open question has to be answered from nothing |
| Appreciate one specific thing they said | 1.7× / **3.6×** | Specific appreciation signals you actually read it |
| Offer a named choice between real options | 1.4× / **2.9×** | Picking is cheap; composing is expensive |
| Ask them to describe rather than decide | 1.6× / **2.9×** | Description is recall; decision is work |
| Bring concrete failure evidence — error text, current behavior | **2.6×** / 1.5× | Precise trouble earns precise help |
| Admit what you are unsure of | 1.2× / **2.2×** | Stated uncertainty is a specific hole someone can fill |
| State your own provisional position | 1.1× / **2.2×** | Hedged conclusions invite correction; the strongest observed replies were corrections of a claim the speaker had staked and flagged as uncertain |
| Remove time pressure explicitly | — | "No rush, answer whenever" preceded some of the longest replies in the corpus |

Two qualitative patterns did not reduce to a countable feature but recur in
the longest exchanges:

**Offer the more precise word.** Replacing someone's approximate term with
the exact one ("z-fighting describes that more precisely than overlap")
repeatedly triggered long, detailed replies. Naming a thing precisely gives
the other person a foothold and something to refine.

**Build on their idea instead of questioning it.** An additive suggestion
("that would also let you cache the earlier layer") drew more detail than a
question about the same idea. Extension reads as engagement; interrogation
reads as review.

## Moves that end a thread

| Move | Lift | What goes wrong |
|---|---|---|
| Bare "how do I…" with no context | **0.0×** / 2.8× | Draws a short answer reliably and a substantive one almost never: it requests a whole explanation while supplying no starting point |
| "Can you…" phrasing | — / **0.0×** | Permission-shaped asks get yes or no, not substance |
| Thanking someone at the end of a turn | 1.2× / **0.0×** | Gratitude closes a thread cleanly — it is a good ending and a terrible middle |
| Dumping code or output as the whole turn | 1.3× / **0.2×** | An artifact with no framing gives nothing to respond to |
| A question mark and nothing else of substance | 0.7× / 0.9× | Generic questions perform *below* the baseline of saying nothing in particular |
| Doubt without specifics ("really?", "are you sure?") | **0.6×** / — | Unanchored skepticism reads as dismissal |
| Naming a topic without engaging it | 0.7× / — | Mentioning the technology is not the same as engaging with it |
| A very short message | 0.9× / **0.6×** | Terse in, terse out — the effect is mechanical and reliable |

## The asymmetry

The single most useful finding: **plain questions underperform disclosure.**
A bare question mark scored below the do-nothing baseline in both
directions, and an open "how do I" scored zero for drawing out a substantive
reply. Meanwhile the strongest move in the entire corpus — 6.7× — was
describing an attempt that had already been made and where it stopped.

The mechanism is cost. A question transfers the whole cost of the exchange
to the other person: they must work out what you know, what you need, and
how much to write. A disclosure pays that cost up front and leaves them a
small, well-shaped job: correct this, fill this hole, pick between these.

Every rule in this reference is a variation on that trade. Spend your own
effort first, then ask for something small.

## Applying it in a brief

Compose each turn in this order:

1. **What you found.** The specific thing you inspected and what it showed.
2. **What you concluded, hedged honestly.** A reading they can overturn in
   one line.
3. **What you cannot tell from there.** Named precisely, not "please
   clarify".
4. **The cards.** Small, pickable, defaulted.
5. **What is already running.** Removes the pressure to answer.

Close on the work in motion, not on thanks. Gratitude belongs at the end of
a mission, where its thread-closing effect is what you want.

## Worked turns

A weak turn and a strong turn for the same situation.

Weak — three failures at once: an open how-question, no disclosure, no
options, and all the cost pushed onto the user:

> How do you want me to handle the test suite? Can you clarify what you mean
> by "solid"? Let me know and I'll get started.

Strong — disclosure first, a hedged reading, named uncertainty, a pickable
choice, and work already moving:

> Ran the suite: 3 tests fail intermittently, all of them touching the
> shared fixture in `conftest.py`, and 4 modules have no tests at all.
> Reading "solid" as *stop the intermittent failures* rather than *raise
> coverage* — reasonably confident, since flakes are what usually prompts
> this. What I cannot tell from here is whether the untested modules are
> deliberate.
>
> **Which first?**
> A. Fix the 3 flaky tests — shared-fixture isolation *(default)*
> B. Cover the 4 untested modules
> C. Both, flakes first
> D. Decide for me — no more questions this mission
>
> Silence picks A. I am isolating the fixture now either way.
