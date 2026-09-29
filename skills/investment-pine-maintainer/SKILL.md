---
name: investment-pine-maintainer
description: Generate Pine source for the Investment Swing Framework. Use when writing, reviewing, or revising a script's logic, gates, MTF behavior, or repainting. Inject, compile, and chart check belong to pine-develop.
---

# Investment Pine Maintainer

## Purpose

This skill generates Pine source. It preserves the framework's economics, risk policy, timeframe authority, external-data boundaries, and non-repainting requirements. It ends when that source meets the contract below. Loading the source into TradingView is `skills/pine-develop/SKILL.md`.

Read `references/project-rules.md` before making or reviewing any substantive Pine behavior. Treat it as the Pine implementation contract. If the project's canonical framework files are available, they remain authoritative over this derived contract according to the precedence defined there.

Swing-profile reference: `references/MTF_Swing_30_50_200_Pivot_v6.pine` (EMA 5/13/34, SMA 30/50/200, confirmed HTF, pivot strength 3, Pivot Bias as timing). Match its confirmation and non-repaint behavior when a new script implements that profile.

## Workflow

1. Classify the request as one or more of:
   - create a new indicator;
   - create a new strategy;
   - review an existing script;
   - debug a specific failure;
   - maintain Pine after a framework change.
2. Establish the applicable canonical rules and stable rule IDs from `references/project-rules.md`.
3. Identify which required inputs are deterministic Pine observables and which remain external.
4. Implement or review the smallest coherent unit of behavior.
5. Audit MTF alignment, confirmation timing, pivots, offsets, and repainting.
6. Verify applicable invariant cases in the source.
7. Hand the finished source to `skills/pine-develop/SKILL.md` when the user wants it on the chart. Generation is complete before that handoff.

## Authority and External-State Boundary

Preserve this canonical precedence:

`estrategia_inversion.md > reglas_riesgo_tecnico.md > regla_tunel.md > tendencia_mercado.md > sentimiento_posicionamiento.md > automatizacion_sentimiento_semanal.md > temporary reports/notes`

Never promote examples, chart outcomes, temporary notes, or backtest results into canonical policy.

Keep these external unless valid deterministic source data is explicitly supplied:

- `fundamental_score`;
- `structural_break` / `structuralBreak`;
- real portfolio exposure;
- framework market regime;
- framework sentiment regime;
- `effective_risk_scalar`.

Represent execution-relevant external gates with `PASS`, `FAIL`, and `UNKNOWN`. Treat `UNKNOWN` as blocking. Never substitute technical indicators for an external gate and never add technical points to the framework fundamental score.

## New Pine Script Rules

Default to Pine Script v6 unless an existing target explicitly requires another compatible version.

Prefer explicit named states and gates over opaque aggregate expressions. Separate:

- calculations;
- decision/gate logic;
- plots and tables;
- alerts;
- simulated strategy orders.

Use grouped inputs, descriptive names, stable rule IDs, source-reference comments, and canonical constants. Avoid favorable hidden defaults and untraceable magic numbers.

For a new long, preserve all applicable blockers, including:

- `fundamental_score < 70`;
- `structuralBreak = true`;
- `effective_risk_scalar <= 0.25` for individual-equity entry;
- HTF/setup conflict;
- invalid structural or protector stop;
- obstacle before viable 2R;
- net `R/R < 2.0`;
- post-trade exposure above `10%`.

Do not let Tunnel output independently authorize execution.

## Existing Script Review

Before modifying an existing script:

1. Read the relevant script completely.
2. Identify indicator versus strategy intent.
3. Inventory every `request.security()` call.
4. Inventory confirmed/unconfirmed pivots and any plot offsets.
5. Inventory stateful `var` usage and cross-bar state transitions.
6. Inventory alerts and all `strategy.*` order calls.
7. Map behavior to stable project rule IDs.
8. State framework violations before changing behavior.
9. Preserve unrelated working behavior.
10. For a bug, define a minimal failing historical/realtime scenario before fixing it.

Do not rewrite a working script wholesale when a localized correction is sufficient.

## MTF and Repainting Audit

Preserve timeframe authority as `HTF > setup > timing`.

Lower timeframes may refine execution but must not independently invalidate a daily/weekly swing thesis. Use the required confirmed close for breakout and thesis invalidation semantics. An isolated intraday wick does not invalidate a daily-close thesis.

Reject or fix:

- future-data leakage;
- signal-producing `barmerge.lookahead_on`;
- negative/future offsets used to imply earlier detection;
- historical use of unconfirmed pivots as known structure;
- historical use of unconfirmed HTF values as already available;
- strategy entries that depend on information unavailable on the execution bar.

Review every `request.security()` call for timeframe, source, gaps behavior, bar alignment, close confirmation, and repainting implications.

## Risk and Stop Rules

Preserve:

- standard risk: `1%`;
- exceptional risk: `<= 2%`, never as the default;
- per-position exposure: `<= 10%`;
- minimum net `R/R`: `2.0`;
- `T1 = 1R`;
- `T2 = 2R`.

Apply `effective_risk_scalar` exactly once.

Keep thesis, protector, and tactical stops distinct. For a long protector engine, require the protector stop outside structural support with `ATR_buffer >= 1.0 * ATR(14)`. Never compress a valid stop merely to increase position size or manufacture acceptable R/R.

## Tunnel and DCA Rules

Treat Tunnel as context/confluence only. It may expose trend, pullback, breakout, impulse, obstacle, zone, and risk states, but it must not directly decide final order, size, stop, or targets without the remaining framework gates.

Keep normal DCA separate from aggressive DCA. Aggressive DCA requires every canonical gate simultaneously. `price <= P20` alone is insufficient. Any required `UNKNOWN` gate makes aggressive DCA false.

## Indicator and Strategy Contract

For indicators, expose diagnostics, states, levels, risk feasibility, and semantic alerts. Do not display a framework-approved BUY when required external gates are unknown.

For strategies, simulate only the historically representable subset. Classify relevant components as:

- `SIMULATED`;
- `EXTERNALLY_SUPPLIED`;
- `OMITTED`;
- `HISTORICALLY_UNAVAILABLE`.

Do not apply a current/manual fundamental score retroactively as historical truth. Do not claim that a profitable Pine backtest validates the full framework or future profitability. Never tune canonical gates solely to improve historical net profit.

## Framework Maintenance

When a canonical framework source changes:

1. Identify the changed source and its precedence.
2. Map the affected stable rule IDs.
3. Update invariant tests first when practical.
4. Make the smallest coherent Pine behavior change.
5. Re-review all affected MTF/repainting behavior.
6. Re-run applicable invariants.
7. Document intentional Pine limitations or divergences.

Never allow Pine to become a divergent second copy of the framework.

## Verification Contract

Generation is complete when the source satisfies the applicable items in `references/project-rules.md`, especially the invariant matrix and Definition of Done. Chart compile is the next skill, not this one.

At minimum, check these deterministic boundaries when relevant:

- score `69` blocks a new entry;
- score `70` permits technical evaluation only when no veto exists;
- `structuralBreak = true` blocks entry and aggressive DCA;
- risk scalar `0.25` blocks an individual-equity entry;
- net R/R `1.99` blocks while `2.00` passes the R/R gate;
- `close >= 1.20 * daily SMA200` activates over-extension;
- HTF/setup conflict blocks a new long;
- an intraday wick alone does not invalidate a daily-close thesis;
- an obstacle before viable 2R blocks or defers;
- any required external `UNKNOWN` fails closed;
- P20 without the remaining DCA gates does not authorize aggressive DCA.

Leave compile results and chart screenshots to `skills/pine-develop/SKILL.md`.

## Response Contract

For code-generation tasks, provide the complete Pine source when the user requests a complete script. Keep rule IDs/source references near major gates.

For review/debug tasks, report in this order:

1. violations or defects;
2. behavioral impact;
3. minimal coherent correction;
4. invariant/repainting verification in the source;
5. the handoff: source is ready for `skills/pine-develop/SKILL.md` when the user wants it on the chart.

Do not claim framework approval, live execution, broker execution, or profitability from Pine-only evidence.
