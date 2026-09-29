# Pine Scripts Project Rules — Investment Swing Framework

## 1. Authority

The Investment Swing Framework is normative. Preserve this precedence exactly:

```text
estrategia_inversion.md > reglas_riesgo_tecnico.md > regla_tunel.md > tendencia_mercado.md > sentimiento_posicionamiento.md > automatizacion_sentimiento_semanal.md > temporary market reports and notes
```

Higher-precedence rules override lower-precedence rules and examples. Never promote an example, backtest result, chart pattern, or temporary market note into canonical policy.

Rule families: AUTH-*, EXT-*, FUND-*, TREND-*, MTF-*, TUNNEL-*, TECH-*, RISK-*, DCA-*, ALERT-*, BT-*, NR-*, MAINT-*.

- **AUTH-01:** The precedence chain above is the source-of-truth order.
- **AUTH-02:** Pine behavior must remain subordinate to the Investment Swing Framework.
- **AUTH-03:** A canonical threshold may change only when a higher-precedence framework source changes it explicitly.

## 2. Scope and non-goals

Pine is a technical decision-support and simulation layer. It may calculate chart observables, setup states, risk feasibility, visual diagnostics, semantic alerts, and strategy simulations for historically representable rules.

Pine must not:

- scrape or invent fundamentals;
- derive the framework fundamental score from technical indicators;
- infer real portfolio state from price history;
- infer framework market/sentiment state from technical price data unless a canonical deterministic source is explicitly supplied;
- treat broker execution as performed merely because a TradingView strategy order exists;
- prove framework profitability from a Pine backtest;
- enable autonomous short trading by default;
- create a universal monolithic indicator that silently absorbs every future framework extension.

## 3. Architecture

```text
Investment Swing Framework
        |
        | canonical policy
        v
External Decision State
score / structuralBreak / thesis state / market context / risk scalar / exposure
        |
        v
Pine Technical Engine
trend / Tunnel / MTF / ATR / volume / structure / P20 / technical DCA gates
        |
        v
Risk & Feasibility Engine
structural stop / protector stop / R / obstacles / concentration input
        |
        v
Execution State
BLOCKED / WAIT / CANDIDATE / CONFIRMED / ELIGIBLE
        |
        +--> Indicator: diagnostics + alerts
        +--> Strategy: historical simulation only
```

No module below External Decision State may recreate the framework fundamental score.

## 4. External data contract

Use three-state gate semantics:

```text
PASS
FAIL
UNKNOWN
```

Required external values include:

```text
fundamental_score: 0..100 | UNKNOWN
structural_break: true | false | UNKNOWN
position_state: NONE | OPEN | UNKNOWN
effective_risk_scalar: 0.00..1.00 | UNKNOWN
portfolio_exposure_after_trade: percent | UNKNOWN
market_regime: framework-defined state | UNKNOWN
sentiment_regime: framework-defined state | UNKNOWN
```

- **EXT-01:** UNKNOWN never evaluates as PASS for an execution gate.
- **EXT-02:** Missing external state must fail closed; no favorable hidden defaults.
- **EXT-03:** `fundamental_score`, `structural_break`, external regime state, real portfolio exposure, and `effective_risk_scalar` remain external unless valid deterministic source data is explicitly supplied.
- **EXT-04:** Manual/current external inputs may control present diagnostics but must not be represented as historically valid inputs for past bars.
- **EXT-05:** Broker-specific costs are external unless explicitly modeled as strategy commission/slippage assumptions.

## 5. State model

Prefer an explicit state machine over opaque `buySignal`/`sellSignal` expressions.

Canonical long-side states:

```text
BLOCKED_EXTERNAL
FUNDAMENTAL_ELIGIBLE
TECHNICAL_WATCH
SETUP_CANDIDATE
SETUP_CONFIRMED
RISK_VALID
EXECUTION_ELIGIBLE
POSITION_MANAGEMENT
```

State progression is diagnostic, not an instruction to place a real order.

- **FUND-GATE-01:** `score < 70` blocks a new long entry.
- **FUND-GATE-02:** `structuralBreak = true` blocks a new entry regardless of score and blocks aggressive DCA.
- **FUND-GATE-03:** `effective_risk_scalar <= 0.25` blocks a new individual-equity entry.
- **FUND-GATE-04:** External eligibility is true only when required external gates are PASS; UNKNOWN cannot advance to `FUNDAMENTAL_ELIGIBLE`.
- **FUND-GATE-05:** Technical evidence must never add points to `fundamental_score` or be displayed as the framework score.

Conceptually:

```text
fundamentalEligible =
    fundamental_score >= 70
    AND structural_break == false
```

Any UNKNOWN required input makes `fundamentalEligible = false` for execution authorization.

## 6. Technical engine

Pine may calculate deterministic chart observables including:

- SMA/WMA 20, 50, and 200;
- RSI(14);
- MACD and MACD histogram;
- ATR(14);
- OBV;
- relative volume;
- YTD high and P20;
- distance from daily SMA/DMA200;
- over-extension;
- documented support/resistance candidates;
- documented gaps;
- confirmed pivot-based market structure;
- Fibonacci levels with explicit deterministic anchors;
- Tunnel observables when their formulas/source series exist;
- higher-timeframe trend state;
- pullback/recovery/breakout conditions;
- structural stop candidates;
- ATR buffers;
- R-multiples and R/R;
- semantic alerts.

A new long setup may progress only when all applicable gates pass:

1. External/fundamental eligibility is valid.
2. Higher and setup timeframes are compatible.
3. Recovery/breakout is confirmed by the required close.
4. Named level/pattern/volume confluence exists.
5. Tunnel long context is compatible.
6. External market/context state is not blocking.
7. No material higher-timeframe obstacle blocks a viable 2R target.
8. A structural thesis stop can be defined.
9. A protector stop can be defined outside structure with a valid ATR buffer.
10. Net `R/R >= 2.0`.
11. `effective_risk_scalar > 0.25` for new individual-equity entries.
12. Exposure after trade remains `<= 10%`.

- **TECH-CONF-01:** Each gate must be named or diagnostically observable.
- **TECH-CONF-02:** Avoid one unreadable boolean that hides why the setup is blocked.
- **TECH-CONF-03:** A technical setup cannot bypass an external veto.

## 7. Trend, P20, and over-extension

Canonical formulas:

```text
P20 = YTD_high * 0.80
overextended = close >= daily_SMA200 * 1.20
```

- **TREND-P20-01:** P20 is a price-location reference, not a standalone authorization to buy or DCA.
- **TREND-OVEREXT-01:** `close >= daily_SMA200 * 1.20` activates `OVEREXTENDED`.
- **TREND-OVEREXT-02:** Over-extension blocks aggressive-chase logic but does not modify the fundamental score.
- **TREND-OVEREXT-03:** Position-management logic may remain active while overextended.
- **TREND-STRUCT-01:** Where implemented, structural context should include price vs daily SMA/DMA200, daily 200 slope, price vs weekly WMA/SMA200, and confirmed HH/HL or LH/LL structure.

## 8. Timeframe hierarchy

Default hierarchy:

```text
TF_HT     = Weekly or Daily
TF_SETUP  = Daily or 4H
TF_TIMING = 5m..60m
HTF > setup > timing
```

Normative authority:

```text
TF_HT defines regime.
TF_SETUP defines setup.
TF_TIMING only refines execution.
```

- **MTF-AUTH-01:** Lower timeframes refine execution and must not independently invalidate a daily/weekly swing thesis.
- **MTF-AUTH-02:** HTF/setup conflict blocks a new long until alignment is restored.
- **MTF-AUTH-03:** Timing-timeframe weakness may emit a warning without becoming thesis authority.
- **MTF-AUTH-04:** Cache repeated MTF requests where practical and keep source/timeframe semantics explicit.

## 9. Tunnel contract

The Tunnel is a context engine, not an autonomous BUY/SELL system.

Required outputs when source data exists:

```text
trend_state_HT
trend_state_SETUP
allowed_long_context
cond_pullback_prev
cond_break_up_now
impulse_strength
upper_obstacle_HT
zone_reference
tunnel_risk_flags
```

Canonical long context:

```text
allowed_long_context
AND cond_pullback_prev
AND cond_break_up_now
AND impulse_strength
```

- **TUNNEL-LONG-01:** Tunnel output remains `SETUP_CANDIDATE` context until all other framework gates pass.
- **TUNNEL-LONG-02:** Tunnel output cannot directly set final order, final position size, final stop, or definitive targets.
- **TUNNEL-OBS-01:** `upper_obstacle_HT` participates in R/R feasibility but does not redefine 1R/2R.
- **TUNNEL-SHORT-01:** Short diagnostics may exist; operational shorts remain disabled by default.

## 10. Confirmation rules

- **TECH-CLOSE-01:** Swing breakouts require confirmed close when the framework requires close confirmation.
- **TECH-CLOSE-02:** Swing thesis invalidation uses the required daily close under the predefined structural level.
- **TECH-CLOSE-03:** An isolated intraday wick below a daily thesis level does not by itself invalidate the thesis.
- **TECH-CLOSE-04:** Pivot-based signals become valid only after pivot confirmation.
- **TECH-CLOSE-05:** Realtime previews must be labeled as previews and separated from confirmed states.

## 11. Non-repainting contract

Correct historical behavior has priority over visually attractive early signals.

- **NR-01:** No future data leakage.
- **NR-02:** No signal-producing `barmerge.lookahead_on`.
- **NR-03:** No negative/future plot offsets used to claim earlier detection.
- **NR-04:** No historical use of unconfirmed HTF values as though they were known at that bar.
- **NR-05:** No historical use of unconfirmed pivots as known structure.
- **NR-06:** Strategy entries may only use information available at the historical execution bar.
- **NR-07:** Every `request.security()` call must be reviewed for timeframe, bar alignment, confirmation semantics, gaps behavior, and repainting.
- **NR-08:** Any unavoidable realtime/historical difference must be documented.

## 12. Risk engine

Canonical constraints:

```text
max_position_fraction = 10%
standard_risk_fraction = 1%
exceptional_risk_fraction <= 2%
minimum_net_RR = 2.0
T1 = 1R
T2 = 2R
```

Conceptual sizing:

```text
base_risk_money = capital * risk_fraction
risk_money = base_risk_money * effective_risk_scalar
risk_per_share = abs(entry - protector_stop)
shares_by_risk = floor(risk_money / risk_per_share)
shares_by_concentration = floor((capital * 0.10) / entry)
approved_shares = min(all valid constraints)
```

- **RISK-SIZE-01:** Standard risk is 1%; exceptional risk is `<= 2%` and is not a default.
- **RISK-SIZE-02:** Per-position exposure must remain `<= 10%` when sizing is implemented.
- **RISK-SIZE-03:** Apply `effective_risk_scalar` once, never twice.
- **RISK-SIZE-04:** If the valid stop makes size too small or R/R invalid, reject/defer the setup rather than compressing the stop.
- **RISK-RR-01:** Execution eligibility requires net `R/R >= 2.0`.
- **RISK-TARGET-01:** `T1 = 1R`.
- **RISK-TARGET-02:** `T2 = 2R`.
- **RISK-OBST-01:** A material obstacle before viable 2R blocks or defers execution; a theoretical unobstructed 2R calculation is insufficient.

## 13. Stop taxonomy

Three stop concepts must remain separate.

### Thesis stop

- structural level where the swing thesis fails;
- validated by daily close for swing positions when that is the canonical rule;
- may be a thesis invalidation line rather than the exact exchange stop order.

### Protector stop

For longs:

```text
protector_stop <= structural_support - ATR_buffer
ATR_buffer >= 1.0 * ATR(14)
```

The ATR buffer may be wider for volatile assets or broad structural zones.

### Tactical stop

Allowed only for explicitly tactical/breakout logic. It must not silently replace the swing thesis stop.

- **RISK-STOP-01:** Do not conflate thesis, protector, and tactical stops.
- **RISK-STOP-02:** Never compress a valid structural/protector stop to manufacture position size or R/R.

## 14. R/R and obstacles

Distinguish gross theoretical 2R from viable/net 2R.

- **RISK-RR-02:** Higher-timeframe obstacles must be evaluated before calling 2R feasible.
- **RISK-RR-03:** Tunnel ribbons may validate/challenge target feasibility but do not redefine `T1 = 1R` or `T2 = 2R`.
- **RISK-COST-01:** Configured strategy slippage/commission is a simulation assumption unless it matches the actual execution venue.

## 15. DCA engine

Maintain distinct states:

```text
DCA_NORMAL
DCA_AGGRESSIVE_ELIGIBLE
```

Aggressive DCA requires every canonical gate simultaneously:

1. `score >= 70`.
2. `structuralBreak = false`.
3. Price above daily WMA200 or confirmed weekly recovery over major support.
4. Explicit Fibonacci 0.50-0.618 zone for the relevant deterministic swing.
5. `price <= P20`.
6. Confirmed reversal with volume.
7. Tunnel long compatibility.
8. External market/sentiment regimes are non-blocking.
9. `effective_risk_scalar > 0.25`.
10. Exposure after purchase remains `<= 10%`.

- **DCA-NORMAL-01:** Normal DCA and aggressive DCA are separate states.
- **DCA-AGG-01:** P20 alone is insufficient for aggressive DCA.
- **DCA-AGG-02:** Any UNKNOWN required condition makes `DCA_AGGRESSIVE_ELIGIBLE = false`.
- **DCA-AGG-03:** Price falling 20% must never be interpreted as fundamental permission to average down.
- **DCA-AGG-04:** `structuralBreak = true` blocks aggressive DCA regardless of price location.

## 16. Indicator contract

Indicators are observation and diagnostics tools.

Preferred outputs:

- trend states;
- MTF alignment;
- major moving averages;
- over-extension;
- Tunnel state;
- pullback/recovery state;
- volume confirmation;
- structural levels;
- stop candidates;
- R/R feasibility;
- P20 and DCA technical-zone status;
- gate dashboard;
- semantic alerts.

Indicators must not display a framework-approved BUY when required external gates are UNKNOWN.

## 17. Strategy contract

Strategies are historical simulations of the subset of framework behavior that can be represented without lookahead.

Every strategy must explicitly classify framework components as:

```text
SIMULATED
EXTERNALLY_SUPPLIED
OMITTED
HISTORICALLY_UNAVAILABLE
```

- **BT-SCOPE-01:** A strategy must not claim to backtest the full framework when historically varying external inputs are unavailable.
- **BT-SCOPE-02:** A current/manual fundamental score must not be applied retroactively as historical truth.
- **BT-SCOPE-03:** Strategy orders are simulation events, not broker-order execution.

## 18. Backtesting principles

Primary goal: verify mechanical correctness and robustness, not maximize historical profit.

Prohibited:

- tuning canonical thresholds solely to maximize historical net profit;
- weakening gates to increase trade count;
- using current fundamentals as historical facts;
- using future earnings, future pivots, future HTF closes, or future structure;
- treating a profitable equity curve as proof of the investment thesis;
- silently selecting favorable assets or windows to manufacture results.

When parameter research is performed, prefer:

- in-sample/out-of-sample separation;
- sensitivity checks around non-canonical implementation parameters;
- explicit transaction-cost assumptions;
- warnings for insufficient trade count;
- simple baselines where useful;
- invariant tests independent of profitability.

- **BT-ROBUST-01:** Backtest success never overrides canonical framework gates.
- **BT-ROBUST-02:** Every backtest report must state simulated, supplied, omitted, and historically unavailable components.

## 19. Alert contract

Prefer semantic alerts over generic BUY/SELL wording.

Canonical alert vocabulary:

```text
WATCH
PULLBACK
RECOVERY
SETUP_CANDIDATE
SETUP_CONFIRMED
RISK_BLOCKED
OBSTACLE_AHEAD
OVEREXTENDED
THESIS_WARNING
THESIS_INVALIDATED
DCA_ZONE
DCA_AGGRESSIVE_ELIGIBLE
```

- **ALERT-SEM-01:** Every alert must be semantically tied to a named state/gate.
- **ALERT-SEM-02:** Alert messages must say whether they are preview or confirmed when realtime behavior differs.
- **ALERT-SEM-03:** BUY/SELL wording is reserved for explicit strategy-order simulation or a script whose required external gates are fully supplied and validated.

## 20. Pine coding conventions

Default to Pine Script v6 unless an existing target script explicitly requires an earlier compatible version.

- use explicit, descriptive names;
- group inputs by domain;
- prefer small pure helper functions where practical;
- use enums/integer constants for multi-state logic;
- use constants for canonical thresholds;
- avoid magic numbers not traceable to a canonical rule or documented implementation choice;
- cache repeated MTF requests where practical;
- keep decision logic separate from plotting;
- keep alert construction separate from gate computation;
- keep simulated order code separate from state calculation;
- do not use favorable hidden defaults for absent external state;
- document any intentional divergence required by Pine limitations.

## 21. Traceability

Major gates require stable rule IDs and canonical source references.

```pine
// RULE: FUND-GATE-01
// Source: estrategia_inversion.md §1

// RULE: RISK-RR-01
// Source: reglas_riesgo_tecnico.md §4

// RULE: TUNNEL-LONG-01
// Source: regla_tunel.md §3-5
```

Rule IDs are stable project references. Source wording may change; ID meaning may change only through explicit framework impact analysis.

## 22. Invariant matrix

The following cases are deterministic acceptance tests for implementations:

| Case | Expected result |
|---|---|
| score = 69 | new entry blocked |
| score = 70, no veto | technical evaluation may proceed |
| structuralBreak = true | new entry and DCA blocked |
| risk scalar = 0.25 | new individual-equity entry blocked |
| risk scalar > 0.25 | may continue if other gates pass |
| net R/R = 1.99 | execution blocked |
| net R/R = 2.00 | R/R gate passes |
| price >= 1.20 * daily SMA200 | over-extension active |
| HT and setup trend conflict | new long blocked |
| intraday wick below thesis, daily close above | thesis not invalidated solely by wick |
| obstacle before viable 2R | wait/improve/cancel, not automatic entry |
| unknown external gate | fail closed |
| P20 met while other DCA gates missing | aggressive DCA false |

## 23. Change management

When the Investment Swing Framework changes:

1. identify the changed canonical source and its precedence;
2. map affected rule IDs;
3. classify impact as logic, documentation, or both;
4. update invariant tests first when practical;
5. make the smallest coherent implementation change;
6. re-review all affected MTF/repainting behavior;
7. re-run invariant checks;
8. document intentional behavioral differences or Pine limitations.

- **MAINT-01:** Pine must never become a divergent second copy of the Investment Swing Framework.
- **MAINT-02:** Do not perform unrelated refactors while changing a canonical rule.
- **MAINT-03:** Any framework threshold change requires corresponding rule-ID and invariant review.

## 24. Review workflow for existing Pine scripts

Before modifying an existing script:

1. read the whole relevant script;
2. identify indicator vs strategy intent;
3. inventory every `request.security()` call, pivot, offset, stateful `var`, alert, and strategy order;
4. map current behavior to rule IDs;
5. state framework violations before changing behavior;
6. preserve unrelated working behavior;
7. define a minimal failing scenario before fixing a bug;
8. change the smallest coherent unit;
9. verify applicable invariants and compile assumptions;
10. disclose remaining TradingView runtime uncertainty.

## 25. Definition of Done

A Pine change is complete only when all applicable checks pass:

```text
[ ] Correct Pine version/compatibility target
[ ] Framework precedence preserved
[ ] Fundamental score remains external to technical scoring
[ ] External UNKNOWN values fail closed
[ ] No unapproved autonomous Tunnel entry
[ ] No lookahead/future leakage
[ ] MTF requests reviewed for repainting
[ ] Closed-bar confirmation used where canonical rules require it
[ ] HTF/setup hierarchy preserved
[ ] Structural, protector, and tactical stops not conflated
[ ] ATR protector buffer respected
[ ] Risk scalar applied once
[ ] Position exposure cap respected when sizing is implemented
[ ] Net R/R >= 2.0 required for execution eligibility
[ ] Over-extension flag blocks aggressive chase
[ ] Aggressive DCA requires every canonical gate
[ ] Indicator and strategy responsibilities remain explicit
[ ] Backtest scope/limitations documented
[ ] Alerts use semantic states
[ ] Rule IDs/source references present for major gates
[ ] Invariant scenarios checked
[ ] Remaining platform-runtime uncertainty disclosed
```

## 26. Acceptance criteria

A conforming future implementation must be able to demonstrate all of the following without reinterpretation:

- refuse to derive the fundamental score from technical indicators;
- block a new entry at score 69 and allow technical evaluation at score 70 when no veto exists;
- treat missing external state as blocking rather than favorable;
- preserve `HTF > setup > timing`;
- distinguish a Tunnel candidate context from framework execution eligibility;
- avoid common MTF repainting patterns;
- preserve standard risk 1%, exceptional risk `<= 2%`, exposure `<= 10%`, and net `R/R >= 2.0`;
- use `protector_stop <= structural_support - ATR_buffer` with `ATR_buffer >= 1.0 * ATR(14)` when the protector engine is implemented;
- implement aggressive DCA only when every required gate is represented and true;
- explain exactly what a strategy backtest does and does not validate;
- preserve traceability from Pine logic to the canonical Investment Swing Framework.
