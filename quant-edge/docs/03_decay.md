# 03 — Decay: the central fact of the business

*An edge is a perishable good. This file is about how it perishes, how fast, why, how to measure it, and
what to do about it before and after you're trading it.*

---

## 0. Three completely different things called "decay"

People use one word for three phenomena with different causes, different math and different fixes. Getting
this straight will save you from most of the confusion in the literature.

| # | name | question it answers | typical scale | measured by |
|---|---|---|---|---|
| **D1** | **horizon decay** (IC decay) | how fast does my *signal's* predictive power fade with the forecast horizon? | days–quarters | `IC(k)` for k = 1…60 |
| **D2** | **historical decay** (alpha decay) | how fast does the *strategy's return* fade over calendar time? | years | rolling alpha / Sharpe, publication-date studies |
| **D3** | **intra-trade decay** | how much of the alpha do I destroy by trading into and out of the position? | minutes–weeks | execution shortfall vs. paper price |

D1 is physics: it determines your holding period and therefore your turnover and costs.
D2 is economics: it determines whether the business still exists.
D3 is engineering: it determines whether you actually capture what D1 and D2 promised.

A strategy can have a beautiful D1, be killed by D2, and never notice D3 until the P&L arrives. Or, very
commonly, it has a great D2 (it worked for 20 years) and a terrible D1 (the signal lasts three days), in
which case the backtest was a measure of your execution algorithm, not your idea.

---

## 1. D2: how fast published anomalies die — the evidence

This is the most-studied question in empirical asset pricing, and the results are remarkably consistent in
direction and remarkably inconsistent in size. The numbers worth knowing:

**McLean & Pontiff (2016, JF), "Does Academic Research Destroy Stock Return Predictability?"**
97 predictors from 57 papers. Returns fall by **26%** out-of-sample (same period, different stocks) and by
**58%** post-publication. The 26% is the pure statistical bias (the predictor was fitted, in part, to the
sample); the extra 32% is the market learning. This is *the* reference decomposition: **roughly half the
decay is statistics, roughly half is arbitrage.**

**Chordia, Subrahmanyam & Tong (2014, JFE)**
All twelve of the well-known anomalies they examine attenuate after decimalisation (2001) and the rise of
algorithmic trading. Their reading: **better technology and lower trading costs are the arbitrage
mechanism**, not just capital flows. The market didn't learn the anomaly, it got cheaper to trade.

**Green, Hand & Soliman (2011, Management Science), "Going, Going, Gone?"**
Sloan's (1996) accruals anomaly — one of the most famous edges ever documented — has decayed "to the point
that they are, on average, no longer reliably positive," and the demise tracks hedge-fund capital and
trading volume in extreme-accrual firms. **The most-cited anomaly in accounting died within 15 years, and
we know roughly who killed it.**

**Green, Hand & Zhang (2017, RFS)**
Of 94 characteristics, **12** were reliably independent determinants of returns over 1980–2014, but
"return predictability fell sharply in 2003 such that **just two** characteristics have been independent
determinants since then," and hedge returns outside microcaps have been statistically indistinguishable
from zero since 2003. This is decay measured as *the disappearance of the whole research programme*, not
one factor.

**Linnainmaa & Roberts (2018, RFS), "The History of the Cross-Section of Stock Returns"**
Extending data back to the 1920s, most accounting-based anomalies — including investment — look like an
artefact of data snooping: when examined out-of-sample by moving backward *or* forward in time, average
returns and Sharpe ratios **decrease** while volatilities and correlations with other anomalies
**increase**. The few that survive correlate with real structural shifts (physical → intangible capital,
rising debt reliance). Decay here isn't arbitrage; it's the discovery that the edge was never general.

**Chen & Velikov (2022, JFQA), "Zeroing In on the Expected Returns of Anomalies"**
204 anomalies, net of (i) effective bid-ask spreads, (ii) post-publication effects, (iii) the modern
trading-technology era from the early 2000s. **The average anomaly's expected net return is 4 basis points
per month.** The strongest net at most 10bp after controlling for data mining; combinations of anomalies
net around 20bp. Their conclusion: expected returns are negligible even with cost mitigation that "produces
impressive net returns in-sample" and even ignoring price impact.

**Chen & Zimmermann (2019, RAPS), "Publication Bias and the Cross-Section of Stock Returns"**
The counterweight, and an important one for calibrating your priors: publication bias alone shrinks returns
by only **12.3%** (s.e. 1.7pp) across 156 published long-short portfolios. The dispersion of returns across
predictors is too large to be explained by data-mined noise, and **the bias is much smaller than
post-publication decay** — which means the decay is mostly *mispricing being corrected*, not statistics.

**Falck, Rej & Thesmar (2021/22), "Why and how systematic strategies decay"**
The most directly useful paper for a practitioner. Using a large set of published anomalies, they regress
out-of-sample Sharpe decay on ex-ante characteristics. Findings:
- **The year of publication alone explains 30% of the variance of Sharpe decay across factors**, and each
  year later a factor is published, its (already worse) Sharpe decay is **5 percentage points larger**.
  Later-published factors are worse — consistent with a depleted pool, and with harder-to-arbitrage
  (weaker) effects being what's left.
- Variables tied to **overfitting** — the number of operations needed to compute the signal, and two
  measures of sensitivity of the in-sample Sharpe to outliers — **add another 15% of explanatory power**.
- Arbitrage-related variables add less. **Overfitting, not just crowding, is the dominant driver of what
  you observe as "decay".**

**Calluzzo, Moneta & Topaloglu (2019, Management Science)**
Direct evidence on the mechanism: institutional trading in 14 anomalies increases when the anomaly becomes
widely publicised and the necessary accounting data is released, concentrated in hedge funds and
high-turnover institutions, and this increase is directly related to the post-publication decay in returns.
Institutions are the arbitrageurs, and you can watch them arrive.

**Shanaev & Ghimire (2020, EJF)**
Across ten notable anomalies through 1926–2018, **academic attention** (article counts / citations) is the
single most dominant factor explaining the disappearance of abnormal returns — ahead of data-snooping bias,
institutional trading, and a pure time trend.

**Hou, Xue & Zhang (2020, RFS), "Replicating Anomalies"** vs.
**Jensen, Kelly & Pedersen (2023, JF), "Is There a Replication Crisis in Finance?"**
The famous disagreement, and you should know both sides:
- HXZ: of 452 anomalies, **65% fail** a t > 1.96 test with NYSE breakpoints and value-weighted returns, and
  **82% fail at t > 2.78**. Conclusion: most anomalies are not real.
- JKP: a Bayesian hierarchical model of replication on 153 factors finds the **majority replicate**, cluster
  into **13 themes**, work out-of-sample across **93 countries**, and — crucially — their evidence is
  *strengthened* rather than weakened by the large number of factors tested, because the hierarchical prior
  learns how much to trust the population of factors.
- Why they differ: construction (equal- vs value-weighted, breakpoints, microcap treatment), the choice of
  the null (independence vs a hierarchical prior over factors), and what counts as "the same factor".
  **Both are probably right about different sets.** The actionable reading: *the canonical, economically
  motivated themes replicate; the long tail of exotic microcap anomalies does not.*

**The trend-following case (Kurth, Eisler, Rej & Bouchaud, 2026)**
A clean, modern, physical example of D2. Systematic trend following was profitable for two centuries; since
about **2009**, short-term trends have stopped delivering. Using ~100 liquid futures, 1995–2025, plus an
industry CTA proxy, they test four explanations — capacity, electronification, regime change in CTA/order-flow
interaction, and a microstructural mechanism — and reject the first three on timing, magnitude or
cross-sectional heterogeneity. The winner is microstructural: **the cross-sectional variable that separates
degraded from surviving trends is the volatility-normalised tick size.** Where the tick got small relative
to volatility, post-2008 trend PnL collapsed. The edge did not die from being known; it died because the
market's *ability to absorb and reverse* a small directional push changed.

**Crowding, measured physically (Volpati et al., 2020)**
Rebalancing a momentum portfolio can explain **1–2% of total order flow** in US equities, and that share has
been rising. The crowding is visible in the aggregate imbalance data *before* it shows up in your P&L.

---

## 2. Why edges decay — the seven mechanisms

Ordered by how often they are actually the cause (my ranking, from the evidence above):

**M1. In-sample overfitting was always there.**
The "edge" never existed out of sample. Signature: the decay happens *immediately* on the first
out-of-sample day, and it's larger for signals with more parameters, more data transformations, or
outlier-sensitive statistics. Falck et al.'s finding that operations-count and outlier-sensitivity add 15%
of explanatory power is the fingerprint of M1. **Roughly half of McLean-Pontiff's 58% is this.**

**M2. Arbitrage capital arrives.**
Real capital sees the published return and trades it. Signature: decay *begins at publication*, is gradual
over 3–10 years, is larger for liquid, easy-to-short, high-capacity signals, and is preceded by rising
institutional ownership/volume in the extreme portfolios (Calluzzo et al.; Green-Hand-Soliman).

**M3. Trading costs fall for everyone, so the marginal arbitrageur arrives.**
Decimalisation, electronic execution, zero-commission retail. Signature: a discrete break around 2001
(Chordia et al.) or 2019–2020 (retail/options), affecting many unrelated anomalies at once.

**M4. The underlying economics change.**
The anomaly was a proxy for something real, and that thing changed: accruals shrank, intangibles became a
larger share of capital, the tick size changed, the index composition changed, shorting became cheap, the
borrow market matured. Signature: the *input variable* itself has a trend (Sloan's accrual magnitude;
Green-Hand-Soliman report exactly this, though they find it weaker than the capital story).

**M5. The market's microstructure changes the payoff function.**
Latency, tick size, auction design, fee structures, maker-taker, payment for order flow. Signature: the
signal still predicts returns in the data but the *fill* is no longer available, or the reversal that used
to generate the profit now happens 30 seconds before you can act. (Kurth et al.'s tick-size result.)

**M6. Regime dependence / conditional edges.**
The edge was real but only in one state of the world (high vol, high dispersion, tight funding, active
retail participation). Signature: the unconditional number decays while the conditional number doesn't;
rolling IC is bimodal. This is the most *fixable* form of decay — you can often trade the conditional
version (Daniel & Moskowitz's dynamic momentum roughly doubles alpha and Sharpe).

**M7. Your own success.**
Capacity, impact, and the fact that your flow moves the price you're forecasting. Signature: gross alpha
per unit of AUM declines with AUM; backtest-to-live ratio falls as you scale. This is not decay over time;
it's decay over size, and it's the one you control.

For any given decayed strategy, the honest attribution is roughly: **40–50% M1, 25–35% M2, 10–20% M4–M5,
the rest M6.** Which means: *when your strategy decays, the most likely explanation is that it was never
as good as you thought.*

---

## 3. The math of decay

### 3.1 Exponential (the default model)

If alpha decays at a constant proportional rate, `α(t) = α₀·e^{−λt}`, then the **half-life** is

```
h = ln 2 / λ          λ = ln 2 / h
```

Fit it by regressing `ln(α_t)` on `t` (weighted, and only on periods where the alpha estimate is
meaningful). With annual data and a 5-year half-life, λ = 0.139/yr: after 10 years you keep 25%, after 20
years 6%.

**Sanity check against the literature.** If McLean-Pontiff's 58% decline is spread over roughly the 5–10
years after publication, that implies an exponential half-life of about **4–9 years** for a typical published
equity anomaly. If you take Chen-Velikov's 4bp/month net as the *end state*, the implied half-life is
shorter. Both are consistent with the folk wisdom: **a published cross-sectional anomaly has a usable life
of about 5 years from the moment it's in a journal, less from the moment it's on SSRN.**

### 3.2 Hyperbolic (often a better fit, and it matters)

Many strategies look like they never quite die: a fast drop then a long slow tail. That is a hyperbolic
decay, `α(t) = α₀/(1 + t/h)`, whose half-life is `h` but which has a *fat tail*: at t = 9h you still have 10%.

Practical consequence: **fitting an exponential to a hyperbolic process makes you think it's dead when it
isn't, and vice versa if you extrapolate.** Fit both, look at which one the residuals prefer, and for
forecasting use the one that is worse for you (they differ most exactly in the horizon you care about).

### 3.3 Decay as a function of publication date (the Falck result)

Regressing out-of-sample Sharpe decay on characteristics gives a usable prior for a *new* signal:

```
expected Sharpe decay ≈ 0.05 × (publication_year − reference_year) + f(complexity, outlier_sensitivity)
```

Read the sign carefully: **later-published factors decay more** — 5 percentage points of Sharpe per year
of publication vintage. A factor published in 2020 should be expected to lose more of its Sharpe than one
published in 1995. This is the "depleted mine" effect and it is why replication studies of old anomalies are
more optimistic than tests of new ones.

### 3.4 The decay-adjusted value of a strategy

Discount the stream: the present value of an edge with initial alpha `α₀`, half-life `h`, discount rate `r`,
and a horizon `T` is

```
PV = ∫₀ᵀ α₀ e^{(−λ−r)t} dt = α₀ (1 − e^{−(λ+r)T}) / (λ + r)
```

With α₀ = 6%/yr, h = 5 years (λ = 0.139), r = 5%, T = ∞: PV = 6% / 0.189 = **31.7% of AUM**, before costs.
If you instead assumed the alpha lasted forever at 6% and discounted at 5%, you'd get 120% — you would
overpay for the business by 4×. **This is how people overpay for asset managers.**

### 3.5 D1: the IC decay curve, and why it sets your holding period

Signal predictive power typically decays roughly geometrically in the horizon:

```
IC(k) ≈ IC(1) · IC(1)^{k−1}    (equivalently: IC(k) = IC(1) · ρ^{k−1}, ρ = "signal persistence")
```

If monthly IC at 1 month is 0.05 and at 2 months is 0.03, then ρ ≈ 0.6 and the signal is essentially gone
by 6 months.

Your holding period balances **alpha accumulation** (hold while IC(k) is large) against **turnover cost**
(trade rarely). With `H` days per rebalance:

```
gross alpha per year ≈ (252/H) · IC(H) · σ_cs · √H
cost per year        ≈ (252/H) · [ τ·spread + τ·Y·σ_daily·√(τ·q) ]      τ = 1 − ρ^H,  q = position/ADV
```

The `√H` in the first line is the whole argument for holding longer: the same signal applied to a longer
window earns its IC on more risk. The `√(τq)` in the second is the argument against trading rarely: bigger
clips pay more impact per share.

Notebook cell 5 solves this for signals whose predictive power peaks at a natural horizon of 3, 10, 21 and
63 days. The result:

- the optimal rebalance interval is **0.6–0.8 × the horizon where IC peaks** — i.e. trade *before* the
  signal starts to die, not after;
- **trading daily destroys a slow signal**: a 21-day signal worth 1.8%/yr at its optimum is worth −0.1%/yr
  rebalanced daily, and the 63-day one goes to −0.5%/yr. Turnover, not IC, is what kills it;
- doubling IC roughly doubles net alpha, but the optimum holding period barely moves — so a better signal
  does not mean you should trade it faster.

Rule of thumb: **rebalance at 0.5–1× the IC peak horizon, and check the cost line before you believe the
alpha line.**

### 3.6 D3: intra-trade decay

Two distinct effects, easy to confuse:

- **Post-trade reversal** — you buy, and the price sags back. Size: comparable to the spread plus impact.
  It's the market charging you for demanding liquidity. It is not alpha decay, it's a cost, and it should be
  in your cost model.
- **True intra-position decay** — the alpha is realised over the holding period but *most of it arrives
  early* (the first day or week), while your execution takes longer. This is why a 3-day VWAP algo on a
  2-day IC half-life is a money-losing machine, and why the Almgren-Chriss (2001) efficient frontier is
  not a nicety but a core part of the strategy design.

---

## 4. How to measure decay on your own strategy

Do all four; they answer different questions.

**(1) Rolling IC.** 12-month rolling rank IC with a ±2 standard-error band. A drift down with the band
following is decay; oscillation inside the band is noise.

**(2) Structural break test.** Regress `α_t` on a constant and a post-publication/post-launch dummy; or run
a CUSUM / Chow test at candidate dates (your launch date, the date the paper circulated, a known
market-structure change). Report the break date with a confidence interval. Nasty detail: with strategies,
the "break" is usually gradual, so what you'll find is a slope change, not a jump.

**(3) Cross-sectional vs. time-series decay.** Decompose your return into (a) the return of the signal's
long-short spread and (b) your deviation from it (timing, sizing, execution). Decay in (a) is the market;
decay in (b) is you.

**(4) The control experiment that nobody runs.** Take a *synthetic* signal with the same autocorrelation,
turnover and factor exposures as yours, but no predictive power, and run it through your whole pipeline
including costs and execution. If your live results decay toward the synthetic's, you never had the edge.
This is the single best test for M1, and it is cheap.

---

## 5. What decay implies for how you build things

1. **Prefer edges whose decay is structurally blocked.** Risk premia (S1), institutional constraints (S5),
   and microstructure (S4) decay slowly or not at all. Mispricings (S2) decay on a clock set by publication
   and capital. Information (S3) decays with the price of the data.
2. **Build a portfolio of edges with uncorrelated decay clocks.** Your fund's life depends on the *joint*
   survival function: with 8 independent strategies each half-life 6 years, expected time to lose half your
   alpha is much longer than 6 years, and the variance of the outcome collapses. This is the actual argument
   for multi-strategy.
3. **Measure decay continuously, not annually.** By the time annual numbers show decay, you've paid for a
   year of it. Track rolling IC monthly with a pre-registered threshold.
4. **Prefer to be early.** The value of a signal is concentrated in the first 2–3 years after *you* find it,
   not after the journal finds it. Research speed is a return driver, not an efficiency.
5. **Assume half of every backtest is fake.** Then your position sizing, your hurdle rate, and your capacity
   estimates are all automatically more honest. (This is the practical use of the McLean-Pontiff and
   Falck et al. numbers: they let you pre-shrink a claimed Sharpe before you believe it.)
6. **Write the kill rule before you trade.** "If rolling 12-month net alpha is below X, or rolling IC t-stat
   is below Y for three consecutive months, we cut size by half and re-underwrite." Decay is only fatal when
   it's discovered late.

---

## 6. The decay diagnostic table

When a strategy stops working, work down this list in order. Each row tells you what to check and what the
answer implies.

| symptom | most likely mechanism | check | implication |
|---|---|---|---|
| dies on day 1 out-of-sample | M1 overfitting | operations count, outlier sensitivity, parameter count | never existed; kill |
| decays gradually over 3–10 yrs from publication | M2 arbitrage | institutional volume in extreme names; short interest | expect the rest to go; harvest while it lasts |
| decay starts at a specific date, all strategies at once | M3 costs / M5 microstructure | decimalisation, tick changes, fee changes | structural; the old version is gone forever |
| the input variable itself has a trend | M4 economics changed | plot the raw signal distribution over time | re-specify; the world moved |
| good in high-vol/high-dispersion only | M6 regime | conditional IC by VIX / dispersion / funding | trade it conditionally, size it down |
| decays with AUM, not with time | M7 capacity | alpha vs AUM curve | shrink, or find a slower cousin |
| IC stable but P&L falls | D3 execution | implementation shortfall, fill rates | fix the trading, not the model |
