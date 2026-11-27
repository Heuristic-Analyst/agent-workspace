# 04 — Worked examples: what edges look like, what they paid, how they died

*Eleven cases, ordered from slowest-decaying to fastest. Each one: the story, the number, the decay, what's
left, and the lesson. Where a figure comes from an abstract in the corpus it is marked; where it is my
recollection of a well-known result I say "approx." — check the paper before you quote it in a deck.*

---

## The ledger at a glance

| edge | source type | peak gross | half-life | status today |
|---|---|---|---|---|
| Equity risk premium | risk premium (S1) | 5–7%/yr | never* | alive, smaller, conditional on valuations |
| Value (HML) | risk premium + mispricing | 4–5%/yr | ~20+ yrs | alive, badly behaved since 2007 |
| Carry | risk premium (S1) | 5–10%/yr | slow | alive, crash-prone |
| Variance risk premium | risk premium (S1) | high SR | slow | alive, catastrophic tails |
| Momentum | mispricing (S2) | ~12%/yr (1993) | ~10 yrs, partially | alive but weaker; works in other assets |
| Trend following | risk premium + behavioural | good pre-2009 | 15 yrs | short-term dead post-2009 (Kurth et al. 2026) |
| Post-earnings drift | mispricing (S2) | 5–10%/yr | ~15 yrs | much weaker in large caps |
| Accruals | mispricing (S2) | ~10%/yr (1996) | ~10 yrs | gone (Green, Hand & Soliman 2011) |
| The "factor zoo" average | mostly artefact | 4–6%/yr gross | 5–8 yrs | **4bp/month net** (Chen & Velikov 2022) |
| Equity stat-arb (daily) | mispricing + microstructure | was huge in the 90s | 5–8 yrs | compressed, capacity-limited |
| Alt-data signals | information (S3) | large, brief | 1–3 yrs | commoditised on arrival |
| Crypto funding/basis | structural (S4/S5) | 20–100%/yr | ~3 yrs | compressed to single digits |
| Latency arbitrage | microstructure (S4) | large, brief | arms race | still exists, capex-gated |

\* "never" = no reliable evidence of decay; the premium varies with price, not with knowledge.

---

## 1. The equity risk premium — the edge that can't be arbitraged

**Story.** You are paid for holding equity, because equity can lose 50% and people dislike that.

**Size.** Historically ~5–7%/yr over cash (long sample, with a large standard error), highly variable:
a century of US data is roughly 4 independent 25-year observations, which is why the "is the premium 3% or
8%?" debate has never been settled.

**Decay.** None in the arbitrage sense, because the "edge" is a risk you must hold. What *does* move is the
price: when valuations are high the forward premium is low (and the reverse). **This is the archetype of an
edge that decays not from knowledge but from being bid up.** It has no kill switch, only a valuation
signal.

**Lesson.** Some edges are not information advantages at all. If your whole book is here, you're not running
a strategy, you're holding a risk. Nothing wrong with that — but it has no capacity limit, no decay from
competition, and a 60% drawdown in its future.

---

## 2. Value — a risk premium wearing a mispricing's clothes

**Story.** Cheap stocks beat expensive ones. Two explanations, probably both partly true: (a) cheap stocks
are riskier (distress, cyclicality) and you're paid for it, (b) investors extrapolate recent growth and
overpay for "glamour."

**Size.** Approx. 4–5%/yr for HML over the long run in the US; the effect is present in most developed
markets, weaker in some emerging ones. Fama & French (1992) is the reference: size and book-to-market
"combine to capture the cross-sectional variation in average stock returns" — the paper that killed CAPM as
a sufficient model.

**Decay.** The interesting case, because value's *underperformance since 2007* was widely (and wrongly)
declared to be death. It wasn't: the value spread widened to historic extremes, which is precisely what the
"it's crowded / it's dead" narrative should have predicted would *raise* forward returns. The 2021–2022
recovery was violent. Meanwhile, Asness, Frazzini & Pedersen's "quality minus junk" (2018) shows a related
point: high-quality stocks *do* have higher prices, just "not by a very large margin", which is why quality
earns high risk-adjusted returns — the market under-reacts to quality.

**What's left.** Value works, but: (i) it is not a timing tool; (ii) it is dramatically better combined with
quality and momentum than alone; (iii) its drawdowns are long enough to end careers (see file 05 on how to
size that).

**Lesson.** *"The strategy is dead"* and *"the strategy is cheap"* are often the same observation. The
distinction is whether the underlying economic reason still holds.

---

## 3. Momentum — the best-documented edge, and the best-documented crash

**Story.** Winners keep winning for 3–12 months, then partially reverse. The mechanism is underreaction
(information diffuses slowly) plus, in the short run, mechanical flows.

**Size.** Jegadeesh & Titman (1993): 6-month formation / 6-month holding, ~1%/month gross (≈12%/yr), 1965–1989.
Asness, Moskowitz & Pedersen (2013) show value and momentum everywhere: consistent premia across 8 markets
and asset classes, with a *negative* correlation between the two factors — the original "diversify your
edges" paper.

**Decay.** Roughly halved in US large caps since the 1990s; still strong in international equities, in
futures, and in smaller/less liquid names (where costs eat more of it). Green, Hand & Zhang's finding that
predictability collapsed after 2003 applies broadly.

**The crash.** Daniel & Moskowitz (2016): momentum crashes are "partly forecastable," occur "in panic
states, following market declines and when market volatility is high," and are "contemporaneous with market
rebounds." Why: the short leg is a bet against the most beaten-down, most option-like stocks, and in a
rebound those explode upward. Their fix is the practical lesson: an implementable dynamic momentum strategy
based on forecasts of momentum's mean and variance **approximately doubles the alpha and Sharpe ratio** of
static momentum.

**Lesson.** A decaying, occasionally catastrophic edge can still be the best thing in a portfolio, *if you
size it dynamically and you understand that its short leg is short optionality.*

---

## 4. Carry — being paid to hold a funding asymmetry

**Story.** Higher-yielding assets beat lower-yielding ones, because someone must be paid to hold the
funding risk. In FX: borrow the low-yielder, lend the high-yielder. In futures: roll yield. In credit: the
spread.

**Size.** G10 FX carry has historically earned ~3–5%/yr with a Sharpe near 0.5–0.7, and *negative skew*:
the worst months (2008, 2015, 2020) wipe out years of gains. Koijen, Moskowitz, Pedersen & Vrugt's "Carry"
(2018) generalises carry to every asset class with a common global factor: a real, robust, risk-based edge.

**Decay.** Slow, because it's a risk premium. What decays is the *level*: when yield differentials compress
to zero, there's nothing left to harvest, exactly as with any risk premium that gets priced away.

**Lesson.** Carry's decay is in the *state variable* (the spread), not in calendar time. Monitor the spread,
not the strategy's Sharpe.

---

## 5. Trend following — an edge killed by a tick-size change

**Story.** Prices trend; you follow them. Profitable for two centuries across futures markets.

**Decay — the cleanest modern case study.** Kurth, Eisler, Rej & Bouchaud (2026) document that **since
about 2009, short-term trends stopped delivering**, across ~100 liquid futures and confirmed by a CTA proxy.
They test capacity constraints, market electronification, a CTA/order-flow regime change, and a
microstructural mechanism. The first three fail on timing, magnitude or cross-sectional heterogeneity. The
winner: **volatility-normalised tick size**. Trend PnL collapsed precisely on the small-tick contracts,
where a given amount of directional pressure moves the price less per unit of flow, and where the
mean-reversion response is faster.

**Lesson.** Some decay has nothing to do with anyone "finding out." The instrument changed, and the same
signal on the same price series now has a different payoff. **Check the plumbing of the venue, not just the
statistics of the signal.**

---

## 6. Accruals — a famous anomaly that simply died

**Story.** Sloan (1996): earnings driven by accruals (accounting estimates) persist less than earnings
driven by cash flow, but investors fail to distinguish them → short high-accrual, long low-accrual.

**Size.** ~10%/yr in the original sample. It was *the* accounting anomaly of the 1990s.

**Decay.** Green, Hand & Soliman (2011): the hedge returns "appear to have decayed in U.S. stock markets to
the point that they are, on average, no longer reliably positive," driven "in part" by hedge-fund capital
and trading volume in extreme accrual firms, with a smaller role for the signal itself shrinking.

**Lesson.** An anomaly can die *because it was published and exploited* — and you can see the killer in the
data (AUM and volume in the extreme names) *before* the return goes to zero.

---

## 7. Post-earnings announcement drift — still there, but only where costs can't reach

**Story.** Prices under-react to earnings surprises and keep drifting in the direction of the surprise for
weeks (Bernard & Thomas 1989). One of the most robust behavioural anomalies ever found.

**Decay.** Large-cap US: much weaker than in the 1980s–90s (consistent with the general post-2003 collapse
documented by Green, Hand & Zhang). Small-cap/illiquid: still present, but the names you'd need to trade
have spreads of 50–200bp and very limited borrow. The edge migrated to where arbitrage is expensive — which
is exactly what theory says should happen (limits to arbitrage: Shleifer & Vishny 1997).

**Lesson.** "Decayed" often means "moved". Before declaring an edge dead, check whether it merely moved to a
capacity band you can't operate in. If you can operate there, it's still a business.

---

## 8. The factor zoo — 4 basis points a month

**Story.** Hundreds of published cross-sectional predictors.

**The numbers.** Harvey, Liu & Zhu (2016): with the historical record of how many factors have been tested,
a new factor needs a **t-statistic above 3.0**, and "most claimed research findings in financial economics
are likely false." Hou, Xue & Zhang (2020): of 452 anomalies, **65% fail at t>1.96**, **82% at t>2.78**.
Chen & Velikov (2022): after effective spreads, post-publication decay and modern trading technology, the
average anomaly's **expected return is 4 basis points per month**; the strongest net at most 10bp;
combinations around 20bp.

**The counterweight.** Jensen, Kelly & Pedersen (2023): with a Bayesian hierarchical model, most factors
replicate, cluster into 13 themes, and work out-of-sample in 93 countries. Chen & Zimmermann (2019):
publication bias is only **12.3%**, far smaller than the post-publication decay.

**The synthesis I believe.** The *themes* are real (value, momentum, quality, investment, low-risk,
seasonality/liquidity...). The long tail is mostly noise. And the average net return of a randomly chosen
published anomaly today is not an investable number.

**Lesson.** The unit of research is not the factor, it's the **theme + implementation + cost band**. Two
people can run "the same factor" and one makes 8% and the other makes 0, depending entirely on construction
(costs, turnover control, weighting, borrow).

---

## 9. Alternative data — an edge with a 24-month half-life

**Story.** In the 2010s, satellite parking-lot counts, credit-card panels and app-download scrapes gave a
genuine information advantage on quarterly revenues.

**Decay.** Compressed brutally. As soon as a dataset becomes a product (vendors, then exchanges, then
"alt-data" marketplaces), the price moves to capture most of the value, and any signal becomes a crowded
factor. The pattern: **first mover 2–4 years, then the edge is in the processing and the history, not the
access.**

**What's left.** (i) proprietary data you *generate* (your own order flow, your own customer data), (ii) the
ability to clean and point-in-time it correctly (a genuine moat, boring and underrated), (iii) speed of
interpretation on a newly-available dataset.

**Lesson.** Information edges decay through the *price of the information*, not through competition in the
strategy. Model the vendor's roadmap as part of your decay curve.

---

## 10. Crypto funding and basis — a structural edge that closed fast

**Story.** Perpetual futures trade at a premium to spot in bull markets; you short perp / long spot and
collect funding. Also: the "cash and carry" basis in dated futures.

**Size.** In 2017–2021 funding rates of 30–100%+ annualised were routine. A capital-constrained market with
retail leverage demand and no prime brokers = a textbook structural edge (S4/S5: someone *must* pay for
leverage).

**Decay.** Compressed to single digits by 2022–2024 as more capital, better infrastructure, and institutional
market makers arrived. The edge moved to: smaller venues, newer tokens, shorter horizons, and operational
competence (custody, exchange risk) — i.e. to where the barrier is *operational*, not analytical.

**Lesson.** In a young market the edge is structural and enormous, and its half-life is the time it takes
capital to route around the friction. Bet on the friction being removed, and plan the next friction.

---

## 11. Latency arbitrage — an edge that is a capex programme

**Story.** Be faster than the market at updating quotes when the underlying moves. Classic 1990s–2000s
example: stale quotes in the futures/ETF arbitrage.

**Shape.** Tiny profit per event, enormous number of events, so the Sharpe is a function of *breadth*
(section 4 of file 01) and the P&L is a function of *infrastructure*. Menkveld (2013) on HFT market makers:
high message-to-trade ratios, small inventories, tiny per-trade profits, and a role as the "new market
makers."

**Decay.** An arms race, not a diffusion: the edge doesn't disappear, its *cost of entry* rises until only
a few firms can afford it. Regulation (tick sizes, access fees, latency floors) can reset it overnight.

**Lesson.** Here the moat is capex and operations, and the research question is "what will the exchange
change next?" It's a different business from everything else in this document, despite sharing a P&L
format.

---

## 12. A case study in what edge is *not*

An arXiv preprint in the corpus (2025) reports a cross-sectional equity factor with **out-of-sample Sharpe
above 13**, annualised return **158.6%**, volatility 12.0%, max drawdown −11.9% over 2004–2024, "produced
entirely out-of-sample with frozen parameters," passing "1,000 randomization trials with p-values below
0.001."

Every one of those numbers is a red flag:

- **Sharpe 13** on a daily equity factor would produce roughly a 1-in-10^30 result under any sensible null.
  The best systematic funds in the world run 1–3 net of costs, with hundreds of people.
- **158%/yr with 12% vol** for 20 years implies turning $1 into ~$4 million with an 12% drawdown. Somebody
  would have noticed.
- **"Randomization trials"** test the wrong null: shuffling labels destroys the *time-series structure* the
  strategy exploits, so passing is nearly guaranteed for anything with a persistence-based entry rule. It is
  an in-sample test wearing out-of-sample clothes.
- **Regime-conditional activation** ("only when stocks show >60% positive days in a 63-day window") is a
  parameter-rich rule fitted on the same 20 years used to report the out-of-sample result.
- The paper is on arXiv, not in a journal, which for a result of this magnitude is itself informative.

**The lesson is not "arXiv is bad."** The lesson is that the human eye is a poor multiple-testing detector,
and that a strategy's *claimed* Sharpe and its *credible* Sharpe are separated by a factor that grows with
how many knobs the researcher turned. Apply the deflated Sharpe ratio (notebook, cell 5) and this collapses
to nothing.

---

## 13. The pattern across all thirteen

1. **Every edge has a mechanism.** The ones that lasted (risk premia) had a reason that isn't "people
   haven't noticed."
2. **Decay is usually fast at first and slow after.** Both exponential and hyperbolic fits are worth doing.
3. **Decay is often *migration*, not death.** PEAD moved to illiquid names; crypto basis moved to operations;
   value moved to a cheaper valuation spread.
4. **The mechanism of death is often not competition but plumbing** — decimalisation, tick size, borrow
   markets, fee schedules.
5. **The published number is an upper bound.** Chen & Velikov's 4bp/month is the single most sobering
   statistic in the corpus.
6. **Survivors are the ones that were never really information edges** — they were risk, structure, or
   constraints.
