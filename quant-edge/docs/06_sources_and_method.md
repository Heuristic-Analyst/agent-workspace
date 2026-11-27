# 06 — Where this comes from: the corpus, the method, and its limits

*Read this before you trust a number in the other files.*

---

## 1. What was actually done

| step | what | result |
|---|---|---|
| 1 | Queried **OpenAlex** with 32 hand-written finance queries, each pulled twice (top-cited page + best-match page, 200 records each) | ~6,900 records |
| 2 | Queried **arXiv** (`export.arxiv.org/api`) restricted to `q-fin.*` with 29 topical queries | ~1,600 records |
| 3 | Fetched 27 canonical papers by exact title (OpenAlex `title.search`) that the topical queries had missed | 27 records |
| 4 | Deduplicated on normalised title | 8,458 unique |
| 5 | Filtered to genuine finance research: a finance/journal vocabulary test plus a noise blocklist that throws out physics, biology, engineering and social-science "momentum"/"value"/"alpha" papers | **4,655 papers, 3,610 with abstracts** |
| 6 | Scored by theme keywords, citation impact, abstract presence and venue credibility; picked round-robin across themes so no single topic dominates | **150 core papers** |
| 7 | Extracted the quantitative sentences from those 150 abstracts (`data/claims.txt`) and read them | the `evidence` in files 01–05 |

Coverage: 1950s → 2026, with 2,013 papers from the 2010s and 1,733 from the 2020s, 26% of them from arXiv
(so: the frontier, not just the published canon).

The files:

```
data/bibliography.json    8,458 records, all fields, ranked by relevance
data/corpus.csv           the 4,655 finance papers: rank, year, cites, themes, title, authors, venue, url, abstract
data/corpus_fin.json       same, machine-readable, with theme tags and scores
data/core.json            the 150 read closely
data/reading_list.md      the 150, human-readable, with links
data/claims.txt           the extracted quantitative claims, paper by paper
data/read/chunk_*.txt     the core abstracts in reading order
data/raw/                 every raw API response (one file per query) - re-run scripts/ to rebuild
scripts/                  collect.py, build_corpus.py, curate.py, reading_list.py, extract_claims.py, fetch_canon.py
```

Rebuild from scratch (needs network; OpenAlex charges $0.001/request and has a ~$0.10/day free budget, so a
full re-pull may need two days or an API key):

```
python3 scripts/collect.py all      # ~90 requests
python3 scripts/build_corpus.py     # local
python3 scripts/curate.py           # local
python3 scripts/reading_list.py     # local
python3 scripts/extract_claims.py   # local
```

---

## 2. The papers that carry the argument

If you read ten things, read these. They are the load-bearing citations in files 01–05.

**On what an edge is**
- Grossman & Stiglitz (1980), *On the Impossibility of Informationally Efficient Markets* — why edge must
  exist for markets to function.
- Grinold (1989), *The Fundamental Law of Active Management* — `IR = IC·√BR`.
- Clarke, de Silva & Thorley (2002), *Portfolio Constraints and the Fundamental Law* — the transfer
  coefficient, and why mandates eat half your edge.
- Shleifer & Vishny (1997), *The Limits of Arbitrage* — why mispricing persists: agency and horizon.
- Brunnermeier & Pedersen (2008), *Market Liquidity and Funding Liquidity* — liquidity spirals, and the
  reason "market-neutral" isn't.

**On decay — the core evidence**
- **McLean & Pontiff (2016)**, *Does Academic Research Destroy Stock Return Predictability?* — 97 predictors,
  −26% out-of-sample, **−58% post-publication**. The reference point for everything else.
- **Falck, Rej & Thesmar (2021)**, *Why and how systematic strategies decay* — publication year alone
  explains 30% of the variance of Sharpe decay, **+5pp per year of vintage**; overfitting proxies add 15%.
- **Chen & Velikov (2022)**, *Zeroing In on the Expected Returns of Anomalies* — 204 anomalies, **4bp/month**
  net after spreads, post-publication decay and modern technology.
- **Chen & Zimmermann (2019)**, *Publication Bias and the Cross-Section of Stock Returns* — the bias is only
  **−12.3%**, much smaller than the decay: the decay is mispricing being corrected, not statistics.
- **Chordia, Subrahmanyam & Tong (2014)** — all twelve major anomalies attenuate after decimalisation: the
  mechanism is the cost of trading, not just capital.
- **Green, Hand & Soliman (2011)**, *Going, Going, Gone?* — the accruals anomaly died, and hedge-fund capital
  is visible in the data as the killer.
- **Green, Hand & Zhang (2017)** — of 94 characteristics, 12 independent; after 2003, **two**.
- **Linnainmaa & Roberts (2018)**, *The History of the Cross-Section of Stock Returns* — most accounting
  anomalies fail when pushed backward in time: they were never general.
- **Hou, Xue & Zhang (2020)**, *Replicating Anomalies* — 65% of 452 fail at t>1.96, 82% at t>2.78.
- **Jensen, Kelly & Pedersen (2023)**, *Is There a Replication Crisis in Finance?* — the other side: most
  factors replicate, 13 themes, 93 countries. Read both sides.
- **Kurth, Eisler, Rej & Bouchaud (2026)**, *Is Trend Still Your Friend?* — the post-2009 death of short-term
  trend, and the tick-size explanation.
- **Volpati et al. (2020)**, *Zooming In on Equity Factor Crowding* — momentum rebalancing is 1–2% of order
  flow, and rising.

**On the machinery**
- Harvey, Liu & Zhu (2016) — **t > 3.0**, and "most claimed findings are likely false".
- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio* — the correction, with code in the notebook.
- Novy-Marx & Velikov (2016), *A Taxonomy of Anomalies and Their Trading Costs* — turnover <50%/month is the
  line between "survives costs" and "doesn't"; buy/hold spreads.
- Frazzini, Israel & Moskowitz (2018), *Trading Costs* — realised costs are far below the academic
  assumptions, for a large, patient, internalising manager. Do not generalise this to yourself.
- Almgren & Chriss (2001) — the execution frontier; Kyle (1985) and Glosten & Milgrom (1985) — the
  microstructure foundations.
- Gu, Kelly & Xiu (2020) — machine learning roughly doubles regression-based performance, and the winning
  signals are still momentum, liquidity and volatility (i.e. old things, better combined).
- Kelly, Pruitt & Su (2019), *Characteristics are Covariances* — characteristics as time-varying factor
  loadings; the cleanest bridge between the two views of the world.
- Daniel & Moskowitz (2016), *Momentum Crashes* — dynamic sizing roughly doubles alpha and Sharpe.
- Khandani & Lo (2010) — the August 2007 quant unwind, with timestamps.

---

## 3. Honest limits

**What this corpus is.** A large, well-organised *map* of the literature, biased toward what is cited,
English-language, and indexed by OpenAlex or posted to arXiv. 4,655 papers with metadata, 3,610 with
abstracts.

**What it is not.** I did not read 4,655 papers cover to cover. I read the metadata of all of them, the
abstracts of 150, and the quantitative claims of those 150 in detail, and I brought background knowledge of
the canon to the synthesis. Where a number in files 01–05 is quoted from an abstract it is marked or
obviously attributable; where it is a well-known result quoted from memory it says "approx."

**Known biases in the corpus:**
- **Citation-weighted**, so it over-represents older, well-cited work and under-represents the last two
  years — which is exactly where the decay evidence is freshest.
- **arXiv is noisy.** It contributes genuinely useful practitioner-grade work (Falck et al., Volpati et al.,
  Kurth et al. are all preprints) and also a lot of machine-learning papers with implausible results (see
  file 04, §12). The 150-paper core was filtered by venue and citations, which helps but does not fix it.
- **Publication and file-drawer bias.** The published record overstates every effect. The whole point of
  files 03 and 05 is that you should shrink what you read before you believe it.
- **OpenAlex budget.** The daily free tier ran out partway through the canonical-title pass (27 of 50
  titles landed). A handful of classics are therefore cited from knowledge and are in the reading list by
  name but not as rows in `corpus_fin.json`. Re-running `scripts/fetch_canon.py` on another day fixes it.

**Three specific claims in this project that I would double-check before relying on them:**
1. The 4–9 year half-life for a published equity anomaly is my *inference* from McLean-Pontiff's 58% and
   the Chen-Velikov endpoint, not a number either paper prints. Both papers give the numbers; neither fits
   an exponential.
2. "Roughly 40–50% of decay is overfitting, 25–35% is arbitrage" (file 03 §2) is my synthesis of
   McLean-Pontiff's 26/32 split, Chen-Zimmermann's 12.3% bias adjustment and Falck et al.'s 45% of
   explained variance. It is a reasonable reading, not a published estimate.
3. The capacity numbers in file 02 and notebook cell 8 are a toy model with round numbers. The *structure*
   (capacity ∝ alpha²·H²·ADV) is right; the levels are illustrative.

**What would make this project better:** full-text (not abstract) reading of the 20 most important decay
papers; a proper meta-analysis of decay estimates instead of a narrative review; and extending the corpus
to SSRN working papers, which is where practitioners actually publish and where the fresh evidence lives.
