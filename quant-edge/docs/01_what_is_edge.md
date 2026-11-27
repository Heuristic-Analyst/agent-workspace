# 01 — What "edge" actually is

*Everything else in this project hangs off the definitions in this file. If you disagree with one, the rest breaks.*

---

## 1. The one-sentence version

**Edge is a repeatable, measurable, exploitable reason why a future return should be different from what
the risk you take would normally pay — after costs, after financing, and after whatever everyone else is
already doing about it.**

Every word in that sentence is load-bearing, and each one fails in practice for a different reason:

| word | fails when | name of the failure |
|---|---|---|
| repeatable | it happened once | luck / a single regime |
| measurable | you can't estimate it from data you had at the time | hindsight, look-ahead, survivorship |
| exploitable | the cost of trading it exceeds it | cost blindness, capacity |
| reason | nobody can say why it should exist | data mining |
| future | it worked because it already happened | overfitting / decay to zero |
| after costs | gross Sharpe is a fantasy number | implementation shortfall |
| already doing it | the trade is crowded; you're the exit liquidity | crowding / crash risk |

Most "edges" die on the second word (measurable) or the fourth (reason). Very few die on the first.

---

## 2. Three different things people call "edge"

Worth separating because they have completely different economics, decay rates and validation methods.

**(a) A risk premium — you are paid to hold something unpleasant.**
You earn because someone else is paying to get rid of a risk. Equity risk premium, credit spread, variance
risk premium, illiquidity premium, the funding-liquidity premium in Brunnermeier & Pedersen (2008).
*Signal quality is not the point; survival is.* Decay: slow, and only when the underlying risk stops being
painful. Never "arbitraged away" in the usual sense — the pain is the product.

**(b) A mispricing — someone is systematically wrong and you are systematically right.**
Underreaction (post-earnings drift, Bernard & Thomas 1989), overreaction (De Bondt & Thaler 1985), accruals
(Sloan 1996), slow diffusion of information (Hong & Stein). You are being paid for *cognitive* work the
market hasn't done yet. Decay: **fast and predictable** — it starts the moment enough capital or enough
publicity arrives (McLean & Pontiff 2016). This is the category that "decays" in the sense people mean.

**(c) An informational or mechanical advantage — you know or can do something others can't.**
Alternative data before it's on everyone's terminal; an exchange feed 200 microseconds earlier; a structural
flow you can see coming (index rebalance, forced deleveraging, a mandated seller). Decay: driven by
technology diffusion and by *other people buying the same advantage*. This is where most "quant" money is
actually made at the high-frequency end, and where the arms race is most literal.

A fourth, less flattering category: **(d) a fee or a spread** — market making, financing, lending, the
"edge" that is really a business rather than a prediction. Perfectly good, systematically underrated by
people who want to be right about the future.

The practical consequence: **ask which of (a)-(d) you have, because the answer tells you how to test it and
when to kill it.** A risk premium that looks bad for 3 years is normal. A mispricing that looks bad for 3
years is dead. An informational edge that shows no decay is probably not informational.

---

## 3. The decomposition

Start with the single most important equation in the field, written plainly:

```
realised return  =  risk compensation  +  edge  +  noise
```

in symbols, for asset *i* at time *t*:

```
r_it  =  α_i  +  β_i·F_t  +  ε_it
```

- `β_i·F_t` — what you get paid for being exposed to things you didn't choose to forecast. Not edge. If your
  Sharpe comes entirely from this, you are a beta salesman with extra steps.
- `α_i` — the part not explained by common risk. **This is the only part that is yours.**
- `ε_it` — noise. Almost all of the variance, almost always. The whole craft is separating `α` from `ε` with
  a sample size that is always too small.

Then subtract the costs, which is where most of the honesty lives:

```
α_net  =  α_gross  −  trading costs  −  financing/borrow  −  taxes  −  the cost of your own impact
```

The trap: `α_gross` is measured on paper, `α_net` is what you keep, and the gap is not a rounding error. On
204 published equity anomalies, Chen & Velikov (2022) estimate the *average net* expected return — after
effective bid-ask, post-publication decay, and modern trading technology — at **4 basis points per month**.
Not 4% a year. 4bp a month, about 0.5%/yr, before price impact.

---

## 4. The arithmetic of an edge (why small numbers are normal)

The unit of edge is **information coefficient (IC)**: the cross-sectional rank correlation between your
signal today and returns over the next period. In equities, a good signal has an IC of **0.02 to 0.05**.
That sounds pathetic. It isn't:

- IC 0.03 on a daily cross-section of 500 names, rebalanced daily, is roughly `0.03 × √(500) ≈ 0.67` of
  "one-day" Sharpe before you account for the fact that bets overlap → annualised, this is a *very* strong
  strategy. Real implementations land at IR 0.5–1.5.
- Grinold's fundamental law (1989): **IR ≈ IC × √BR**, where BR is the number of independent bets per year.
- With constraints (short limits, sector neutrality, turnover caps), Clarke, de Silva & Thorley (2002)
  extend it: **IR ≈ TC × IC × √BR**, where TC is the transfer coefficient — the correlation between your
  forecast and your actual positions, in [0,1]. A long-only, sector-neutral, 40-name portfolio has TC
  around 0.3–0.6. You lose half your edge to the mandate, silently.

Concretely, using the law as a design tool:

| setting | IC | bets/yr (BR) | TC | IR |
|---|---|---|---|---|
| 500 stocks, monthly, genuinely independent bets | 0.04 | 500×12 = 6,000 | 1.0 | 3.10 |
| same, but with ρ=0.03 average correlation between residual bets | 0.04 | 376 | 1.0 | 0.78 |
| same, but ρ=0.15 (a normal, non-neutralised cross-section) | 0.04 | 79 | 1.0 | 0.36 |
| long-only 40 names, monthly | 0.04 | 40×12 = 480 | 0.5 | 0.44 |
| 15 futures, weekly trend | 0.06 | 15×52 = 780 | 0.8 | 1.34 |
| 3 macro trades a year | 0.15 | 3 | 0.9 | 0.23 |

(Rows 2-3 are the honest ones: bets in a cross-section are *not* independent. The effective-breadth
correction is `BR_eff ≈ T · N / (1 + (N−1)·ρ̄)` with ρ̄ the average pairwise correlation of the bets, i.e. of
your *residual* returns once common factors are gone. Notebook cells 3-4 compute and simulate this, and reproduce the table. The lesson is brutal and worth internalising: 500 names do not give you 500 independent bets — with
ρ̄=0.15 you have about **two** per month, which is why a cross-sectional strategy lives or dies on being
factor-neutral, and why the 40-name long-only portfolio with a *third* the IC beats it.)

Three lessons fall out:
1. **Breadth beats brilliance.** A mediocre signal applied to thousands of independent bets beats a
   brilliant call made three times a year. This is why quant exists.
2. **Constraints quietly eat half the edge.** TC is where "we have a great model but the fund doesn't make
   money" comes from.
3. **Edge is not a number, it's a product of three numbers.** Any one of them near zero kills it.

---

## 5. Where edge comes from — the five sources

Every real strategy is a blend of these. Naming them explicitly prevents the classic error of thinking you
have (c) when you have (a).

**S1. Structural risk transfer.** Someone needs to shed risk and will pay you to take it: insurers selling
tail risk, hedgers in commodity futures, issuers of convertible bonds, anyone who must roll exposure.
*Edge = the price of risk, not the price of being right.* Diagnostic: the return is negatively skewed, it
hurts in crises, and it survives being publicised. If your strategy has negative skew and refuses to die,
you are probably here.

**S2. Behavioural mispricing.** Systematic errors by other participants: extrapolation, anchoring,
disposition effect, attention limits, category thinking. *Edge = doing the cognitive work first.*
Diagnostic: works better when limits to arbitrage are high (small, illiquid, hard-to-short names), works
worse after publication, and shows up in sentiment-conditioned subsamples.

**S3. Information.** Better, faster, or uniquely-processed data — satellite counts, card transactions,
shipping manifests, job postings, an expert network, or just a cleaner interpretation of public filings.
*Edge = the information asymmetry itself.* Diagnostic: decays when the data becomes cheap; value lives in
the *processing*, not the *access*.

**S4. Microstructure and mechanics.** The order book, the auction, the index rebalance, the options
expiry, the closing print, the forced seller. *Edge = being structurally positioned to be the counterparty
of flow.* Diagnostic: tiny capacity per trade, enormous breadth, brutally competitive, and it dies when the
venue changes its rules (tick size, fee schedule, auction design).

**S5. Institutional constraints on others.** Benchmarks, mandates, regulation, tax, accounting, career risk
force other people to trade for reasons that are not returns. Index inclusion, forced selling by
redemptions, benchmark-hugging, "prudent man" rules, leverage constraints (Frazzini & Pedersen 2014's
betting-against-beta is exactly this: the edge exists because many investors *cannot* lever).
*Edge = other people's rules.* Diagnostic: it survives publication, and it breaks when the rule breaks.

---

## 6. What edge is *not*

- **Not a backtest.** A backtest is a measurement with an error bar you usually can't compute and a
  selection bias you usually don't want to. See Bailey & López de Prado (2014) on the deflated Sharpe
  ratio, and Harvey, Liu & Zhu (2016): with hundreds of factors tested, **t > 3.0** is the honest hurdle,
  and "most claimed research findings in financial economics are likely false."
- **Not a high hit rate.** A 35% hit rate with 3:1 payoff is a great business. A 90% hit rate with a
  −20:1 tail (short vol) is a time bomb. Hit rate without payoff asymmetry is a number without meaning.
- **Not a positive Sharpe over 3 years.** With IR 1.0 and 3 years of data, the standard error of your
  estimated Sharpe is ~0.58. Your "1.0" is statistically indistinguishable from 0.
- **Not information.** Information without a position is a hobby. The edge includes the ability to *get the
  trade on* at a size that matters.
- **Not permanent.** See file 03. The half-life of a published equity anomaly is measured in years, not
  decades, and the decay is front-loaded.

---

## 7. The four questions (use these on every idea)

1. **Why does this return exist?** Not "what pattern is in the data" — *who is on the other side and why
   are they willing to lose?* If you can't name the counterparty, you are the counterparty.
2. **Why hasn't it been arbitraged?** What is the barrier — capital, mandate, pain, expertise, regulation,
   liquidity, size? If the answer is "nobody noticed," the edge has a half-life measured in months and is
   not yours.
3. **What does it cost to harvest, and at what size?** Breakeven AUM, impact, borrow, financing.
4. **What would have to change for it to stop working, and how would I know first?** Write the answer down
   before you trade. This is your kill switch (file 05).

A strategy that answers all four is a business. One that answers none is a chart.

---

## 8. The uncomfortable structural truth

Grossman & Stiglitz (1980): markets cannot be perfectly efficient, because if prices already reflected all
information, nobody would be paid to gather it — so a small, persistent degree of inefficiency is
*required* for a market to function. Edge therefore never disappears globally; it migrates.

It migrates toward:
- **higher cost of research** (nobody will do the boring work),
- **lower capacity** (too small to matter for a large fund),
- **higher pain** (risk nobody wants),
- **faster timescales** (milliseconds, where the capex barrier is real),
- **worse liquidity** (where exit is the problem),
- **newer markets** (where the participants are less sophisticated).

This migration is the single most useful mental model in the field: **your job is not to find a secret, it
is to stand where the migration is going next, and to be able to leave before the crowd arrives.**
