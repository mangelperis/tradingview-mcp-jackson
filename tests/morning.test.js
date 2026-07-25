/**
 * Morning brief unit tests — no TradingView connection needed.
 * Run: node --test tests/morning.test.js
 */
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  resolveWatchlist,
  applyWatchlistSync,
} from "../src/core/morning.js";

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

  it("accepts string symbols from TradingView payload", () => {
    const r = resolveWatchlist({
      rulesWatchlist: null,
      tvSymbols: ["BTCUSD"],
    });
    assert.deepEqual(r, { symbols: ["BTCUSD"], source: "tradingview" });
  });

  it("throws actionable error when both empty", () => {
    assert.throws(
      () => resolveWatchlist({ rulesWatchlist: [], tvSymbols: [] }),
      /TradingView watchlist/,
    );
  });
});

describe("applyWatchlistSync", () => {
  it("replaces watchlist and preserves other fields", () => {
    const base = {
      watchlist: ["OLD"],
      default_timeframe: "D",
      bias_criteria: { bullish: ["x"] },
      risk_rules: ["y"],
      notes: "keep me",
    };
    const out = applyWatchlistSync({
      rules: base,
      symbols: [{ symbol: "AAPL" }, "MSFT", { symbol: "AAPL" }],
    });
    assert.deepEqual(out.symbols, ["AAPL", "MSFT"]);
    assert.equal(out.previous_count, 1);
    assert.deepEqual(out.rules.watchlist, ["AAPL", "MSFT"]);
    assert.equal(out.rules.default_timeframe, "D");
    assert.equal(out.rules.notes, "keep me");
    assert.deepEqual(out.rules.bias_criteria, { bullish: ["x"] });
  });

  it("refuses empty TV list so rules are not wiped", () => {
    assert.throws(
      () =>
        applyWatchlistSync({
          rules: { watchlist: ["KEEP"], notes: "x" },
          symbols: [],
        }),
      /refusing to overwrite/,
    );
  });
});
