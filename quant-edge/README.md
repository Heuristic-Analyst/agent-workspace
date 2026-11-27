# quant-edge — what an edge is, what it looks like, and how fast it dies

A research project on the economics of alpha in quantitative finance: where returns above the risk you take
come from, what measurable shape an edge has, and the evidence on how fast it decays — plus the arithmetic,
worked examples, and a validation playbook you can run.

**Corpus:** 4,655 finance papers (8,458 unique records pulled, 1950s–2026), 150 read closely.
**Output:** five essays, a notebook of computations, and the whole machine-readable bibliography.

---

## Start here

| file | what's in it |
|---|---|
| [`docs/01_what_is_edge.md`](docs/01_what_is_edge.md) | definition, the decomposition, the arithmetic of IC × breadth, the five sources of edge, what edge is *not* |
| [`docs/02_anatomy_of_an_edge.md`](docs/02_anatomy_of_an_edge.md) | every measurable characteristic: IC, decay curve, turnover, cost hurdle, capacity, crowding, skew, stability, live-vs-backtest |
| [`docs/03_decay.md`](docs/03_decay.md) | **the core file.** Three kinds of decay, the seven mechanisms, the empirical evidence with numbers, the half-life math, how to measure it, how to detect it |
| [`docs/04_examples.md`](docs/04_examples.md) | 13 cases: momentum, value, carry, trend, accruals, PEAD, the factor zoo, alt-data, crypto basis, latency, and a case study of what edge is *not* |
| [`docs/05_playbook.md`](docs/05_playbook.md) | where to hunt, the 10-step research protocol, a scorecard, sizing, combining edges, monitoring dashboard, kill rules |
| [`docs/06_sources_and_method.md`](docs/06_sources_and_method.md) | how the corpus was built, the load-bearing papers, and the honest limits |
| [`notebooks/edge_lab.ipynb`](notebooks/edge_lab.ipynb) | the arithmetic, executed: breadth, holding period, deflated Sharpe, a simulated factor zoo, capacity, decay fitting, valuation, Kelly |
| [`data/reading_list.md`](data/reading_list.md) | the 150 core papers with links |

## The ten findings, in brief

1. **Edge = signal × breadth × transfer − costs, times persistence.** Any factor near zero kills the product;
   constraints (transfer coefficient) silently halve it.
2. **Breadth is not the number of stocks.** 500 names with 0.03 average residual correlation give an IR of
   0.78 at IC 0.04, not the 3.1 the naive law promises. At 0.15 correlation you have about two independent
   bets a month.
3. **The honest significance hurdle is t > 3, not 2.** The best of 100 zero-skill strategies shows a Sharpe
   of 1.13 over five years; the best of 1,000, 1.46.
4. **Half of a typical published anomaly is overfitting** (McLean & Pontiff: −26% out-of-sample) **and the
   other half dies after publication** (−58% in total).
5. **The end state is tiny.** Across 204 anomalies, net expected return after effective spreads,
   post-publication decay and modern trading technology: **4 basis points per month** (Chen & Velikov).
6. **Half-lives are short and measurable** — roughly 4–9 years for a published equity anomaly, with
   front-loaded decay; the accruals anomaly went from ~10%/yr to nothing in 15 years.
7. **Decay is mostly not "being found out."** Falck et al.: publication vintage alone explains 30% of the
   variance of Sharpe decay; overfitting proxies add 15%. Robustness, not secrecy, is what survives.
8. **Capacity scales with alpha² × holding period² × ADV.** The same signal supports $78m at 4%/yr and a
   21-day hold, and $1m at a 5-day hold. Liquidity, not insight, is the binding constraint.
9. **Decay migrates rather than dying:** to smaller names, newer markets, faster timescales, worse liquidity.
   An edge that "died" usually moved to a capacity band you can't operate in.
10. **Write the kill rule before you trade.** Every edge is a perishable good with an expiry date nobody
    tells you.

## Example of the arithmetic (from the notebook)

```
IC = 0.04, 500 names, monthly rebalance, residual correlation 0.03
    IR = IC · √(T·N/(1+(N−1)ρ)) = 0.04 · √376 = 0.78

Same signal, one-way cost 15bp, turnover 30%/month:
    cost drag = 0.30 × 0.0015 × 12 × 2 = 1.08%/yr

That signal requires >10 years of patience and about $80m of capacity to be worth the effort.
```

## Rebuild it

`scripts/` holds the whole pipeline (OpenAlex + arXiv → dedupe → finance filter → theme tagging → core
reading list → claim extraction). See `docs/06_sources_and_method.md` for the commands and the caveats.
