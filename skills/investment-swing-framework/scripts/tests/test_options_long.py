import importlib
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))

class OptionsLongTests(unittest.TestCase):
    def module(self): return importlib.import_module('options_long')
    def base(self):
        return dict(option_type='CALL',order_mode='PREMIUM',broker_action='BUY_CALL',
            underlying_price=12.03,strike=12.50,target_price=14.00,option_price=0.251,
            volume=3.98,premium_total=99.90,broker_max_loss=99.90,broker_break_even=12.75,
            capital_total=20000,base_risk_pct=0.01,effective_risk_scalar=0.75,
            direct_costs_total=0,dte=17,planned_holding_days=5,quote_current=True,
            underlying_thesis_valid=True,bearish_requested=False)
    def test_xtb_preview_infers_multiplier_about_100(self):
        r=self.module().calculate(self.base())
        self.assertAlmostEqual(r['effective_multiplier'],100,places=1)
        self.assertTrue(r['valid'],r)
    def test_three_dte_blocked(self):
        x=self.base(); x['dte']=3
        r=self.module().calculate(x)
        self.assertFalse(r['valid']); self.assertIn('dte_min_14',r['failed_conditions'])
    def test_risk_budget_blocks_large_premium(self):
        x=self.base(); x['capital_total']=10000
        r=self.module().calculate(x)
        self.assertFalse(r['valid']); self.assertIn('max_loss_within_budget',r['failed_conditions'])
    def test_dynamic_broker_volume_limit(self):
        x=self.base(); x['broker_volume_limit']=3.5
        r=self.module().calculate(x)
        self.assertFalse(r['valid']); self.assertIn('broker_volume_limit',r['failed_conditions'])
    def test_put_requires_explicit_bearish_request(self):
        x=self.base(); x.update(option_type='PUT',broker_action='BUY_PUT',underlying_price=12.03,
          strike=12.0,target_price=10.0,option_price=0.4,volume=2.5,premium_total=100,
          broker_max_loss=100,broker_break_even=11.6,bearish_requested=False)
        r=self.module().calculate(x)
        self.assertFalse(r['valid']); self.assertIn('bearish_request_explicit',r['failed_conditions'])
    def test_short_or_multileg_action_not_accepted(self):
        x=self.base(); x['broker_action']='SELL_CALL'
        r=self.module().calculate(x)
        self.assertFalse(r['valid']); self.assertIn('broker_buy_action_confirmed',r['failed_conditions'])

if __name__=='__main__': unittest.main()
