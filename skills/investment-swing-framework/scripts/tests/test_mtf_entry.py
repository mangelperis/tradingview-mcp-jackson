import importlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helpers import analysis_input


def mtf_input(setup_type='REACCELERATION'):
    return {
        'setup_type': setup_type,
        'bar_closed': True,
        'htf_confirmed': True,
        'ma_types': {'operating':'EMA','structural_htf':'SMA'},
        'operating': {'close':105,'fast5':104,'mid13':102,'slow34':100},
        'htf': {'close':110,'fast30':108,'mid50':104,'slow200':95},
        'recent_bull_cross': True,
        'breakout_confirmed': True,
        'volume_confirmed': True,
        'support_state': 'CONFIRMED',
        'seller_exhaustion': 'CONFIRMED',
        'pivot_bias': {'bias':'ALCISTA','event':'RECUPERA_PIVOT','source':'PREVIOUS_CONFIRMED_DAILY_HLC'},
    }


class MTFEntryTests(unittest.TestCase):
    def module(self):
        return importlib.import_module('technical_entry_context')

    def test_reacceleration_matches_reference_structure(self):
        r=self.module().calculate(mtf_input('REACCELERATION'))
        self.assertTrue(r['valid'])
        self.assertTrue(r['htf_long_compatible'])
        self.assertTrue(r['operating_bullish_stack'])

    def test_trend_continuation_does_not_require_recent_cross(self):
        x=mtf_input('TREND_CONTINUATION'); x['recent_bull_cross']=False
        r=self.module().calculate(x)
        self.assertTrue(r['valid'])

    def test_reacceleration_requires_recent_cross(self):
        x=mtf_input('REACCELERATION'); x['recent_bull_cross']=False
        self.assertFalse(self.module().calculate(x)['valid'])

    def test_pivot_bias_alone_never_authorizes(self):
        x=mtf_input('RECOVERY_ENTRY')
        x['support_state']='NONE'; x['seller_exhaustion']='NONE'; x['recent_bull_cross']=False
        self.assertFalse(self.module().calculate(x)['valid'])

    def test_recovery_entry_can_precede_full_htf_alignment(self):
        x=mtf_input('RECOVERY_ENTRY')
        x['htf']={'close':98,'fast30':92,'mid50':100,'slow200':95}
        r=self.module().calculate(x)
        self.assertTrue(r['valid'])
        self.assertFalse(r['htf_long_compatible'])
        self.assertFalse(r['htf_bearish_structural'])

    def test_recovery_entry_blocks_structural_bear(self):
        x=mtf_input('RECOVERY_ENTRY')
        x['htf']={'close':80,'fast30':85,'mid50':90,'slow200':100}
        self.assertFalse(self.module().calculate(x)['valid'])

    def test_open_bar_blocks(self):
        x=mtf_input(); x['bar_closed']=False
        self.assertFalse(self.module().calculate(x)['valid'])

    def test_unconfirmed_htf_blocks(self):
        x=mtf_input(); x['htf_confirmed']=False
        self.assertFalse(self.module().calculate(x)['valid'])

    def test_analysis_no_longer_requires_allowed_long_context(self):
        x=analysis_input()
        x['technical']['mtf']=mtf_input('REACCELERATION')
        # Deliberately make Tunnel incompatible but keep its obstacle data present.
        x['tunnel']['ht'].update(Z_color='RED', G_color='RED', slope_G=-1, close=80)
        x['tunnel']['setup'].update(Z_color='RED', G_color='RED', slope_G=-1, close=80)
        e=importlib.import_module('analysis_engine').build(x)
        self.assertNotIn('TUNNEL_NOT_CONFIRMED',e['computed']['eligibility']['reasons'])
        self.assertEqual(e['presentation']['entry'],'VALIDA')

    def test_tunnel_obstacle_still_blocks(self):
        x=analysis_input(); x['technical']['mtf']=mtf_input('REACCELERATION')
        x['tunnel']['ht']['B_blue_high']=110
        e=importlib.import_module('analysis_engine').build(x)
        self.assertIn('UPPER_OBSTACLE_BEFORE_TARGET',e['computed']['eligibility']['reasons'])

if __name__=='__main__': unittest.main()
