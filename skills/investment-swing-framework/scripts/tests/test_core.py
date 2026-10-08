import importlib
import json
import math
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helpers import score_input, context_input, risk_input, tunnel_input, dca_input, analysis_input

class CoreTests(unittest.TestCase):
    def module(self, name):
        self.assertTrue((Path(__file__).resolve().parents[1] / (name+'.py')).exists(),
                        'Missing implementation: '+name)
        return importlib.import_module(name)

    def test_score_normal(self):
        r=self.module('fundamental_score').calculate(score_input())
        self.assertEqual((r['raw_score'],r['score'],r['decision']), (85,85,'ALTA_CONVICCION'))
    def test_score_no_technical_category(self):
        x=score_input(); x['categories']['RSI']=10
        with self.assertRaises(ValueError): self.module('fundamental_score').calculate(x)
    def test_score_out_of_range(self):
        x=score_input(); x['categories']['valuation']=21
        with self.assertRaises(ValueError): self.module('fundamental_score').calculate(x)
    def test_score_bool_rejected(self):
        x=score_input(); x['categories']['growth']=True
        with self.assertRaises(ValueError): self.module('fundamental_score').calculate(x)
    def test_structural_override_preserves_raw_score(self):
        x=score_input(); x['buffett']['structuralBreak']=True
        r=self.module('fundamental_score').calculate(x)
        self.assertEqual(r['raw_score'],85); self.assertEqual(r['decision'],'NO_TRADE')
        self.assertFalse(r['phase2_allowed'])
    def test_short_thesis_override(self):
        x=score_input(); x['buffett']['shortThesisRisk']='HIGH'
        self.assertEqual(self.module('fundamental_score').calculate(x)['decision'],'NO_TRADE')
    def test_missing_financials(self):
        x=score_input(); x['data_quality']['recent_statements']=False
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],59)
    def test_missing_debt(self):
        x=score_input(); del x['data_quality']['debt_verified']
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],59)
    def test_missing_fcf(self):
        x=score_input(); x['data_quality']['fcf_verified']=False
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],59)
    def test_preprofit_narrative_cap(self):
        x=score_input(); x['data_quality'].update(pre_profit=True,narrative_only=True)
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],59)
    def test_gray_exception_requires_evidence(self):
        x=score_input(); x['buffett'].update(badge='GRAY', alternative_valuation={'robust':True})
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],59)
    def test_gray_robust_exception(self):
        x=score_input(); x['buffett'].update(badge='GRAY', alternative_valuation={
            'robust':True,'rationale':'Synthetic documented valuation','source_ids':['s1']})
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],85)
    def test_unknown_structural_break_blocks(self):
        x=score_input(); x['buffett']['structuralBreak']=None
        self.assertFalse(self.module('fundamental_score').calculate(x)['phase2_allowed'])
    def test_context_missing_weekly(self):
        x=context_input(); x['weekly_report']=None
        x['layers']['SECTOR']['sentiment_cap']=0.25
        r=self.module('context_caps').calculate(x)
        self.assertEqual(r['effective_risk_scalar'],1)
        self.assertEqual(r['sentiment_effect'],'NONE'); self.assertFalse(r['positive_evidence'])
    def test_context_stale_weekly(self):
        x=context_input(); x['weekly_report']['valid_until']='1999-12-31T00:00:00+00:00'
        r=self.module('context_caps').calculate(x)
        self.assertFalse(r['weekly_report_valid']); self.assertEqual(r['sentiment_effect'],'NONE')
    def test_context_low_coverage(self):
        x=context_input(); x['weekly_report']['data_coverage']=0.69
        self.assertFalse(self.module('context_caps').calculate(x)['weekly_report_valid'])
    def test_context_coverage_boundary(self):
        x=context_input(); x['weekly_report']['data_coverage']=0.70
        self.assertTrue(self.module('context_caps').calculate(x)['weekly_report_valid'])
    def test_context_missing_critical_layer(self):
        x=context_input(); x['weekly_report']['missing_critical_layers']=['INDUSTRY']
        self.assertFalse(self.module('context_caps').calculate(x)['weekly_report_valid'])
    def test_context_shock(self):
        x=context_input(); x['weekly_report']['material_shock']=True
        self.assertFalse(self.module('context_caps').calculate(x)['weekly_report_valid'])
    def test_context_all_missing_not_positive(self):
        x=context_input(); x['layers']={}; x['divergence']={'state':'INSUFFICIENT'}
        r=self.module('context_caps').calculate(x)
        self.assertEqual(r['effective_risk_scalar'],1); self.assertFalse(r['positive_evidence'])
        self.assertEqual(r['weakest_context_layer'],'INSUFFICIENT')
    def test_rotation_out_capped_by_authority(self):
        x=context_input(); x['divergence'].update(state='ROTATION_OUT',cap=1)
        r=self.module('context_caps').calculate(x)
        self.assertEqual(r['effective_risk_scalar'],0.25)
    def test_sector_weak_dominates_index(self):
        x=context_input(); x['layers']['SECTOR']['market_risk_scalar']=0.5
        r=self.module('context_caps').calculate(x)
        self.assertEqual(r['effective_risk_scalar'],0.5); self.assertEqual(r['weakest_context_layer'],'SECTOR')
    def test_market_regime_maximum(self):
        x=context_input(); x['layers']['SECTOR']['market_regime']='RISK_OFF'
        self.assertEqual(self.module('context_caps').calculate(x)['effective_risk_scalar'],0.5)
    def test_context_nan_rejected(self):
        x=context_input(); x['layers']['GLOBAL']['market_risk_scalar']=float('nan')
        with self.assertRaises(ValueError): self.module('context_caps').calculate(x)
    def test_context_future_report(self):
        x=context_input(); x['weekly_report']['published_at']='2000-01-04T00:00:00+00:00'
        self.assertFalse(self.module('context_caps').calculate(x)['weekly_report_valid'])
    def test_size_cap(self):
        x=risk_input(); x.update(stop_protector=97,support=99,atr14=2)
        r=self.module('risk_position_size').calculate(x)
        self.assertEqual(r['shares'],100); self.assertEqual(r['position_weight'],0.1)
    def test_rr_includes_costs(self):
        x=risk_input(); x['target']=120
        r=self.module('risk_position_size').calculate(x)
        self.assertEqual(r['rr_net'],1.95); self.assertFalse(r['rr_sufficient'])
        self.assertEqual(r['minimum_net_target'],120.5)
    def test_existing_position_concentration(self):
        x=risk_input(); x.update(existing_shares=95,stop_protector=97,support=99,atr14=2)
        r=self.module('risk_position_size').calculate(x)
        self.assertEqual(r['shares'],5); self.assertEqual(r['position_weight'],0.1)
    def test_existing_risk_consumes_budget(self):
        x=risk_input(); x['existing_shares']=50
        r=self.module('risk_position_size').calculate(x)
        self.assertEqual(r['shares'],50); self.assertEqual(r['existing_stop_risk'],500)
    def test_currency_mismatch(self):
        x=risk_input(); x['capital_currency']='EUR'
        with self.assertRaises(ValueError): self.module('risk_position_size').calculate(x)
    def test_stop_atr_invalid(self):
        x=risk_input(); x['stop_protector']=91
        with self.assertRaises(ValueError): self.module('risk_position_size').calculate(x)
    def test_stop_above_entry_invalid(self):
        x=risk_input(); x['stop_protector']=101
        with self.assertRaises(ValueError): self.module('risk_position_size').calculate(x)
    def test_risk_two_percent_without_exception(self):
        x=risk_input(); x['risk_fraction']=0.02
        with self.assertRaises(ValueError): self.module('risk_position_size').calculate(x)
    def test_risk_two_percent_exception(self):
        x=risk_input(); x.update(risk_fraction=0.02,exceptional_setup=True)
        self.assertEqual(self.module('risk_position_size').calculate(x)['base_risk_money'],2000)
    def test_no_reapply_scalar_input(self):
        x=risk_input(); x['risk_money']=500
        with self.assertRaises(ValueError): self.module('risk_position_size').calculate(x)
    def test_tunnel_long(self):
        r=self.module('tunnel_context').calculate(tunnel_input())
        self.assertTrue(r['AllowedLongContext']); self.assertTrue(r['LongSetupContext'])
        self.assertEqual(r['UpperObstacle_HT'],140)
    def test_tunnel_open_bar_no_signal(self):
        x=tunnel_input(); x['setup']['closed']=False
        self.assertFalse(self.module('tunnel_context').calculate(x)['LongSetupContext'])
    def test_tunnel_missing_observations(self):
        r=self.module('tunnel_context').calculate({})
        self.assertFalse(r['AllowedLongContext']); self.assertTrue(r['pending'])
    def test_tunnel_short_not_enabled(self):
        x=tunnel_input()
        for k in ('ht','setup'): x[k].update(Z_color='RED',G_color='RED',slope_G=-1,close=80)
        r=self.module('tunnel_context').calculate(x)
        self.assertTrue(r['AllowedShortContext']); self.assertFalse(r['ShortSetupContext'])
    def test_dca_valid(self):
        self.assertEqual(self.module('decision_rules').evaluate_dca(dca_input())['decision'],'DCA_AGRESIVO')
    def test_dca_above_p20(self):
        x=dca_input(); x['price']=81
        self.assertNotEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'DCA_AGRESIVO')
    def test_dca_no_sentiment(self):
        x=dca_input(); x['sentiment_complete']=False
        self.assertNotEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'DCA_AGRESIVO')
    def test_dca_broken_thesis(self):
        x=dca_input(); x['thesis_intact']=False
        self.assertEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'NO_DCA')
    def test_dca_rotation_out(self):
        x=dca_input(); x['divergence_state']='ROTATION_OUT'; x['reversal_confirmed']=False
        self.assertNotEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'DCA_AGRESIVO')
    def test_dca_overweight(self):
        x=dca_input(); x['final_weight']=0.101
        self.assertEqual(self.module('decision_rules').evaluate_dca(x)['decision'],'NO_DCA')
    def test_overshoot_boundary(self):
        self.assertTrue(self.module('decision_rules').overextended(120,100))
        self.assertFalse(self.module('decision_rules').overextended(119.99,100))


def badge_case(badge, score):
    def test(self):
        x=score_input(); x['buffett']['badge']=badge
        self.assertEqual(self.module('fundamental_score').calculate(x)['score'],score)
    return test
for badge, cap in [('AMBER',69),('RED',59),('GRAY',59)]:
    setattr(CoreTests,'test_badge_'+badge,badge_case(badge,cap))

def scalar_case(s):
    def test(self):
        x=risk_input(); x['effective_risk_scalar']=s
        r=self.module('risk_position_size').calculate(x)
        self.assertEqual(r['risk_money'],1000*s)
        self.assertEqual(r['shares'],math.floor(100*s))
        self.assertEqual(r['scalar_application_count'],1)
    return test
for s in (1,0.75,0.5,0.25,0):
    setattr(CoreTests,'test_scalar_'+str(s).replace('.','_'),scalar_case(s))

class IntegrationTests(CoreTests):
    # Inherit helper only, not core test cases (adjusted below).
    def test_valid_pipeline(self):
        e=self.module('analysis_engine').build(analysis_input())
        self.assertEqual(e['presentation']['entry'],'VALIDA')
        self.assertTrue(self.module('validate_analysis').validate(e)['valid'])
    def test_existing_position_not_automatic_sell(self):
        x=analysis_input(); x['fundamentals']['buffett']['badge']='RED'; x['buffett']['badge']='RED'
        x['technical']['entry_plan']=False; x['risk']=None
        x['position'].update(status='OPEN',shares=10,avg_price=90)
        e=self.module('analysis_engine').build(x)
        self.assertEqual(e['presentation']['position_action'],'NO ANADIR')
        self.assertTrue(self.module('validate_analysis').validate(e)['valid'])
    def test_no_changes_no_title_update(self):
        x=analysis_input(); x['review']={'mode':'FOLLOWUP','prior':{'score':85,'decision':'ALTA_CONVICCION'},'material_changes':[]}
        e=self.module('analysis_engine').build(x)
        self.assertFalse(e['computed']['review']['emit_updated_title'])
    def test_synthetic_rejected_as_operational(self):
        e=self.module('analysis_engine').build(analysis_input())
        self.assertFalse(self.module('validate_analysis').validate(e,operational=True)['valid'])
    def test_missing_report_can_use_independent_market_data(self):
        x=analysis_input(); x['context_stack']['weekly_report']=None
        e=self.module('analysis_engine').build(x)
        self.assertEqual(e['presentation']['entry'],'VALIDA')
        self.assertFalse(e['computed']['context']['positive_evidence'])
    def test_macro_etf_research_only(self):
        x=analysis_input(); x['instrument']['kind']='ETF_BROAD'
        e=self.module('analysis_engine').build(x)
        self.assertNotEqual(e['presentation']['entry'],'VALIDA')
    def test_invalid_json_cli(self):
        self.module('fundamental_score')
        p=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'fundamental_score.py')],
                         input='{"categories":NaN}',text=True,capture_output=True)
        self.assertNotEqual(p.returncode,0)

# Do not count inherited core tests twice.
for k in list(CoreTests.__dict__):
    if k.startswith('test_') and k not in IntegrationTests.__dict__:
        setattr(IntegrationTests,k,None)


def tamper_case(path, value):
    def test(self):
        e=self.module('analysis_engine').build(analysis_input())
        d=e
        for k in path[:-1]: d=d[k]
        d[path[-1]]=value
        self.assertFalse(self.module('validate_analysis').validate(e)['valid'])
    return test
for name,path,value in [
    ('score',['presentation','score'],67),
    ('decision',['presentation','decision'],'APTO'),
    ('rr',['computed','risk','rr_net'],1.75),
    ('double_scalar_money',['computed','risk','risk_money'],250),
    ('double_scalar_shares',['computed','risk','shares'],50),
    ('scalar_count',['computed','risk','scalar_application_count'],2),
    ('weight',['computed','risk','position_weight'],0.11),
    ('context',['computed','context','effective_risk_scalar'],0.25),
    ('title',['computed','review','emit_updated_title'],True),
    ('technical_claim',['presentation','technical_entry_present'],False),
    ('extra_technical_score',['computed','fundamental','score'],95),
]:
    setattr(IntegrationTests,'test_tamper_'+name,tamper_case(path,value))

def blocked_case(key, change):
    def test(self):
        x=analysis_input(); change(x)
        e=self.module('analysis_engine').build(x)
        self.assertNotEqual(e['presentation']['entry'],'VALIDA')
    return test
cases={
 'panic':lambda x:x['context_stack']['layers']['SECTOR'].update(sentiment_regime='PANIC_LIQUIDATION'),
 'rotation':lambda x:x['context_stack']['divergence'].update(state='ROTATION_OUT'),
 'low_scalar':lambda x:x['context_stack']['layers']['SECTOR'].update(market_risk_scalar=0.25),
 'no_reversal':lambda x:x['technical']['mtf'].update(recent_bull_cross=False),
 'no_volume':lambda x:x['technical']['mtf'].update(volume_confirmed=False),
 'obstacle':lambda x:x['technical'].update(obstacles=[110]),
 'aggressive_extended':lambda x:(x['instrument'].update(price=120),x['technical'].update(aggressive_entry=True)),
 'crowded_aggressive':lambda x:(x['buffett'].update(crowdingRisk='HIGH'),x['technical'].update(aggressive_entry=True)),
 'not_a_plus_half_risk':lambda x:(x['context_stack']['layers']['SECTOR'].update(market_risk_scalar=0.5),x['technical'].update(setup_grade='NORMAL')),
 'freshness_missing':lambda x:x['data_quality'].update(price_current=False),
 'short_not_requested':lambda x:x['technical'].update(side='SHORT'),
}
for name,change in cases.items():
    setattr(IntegrationTests,'test_gate_'+name,blocked_case(name,change))

if __name__=='__main__': unittest.main()
