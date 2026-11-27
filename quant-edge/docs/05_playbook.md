# 05 — The playbook: find, validate, size, monitor, kill

*A process document. Everything here is either a procedure you can run or a rule you can break knowingly.
Sections 1–7 are for finding and proving an edge; 8–11 are for keeping one.*

---

## 1. Where to hunt (a map, not a list)

Edges live where one of these is true. Go where the friction is, not where the data is easy.

| hunting ground | why it works | how you'd start |
|---|---|---|
| **Forced flows** | someone must trade regardless of price: index rebalances, fund redemptions, option expiry/dealer hedging, margin calls, lockup expiries, tax-driven selling | build a calendar of known forced-flow dates; measure price pressure around them |
| **Mandates and constraints** | other investors are structurally unable to hold something (can't short, can't lever, can't hold illiquid, can't hold negative earnings) | list what a typical mandate forbids; the forbidden set is the opportunity set |
| **Pain transfer** | someone wants to shed a risk and will pay: hedgers, insurers, over-levered operators | find who is *selling* insurance/optionality and why |
| **Boring work** | nobody wants to read 400 pages of lease accounting or reconcile a vendor's point-in-time history | pick a data source the market under-processes |
| **New instruments / venues** | pricing is immature, participants are unsophisticated, frictions are large | follow listings, new venues, new derivatives |
| **Microstructure detail** | auction design, tick size, fee schedules, order types | read the exchange rulebook; literally |
| **Cross-sectional dispersion** | where the cross-section is wide (small caps, EM, single-name credit), selection pays | measure dispersion first, then predict within it |
| **Behavioural regularity with a limit to arbitrage** | the mispricing can't be closed by everyone: hard to short, illiquid, requires patience | require BOTH a bias story and a barrier |

What *not* to do: run a factor library on the S&P 500 and look for the highest Sharpe. That is a search over
the most-arbitraged, most-studied dataset on earth, and it will produce exactly what the factor zoo produced:
4 basis points a month.

---

## 2. The research protocol (this is the part people skip)

**Step 0 — write the memo before the test.** One page: mechanism, counterparty, why it isn't arbitraged,
predicted sign, predicted IC range, predicted turnover, predicted capacity, and the falsification criteria
(what result would make you abandon it). Timestamp it. This single habit eliminates most of the industry's
bad research, because it converts hindsight into a prediction.

**Step 1 — data hygiene, before any modelling.**
- Point-in-time or nothing. A restated fundamental is future information.
- Survivorship: include delisted names, including the ones that went to zero.
- Universe definition fixed *at the time*, not by today's liquidity.
- Corporate actions, splits, tickers changes, symbol reuse.
- Timestamps: when was the datum *available*, not when it refers to. (Most vendor data has a
  publication lag that's easy to get wrong by one day, and one day is enough to fake a Sharpe.)

**Step 2 — the naive test, deliberately simple.** Single sort, equal-weighted, no parameters. If the raw
effect isn't visible in a quintile spread or a simple IC, sophisticated modelling will only manufacture one.
**Do the simple test first, and keep it in the memo.**

**Step 3 — the honest test.**
- Walk-forward only: fit on [t0, t1), trade [t1, t2). Never shuffle time.
- Purge and embargo: drop observations whose label window overlaps the test window (this matters enormously
  for anything with overlapping horizons), and leave a gap between train and test.
- Costs from the start: half-spread + impact model + borrow. Not "we'll add costs later" — the sign of the
  strategy's value often flips with costs, and finding that out early saves months.
- Report the whole family of variants you tried, not the winner. If you tried 40, say 40.

**Step 4 — the null model.** Build a synthetic signal with your signal's autocorrelation, cross-sectional
dispersion and factor exposures, but **no** predictive power. Push it through the identical pipeline. Your
real signal must beat the synthetic's distribution by a wide margin. This is the cheapest defence against
M1 (file 03) that exists.

**Step 5 — the multiple-testing adjustment.** Deflated Sharpe ratio (Bailey & López de Prado 2014) or the
Harvey-Liu-Zhu t>3.0 hurdle, applied with the *actual* number of trials. If you can't count your trials
(because "the research team has been looking at this for a year"), assume 100.

**Step 6 — robustness, in this order:**
1. Different universes (large/mid/small; US/Europe/Japan; liquid/illiquid).
2. Different weighting (equal vs value vs liquidity).
3. Different subperiods, with special attention to pre/post 2003 and pre/post 2008.
4. Different definitions of the signal (this is where you learn whether it's an economic effect or a
   formula).
5. Neighbouring horizons and parameters — a real effect degrades smoothly; an overfit one has a spike.
6. Placebo variables (a signal that should have no power, run through the same pipeline).

**Step 7 — the residual test.** Regress on standard factors + your existing book. If the alpha is gone, the
"new" signal is a re-parameterisation of something you already own.

**Step 8 — costs, capacity, and the business case.** Breakeven cost ≥ 3× realistic cost. Capacity ≥ 10×
target AUM. Then write down what AUM makes it stop working.

**Step 9 — paper trading / incubation.** Minimum 3 months, ideally 6, with the exact execution you'll use.
Compare realised IC to predicted IC. If realised IC is below the predicted confidence interval, do not
allocate; find out why first.

**Step 10 — allocate small, and scale on evidence.** Not "backtest says Sharpe 2, so lever to the sky."
Start at a size where the maximum acceptable loss is survivable, scale only as live evidence accumulates.

---

## 3. A one-page scorecard

Score each 0–3. Below 15/30, don't trade it; 15–22, paper trade; above 22, allocate small.

| criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| mechanism clarity | none | hand-wave | one named counterparty | counterparty + why they persist |
| data quality | non-PIT | partially clean | PIT, no survivorship | PIT + vintage archive |
| statistical strength | t<2 | t 2–3 | t>3 | t>4 *and* OOS |
| out-of-sample | none | 1 split | walk-forward | multiple countries/decades |
| cost margin | breakeven ≈ cost | 1.5× | 3× | 5×+ |
| capacity | < 1× AUM | 3× | 10× | 50×+ |
| novelty | clone | correlated | residual alpha | orthogonal |
| crowding | extreme | rising | normal | uncrowded |
| tail risk | ruinous | fat left tail | manageable | convex |
| decay outlook | dying now | unclear | mechanism intact | structurally blocked |

---

## 4. Sizing

**The formula.** For a strategy with expected excess return μ and variance σ², on a portfolio with other
strategies:

```
w_i  ∝  μ_i / (σ_i² · (1 + estimation_error_penalty))  ×  diversification adjustment
```

In practice everyone uses the same shortcuts, in increasing order of sophistication:

1. **Vol targeting**: scale to a fixed portfolio volatility. Necessary, not sufficient.
2. **Inverse-vol across strategies** (risk parity): equal risk, not equal capital. Simple, robust, and hard
   to beat.
3. **Mean-variance with shrunk means** (Bayes-Stein / James-Stein on μ): estimate μ as a shrunk version of
   the historical mean toward the cross-strategy average. Without shrinkage, MVO is an error-maximiser.
4. **Fractional Kelly**: `f = κ · μ/σ²` with κ ≈ 0.25–0.5. Kelly with estimated μ and fat tails overbets
   catastrophically; fractional Kelly costs you a bit of growth and buys you survival.
5. **Drawdown-aware**: cap the size so that the 95th-percentile drawdown implied by the strategy's own
   history is within the fund's tolerance. Recompute with the *worst* variant of the strategy you can
   imagine, not the backtest's.

**Three sizing rules that are not negotiable:**
- **Size for the tail, not the Sharpe.** Skew-adjusted sizing. A strategy with −3 skew needs roughly half
  the weight of a symmetric one with the same Sharpe.
- **Correlation is state-dependent.** Size using the correlation in the *bad* state (all strategies losing
  together), not the average.
- **Decay-adjusted capital allocation.** If half-life is 4 years, don't build a 10-year business plan on it
  (see the PV formula in file 03 §3.4).

---

## 5. Combining edges (the only real free lunch)

The mathematics of diversification of *decay clocks*:

```
If you have n strategies, each with alpha decaying at rate λ_i and independent shocks,
portfolio alpha(t) = Σ a_i e^{−λ_i t}.
With staggered λ (e.g. 0.3, 0.2, 0.1, 0.05 per year), the portfolio's alpha decays to half
its initial value in ~T years where T solves Σ a_i e^{-λ_i T} = 0.5 Σ a_i.
```

With four equally-weighted strategies at λ = 0.3, 0.2, 0.1, 0.05 (half-lives 2.3, 3.5, 6.9 and 13.9
years), the half-life of the *blend* is **4.9 years** — versus 2.3 years for the fastest alone, and it keeps
**29% of its alpha after 10 years where the fastest one keeps 5%**. Notebook cell 9 computes it. The gain is
real but it is not magic: blending buys you a factor of about two in half-life, and it also cuts the
variance of the outcome sharply (your fund's death is no longer a single draw).

The bigger effect is *renewal*: if you keep adding strategies at roughly the rate they decay, the portfolio
does not decay at all in steady state. Most long-lived funds are not running better strategies than the
dead ones — they are running a research process that replaces them. **This is the real argument for a
multi-strategy shop: not Sharpe, survival.**

Two practical corollaries:
- **Prefer low mutual correlation over high individual Sharpe.** Twenty signals at IC 0.03 with 0.2 mutual
  correlation beat five signals at IC 0.05 with 0.8 correlation.
- **Stagger your research vintages.** If everything you run was discovered in the same 18-month window, you
  have one strategy with many names, and one decay clock.

---

## 6. Common ways a good edge is destroyed by implementation

| failure | mechanism | fix |
|---|---|---|
| **Over-trading** | rebalancing a slow signal monthly because "more data" | match rebalance frequency to IC half-life |
| **Ignoring the bid-ask bounce** | measuring signal returns off mid-quotes, trading at the touch | use effective spreads and lag the trade |
| **Chasing fills** | assuming you trade at the close you predicted from | model a delay; measure the alpha lost per minute |
| **Unmodelled borrow** | shorting names that cost 30%/yr to borrow | pull borrow data; exclude hard-to-borrow |
| **Capacity blindness** | backtesting 500 names, trading 50 | simulate your actual tradable universe and participation rate |
| **Silent leverage** | using the strategy's own vol as if it were fixed | vol-target with a cap and a floor |
| **Benchmark mismatch** | a long-only portfolio judged vs a benchmark it can't deviate from | compute TC; the mandate is part of the strategy |
| **Data leakage through the universe** | "we only trade stocks that exist today" | point-in-time universe, include delistings |
| **Restatement leakage** | using the current value of a fundamental | vintage the data |

---

## 7. Anti-patterns in research culture

- **The hero model.** One researcher, one giant model, no independent replication. When it breaks, nobody
  can fix it and nobody can argue with it.
- **Sharpe-based promotion.** Rewards overfitting, because the highest backtest Sharpe wins. Reward
  *pre-registered predictions that came true* instead.
- **No negative results ledger.** If the firm doesn't record what was tested and failed, it will re-test it
  every 18 months, and its multiple-testing problem grows without anyone noticing.
- **One dataset.** Everyone using the same vendor's cleaned panel is a crowding mechanism in itself.
- **Confusing research with backtesting.** The backtest is the last 10% of the work.

---

## 8. Monitoring: the monthly dashboard

Twelve numbers, every month, for every strategy. Anything outside its band gets a written explanation.

```
1.  realised gross alpha (MTD, YTD, ITD)     vs. backtest expectation
2.  realised net alpha                        vs. gross (this ratio is your execution quality)
3.  rolling 12m IC and IC_IR                  vs. confidence band from the backtest
4.  rolling 24m Sharpe                       vs. the backtest's 5th percentile
5.  turnover realised vs. modelled            (a rise here usually precedes a fall in net alpha)
6.  cost per unit traded, realised vs. modelled
7.  capacity used (AUM / capacity estimate), and participation rate by name
8.  crowding proxies: borrow utilisation, short interest in your names, factor valuation spread
9.  correlation to your other strategies and to the market in the tail
10. tracking error to the strategy's own model portfolio  ← the earliest decay signal, usually
11. days since the last independent (non-data) confirmation of the mechanism
12. the number of live strategies whose half-life has passed
```

**Number 10 is the one most people miss.** If the strategy's live portfolio drifts from the model portfolio,
the model is no longer describing the world — that precedes a P&L problem by months.

---

## 9. Detecting decay early (a procedure with thresholds)

1. **Control chart on rolling IC.** Plot 12-month rolling IC with a ±2σ band computed from the backtest
   period. Two consecutive months outside the lower band (or one outside 3σ) = investigate.
2. **Decompose the alpha.** Into (a) the signal's long-short spread return (the market side) and (b) your
   deviation (the execution side). If (a) is fine and (b) is bad, it's an implementation problem — check
   costs, fills, universe.
3. **Check the mechanism, not just the numbers.** Is the input variable still distributed the way it was?
   Is the borrow still available? Is the venue still the same? Is the data still arriving at the same time?
4. **Ask whether the effect is present in a market where you don't trade.** If a US equity signal has
   vanished in the US but persists in Japan, you're looking at local arbitrage, not death.
5. **Compute the implied half-life from the last 24 months** and compare it to your prior. If it has
   shortened by more than 50%, the clock has moved.

---

## 10. Kill rules (write them before you trade)

A decayed edge does not kill you. A decayed edge you keep trading at full size does. Templates:

**Rule A — statistical.** "If rolling 24-month net alpha has a t-statistic below −1 for two consecutive
months, reduce size by 50%. If the rolling 36-month net alpha is negative, stop."

**Rule B — mechanism.** "If [the input variable / the borrow / the flow] changes structurally, re-underwrite
from zero before the next rebalance." (E.g. the exchange changes the tick size; the vendor starts selling
your dataset to everyone; the index provider changes the rebalance methodology.)

**Rule C — capacity.** "If AUM exceeds 60% of the estimated capacity, cap the strategy and distribute excess
to other strategies."

**Rule D — crowding.** "If the factor valuation spread enters the top decile *and* our correlation with the
crowded factor rises above 0.8, halve. Expect the crash, don't predict its timing."

**Rule E — time.** "Every strategy gets a scheduled re-underwriting 3 years after launch, regardless of
performance. Half-lives are short; a strategy that hasn't been re-examined is a position, not a strategy."

---

## 11. The 10-line summary of this whole project

1. Edge is a **product** of signal quality, breadth, transfer, cost margin and persistence — any zero kills it.
2. **Mechanism first.** If you can't name the counterparty, you are the counterparty.
3. The measurement error is enormous: with 3 years of data, a Sharpe of 1.0 is indistinguishable from 0.
4. **Multiply your trials.** t>3 is the honest hurdle, and deflated Sharpe is how you compute it.
5. Half of a typical backtest's alpha is overfitting, and it dies on the first out-of-sample day.
6. The other half dies after publication, on a half-life of roughly **4–9 years** for equity anomalies, with
   a **58% total decline** (McLean & Pontiff) and an end state near **4bp/month net** (Chen & Velikov).
7. Decay is often **migration** (to smaller, illiquid, newer, faster places) rather than death.
8. Costs, borrow, capacity and turnover bound the strategy before the statistics do.
9. Diversify **decay clocks**, not just returns; the blend's half-life is much longer than any component's.
10. Write the kill rule first. Every edge is a perishable good with an expiry date you don't get told.
