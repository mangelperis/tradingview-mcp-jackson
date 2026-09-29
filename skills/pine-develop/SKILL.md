---
name: pine-develop
description: Integrate existing Pine source into TradingView. Use when source is already written and must be pushed into the editor, compiled, error-fixed, and checked on the chart.
---

# Integrate Pine into TradingView

This skill loads finished Pine source into the TradingView editor. Generating or revising framework logic is `skills/investment-pine-maintainer/SKILL.md`. Done means the editor compile is clean and the chart check is shown.

## Step 1: Take the source

Place the finished script at `scripts/current.pine`.

When the editor already holds a newer copy, pull that copy first:

```bash
node scripts/pine_pull.js
```

A change to gates, MTF behavior, or risk rules goes back to `skills/investment-pine-maintainer/SKILL.md` before the next push. A compile or display fix stays in this loop.

## Step 2: Push and Compile

```bash
node scripts/pine_push.js
```

This injects the code into TradingView's Pine Editor, clicks compile, and reports any errors.

## Step 3: Fix compile errors

If errors are reported:
1. Read the error messages (line number + description)
2. Edit `scripts/current.pine` locally — fix the specific lines
3. Push again: `node scripts/pine_push.js`
4. Repeat until 0 errors

Common Pine Script errors:
- **"Mismatched input"** — usually indentation (Pine uses 4-space indentation, not braces)
- **"Could not find function or function reference"** — typo in function name or wrong version
- **"Undeclared identifier"** — variable used before declaration
- **"Cannot call X with argument type Y"** — wrong parameter type

## Step 4: Verify on the chart

After clean compilation:
1. `capture_screenshot` — take a screenshot to verify it looks right
2. `data_get_strategy_results` — if it's a strategy, check performance
3. Show the user the results

## Step 5: Iterate on the chart

When TradingView changed the editor copy, pull it, then push and compile again:

```bash
node scripts/pine_pull.js
```

Done means `pine_push` reports 0 errors and the screenshot (or strategy results) is shown.
