# 02 — The anatomy: what an edge looks like when you measure it

*A checklist of the quantities that describe an edge, in the order you should compute them. Each has a
formula, a typical value, and the way it lies to you.*

---

## 0. The one-page version

| # | quantity | symbol | typical good value | what it tells you |
|---|---|---|---|---|
| 1 | gross alpha, annualised | α | 2–10% | is there anything here |
| 2 | t-stat of alpha | t | > 3.0 (after mining) | is it real |
| 3 | information coefficient | IC | 0.02–0.06 | quality of the forecast |
| 4 | IC information ratio | IC_IR = mean(IC)/std(IC) | > 0.3 | stability of the forecast |
| 5 | IC half-life | h | 1 day – 3 months | how fast the signal dies inside the trade |
| 6 | turnover | τ | 5–50%/month | how much it costs |
| 7 | breakeven cost | c* | > 3× actual cost | margin of safety |
| 8 | capacity | AUM* | > 10× your AUM | can you scale |
| 9 | residual alpha vs known factors | α⊥ | > 50% of α | is it new |
| 10 | crowding proxy | z_crowd | < 1.5σ | how many people are in your trade |
| 11 | skew / max drawdown | γ₁, MDD | γ₁ > −2 | how it kills you |
| 12 | live-vs-backtest slippage | δ | < 30% of gross | did the measurement lie |

If you can't fill this table for a strategy, you don't have a strategy, you have an opinion.

---

## 1. The return, and the only t-stat you should trust

```
α_net = mean(r_p − β·F) − costs
t     = α_net / (σ(α_net)/√T)
```

Two things that get faked constantly:

- **Annualising** by multiplying monthly numbers by 12 and dividing the standard error by √12 — fine, but
  the standard error must come from the *net* return series, not the gross one. Costs are not noise; they
  are a level shift with their own variance.
- **Ignoring how many things you tried.** If you tested 50 signal variants, the right hurdle is not
  t=2. The expected maximum t-stat of 50 pure-noise strategies is around `√(2·ln 50) ≈ 2.8` — so a t of
  2.8 from 50 tries is exactly what nothing looks like. Harvey, Liu & Zhu (2016) put the practical hurdle at
  **t > 3.0**; Bailey & López de Prado's (2014) deflated Sharpe ratio does the same adjustment explicitly
  and is what you should actually run (notebook, cell "deflated Sharpe").

**Rule of thumb:** with N independent trials, the hurdle scales like `√(2 ln N)`. 10 trials → 2.15.
100 → 3.0. 1,000 → 3.7. 10,000 → 4.3. This is why "we found a factor with t=3" from a machine-learning
search over thousands of features is worth approximately nothing.

---

## 2. The signal: IC and its decay curve

The IC is the correlation between your signal at time *t* and the return over *t+1*. Two versions:

- **Pearson IC** — linear correlation of standardised signal vs. return. Sensitive to outliers.
- **Rank IC (Spearman)** — correlation of ranks. The default for equity selection. Robust, and it's what
  "IC" means in most funds.

Report both, plus:

```
IC_IR   = mean_t(IC_t) / std_t(IC_t)      # stability, not size
hit     = P(sign(signal) == sign(return)) # for directional signals
```

Then the **IC decay curve** — the single most neglected diagnostic:

```
IC(k) = corr(signal_t, return_{t → t+k})     for k = 1, 2, 5, 10, 20, 60 days
```

Three canonical shapes, each with a different strategy design:

- **Monotone decay** (typical fundamental signal): strongest at 1–3 months, gone by 12. → Hold ~1 month,
  rebalance monthly. Trading faster adds cost, not alpha.
- **Reversal / negative at short horizons** (typical for anything mean-reverting, e.g. short-term reversal,
  or a signal built on a price move): positive at k=1 but *negative* at k=1 day because of bid-ask bounce.
  → You must wait out the bounce or you pay it.
- **Slow build** (information diffusion, e.g. complex accounting signals): IC rises for weeks before
  peaking. → Early is wrong; be patient, size up over time.

The area under the IC decay curve, divided by the cost of holding the position, gives you the optimal
holding period. That computation is in the notebook (cell 3) and it is the most directly money-making
calculation in this whole project.

**Typical magnitudes** (equity cross-section, monthly): IC 0.02 = marginal, 0.04 = good, 0.06 = excellent,
0.10 = either a very short horizon or a mistake. IC_IR above 0.5 monthly is exceptional.

---

## 3. Turnover, costs and the breakeven

Let `τ` be one-way turnover per rebalance (fraction of the portfolio traded), `c` the one-way cost in
return units (half-spread + impact + fees + borrow), `n` rebalances per year:

```
cost_drag_per_year = τ · c · n · 2         # ×2 because you buy and sell
```

Example: monthly rebalance, 30% one-way turnover, 15bp one-way cost → `0.30 × 0.0015 × 12 × 2 = 1.08%/yr`.
On a 4%/yr gross alpha, that is a quarter of your edge, silently.

**Breakeven cost** — the cost at which the strategy's net alpha hits zero:

```
c*  =  α_gross / (2 · τ · n)
```

If `c*` is not at least 3× your realistic cost estimate, do not trade it. Margin of safety is not optional
here because your cost estimate is the least reliable number you have (see §4).

**The Novy-Marx & Velikov (2016) result** is the most useful empirical anchor: studying a large set of
published anomalies, **most anomalies with turnover below 50% per month remain significant after costs when
you use a buy/hold spread** (stricter entry than exit requirements), and **few with higher turnover do**.
Turnover, not IC, is the first thing to check on any equity signal.

Cost components, in the order they usually surprise people:

1. **Half-spread** — visible in quotes, but the *effective* spread you pay is often 2–4× the quoted one in
   small caps.
2. **Impact** — your own footprint. Empirically close to a square-root law
   (`impact ≈ Y·σ_daily·√(Q/ADV)` with Y ≈ 0.5–1.0), which means impact grows with size but *sublinearly*.
   Doubling size does not double cost per share — it multiplies it by √2. This is the only reason large
   funds can exist.
3. **Timing/opportunity cost** — the alpha you lose while working the order. This is usually the biggest
   term for fast-decaying signals, and the reason a slow execution algorithm can destroy a good backtest.
4. **Borrow** — for shorts. A hard-to-borrow name can cost 10–100%/yr, which annihilates most short legs.
   Any small-cap long/short backtest that ignores borrow is fiction.
5. **Financing** — the leverage to make a 4%/yr edge into a 15%/yr return. Rates move; your edge doesn't.

---

## 4. Capacity

Capacity is the AUM at which impact eats the alpha. Rough model:

```
Given: alpha per unit of position a (annual), volatility σ, ADV, participation limit p (e.g. 10% of ADV),
       holding period H days.
Turnover per year ≈ 252/H.   Position size Q = AUM · w  (w = weight per name).
Cost per unit traded ≈ Y·σ_daily·√(Q/ADV).
Set  a = 2·(252/H)·Y·σ_daily·√(AUM·w/ADV)   →   AUM* = ADV/(w) · [ a·H / (2·252·Y·σ_daily) ]²
```

The important structure, not the exact constant: **capacity scales with the square of the alpha and with
the square of the holding period, and linearly with ADV.**

Consequences that people find surprising until they run the numbers (notebook cell 8, with ADV $50m per
name, 200 names, 2% daily vol, 5bp spread, alpha 4%/yr, 21-day holding):

| what changes | capacity |
|---|---|
| base: alpha 4%/yr, hold 21 days | **$78m** |
| alpha doubles to 8% | $371m |
| holding doubles to 42 days | $371m |
| both | $1.6bn |
| ADV falls to $10m (thin names) | $16m |
| holding falls to 5 days (fast signal) | **$1m** |

- Doubling alpha roughly quadruples capacity (slightly more than 4x, because the spread you subtract is
  fixed, so it is a larger share of a smaller alpha).
- Doubling holding period does the same. **Slow strategies can be big; fast strategies cannot.** A 5-day
  signal has 1/78th the capacity of a 21-day one on the same names.
- Capacity is per-name; a strategy concentrated in 50 names has 1/10th the capacity of the same signal
  spread over 500.
- Novy-Marx & Velikov find the *capacity to absorb new capital* is inversely related to turnover, and that
  size, value and profitability signals have the greatest capacity — exactly as the formula predicts.

---

## 5. Novelty: residual alpha

Regress your strategy on the standard factors (market, size, value, momentum, profitability, investment,
and whatever else is standard in your asset class) **and on other strategies you already run**:

```
r_p = α + β₁MKT + β₂SMB + β₃HML + β₄MOM + β₅RMW + β₆CMA + Σ γ_j·(your existing strategies) + ε
```

You want `α` to survive. If your "new" signal has β on momentum of 0.6 and its alpha disappears, you have a
momentum clone with worse infrastructure. Green, Hand & Zhang (2017) did this at scale: of 94 firm
characteristics, only **12** provided reliably independent information about average returns over
1980–2014 — and after 2003, **only two** did.

Related, and worth internalising: **a signal's value is its correlation with what you already own.** Twenty
signals with IC 0.03 and mutual correlation 0.8 are one signal. Twenty with correlation 0.2 are twenty.

---

## 6. Crowding

Crowding is the risk that the exit is narrower than the entrance. Observable proxies:

- **Short interest / borrow utilisation** in your long and short names, and its *change*.
- **Factor-level valuation spread**: the price of your factor relative to history (value spread, momentum
  spread). When the spread is at a 90th percentile, the trade is crowded *and* the forward return is
  usually high — a nasty, counterintuitive combination that has destroyed more funds than any single bad
  model.
- **Correlation of your returns with peers / with published factor returns** — rising correlation means
  the same flow is driving both.
- **Volpati et al. (2020)** build direct crowding metrics from order-flow imbalance and metaorder data, and
  find that rebalancing a plain momentum portfolio can explain **1–2% of total order flow** in US equities,
  a share that has been rising. That is the physical footprint of your trade being visible in the tape.
- **Khandani & Lo (2010)** on August 2007: they reconstruct the quant unwind minute by minute — two
  distinct liquidation waves (1 Aug 10:45–11:30, 6 Aug at the open to 13:00), starting in financials, long
  book-to-market, short earnings momentum. Crowding is not a metaphor; it has timestamps.

---

## 7. Shape of the risk

Same Sharpe, different animal. Three numbers:

- **Skewness.** Momentum has positive skew in normal times and catastrophic negative skew in rebounds
  (Daniel & Moskowitz 2016: momentum crashes happen in panic states, after market declines and high
  volatility, and coincide with market rebounds). Short volatility has permanent negative skew and looks
  like a genius for years.
- **Drawdown and recovery time.** A Sharpe-1 strategy with a 40% drawdown and 4-year recovery is
  uninvestable for most allocators regardless of its statistics.
- **Correlation to the market in the tail.** Compute correlation *conditional on the market being down more
  than 3%*. Many "market-neutral" strategies are only neutral in calm markets.

Sizing follows the shape, not the Sharpe. For a strategy with expected return μ and variance σ², the
growth-optimal fraction is `f* ≈ μ/σ²` (Kelly), and the growth rate at the optimum is `g* ≈ SR²/2` — so a
Sharpe-1 strategy grows at ~50%/yr in log terms *if you can lever it freely and know μ exactly*, which you
can't. In practice: fractional Kelly (¼ to ½), then cut again for estimation error and for the fact that
your μ estimate is the least reliable input.

---

## 8. Stability

The edge is a *time series*, not a constant. Plot these:

- **Rolling 12-month IC** and its confidence band. Is the IC slowly declining (decay) or bouncing around
  zero (noise)?
- **Rolling realised Sharpe** vs. the backtest's expectation.
- **Subsample splits**: pre/post 2003 (decimalisation/HFT), pre/post 2008 (funding), pre/post 2010
  (post-crisis regulation), pre/post 2020 (retail flow + zero-day options). If your edge only exists in
  one regime, say so out loud and size accordingly.
- **Cross-country / cross-asset replication.** An anomaly that exists in the US and nowhere else is more
  likely a data artefact than a law of nature. Jensen, Kelly & Pedersen (2023) test factors across 93
  countries; that is the standard to aspire to, and the reason their conclusion (most factors *do*
  replicate) differs so sharply from single-market replication studies.

---

## 9. The live-versus-backtest gap

Track four numbers every month once you trade:

```
1. gross backtest alpha (the promise)
2. gross live alpha (the model)
3. net live alpha (the business)
4. the ratio (3)/(1)  ← this is the only honest measure of your research process
```

A ratio below 0.3 means your backtest is a work of fiction. The typical causes, in order: costs
underestimated, fill assumptions too generous, survivorship or restatement in the data, the signal relies
on data that arrives later than you thought (point-in-time failures), and regime change. The last is rare;
the first four are the norm.

---

## 10. The full checklist

Copy this into the top of every new strategy memo.

```
[ ] Economic story: who is the counterparty and why do they lose?
[ ] Why it isn't arbitraged: what barrier protects it?
[ ] Data: point-in-time, no survivorship, no restatement, no look-ahead.
[ ] Gross alpha and t-stat (with multiple-testing adjustment).
[ ] IC, IC_IR, IC decay curve, optimal holding period.
[ ] Turnover, breakeven cost, realistic cost estimate (≥3× margin).
[ ] Capacity estimate at your target AUM and at 10× it.
[ ] Residual alpha against standard factors AND against my existing book.
[ ] Crowding proxies and their trend.
[ ] Skew, drawdown, tail correlation to the market.
[ ] Subsample stability and cross-market replication.
[ ] Kill criteria written down in advance: what number, what threshold, what date.
[ ] Size: fractional Kelly, capped by drawdown tolerance.
```
