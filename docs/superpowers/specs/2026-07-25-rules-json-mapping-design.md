# Design: Map trading docs into `rules.json` + TV watchlist fallback

Date: 2026-07-25  
Status: approved (pending user review of this written spec)

## Goal

Map the operator’s trading instruction docs into the repository’s expected `rules.json` shape so `morning_brief` can apply them daily, and allow an empty `watchlist` to fall back to the live TradingView watchlist.

## Sources (compressed, not dumped)

- `25072026_estrategia_inversion.md` — risk, sizing, stops, score, overextension, trade plan
- `25072026_regla_tunel.md` — Tunnel Domènech states, MTF alignment, entry/exit rules
- `25072026_tendencia_mercado.md` — market-phase / regime checklist
- `25072026_bac_2026_scenarios.md` — 2026 CIO scenario map (context only)
- `25072026_Institutional Price Action - Cheat Sheet.pdf` — QM/QML/fakeout tags as confluence only

## Decisions locked with operator

| Decision | Choice |
|---|---|
| Watchlist | Empty in `rules.json`; fall back to TradingView when empty |
| Density | Essentials only (short checklist lines) |
| Language | English |
| Bias style | Hybrid: Tunnel states + DMA200/WMA200/structure |
| Notes | Keep profile, regime, CIO map, Tunnel entry, IPA, trade-plan; **omit** brokers and FX/ops |

## `rules.json` shape

Keep the existing five fields only (no new schema keys):

```json
{
  "watchlist": [],
  "default_timeframe": "D",
  "bias_criteria": {
    "bullish": [],
    "bearish": [],
    "neutral": []
  },
  "risk_rules": [],
  "notes": ""
}
```

### `bias_criteria`

**Bullish**

- Tunnel HT + entry aligned: `IMPULSE_UP` or `PULLBACK_UP` (zone green, Genial Line green with positive slope)
- Price above daily DMA200/WMA200 (or reclaiming after a weekly pivot on major support)
- Structure: HH/HL on the daily (or clear pullback into Tunnel correction zone that holds)
- RSI(14) has room to run (not extreme exhaustion into pink ribbon / overbought climax)

**Bearish**

- Tunnel HT + entry aligned: `IMPULSE_DOWN` or `PULLBACK_DOWN` (zone red, Genial Line red with negative slope)
- Price below daily DMA200/WMA200 (or failing under broken major support)
- Structure: LH/LL on the daily (or bounce into Tunnel correction zone that fails)
- RSI(14) has room to drop (not washed-out climax / pink-ribbon exhaustion)

**Neutral**

- Tunnel `NEUTRAL`, or HT vs entry conflict (no AllowedLong/Short context)
- `BROKEN_UP` / `BROKEN_DOWN` until structure reclaims
- Price chopping around DMA200/WMA200 with mixed Tunnel colors / flat Genial slope
- Distribution / relief-rally / dead-cat context (good news sold, weak breadth) → treat as no new aggressive bias

### `risk_rules`

- Max 10% of portfolio per position; risk 1–2% per trade = (entry − stop) × shares
- No market orders — limit on pullbacks; stop orders only for confirmed breakouts or protective exits
- Swing stops invalidate on daily close below the key level, not wicks; technical stop = key support − (1–1.5)×ATR(14); if that exceeds 2% portfolio risk, cut size or skip
- Min R:R 1:1.5 (prefer ≥1:2 net of commissions + FX)
- VIX sizing: ≤20 → 1×; 20–28 → 0.75×; >28 or VIX backwardation → pause unless A+ and ≤0.5× with wider stops
- Overextension: if bullish name is ≥20% above DMA/SMA200 → caution; no aggressive new buys; prefer manage/wait for pullback (especially if Elliott suggests wave 5 + deep Tunnel red-line corrections)
- No new entries when Tunnel entry state is `NEUTRAL` or HT/entry contexts conflict
- Block long if HT obstacle sits between price and target1; same for shorts downward
- Fridays: avoid late new entries unless A+ setup
- Score gate: discard &lt;60; consider ≥70; prioritize ≥80; mark “data pending” if a key input is missing
- Never let a winner return to a full loss: at 1R take 25–40% and move stop to break-even (incl. costs); trail remainder

### `notes`

Single string covering:

- Profile: retail beginner; small tickets; base currency EUR; timezone Europe/Madrid
- Market-phase checklist: index vs DMA50/200; VIX level + contango/backwardation; breadth (% above DMA50/200, 90% up/down); distribution vs accumulation; news reaction (panic absorb vs good-news-sold)
- 2026 CIO map (as of 2026-06-29, not a signal): Bull ~25% / Base ~55% / Bear ~15% / Grizzly ~5%; combined Bull+Base ~80% constructive; monitor earnings, AI capex, inflation stickiness, unemployment >5%, credit spreads, USD risk-off
- Tunnel entry reminder: long = prior bar in correction zone, break above Z_high with impulse/volume, stop under min(Z_low, Genial) − buffer, TP toward blue then pink ribbons; shorts mirrored
- IPA (cheat sheet): Quasimodo / QML / fakeouts / compression = confluence tags only, never standalone entries
- Trade plan must include: thesis, pattern+TF, entry, daily-close stop, T1/T2, costs, ≥3 scenarios (base / acceleration / invalidation)

Explicitly excluded from notes: broker platform rules, FX cost math / Lightyear-XTB-MyInvestor ops.

## Code change: TradingView watchlist fallback

File: `src/core/morning.js`

Behavior:

1. Load `rules.json` as today.
2. If `watchlist` is missing or `[]`, call `watchlist.get()` (same core as MCP `watchlist_get`).
3. Map returned rows to ticker strings (prefer `data-symbol-full` / `symbol` field).
4. If TV returns none → clear error asking to open/populate the TradingView watchlist or set `rules.json` watchlist.
5. If `rules.json` has one or more symbols → those win (explicit override).
6. Brief payload includes `watchlist_source: "rules.json" | "tradingview"`.

No schema extension required; empty `watchlist: []` is the intentional “use TV” signal.

## Out of scope

- Dumping full pattern playbooks, Elliott wave tutorials, or BAC narrative prose into JSON
- Changing `morning_brief` instruction text beyond watchlist source metadata
- Broker/ops automation

## Acceptance criteria

1. `rules.json` matches the approved hybrid essentials content in English.
2. `morning_brief` with empty watchlist scans symbols from the open TradingView watchlist.
3. Non-empty `rules.json` watchlist still overrides TV.
4. Empty TV + empty rules watchlist fails with an actionable error.
5. Brief still returns `bias_criteria`, `risk_rules`, and `notes` for Claude to apply.
