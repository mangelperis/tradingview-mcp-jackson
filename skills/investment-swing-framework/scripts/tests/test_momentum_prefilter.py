"""Momentum-leadership discovery-only behavior; deliberately synthetic OHLC."""
import copy
import math
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import InputError
import momentum_prefilter


def sample_payload(n=252):
    cursor = date(2025, 1, 2)
    dates = []
    while len(dates) < n:
        if cursor.weekday() < 5:
            dates.append(cursor)
        cursor += timedelta(days=1)
    bars = []
    for i, day in enumerate(dates):
        price = 100.0 + i * 0.1
        bars.append({'date': day.isoformat(), 'open': price,
                     'high': price + 1.0, 'low': price - 1.0, 'close': price})
    last = dates[-1].isoformat()
    observed_at = datetime.combine(dates[-1] + timedelta(days=1), datetime.min.time(), timezone.utc)
    return {
        'analysis_at': observed_at.isoformat(),
        'instrument': {'ticker': 'SYN.US', 'exchange': 'NYSE',
                       'kind': 'STOCK', 'currency': 'USD', 'identity_verified': True},
        'market_data': {'price_basis': 'SPLIT_ADJUSTED',
                        'expected_last_completed_session': last, 'bars': bars},
        'source': {'reference': 'urn:synthetic:test', 'kind': 'DAILY_OHLC',
                   'as_of': last, 'retrieved_at': observed_at.isoformat()},
    }


class ContractTests(unittest.TestCase):
    def check_empty(self, data, status, reason):
        result = momentum_prefilter.calculate(data)
        self.assertEqual(result['status'], status)
        self.assertEqual(result['role'], 'DISCOVERY_ONLY')
        self.assertTrue(any(reason in line for line in result['pending']), result)
        self.assertTrue(all(value is None for value in result['checks'].values()))
        self.assertTrue(all(value is None for value in result['metrics'].values()))

    def test_nonstock_not_applicable(self):
        x = sample_payload(); x['instrument']['kind'] = 'ETF_BROAD'
        x['market_data'] = {}; x['source'] = {}
        self.check_empty(x, 'NOT_APPLICABLE', 'NOT_STOCK')

    def test_non_usd_eur_not_applicable(self):
        x = sample_payload(); x['instrument']['currency'] = 'GBP'
        self.check_empty(x, 'NOT_APPLICABLE', 'QUOTE_CURRENCY')

    def test_short_history_insufficient(self):
        x = sample_payload(n=251)
        self.check_empty(x, 'INSUFFICIENT', 'HISTORY')

    def test_unverified_identity_insufficient(self):
        x = sample_payload(); x['instrument']['identity_verified'] = False
        self.check_empty(x, 'INSUFFICIENT', 'IDENTITY')

    def test_unadjusted_prices_insufficient(self):
        x = sample_payload(); x['market_data']['price_basis'] = 'UNADJUSTED'
        self.check_empty(x, 'INSUFFICIENT', 'SPLIT_ADJUSTED')

    def test_missing_source_insufficient(self):
        x = sample_payload(); x.pop('source')
        self.check_empty(x, 'INSUFFICIENT', 'SOURCE')

    def test_stale_or_incomplete_session(self):
        x = sample_payload()
        x['market_data']['expected_last_completed_session'] = (
            date.fromisoformat(x['source']['as_of']) + timedelta(days=1)).isoformat()
        self.check_empty(x, 'INSUFFICIENT', 'LAST_COMPLETED_SESSION')

    def test_impossible_ohlc_rejected(self):
        x = sample_payload(); x['market_data']['bars'][-1]['high'] = 1
        with self.assertRaises(InputError): momentum_prefilter.calculate(x)

    def test_duplicate_or_out_of_order_date_rejected(self):
        x = sample_payload()
        x['market_data']['bars'][-1]['date'] = x['market_data']['bars'][-2]['date']
        with self.assertRaises(InputError): momentum_prefilter.calculate(x)
        x = sample_payload()
        x['market_data']['bars'][-1], x['market_data']['bars'][-2] = (
            x['market_data']['bars'][-2], x['market_data']['bars'][-1])
        with self.assertRaises(InputError): momentum_prefilter.calculate(x)

    def test_future_source_time_rejected(self):
        x = sample_payload()
        x['source']['retrieved_at'] = (
            datetime.fromisoformat(x['analysis_at']) + timedelta(seconds=10)).isoformat()
        with self.assertRaises(InputError): momentum_prefilter.calculate(x)

    def test_nonfinite_or_bool_price_rejected(self):
        for bad_value in [math.nan, True, '100.0', math.inf, 0.0]:
            with self.subTest(value=bad_value):
                x = sample_payload(); x['market_data']['bars'][10]['close'] = bad_value
                with self.assertRaises(InputError): momentum_prefilter.calculate(x)

    def test_future_bar_rejected(self):
        x = sample_payload()
        x['market_data']['bars'][-1]['date'] = (
            date.fromisoformat(x['market_data']['bars'][-1]['date']) + timedelta(days=3)).isoformat()
        with self.assertRaises(InputError): momentum_prefilter.calculate(x)

class ArithmeticTests(unittest.TestCase):
    def test_ema_uses_sma_seed(self):
        self.assertEqual(momentum_prefilter.ema_series([10., 12., 14., 16.], 3),
                         [None, None, 12., 14.])

    def test_true_range_includes_gap(self):
        bars = [
            {'high': 11., 'low': 9., 'close': 10.},
            {'high': 14., 'low': 12., 'close': 13.},
        ]
        self.assertEqual(momentum_prefilter.true_ranges(bars), [2., 4.])

    def test_window_index_contract(self):
        bars = sample_payload(253)['market_data']['bars']
        bars[0].update(high=900.0)
        last = len(bars)-1
        bars[last-63].update(open=50.0, high=51.0, low=49.0, close=50.0)
        metrics = momentum_prefilter.compute_metrics(bars)
        self.assertEqual(metrics['high_52w'], max(b['high'] for b in bars[-252:]))
        self.assertNotEqual(metrics['high_52w'], 900.0)
        self.assertAlmostEqual(metrics['return_63_sessions'], bars[-1]['close']/50.0-1)
        em11 = momentum_prefilter.ema_series([b['close'] for b in bars], 11)
        em21 = momentum_prefilter.ema_series([b['close'] for b in bars], 21)
        self.assertAlmostEqual(metrics['ema11_lag5'], em11[-6])
        self.assertAlmostEqual(metrics['ema21_lag5'], em21[-6])
        tr = momentum_prefilter.true_ranges(bars)
        from statistics import median
        self.assertAlmostEqual(metrics['median_tr20'], median(tr[-20:]))
        self.assertAlmostEqual(metrics['median_tr5'], median(tr[-5:]))

    def test_constant_range_ratio(self):
        bars = sample_payload()['market_data']['bars']
        for i, bar in enumerate(bars):
            bar.update(open=100., close=100., high=102., low=98.)
            if i >= len(bars) - 5:
                bar.update(high=101., low=99.)
        metrics = momentum_prefilter.compute_metrics(bars)
        self.assertAlmostEqual(metrics['median_tr5'], 2.)
        self.assertAlmostEqual(metrics['median_tr20'], 4.)
        self.assertAlmostEqual(metrics['tight_range_ratio'], 0.5)


def leadership_payload():
    """252 completed synthetic candles with momentum and compressed final range."""
    data = sample_payload()
    bars = data['market_data']['bars']
    for i, bar in enumerate(bars):
        close = 100.0 + max(0, i - 187) * 0.8
        half = 0.3 if i >= len(bars) - 5 else 2.0
        bar.update(open=close, high=close + half, low=close - half, close=close)
    return data


class ClassificationTests(unittest.TestCase):
    def test_all_conditions_pass(self):
        result = momentum_prefilter.calculate(leadership_payload())
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['role'], 'DISCOVERY_ONLY')
        self.assertTrue(all(result['checks'].values()))
        self.assertEqual(result['failed_conditions'], [])
        self.assertEqual(result['pending'], [])
        self.assertEqual(len(result['metrics']), 10)

    def test_distance_from_52w_high_fails(self):
        x = leadership_payload()
        x['market_data']['bars'][-15]['high'] = 250.0
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'FAIL')
        self.assertIn('NEAR_52W_HIGH', r['failed_conditions'])
        self.assertLess(r['metrics']['distance_52w_high'], -0.1)

    def test_return_63_below_threshold_fails(self):
        x = sample_payload()
        for b in x['market_data']['bars'][-5:]:
            b.update(high=b['close']+0.25, low=b['close']-0.25)
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'FAIL')
        self.assertIn('MOMENTUM_63_SESSIONS', r['failed_conditions'])

    def test_ema11_not_rising_fails(self):
        x = leadership_payload()
        bars = x['market_data']['bars']
        for i in range(12):
            bar = bars[-12+i]
            close = 153.0 - 2.0 * i
            bar.update(open=close, high=close+2, low=close-2, close=close)
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'FAIL')
        self.assertIn('EMA11_SLOPE', r['failed_conditions'])

    def test_ema21_not_rising_fails(self):
        x = leadership_payload()
        bars = x['market_data']['bars']
        for i in range(30):
            bar = bars[-30+i]
            close = 160.0 - 1.2*i
            bar.update(open=close, high=close+2, low=close-2, close=close)
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'FAIL')
        self.assertIn('EMA21_SLOPE', r['failed_conditions'])

    def test_tight_range_fails(self):
        x = leadership_payload()
        for b in x['market_data']['bars'][-5:]:
            b.update(high=b['close']+8.0, low=b['close']-8.0)
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'FAIL')
        self.assertIn('TIGHT_RANGE', r['failed_conditions'])

    def test_boundaries_and_flat_series(self):
        m = momentum_prefilter.compute_metrics(leadership_payload()['market_data']['bars'])
        boundary = dict(m, distance_52w_high=-0.10,
                        return_63_sessions=0.30, tight_range_ratio=0.80)
        self.assertTrue(all(momentum_prefilter.evaluate_checks(boundary).values()))
        just_below = dict(boundary, distance_52w_high=math.nextafter(-0.10, -math.inf))
        self.assertFalse(momentum_prefilter.evaluate_checks(just_below)['NEAR_52W_HIGH'])
        just_below = dict(boundary, return_63_sessions=math.nextafter(0.30, -math.inf))
        self.assertFalse(momentum_prefilter.evaluate_checks(just_below)['MOMENTUM_63_SESSIONS'])
        just_above = dict(boundary, tight_range_ratio=math.nextafter(0.80, math.inf))
        self.assertFalse(momentum_prefilter.evaluate_checks(just_above)['TIGHT_RANGE'])
        x = sample_payload()
        for b in x['market_data']['bars']:
            b.update(open=100., high=102., low=98., close=100.)
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'FAIL')
        self.assertFalse(r['checks']['EMA11_SLOPE'])
        self.assertFalse(r['checks']['EMA21_SLOPE'])
        for b in x['market_data']['bars']:
            b.update(open=100., high=100., low=100., close=100.)
        r = momentum_prefilter.calculate(x)
        self.assertEqual(r['status'], 'INSUFFICIENT')
        self.assertIn('ZERO_TR20_BASELINE', r['pending'])

    def test_no_score_position_or_execution_fields(self):
        result = momentum_prefilter.calculate(leadership_payload())
        for key in ('score', 'entry', 'risk', 'position', 'approved_shares',
                    'technical_entry_valid', 'effective_risk_scalar'):
            self.assertNotIn(key, result)

    def test_cli_json_file_stdout_and_stdin(self):
        import json
        import subprocess
        import tempfile
        script = Path(__file__).resolve().parents[1] / 'momentum_prefilter.py'
        payload = json.dumps(leadership_payload())
        with tempfile.TemporaryDirectory() as dirname:
            input_path = Path(dirname)/'synthetic-input.json'
            output_path = Path(dirname)/'result.json'
            input_path.write_text(payload)
            from_file = subprocess.run([sys.executable, str(script), str(input_path)],
                                       text=True, capture_output=True)
            from_stdin = subprocess.run([sys.executable, str(script)], input=payload,
                                        text=True, capture_output=True)
            saved = subprocess.run([sys.executable, str(script), str(input_path), '--output', str(output_path)],
                                   text=True, capture_output=True)
            self.assertEqual((from_file.returncode, from_stdin.returncode, saved.returncode), (0,0,0))
            expected = json.loads(from_file.stdout)
            self.assertEqual(expected, json.loads(from_stdin.stdout))
            self.assertEqual(expected, json.loads(output_path.read_text()))
            self.assertEqual(expected['status'], 'PASS')

    def test_invalid_cli_exit_two(self):
        import json
        import subprocess
        script = Path(__file__).resolve().parents[1] / 'momentum_prefilter.py'
        for text in ('{"analysis_at":1,"analysis_at":2}', '{"analysis_at":NaN}',
                     json.dumps(dict(leadership_payload(), analysis_at='bad-date'))):
            with self.subTest(payload=text[:28]):
                proc = subprocess.run([sys.executable, str(script)],
                                      input=text, text=True, capture_output=True)
                self.assertEqual(proc.returncode, 2)
                self.assertFalse(json.loads(proc.stdout)['valid'])

class DiscoveryRoutingTests(unittest.TestCase):
    def test_skill_links_prefilter_only_for_discovery(self):
        root = Path(__file__).resolve().parents[2]
        text = (root / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('](references/momentum_prefilter.md)', text)
        self.assertIn('DISCOVERY_ONLY', text)
        self.assertIn('Seguimiento', text)
        self.assertIn('discovery', text.lower())

    def test_prefilter_is_not_operational_input(self):
        import analysis_engine
        from helpers import analysis_input
        prefilter = momentum_prefilter.calculate(leadership_payload())
        self.assertEqual(prefilter['status'], 'PASS')
        x = analysis_input()
        self.assertNotIn('momentum_prefilter', x)
        result = analysis_engine.build(x)
        self.assertEqual(result['presentation']['score'], 85)
        self.assertEqual(result['presentation']['entry'], 'VALIDA')
        self.assertGreater(result['computed']['approved_shares'], 0)
        self.assertNotIn('momentum_prefilter', result['computed'])
        self.assertNotIn('momentum_prefilter', result['input'])

    def test_source_reference_declares_non_authority(self):
        root = Path(__file__).resolve().parents[2]
        text = (root / 'references' / 'momentum_prefilter.md').read_text(encoding='utf-8')
        self.assertIn('DISCOVERY_ONLY', text)
        self.assertIn('SOURCE-DERIVED', text)
        self.assertIn('IMPLEMENTATION CONVENTIONS', text)
        self.assertIn('NO_TRADE', text)
        self.assertIn('score', text)
        self.assertIn('entrada_tecnica_mtf', text)
        self.assertIn('not validated', text.lower())

class FinalReviewTests(unittest.TestCase):
    def test_data_contract_section_numbers_are_unique(self):
        import re
        root = Path(__file__).resolve().parents[2]
        text = (root/'references/data-contract.md').read_text(encoding='utf-8')
        numbers = [int(v) for v in re.findall(r'^## (\d+)\.', text, flags=re.MULTILINE)]
        self.assertEqual(numbers, list(range(1, len(numbers)+1)))
        self.assertIn('11. Contrato de opciones XTB V1',text)
        self.assertIn('12. Prefiltro momentum independiente',text)

    def test_unfinished_candle_cannot_pass(self):
        x = leadership_payload()
        x['market_data']['bars'][-1]['completed'] = False
        result = momentum_prefilter.calculate(x)
        self.assertEqual(result['status'], 'INSUFFICIENT')
        self.assertTrue(all(value is None for value in result['checks'].values()))

    def test_nonnumeric_completion_flag_rejected(self):
        x = leadership_payload()
        x['market_data']['bars'][-1]['completed'] = 0
        with self.assertRaises(InputError):
            momentum_prefilter.calculate(x)

    def test_numeric_metric_overflow_never_returns_a_signal(self):
        x = leadership_payload()
        bars = x['market_data']['bars']
        for b in bars:
            b.update(open=1e308, close=1e308, high=1e308, low=1e-308)
        result = momentum_prefilter.calculate(x)
        self.assertEqual(result['status'], 'INSUFFICIENT')
        self.assertIn('METRICS_NOT_FINITE', result['pending'])
