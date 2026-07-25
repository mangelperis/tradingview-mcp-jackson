/**
 * Morning brief core logic.
 * Reads rules.json, scans watchlist symbols, returns structured data
 * for Claude to apply bias criteria and generate a session brief.
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import * as chart from "./chart.js";
import * as data from "./data.js";
import * as watchlist from "./watchlist.js";
import * as ui from "./ui.js";

/**
 * Resolve which symbols morning_brief should scan.
 * Non-empty rules.json watchlist wins; otherwise use TradingView watchlist rows.
 * @param {{ rulesWatchlist?: string[]|null, tvSymbols?: Array<string|{symbol?: string}>|null }} opts
 * @returns {{ symbols: string[], source: "rules.json"|"tradingview" }}
 */
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

/**
 * Pure sync: replace rules.watchlist from TV symbols.
 * Refuses empty lists so a failed TV read cannot wipe rules.json.
 * @param {{ rules: object, symbols: Array<string|{symbol?: string}> }} opts
 * @returns {{ rules: object, symbols: string[], previous_count: number }}
 */
export function applyWatchlistSync({ rules, symbols = [] } = {}) {
  if (!rules || typeof rules !== "object") {
    throw new Error("rules object is required");
  }
  const next = [];
  const seen = new Set();
  for (const s of symbols || []) {
    const sym = typeof s === "string" ? s : s?.symbol;
    if (!sym || seen.has(sym)) continue;
    seen.add(sym);
    next.push(sym);
  }
  if (!next.length) {
    throw new Error(
      "TradingView watchlist is empty — refusing to overwrite rules.json. Open the watchlist panel and ensure it has symbols.",
    );
  }
  const previous_count = Array.isArray(rules.watchlist)
    ? rules.watchlist.length
    : 0;
  return {
    rules: { ...rules, watchlist: next },
    symbols: next,
    previous_count,
  };
}

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "../../");
const SESSIONS_DIR = join(homedir(), ".tradingview-mcp", "sessions");
const USER_DATA_DIR = resolve(join(homedir(), ".tradingview-mcp"));

function assertSafeRulesPath(p) {
  const resolved = resolve(p);
  const inProject =
    resolved === resolve(join(PROJECT_ROOT, "rules.json")) ||
    resolved.startsWith(resolve(PROJECT_ROOT) + "/");
  const inUserData = resolved.startsWith(USER_DATA_DIR + "/");
  if (!inProject && !inUserData) {
    throw new Error(
      `rules_path must live inside the project (${PROJECT_ROOT}) or ~/.tradingview-mcp/. Got: ${resolved}`,
    );
  }
}

function assertSafeDate(dateStr) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    throw new Error(
      `Invalid date: ${dateStr}. Use YYYY-MM-DD (e.g. 2026-05-11).`,
    );
  }
}

function loadRules(rulesPath) {
  if (rulesPath) assertSafeRulesPath(rulesPath);

  const candidates = [
    rulesPath,
    join(PROJECT_ROOT, "rules.json"),
    join(homedir(), ".tradingview-mcp", "rules.json"),
  ].filter(Boolean);

  for (const p of candidates) {
    if (existsSync(p)) {
      try {
        return { rules: JSON.parse(readFileSync(p, "utf8")), path: p };
      } catch (e) {
        throw new Error(`Failed to parse rules.json at ${p}: ${e.message}`);
      }
    }
  }

  throw new Error(
    "No rules.json found. Copy rules.example.json to rules.json and fill in your trading rules.\n" +
      "Looked in:\n" +
      candidates
        .filter(Boolean)
        .map((p) => `  - ${p}`)
        .join("\n"),
  );
}

/**
 * Pull TradingView watchlist into rules.json (replace). Refuses empty TV lists.
 * @param {{ rules_path?: string }} [opts]
 */
export async function syncWatchlistToRules({ rules_path } = {}) {
  const { rules, path: loadedFrom } = loadRules(rules_path);

  try {
    await ui.openPanel({ panel: "watchlist", action: "open" });
    await new Promise((r) => setTimeout(r, 400));
  } catch (_) {
    // Panel open is best-effort; get() will still try to read
  }

  const tv = await watchlist.get();
  const applied = applyWatchlistSync({
    rules,
    symbols: tv.symbols || [],
  });

  writeFileSync(loadedFrom, JSON.stringify(applied.rules, null, 2) + "\n");

  return {
    success: true,
    path: loadedFrom,
    count: applied.symbols.length,
    symbols: applied.symbols,
    previous_count: applied.previous_count,
    tv_source: tv.source || null,
  };
}

export async function runBrief({ rules_path } = {}) {
  const { rules, path: loadedFrom } = loadRules(rules_path);
  const { watchlist: rulesWatchlist = [], default_timeframe = "240" } = rules;

  let symbols;
  let watchlistSource;
  if (rulesWatchlist.length) {
    ({ symbols, source: watchlistSource } = resolveWatchlist({
      rulesWatchlist,
      tvSymbols: [],
    }));
  } else {
    const tv = await watchlist.get();
    ({ symbols, source: watchlistSource } = resolveWatchlist({
      rulesWatchlist: [],
      tvSymbols: tv.symbols || [],
    }));
  }

  // Save current chart state so we can restore after scanning
  let originalSymbol, originalTimeframe;
  try {
    const currentState = await chart.getState();
    originalSymbol = currentState.symbol;
    originalTimeframe = currentState.resolution;
  } catch (_) {}

  const results = [];

  for (const symbol of symbols) {
    try {
      await chart.setSymbol({ symbol });
      await new Promise((r) => setTimeout(r, 900));
      await chart.setTimeframe({ timeframe: default_timeframe });
      await new Promise((r) => setTimeout(r, 900));

      const [state, indicators, quote] = await Promise.all([
        chart.getState(),
        data.getStudyValues(),
        data.getQuote({}),
      ]);

      results.push({
        symbol,
        timeframe: default_timeframe,
        state,
        indicators,
        quote,
      });
    } catch (err) {
      results.push({ symbol, error: err.message });
    }
  }

  // Restore original chart state
  if (originalSymbol) {
    try {
      await chart.setSymbol({ symbol: originalSymbol });
      if (originalTimeframe)
        await chart.setTimeframe({ timeframe: originalTimeframe });
    } catch (_) {}
  }

  return {
    success: true,
    generated_at: new Date().toISOString(),
    rules_loaded_from: loadedFrom,
    watchlist_source: watchlistSource,
    rules: {
      bias_criteria: rules.bias_criteria || null,
      risk_rules: rules.risk_rules || null,
      notes: rules.notes || null,
    },
    symbols_scanned: results,
    instruction: [
      "For each symbol in symbols_scanned, apply the bias_criteria from rules to the indicator readings.",
      "Output one line per symbol: SYMBOL | BIAS: [bullish/bearish/neutral] | KEY LEVEL: [price] | WATCH: [what to monitor]",
      "End with a one-sentence overall market read.",
      "Be direct. No preamble.",
    ].join(" "),
  };
}

export function saveSession({ brief, date } = {}) {
  const dateStr = date || new Date().toISOString().split("T")[0];
  assertSafeDate(dateStr);
  mkdirSync(SESSIONS_DIR, { recursive: true });
  const filePath = join(SESSIONS_DIR, `${dateStr}.json`);

  const existing = existsSync(filePath)
    ? JSON.parse(readFileSync(filePath, "utf8"))
    : {};
  const record = {
    ...existing,
    date: dateStr,
    saved_at: new Date().toISOString(),
    brief,
  };

  writeFileSync(filePath, JSON.stringify(record, null, 2));
  return { success: true, path: filePath, date: dateStr };
}

export function getSession({ date } = {}) {
  const dateStr = date || new Date().toISOString().split("T")[0];
  assertSafeDate(dateStr);
  const filePath = join(SESSIONS_DIR, `${dateStr}.json`);

  if (existsSync(filePath)) {
    return { success: true, ...JSON.parse(readFileSync(filePath, "utf8")) };
  }

  // Fall back to yesterday
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().split("T")[0];
  const yesterdayPath = join(SESSIONS_DIR, `${yesterdayStr}.json`);

  if (existsSync(yesterdayPath)) {
    return {
      success: true,
      note: "No session for today — returning yesterday",
      ...JSON.parse(readFileSync(yesterdayPath, "utf8")),
    };
  }

  return {
    success: false,
    error: `No session found for ${dateStr} or ${yesterdayStr}`,
    sessions_dir: SESSIONS_DIR,
  };
}
