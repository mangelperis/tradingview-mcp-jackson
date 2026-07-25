# Design: `tv watchlist sync` → `rules.json`

Date: 2026-07-25  
Status: approved

## Goal

CLI command that copies the live TradingView watchlist into `rules.json` `watchlist` (replace), refusing to write if TV returns empty. `CLAUDE.md` requires running it at session start.

## Behavior

`tv watchlist sync [--rules path]`

1. Load `rules.json` (same path resolution as morning brief).
2. Ensure watchlist panel is open; call `watchlist.get()`.
3. If symbols empty → throw; leave file unchanged.
4. Else replace `watchlist` only; preserve other fields; write pretty JSON.
5. Return `{ success, path, count, symbols, previous_count }`.

## Code

- Pure: `applyWatchlistSync({ rules, symbols })` in `src/core/morning.js`
- Async: `syncWatchlistToRules({ rules_path })`
- CLI: `src/cli/commands/watchlist.js` → `sync` subcommand
- No new MCP tool

## CLAUDE.md

Session-start rule: always run `tv watchlist sync` before morning brief / multi-symbol work.
