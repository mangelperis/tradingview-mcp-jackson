# Referencia canónica: buffet_value_invest.md

> Fuente permanente proporcionada por el usuario; cuerpo conservado sin cambios.
> Se ha retirado únicamente el frontmatter de la fuente independiente.

## Índice de la fuente

- Authority and integration
- Core principle
- Decision flow
- Universe eligibility
- Defaults (classification baseline)
- Durable-compounder gate
- Structural-break test
- Derived prices
- Quality gate (hard; fail-closed)
- Valuation discipline
- Weekly 200-period timing overlay
- Retail-crowding overlay
- Short-interest and institutional-ownership overlay
- Badge classification (priority order)
- Meaning (for search / ranking)
- Mapping to the canonical 0–100 score
- Actionability overlay
- Portfolio construction and concentration
- Holding-period discipline
- Index fallback rule
- Manual search proxies (when full DCF is unavailable)
- Output when screening
- Final operating rule

---

# Buffett Value Screen Rules

## Authority and integration

This file is a specialized fundamental submodule of `estrategia_inversion.md`. It produces a Buffett badge, quality diagnostics, and a score cap; it does not replace the canonical 0–100 score or authorize technical execution.

Precedence:

```text
estrategia_inversion.md > buffet_value_invest.md
```

Hard integration rules:

- `structuralBreak = true` always forces the canonical decision `NO TRADE`.
- A weekly-200 breach is a research trigger, never an automatic entry.
- GOLD/GREEN still require the technical and risk gates of the canonical framework.
- Prices and derived levels remain in the asset's quotation currency only.

Use these rules to classify equities. Stocks/financial issuers only. Ignore crypto, currencies, and most futures.

Do not invent numbers. If a required input is missing, mark that check `NA` and fail closed where stated.

## Core principle

The objective is not to promise that a rule will beat the S&P 500. The objective is to combine:

1. A durable, understandable business.
2. High returns on incremental capital.
3. Conservative financing and reliable owner earnings.
4. A purchase price below conservative intrinsic value.
5. A long-term technical dislocation that offers favorable asymmetry.
6. Patience, low turnover, and enough concentration to matter without creating portfolio fragility.

A quality company below its 200-week moving average is a **research trigger**, not an automatic purchase. First determine whether the decline is a temporary scare, a valuation reset, or evidence that the business has structurally deteriorated.

## Decision flow

Evaluate in this order:

1. `eligibleUniverse`
2. `compounderPass`
3. `structuralBreak`
4. `canValue` and DCF
5. `qualityPass`
6. `weekly200Context`
7. `crowdingRisk`
8. `shortThesisRisk`
9. badge classification
10. portfolio fit and execution decision

No single signal overrides the full sequence.

## Universe eligibility

Prefer companies with:

- At least 5 years of operating history, preferably 10.
- Audited financial statements and understandable segment reporting.
- Sufficient liquidity for the intended position size.
- Positive normalized owner earnings or a credible, evidence-based path to them.
- A business model that can be explained without relying primarily on narrative, total-addressable-market claims, or multiple expansion.

Exclude or mark `specialSituation = true` when the company is:

- Pre-revenue, binary biotech, highly promotional, or dependent on one regulatory event.
- A shell, SPAC-like structure, or serial reverse-split issuer.
- Persistently loss-making without a valuation method grounded in cash generation.
- Too opaque to estimate normalized owner earnings.

Special situations cannot receive an actionable GOLD/GREEN conclusion under this screen without a separate framework.

## Defaults (classification baseline)

| Parameter | Default | Unit |
|-----------|---------|------|
| Cash base | Owner earnings per share (else FCF/share) | currency / share |
| Stage-1 growth `g1` | 8 | % |
| Terminal growth `gT` | 2.5 | % |
| Discount rate `r` | 10 | % |
| Projection years `N` | 10 | years |
| Margin of safety `MoS%` | 25 | % |
| Equity bridge | ON | — |
| Min ROIC (else ROE) | 10 | % |
| Min operating margin | 10 | % |
| Max net debt / equity | 1.0 | ratio |
| Preferred median ROIC | 12 | % over 5 years |
| Preferred FCF conversion | 80 | % of net income |
| Max position size | 10 | % of portfolio |
| Preferred portfolio size | 8–15 | holdings |

## Durable-compounder gate

`compounderPass` is separate from the minimum quality gate. It identifies businesses capable of compounding intrinsic value for many years.

### Required evidence

All required checks must pass. Missing data means `compounderPass = false`.

| Check | Preferred evidence | Pass condition |
|-------|--------------------|----------------|
| Returns on capital | 5-year median ROIC | `≥ 12%`, or clearly above estimated WACC |
| Incremental economics | Incremental ROIC or reinvestment returns | Positive and not structurally declining |
| Margin durability | Gross and operating margins | Stable or improving through a full cycle |
| Cash conversion | Cumulative FCF / cumulative net income | `≥ 80%` over 5 years, adjusted for justified investment cycles |
| Balance sheet | Net debt, interest coverage, maturities | Debt service remains comfortable under a downside case |
| Reinvestment runway | Organic growth opportunities | Can reinvest meaningful capital without destroying returns |
| Shareholder discipline | Dilution, buybacks, acquisitions | No persistent value-destructive dilution or empire building |
| Business clarity | Revenue drivers and unit economics | Explainable, monitorable, and not dependent on one heroic assumption |

### Preferred qualitative traits

- Recurring or repeat revenue without excessive customer concentration.
- Pricing power demonstrated by stable volumes and margins after price increases.
- Low capital intensity, or high capital intensity paired with regulated/contracted returns.
- Switching costs, network effects, scale advantages, cost leadership, brand strength, or scarce assets.
- Management incentives aligned with per-share value creation rather than revenue growth alone.

### Compounder failure conditions

Set `compounderPass = false` when any of the following is material and persistent:

- ROIC is below the cost of capital without a credible recovery.
- Margins are structurally compressing.
- Growth requires accelerating dilution or leverage.
- Acquisitions regularly consume cash without improving per-share economics.
- Customer, product, supplier, or regulatory concentration creates binary risk.
- The thesis depends primarily on paying a higher multiple later.

## Structural-break test

A price below the 200-week moving average is only attractive if `structuralBreak = false`.

Set `structuralBreak = true` when evidence supports one or more of these:

- Permanent demand impairment or product obsolescence.
- Loss of moat, pricing power, distribution, licenses, or key intellectual property.
- Accounting irregularities, auditor resignation, repeated restatements, or aggressive capitalization.
- Debt maturity/refinancing risk that can force dilution or asset sales.
- A regulatory or legal change that materially lowers normalized owner earnings.
- Management credibility failure, capital-allocation failure, or governance abuse.
- A lasting step-down in normalized margins, returns on capital, or cash conversion.
- Share count growth that overwhelms per-share operating progress.

If `structuralBreak = true`:

- Do not treat the weekly-200 breach as a value opportunity.
- Keep the raw valuation badge for diagnostic purposes, but force `actionability = NO_TRADE` and display a `STRUCTURAL_BREAK_OVERRIDE`.
- Do not describe a raw GOLD/GREEN badge as investable while the override is active.
- Require a new thesis and fresh normalized financial estimates before reconsideration.

## Derived prices

### Cash base `cf0`

- Prefer **owner earnings / share**.
- Owner earnings should approximate normalized operating cash flow minus maintenance capex and other recurring cash requirements.
- If maintenance capex mode treats D&A as maintenance, owner earnings / share may approximate **net income / shares**, but document why.
- Else `cf0 = free cash flow / share`.
- Use normalized, cycle-aware cash flow rather than one unusually strong year.
- **Rule:** `cf0` must be `> 0`. Else cannot value.

### Two-stage DCF → `cashflowPv`

1. Grow `cf0` for years `1..N` at `g1` as a decimal.
2. Discount each year’s cash flow at `r`.
3. Terminal value at year N: `CF_N × (1 + gT) / (r − gT)`, discounted `N` years.
4. `cashflowPv` = sum of discounted stage-1 cash flows + discounted terminal value.

**Rules:**

- IF `r ≤ gT` THEN cannot value.
- IF `cf0 ≤ 0` OR `cf0` missing THEN cannot value.
- IF the business is highly cyclical, use normalized mid-cycle `cf0` and a conservative `g1`.
- IF growth requires large incremental capital, do not apply revenue or EPS growth directly to owner earnings without checking reinvestment needs.
- Run bear/base/bull sensitivities. The badge baseline uses the conservative base case, not the bull case.

### Equity fair value `FV` (blue line)

- Net debt = total debt − cash.
- Net debt / share = net debt / diluted shares.
- IF bridge ON AND debt, cash, and diluted shares are available THEN  
  `FV = cashflowPv − (total debt − cash) / diluted shares`
- IF bridge ON AND debt/cash/shares are missing THEN  
  `FV = cashflowPv` and mark `equityBridge = SKIPPED`.
- IF bridge OFF THEN  
  `FV = cashflowPv`.
- Add non-operating assets only when they are separable, realizable, and not already contributing to `cf0`.
- Deduct material pension deficits, preferred claims, minority interests, or recurring stock-based compensation when relevant.

### Buy-under / margin-of-safety price `BuyUnder` (green line)

```text
BuyUnder = FV × (1 − MoS% / 100)
```

With defaults: `BuyUnder = 0.75 × FV`.

Increase the required margin of safety to 30–40% when:

- Cash flows are cyclical or commodity-linked.
- Leverage is elevated.
- The moat is uncertain.
- The valuation depends heavily on terminal value.
- Management has a weak capital-allocation record.

## Quality gate (hard; fail-closed)

All three minimum checks must pass. Any `NA` on a required check means that check fails and `qualityPass = false`.

| Check | Metric | Pass condition (defaults) |
|-------|--------|---------------------------|
| Return | ROIC if available, else ROE | `≥ 10%` |
| Margin | Operating margin | `≥ 10%` |
| Leverage | `(total debt − cash) / stockholders equity` | `≤ 1.0` |

**Rules:**

- IF ROIC is missing THEN use ROE for the return check.
- IF ROIC and ROE are both missing THEN return check FAIL.
- IF operating margin is missing THEN margin check FAIL.
- IF equity is missing, equity equals zero, or net debt is missing THEN leverage check FAIL.
- For banks and insurers, replace industrial-company leverage and FCF checks with sector-appropriate capital, reserving, underwriting, and book-value metrics.
- `qualityPass = return PASS AND margin PASS AND leverage PASS`.

The hard quality gate is a minimum threshold. `compounderPass` is the stronger standard for long-term concentration.

## Valuation discipline

Valuation matters even for exceptional businesses.

- Compare current and forward P/E, EV/EBIT, EV/FCF, and FCF yield with the company’s own history and relevant peers.
- Treat 40–50× earnings as requiring unusually durable growth, high incremental returns, and low disruption risk. Do not assume growth persists indefinitely.
- Reject valuations where most of the DCF depends on aggressive terminal assumptions.
- Use per-share growth, not total-company growth, when dilution is material.
- A high-quality company can still be a poor investment at an excessive price.
- A statistically cheap company can still be a value trap when normalized owner earnings are declining.

## Weekly 200-period timing overlay

Use the weekly 200-period moving average, preferably `WMA200_weekly`; use `SMA200_weekly` only when WMA is unavailable and label the substitution.

### Context states

```text
IF price >= weekly200 AND weekly200_slope > 0:
    weekly200Context = ABOVE_RISING
ELSE IF price < weekly200 AND weekly200_slope > 0:
    weekly200Context = BELOW_RISING
ELSE IF price < weekly200 AND weekly200_slope <= 0:
    weekly200Context = BELOW_FLAT_OR_FALLING
ELSE:
    weekly200Context = MIXED
```

### Interpretation

- `ABOVE_RISING`: trend intact; valuation must still justify purchase.
- `BELOW_RISING`: preferred research zone for a proven compounder when the business remains intact.
- `BELOW_FLAT_OR_FALLING`: higher probability of prolonged impairment; demand a larger margin of safety and evidence of stabilization.
- `MIXED`: no timing edge.

### Entry requirements below the weekly 200

Do not buy solely because price is below the line. Require:

1. `compounderPass = true`.
2. `structuralBreak = false`.
3. Price `≤ FV`; prefer `≤ BuyUnder`.
4. Normalized owner earnings remain positive.
5. Debt and liquidity remain safe under a bear case.
6. Evidence of price stabilization: base formation, failed breakdown, higher low, or reclaim of the weekly-200 line.
7. No unresolved earnings, legal, accounting, or refinancing event capable of invalidating the estimate.

### Staging

- Initial research tranche: only after the fundamental and valuation gates pass.
- Full position: only after stabilization or trend repair.
- Do not average down mechanically while estimates are falling.
- Use the portfolio risk framework; no holding exceeds 10% of portfolio cost without an explicit exception.

## Retail-crowding overlay

Heavy retail attention is a risk factor because it can coincide with promotional narratives, unstable positioning, elevated options activity, and valuation disconnected from owner earnings. It is not proof that a company is poor.

### Evidence of crowding

Assess with available data:

- Abnormally high social/search attention relative to company size.
- Persistent ranking among most-traded retail names.
- Call-option volume or implied volatility far above normal without matching fundamental change.
- Rapid multiple expansion accompanied by promotional narratives.
- High turnover, low float, meme-like price gaps, or repeated short-squeeze behavior.
- Management promotion that emphasizes stock price, themes, or adjusted metrics over cash economics.

### Classification

```text
crowdingRisk ∈ {LOW, MODERATE, HIGH, NA}
```

- `LOW`: little evidence of speculative crowding.
- `MODERATE`: attention is elevated but valuation and ownership remain orderly.
- `HIGH`: speculation dominates price discovery or valuation.
- `NA`: insufficient data.

### Rules

- `HIGH` crowding prevents an aggressive new position even when the badge is GOLD/GREEN.
- Require a wider margin of safety and smaller initial size when `crowdingRisk = HIGH`.
- Do not automatically reject a widely followed mega-cap; distinguish broad ownership from speculative crowding.
- Prefer quiet, underfollowed setups only when liquidity, disclosure quality, and business evidence remain adequate.

## Short-interest and institutional-ownership overlay

High short interest combined with low-quality sponsorship can signal informed opposition, financing risk, weak governance, or poor business economics. It can also arise mechanically from hedging, arbitrage, low float, or event-driven positioning. Investigate the thesis; do not infer causality from the percentage alone.

### Required fields

- Short interest as % of float.
- Days to cover.
- Borrow fee or utilization when available.
- Institutional ownership and its direction.
- Insider ownership and recent transactions.
- Convertible, merger-arbitrage, warrant, or hedging effects.
- The strongest documented short thesis.

### Risk classification

```text
shortThesisRisk ∈ {LOW, MODERATE, HIGH, NA}
```

Typical warning conditions:

- Short interest `≥ 10%` of float: investigate.
- Short interest `≥ 20%`, high borrow cost, or rising days-to-cover: severe warning.
- High short interest plus falling institutional ownership and weak liquidity: `HIGH` unless a mechanical explanation is documented.
- Low institutional ownership alone is not a veto for small caps, spin-offs, or newly listed firms.

### Rules

- `HIGH` short-thesis risk means `NO TRADE` until the thesis is rebutted with evidence.
- A squeeze is not a value thesis.
- Do not buy merely because short interest is high.
- When credible short claims involve accounting, solvency, product integrity, or regulation, set `structuralBreak = true` until resolved.

## Badge classification (priority order)

Evaluate top to bottom; first match wins.

| Priority | Badge | Condition |
|----------|-------|-----------|
| 1 | **GRAY** | Cannot value (`cf0` invalid, `r ≤ gT`, or `FV` unavailable) |
| 2 | **RED** | Can value AND `price > FV` |
| 3 | **AMBER** | Can value AND `price ≤ FV` AND `qualityPass = false` |
| 4 | **GOLD** | Can value AND `qualityPass = true` AND `price ≤ BuyUnder` |
| 5 | **GREEN** | Can value AND `qualityPass = true` AND `BuyUnder < price ≤ FV` |

Equivalently:

```text
IF NOT canValue → GRAY
ELSE IF price > FV → RED
ELSE IF NOT qualityPass → AMBER
ELSE IF price ≤ BuyUnder → GOLD
ELSE IF price ≤ FV → GREEN
ELSE → RED
```

## Meaning (for search / ranking)

| Badge | Meaning |
|-------|---------|
| GOLD | Cheap, at least the required margin of safety below FV, and minimum quality PASS |
| GREEN | Fair-to-cheap, at or below FV but above BuyUnder, and minimum quality PASS |
| AMBER | At or below FV but minimum quality FAIL |
| RED | Above FV |
| GRAY | Not valued |

The badge describes valuation plus the minimum quality gate. It does not by itself authorize a purchase.

## Mapping to the canonical 0–100 score

The canonical score remains calculated in `estrategia_inversion.md`. This module applies the following compatibility ranges and caps:

| Buffett result | Canonical integration |
|---|---|
| GOLD + `compounderPass = true` + no structural break | Compatible with score 80–100 |
| GREEN + `compounderPass = true` + no structural break | Compatible with score 70–89 |
| AMBER | Canonical score capped at 69 |
| RED | Canonical score capped at 59 |
| GRAY | Canonical score capped at 59 unless a robust alternative valuation is documented |
| `structuralBreak = true` | `NO TRADE` regardless of raw badge or arithmetic score |
| `shortThesisRisk = HIGH` | `NO TRADE` until rebutted with evidence |

A badge never adds points mechanically. It constrains the range that the full fundamental analysis may justify.

## Actionability overlay

```text
IF badge == GOLD
   AND compounderPass
   AND NOT structuralBreak
   AND crowdingRisk != HIGH
   AND shortThesisRisk != HIGH:
       actionability = HIGH_CONVICTION_FUNDAMENTAL_CANDIDATE

ELSE IF badge IN {GOLD, GREEN}
   AND compounderPass
   AND NOT structuralBreak
   AND shortThesisRisk != HIGH:
       actionability = FUNDAMENTAL_CANDIDATE

ELSE:
       actionability = NO_TRADE
```

A weekly-200 dislocation improves research priority only after the fundamental conditions above pass. Technical execution still requires canonical score ≥70, Phase 2 confirmation, and the risk module.

## Portfolio construction and concentration

Concentration can improve returns only when research quality, valuation, and risk control are strong. It can also magnify permanent capital loss.

### Default portfolio rules

- Preferred focused portfolio: 8–15 independently researched holdings.
- Maximum position at cost: 10% of portfolio unless a separate mandate overrides it.
- Start smaller when uncertainty, cyclicality, leverage, or event risk is elevated.
- Limit correlated exposure by sector, factor, geography, customer, and macro driver.
- Do not count multiple companies dependent on the same commodity, AI capex cycle, regulator, or customer as true diversification.
- Add to a winner when intrinsic value and business performance rise, not merely because price rises.
- Add to a loser only when the thesis, estimates, and balance-sheet safety remain intact and the canonical DCA conditions pass.

### Understanding test

Do not concentrate in a company unless the investor can state from memory:

1. How it makes money.
2. Why customers stay.
3. What determines margins.
4. How much capital growth requires.
5. The main balance-sheet risk.
6. The strongest bear case.
7. What evidence would invalidate the thesis.
8. A conservative range of intrinsic value.

Failure means WATCHLIST or NO TRADE; it does not justify a starter position.

## Holding-period discipline

- Prefer businesses that can compound per-share owner earnings for 10–20 years.
- Do not sell solely because price volatility increases or the market becomes bored.
- Revalue after material earnings, capital allocation, balance-sheet, or moat changes.
- Sell or reduce when price exceeds a defensible optimistic FV, the thesis breaks, opportunity cost becomes extreme, or portfolio risk becomes concentrated.
- Avoid trying to call every market top and bottom.
- Maintain market exposure through quality holdings or a broad index rather than repeatedly moving fully in and out.
- The edge sought is consistency, survival, and disciplined reinvestment, not exceptional one-year returns.

## Index fallback rule

Use a low-cost broad index instead of active stock selection when any of these apply:

- The investor cannot maintain current estimates and thesis reviews.
- The portfolio contains many names that are not understood deeply.
- Decisions are being driven by FOMO, social attention, or price action alone.
- Research is partial: reading summaries without checking filings, cash flow, debt, and valuation.
- The active process lacks documented rules and post-mortems.

Half-researched concentration is worse than deliberate indexing.

## Manual search proxies (when full DCF is unavailable)

Use to **shortlist only**. Final GOLD/GREEN still requires FV, BuyUnder, and the minimum quality gate.

1. 5-year median ROIC or ROE `≥ 10%`; prefer ROIC `≥ 12%`.
2. Operating margin `≥ 10%` and stable.
3. Net debt / equity `≤ 1.0`; prefer net cash or conservative debt maturities.
4. Positive normalized owner earnings or FCF per share.
5. Five-year cumulative FCF broadly supports reported earnings.
6. Share count is stable or declining unless dilution clearly creates more per-share value.
7. Price looks discounted versus a conservative earnings/FCF multiple or simple DCF using `g1=8%`, `r=10%`, `gT=2.5%`, `N=10`, subtracting net debt/share.
8. Require at least a 25% discount for GOLD; increase the margin for cyclicality or uncertainty.
9. Check whether price is below the weekly 200-period moving average and whether the line is rising or falling.
10. Check retail crowding, short interest, borrow conditions, institutional ownership, and the strongest bear thesis.

## Output when screening

For each ticker report:

### Valuation

- `price`
- `cf0`
- `FV`
- `BuyUnder`
- `upside% = (FV − price) / price`
- bear/base/bull sensitivity
- DCF assumptions and equity-bridge status

### Quality and durability

- return on capital: PASS|FAIL|NA with current and 5-year median values
- operating margin: PASS|FAIL|NA with current and historical range
- leverage: PASS|FAIL|NA
- FCF conversion: PASS|FAIL|NA
- reinvestment runway: PASS|FAIL|NA
- dilution/capital allocation: PASS|FAIL|NA
- `qualityPass`
- `compounderPass`
- `structuralBreak`

### Timing and positioning

- weekly WMA/SMA200 value, slope, and percentage distance
- `weekly200Context`
- evidence of stabilization or continued breakdown
- `crowdingRisk` with evidence
- short interest, days to cover, borrow conditions, institutional ownership
- `shortThesisRisk` and strongest bear case

### Decision

- `badge`: GOLD | GREEN | AMBER | RED | GRAY
- `actionability`: HIGH_CONVICTION_FUNDAMENTAL_CANDIDATE | FUNDAMENTAL_CANDIDATE | NO_TRADE
- portfolio-fit check: weight, correlations, and maximum permitted size
- one-line reason identifying the decisive rule
- explicit invalidation conditions

## Final operating rule

Buy a good business only when both the economics and the price are favorable. Treat fear, low attention, or a weekly-200 breach as sources of possible opportunity, never as substitutes for evidence. Hold while per-share intrinsic value compounds and the thesis remains intact. Use the index when the required research depth and discipline are absent.
