"""Evaluate split-adjusted daily OHLC for discovery-only momentum leadership."""
from datetime import date
import math
import re
from statistics import median

from common import InputError, cli, number, stamp

MODULE = 'MOMENTUM_LEADERSHIP_PREFILTER_V1'
CHECK_KEYS = ('NEAR_52W_HIGH', 'MOMENTUM_63_SESSIONS', 'EMA11_SLOPE', 'EMA21_SLOPE', 'TIGHT_RANGE')
METRIC_KEYS = ('high_52w', 'distance_52w_high', 'return_63_sessions',
               'ema11_now', 'ema11_lag5', 'ema21_now', 'ema21_lag5',
               'median_tr5', 'median_tr20', 'tight_range_ratio')


def ema_series(closes: list[float], period: int) -> list[float | None]:
    """SMA-seeded EMA; unavailable warmup indices are None."""
    if isinstance(period, bool) or not isinstance(period, int) or period < 1:
        raise InputError('EMA period must be positive integer')
    if len(closes) < period:
        return [None] * len(closes)
    values = [None] * (period - 1)
    previous = sum(closes[:period]) / period
    values.append(previous)
    alpha = 2.0 / (period + 1)
    for close in closes[period:]:
        previous = alpha * close + (1 - alpha) * previous
        values.append(previous)
    return values


def true_ranges(bars: list[dict]) -> list[float]:
    """Gap-aware daily true range, with the first period using high-low."""
    values = []
    previous_close = None
    for bar in bars:
        hi, lo = bar['high'], bar['low']
        tr = hi - lo if previous_close is None else max(
            hi - lo, abs(hi - previous_close), abs(lo - previous_close))
        values.append(tr)
        previous_close = bar['close']
    return values


def compute_metrics(bars: list[dict]) -> dict[str, float | None]:
    """Calculate the five checks' observables from already validated daily bars."""
    if len(bars) < 252:
        raise InputError('compute_metrics requires at least 252 daily observations')
    closes = [bar['close'] for bar in bars]
    high52 = max(bar['high'] for bar in bars[-252:])
    ema11 = ema_series(closes, 11)
    ema21 = ema_series(closes, 21)
    ranges = true_ranges(bars)
    med5 = median(ranges[-5:])
    med20 = median(ranges[-20:])
    return {
        'high_52w': high52,
        'distance_52w_high': closes[-1] / high52 - 1,
        'return_63_sessions': closes[-1] / closes[-64] - 1,
        'ema11_now': ema11[-1],
        'ema11_lag5': ema11[-6],
        'ema21_now': ema21[-1],
        'ema21_lag5': ema21[-6],
        'median_tr5': med5,
        'median_tr20': med20,
        'tight_range_ratio': med5 / med20 if med20 > 0 else None,
    }


def evaluate_checks(metrics: dict[str, float]) -> dict[str, bool]:
    """Compare observables with inclusive thresholds; do not assign a score."""
    return {
        'NEAR_52W_HIGH': metrics['distance_52w_high'] >= -0.10,
        'MOMENTUM_63_SESSIONS': metrics['return_63_sessions'] >= 0.30,
        'EMA11_SLOPE': metrics['ema11_now'] > metrics['ema11_lag5'],
        'EMA21_SLOPE': metrics['ema21_now'] > metrics['ema21_lag5'],
        'TIGHT_RANGE': metrics['tight_range_ratio'] <= 0.80,
    }


def iso_day(value, name):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise InputError(f'{name}: ISO date required')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f'{name}: invalid ISO date') from exc


def empty_result(ticker, status, pending, as_of_session=None, reference=None):
    return {
        'module': MODULE, 'role': 'DISCOVERY_ONLY', 'ticker': ticker,
        'as_of_session': as_of_session, 'status': status,
        'checks': {key: None for key in CHECK_KEYS},
        'metrics': {key: None for key in METRIC_KEYS},
        'failed_conditions': [], 'pending': list(pending),
        'source_reference': reference,
    }


def calculate(data: dict) -> dict:
    if not isinstance(data, dict):
        raise InputError('Top-level object required')
    analysis_at = stamp(data.get('analysis_at'), 'analysis_at')
    instrument = data.get('instrument')
    if instrument is None:
        return empty_result(None, 'INSUFFICIENT', ['INSTRUMENT_IDENTITY_MISSING'])
    if not isinstance(instrument, dict):
        raise InputError('instrument: object required')
    ticker = instrument.get('ticker')
    kind = instrument.get('kind')
    currency = instrument.get('currency')
    identity_verified = instrument.get('identity_verified')
    if identity_verified is not True or not isinstance(ticker, str) or not ticker.strip() or not isinstance(instrument.get('exchange'), str) or not instrument.get('exchange').strip():
        return empty_result(ticker, 'INSUFFICIENT', ['IDENTITY_NOT_VERIFIED'])
    if not isinstance(kind, str) or not kind.strip() or not isinstance(currency, str) or not currency.strip():
        return empty_result(ticker, 'INSUFFICIENT', ['INSTRUMENT_SCOPE_UNKNOWN'])
    if kind != 'STOCK':
        return empty_result(ticker, 'NOT_APPLICABLE', ['NOT_STOCK'])
    if currency not in ('USD', 'EUR'):
        return empty_result(ticker, 'NOT_APPLICABLE', ['QUOTE_CURRENCY_NOT_USD_EUR'])
    data_block = data.get('market_data')
    if data_block is None:
        return empty_result(ticker, 'INSUFFICIENT', ['MARKET_DATA_MISSING'])
    if not isinstance(data_block, dict):
        raise InputError('market_data: object required')
    if data_block.get('price_basis') != 'SPLIT_ADJUSTED':
        return empty_result(ticker, 'INSUFFICIENT', ['SPLIT_ADJUSTED_OHLC_NOT_VERIFIED'])
    expected_string = data_block.get('expected_last_completed_session')
    if expected_string is None:
        return empty_result(ticker, 'INSUFFICIENT', ['LAST_COMPLETED_SESSION_UNKNOWN'])
    expected = iso_day(expected_string, 'expected_last_completed_session')
    if expected > analysis_at.date():
        raise InputError('expected_last_completed_session: future observation')
    source = data.get('source')
    if source is None:
        return empty_result(ticker, 'INSUFFICIENT', ['SOURCE_NOT_VERIFIED'], expected_string)
    if not isinstance(source, dict):
        raise InputError('source: object required')
    reference = source.get('reference')
    if not isinstance(reference, str) or not reference.strip() or source.get('kind') != 'DAILY_OHLC' or not source.get('retrieved_at') or not source.get('as_of'):
        return empty_result(ticker, 'INSUFFICIENT', ['SOURCE_NOT_VERIFIED'], expected_string, reference)
    retrieved_at = stamp(source['retrieved_at'], 'source.retrieved_at')
    if retrieved_at > analysis_at:
        raise InputError('source.retrieved_at: future observation')
    source_day = iso_day(source['as_of'], 'source.as_of')
    if source_day > analysis_at.date():
        raise InputError('source.as_of: future observation')
    bars = data_block.get('bars')
    if bars is None:
        return empty_result(ticker, 'INSUFFICIENT', ['HISTORY_MISSING'], expected_string, reference)
    if not isinstance(bars, list):
        raise InputError('market_data.bars: list required')
    if not bars:
        return empty_result(ticker, 'INSUFFICIENT', ['HISTORY_MISSING'], expected_string, reference)
    previous = None
    for index, bar in enumerate(bars):
        if not isinstance(bar, dict):
            raise InputError(f'bars[{index}]: OHLC object required')
        if bar.get('date') is None or any(bar.get(key) is None for key in ('open', 'high', 'low', 'close')):
            return empty_result(ticker, 'INSUFFICIENT', ['HISTORY_INCOMPLETE_OHLC'], expected_string, reference)
        day = iso_day(bar['date'], f'bars[{index}].date')
        if day > analysis_at.date():
            raise InputError(f'bars[{index}].date: future observation')
        if previous is not None and day <= previous:
            raise InputError(f'bars[{index}].date: duplicate or unsorted observation')
        previous = day
        o, h, l, c = [number(bar[key], f'bars[{index}].{key}', minimum=0) for key in ('open', 'high', 'low', 'close')]
        if min(o, h, l, c) <= 0 or not (l <= o <= h and l <= c <= h):
            raise InputError(f'bars[{index}]: impossible OHLC candle')
        if 'completed' in bar:
            if not isinstance(bar['completed'], bool):
                raise InputError(f'bars[{index}].completed: boolean required')
            if not bar['completed']:
                return empty_result(ticker, 'INSUFFICIENT', ['LAST_COMPLETED_SESSION_UNCONFIRMED'], expected_string, reference)
    if bars[-1]['date'] != expected_string or source_day != expected:
        return empty_result(ticker, 'INSUFFICIENT', ['LAST_COMPLETED_SESSION_MISMATCH'], expected_string, reference)
    if len(bars) < 252:
        return empty_result(ticker, 'INSUFFICIENT', ['HISTORY_LT_252_COMPLETED_SESSIONS'], expected_string, reference)
    try:
        metrics = compute_metrics(bars)
    except (OverflowError, ZeroDivisionError):
        return empty_result(ticker, 'INSUFFICIENT', ['METRICS_NOT_FINITE'], expected_string, reference)
    if any(value is not None and not math.isfinite(value) for value in metrics.values()):
        return empty_result(ticker, 'INSUFFICIENT', ['METRICS_NOT_FINITE'], expected_string, reference)
    if metrics['tight_range_ratio'] is None:
        return empty_result(ticker, 'INSUFFICIENT', ['ZERO_TR20_BASELINE'], expected_string, reference)
    checks = evaluate_checks(metrics)
    failed = [key for key in CHECK_KEYS if not checks[key]]
    result = empty_result(ticker, 'FAIL' if failed else 'PASS', [], expected_string, reference)
    result['checks'] = checks
    result['metrics'] = metrics
    result['failed_conditions'] = failed
    return result


if __name__ == '__main__':
    raise SystemExit(cli(calculate, __doc__))
