import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from helpers import analysis_input,context_input,dca_input,risk_input,score_input

class SafetyTests(unittest.TestCase):
    def module(self,name):
        self.assertTrue((Path(__file__).resolve().parents[1]/(name+'.py')).exists(),'Missing '+name)
        return importlib.import_module(name)
    def test_negative_alignment_no_invented_cap(self):
        x=context_input(); x['divergence'].update(state='ALIGNED_NEGATIVE',cap=1)
        self.assertEqual(self.module('context_caps').calculate(x)['divergence_cap'],1)
    def test_unresolved_position_blocks_entry(self):
        x=analysis_input(); x['position']={'status':'UNKNOWN'}
        self.assertFalse(self.module('analysis_engine').build(x)['computed']['eligibility']['valid'])
    def test_approved_shares_zero_when_waiting(self):
        x=analysis_input(); x['technical']['mtf']['recent_bull_cross']=False
        self.assertEqual(self.module('analysis_engine').build(x)['computed'].get('approved_shares'),0)
    def test_structural_break_existing_action_enum(self):
        x=analysis_input(); x['buffett']['structuralBreak']=True
        x['fundamentals']['buffett']['structuralBreak']=True
        x['position'].update(status='OPEN',shares=10,avg_price=90)
        x['technical']['entry_plan']=False; x['risk']=None
        self.assertEqual(self.module('analysis_engine').build(x)['presentation']['position_action'],'CERRAR')
    def test_unknown_context_not_aligned(self):
        x=context_input(); x['weekly_report']=None
        self.assertFalse(self.module('context_caps').calculate(x)['positive_evidence'])
    def test_dca_normal_cannot_bypass_panic(self):
        x=dca_input(); x['sentiment_regimes']=['PANIC_LIQUIDATION']
        self.assertEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'ESPERAR')
    def test_dca_crowded_not_aggressive(self):
        x=dca_input(); x['sentiment_regimes']=['CROWDED_LONG']
        self.assertNotEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'DCA_AGRESIVO')
    def test_peg_negative_growth_uninterpretable(self):
        r=self.module('valuation_metrics').calculate({'pe':20,'eps_growth_pct':-5})
        self.assertIsNone(r['PEG']); self.assertEqual(r['PEG_status'],'PEG no interpretable')
    def test_peg_percent_units(self):
        r=self.module('valuation_metrics').calculate({'pe':20,'eps_growth_pct':10,'growth_reliable':True})
        self.assertEqual(r['PEG'],2)
    def test_fcf_yield_decimal(self):
        r=self.module('valuation_metrics').calculate({'fcf':5,'market_cap':100})
        self.assertEqual(r['fcf_yield'],0.05)
    def test_missing_fcf_not_zero(self):
        self.assertIsNone(self.module('valuation_metrics').calculate({'market_cap':100})['fcf_yield'])
    def test_ytd_p20(self):
        self.assertEqual(self.module('valuation_metrics').calculate({'ytd_high':100,'price':80})['P20'],80)
    def test_position_profit_loss(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100,
                  'capital_total':10000,'stop_protector':85})
        self.assertEqual(r['unrealized_pl'],100); self.assertEqual(r['weight'],0.1)
        self.assertEqual(r['remaining_stop_risk'],150)
    def test_position_missing_capital_pending(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100})
        self.assertIsNone(r['weight'])
    def test_wick_not_swing_invalidation(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100,
                   'stop_thesis':92,'intraday_low':89,'daily_close':95,'daily_close_confirmed':True})
        self.assertFalse(r['thesis_invalidated'])
    def test_confirmed_close_invalidates(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100,
                   'stop_thesis':92,'daily_close':91,'daily_close_confirmed':True})
        self.assertTrue(r['thesis_invalidated'])
    def test_break_even_before_t1_invalid(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100,
                   'atr14':2,'request_break_even':True,'t1_taken':False})
        self.assertFalse(r['break_even_allowed'])
    def test_break_even_noise_invalid(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':90.5,
                   'atr14':2,'request_break_even':True,'t1_taken':True})
        self.assertFalse(r['break_even_allowed'])
    def test_break_even_after_t1_valid(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100,
                   'atr14':2,'request_break_even':True,'t1_taken':True})
        self.assertTrue(r['break_even_allowed'])
    def test_trailing_weekly_low(self):
        r=self.module('position_management').calculate({'shares':10,'avg_price':90,'current_price':100,
                   'atr14':2,'weekly_low':95})
        self.assertEqual(r['trailing_candidates']['weekly_low_minus_half_atr'],94)
    def test_json_duplicate_key_rejected(self):
        self.module('fundamental_score')
        p=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'fundamental_score.py')],
             input='{"categories":{},"categories":{}}',capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
    def test_sources_dangling_rejected(self):
        x=analysis_input(); x['technical']['source_ids']=['missing']
        e=self.module('analysis_engine').build(x)
        self.assertFalse(self.module('validate_analysis').validate(e)['valid'])
    def test_low_score_entry_payload_invalid(self):
        x=analysis_input(); x['buffett']['badge']='AMBER'; x['fundamentals']['buffett']['badge']='AMBER'
        e=self.module('analysis_engine').build(x)
        self.assertFalse(self.module('validate_analysis').validate(e)['valid'])
    def test_buffett_quality_mismatch_rejected(self):
        x=analysis_input(); x['buffett']['qualityPass']=False; x['fundamentals']['buffett']['qualityPass']=False
        e=self.module('analysis_engine').build(x)
        self.assertFalse(self.module('validate_analysis').validate(e)['valid'])
    def test_followup_unexplained_score_rejected(self):
        x=analysis_input(); x['review']={'mode':'FOLLOWUP','prior':{'score':80,'decision':'ALTA_CONVICCION'},'material_changes':[]}
        e=self.module('analysis_engine').build(x)
        self.assertFalse(self.module('validate_analysis').validate(e)['valid'])
    def test_followup_material_change_title(self):
        x=analysis_input(); x['review']={'mode':'FOLLOWUP','prior':{'score':80,'decision':'ALTA_CONVICCION'},
          'material_changes':[{'kind':'EARNINGS','reason':'Synthetic improved cash flow','source_ids':['s1'],'categories':['free_cash_flow']}]}
        e=self.module('analysis_engine').build(x)
        self.assertTrue(e['computed']['review']['emit_updated_title'])
        self.assertTrue(self.module('validate_analysis').validate(e)['valid'])

if __name__=='__main__': unittest.main()
