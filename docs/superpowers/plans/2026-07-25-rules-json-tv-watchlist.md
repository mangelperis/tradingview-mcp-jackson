# Rules.json Mapping + TV Watchlist Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write essentials-only English `rules.json` from the approved spec, and make `morning_brief` fall back to the TradingView watchlist when `rules.json` watchlist is empty.

**Architecture:** Extract a pure `resolveWatchlist()` helper in `src/core/morning.js` so rules override vs TV fallback is unit-testable without CDP. `runBrief` calls `watchlist.get()` only when rules watchlist is empty, then scans as today. `rules.json` holds hybrid Tunnel+MA bias, hard risk gates, and condensed notes (no brokers/ops).

**Tech Stack:** Node.js ESM, `node:test`, existing `src/core/watchlist.js` CDP reader.

## Global Constraints

- Language: English rule strings
- Density: essentials only (no full playbook dump)
- Bias style: hybrid Tunnel + DMA200/WMA200/structure
- Notes: omit brokers and FX/ops
- Empty `watchlist: []` means use TradingView
- Non-empty rules watchlist overrides TV
- Do not commit unless the operator asks

---

### Task 1: `resolveWatchlist` helper + unit tests

**Files:**
- Modify: `src/core/morning.js`
- Create: `tests/morning.test.js`
- Modify: `package.json` (add unit test file to `test:unit` if needed)

**Interfaces:**
- Produces: `export function resolveWatchlist({ rulesWatchlist, tvSymbols })` → `{ symbols: string[], source: "rules.json" | "tradingview" }` or throws

- [ ] **Step 1: Write the failing test**

```js
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { resolveWatchlist } from "../src/core/morning.js";

describe("resolveWatchlist", () => {
  it("prefers non-empty rules watchlist", () => {
    const r = resolveWatchlist({
      rulesWatchlist: ["AAPL"],
      tvSymbols: [{ symbol: "MSFT" }],
    });
    assert.deepEqual(r, { symbols: ["AAPL"], source: "rules.json" });
  });

  it("falls back to TradingView symbols when rules watchlist empty", () => {
    const r = resolveWatchlist({
      rulesWatchlist: [],
      tvSymbols: [{ symbol: "NASDAQ:AAPL" }, { symbol: "NYSE:IBM" }],
    });
    assert.deepEqual(r, {
      symbols: ["NASDAQ:AAPL", "NYSE:IBM"],
      source: "tradingview",
    });
  });

  it("throws actionable error when both empty", () => {
    assert.throws(
      () => resolveWatchlist({ rulesWatchlist: [], tvSymbols: [] }),
      /TradingView watchlist/,
    );
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/morning.test.js`  
Expected: FAIL (export missing or function undefined)

- [ ] **Step 3: Implement `resolveWatchlist`**

```js
export function resolveWatchlist({ rulesWatchlist = [], tvSymbols = [] } = {}) {
  const fromRules = (rulesWatchlist || []).filter(Boolean);
  if (fromRules.length) {
    return { symbols: fromRules, source: "rules.json" };
  }
  const fromTv = (tvSymbols || [])
    .map((s) => (typeof s === "string" ? s : s?.symbol))
    .filter(Boolean);
  if (fromTv.length) {
    return { symbols: fromTv, source: "tradingview" };
  }
  throw new Error(
    "No symbols to scan. Open/populate the TradingView watchlist, or set watchlist in rules.json.",
  );
}
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `node --test tests/morning.test.js`  
Expected: PASS

- [ ] **Step 5: Commit** — skip unless operator asks

---

### Task 2: Wire `runBrief` to TV fallback

**Files:**
- Modify: `src/core/morning.js`

**Interfaces:**
- Consumes: `resolveWatchlist`, `watchlist.get` from `./watchlist.js`
- Produces: brief includes `watchlist_source`

- [ ] **Step 1: Import watchlist core and resolve symbols before scan loop**

```js
import * as watchlist from "./watchlist.js";

// inside runBrief, replace empty-watchlist throw:
let watchlistSource = "rules.json";
let symbols = watchlistArr;
if (!symbols.length) {
  const tv = await watchlist.get();
  const resolved = resolveWatchlist({
    rulesWatchlist: [],
    tvSymbols: tv.symbols || [],
  });
  symbols = resolved.symbols;
  watchlistSource = resolved.source;
} else {
  ({ symbols, source: watchlistSource } = resolveWatchlist({
    rulesWatchlist: symbols,
    tvSymbols: [],
  }));
}
```

- [ ] **Step 2: Add `watchlist_source` to return payload**

- [ ] **Step 3: Re-run unit tests**

Run: `node --test tests/morning.test.js`  
Expected: PASS

- [ ] **Step 4: Commit** — skip unless operator asks

---

### Task 3: Write `rules.json` from approved spec

**Files:**
- Modify: `rules.json`

- [ ] **Step 1: Replace contents** with approved hybrid bias, risk_rules, notes, `watchlist: []`, `default_timeframe: "D"` (exact text from `docs/superpowers/specs/2026-07-25-rules-json-mapping-design.md`)

- [ ] **Step 2: Validate JSON**

Run: `node -e "JSON.parse(require('fs').readFileSync('rules.json','utf8')); console.log('ok')"`  
Expected: `ok`

- [ ] **Step 3: Commit** — skip unless operator asks

---

### Task 4: Smoke verify package scripts

**Files:**
- Modify: `package.json` — add `tests/morning.test.js` to `test:unit`

- [ ] **Step 1: Update `test:unit` script** to include `tests/morning.test.js`

- [ ] **Step 2: Run unit tests**

Run: `npm run test:unit`  
Expected: all PASS (including morning)

---

## Spec coverage checklist

| Spec acceptance | Task |
|---|---|
| rules.json hybrid essentials EN | Task 3 |
| empty watchlist → TV scan | Task 2 |
| non-empty rules overrides TV | Task 1 + 2 |
| both empty → actionable error | Task 1 |
| brief still returns bias/risk/notes | Task 2 (unchanged return shape + `watchlist_source`) |
