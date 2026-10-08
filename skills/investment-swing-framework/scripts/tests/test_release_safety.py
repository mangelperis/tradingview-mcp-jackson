"""Release regression tests for missing evidence and identity consistency."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from helpers import analysis_input, context_input, dca_input
from decision_rules import evaluate_dca
from analysis_engine import build
from context_caps import calculate
from validate_analysis import validate

class ReleaseSafetyTests(unittest.TestCase):
    def test_missing_cost_estimate_cannot_authorize_entry(self):
        data=analysis_input(); data['risk'].pop('roundtrip_cost_per_share')
        result=build(data)
        self.assertFalse(result['computed']['eligibility']['valid'])
    def test_missing_divergence_not_a_complete_context(self):
        data=context_input(); data.pop('divergence')
        self.assertEqual(calculate(data)['context_status'],'INSUFFICIENT')
    def test_missing_divergence_cannot_authorize_entry(self):
        data=analysis_input(); data['context_stack'].pop('divergence')
        self.assertFalse(build(data)['computed']['eligibility']['valid'])
    def test_zero_quoted_price_invalid(self):
        data=analysis_input(); data['instrument']['price']=0; data['risk']=None
        self.assertFalse(validate(build(data))['valid'])
    def test_empty_source_id_invalid(self):
        data=analysis_input(); data['sources'].append(dict(id='',reference='urn:synthetic:empty',
          retrieved_at=data['analysis_at'],as_of=data['analysis_at']))
        self.assertFalse(validate(build(data))['valid'])
    def test_position_currency_mismatch_invalid(self):
        data=analysis_input(); data['position']['currency']='EUR'
        self.assertFalse(validate(build(data))['valid'])

    def test_missing_ht_ribbons_do_not_become_tunnel_authorization_gate(self):
        data=analysis_input(); data['tunnel']['ht'].pop('B_blue_high')
        result=build(data)
        self.assertNotIn('TUNNEL_NOT_CONFIRMED',result['computed']['eligibility']['reasons'])
        self.assertTrue(result['computed']['eligibility']['valid'])
    def test_dca_overextended_not_aggressive(self):
        data=dca_input(); data['overextended']=True
        self.assertNotEqual(evaluate_dca(data)['decision'],'DCA_AGRESIVO')
    def test_dca_extension_unknown_not_aggressive(self):
        data=dca_input(); data.pop('overextended')
        self.assertNotEqual(evaluate_dca(data)['decision'],'DCA_AGRESIVO')
    def test_dca_pipeline_derives_extension_instead_of_trusting_flag(self):
        data=analysis_input(); data['structural_trend']['sma200_daily']=80
        data['dca']=dca_input(); data['dca']['ytd_high']=125
        self.assertNotEqual(build(data)['computed']['dca']['decision'],'DCA_AGRESIVO')

if __name__=='__main__': unittest.main()
