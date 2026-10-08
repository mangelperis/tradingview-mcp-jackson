"""Synthetic inputs only. No fixture is an operational market recommendation."""
from copy import deepcopy

CATEGORIES = dict(business_quality=18, profitability=13, balance_sheet=13,
                  free_cash_flow=13, growth=8, valuation=16, governance=4)

def score_input():
    return {'categories':deepcopy(CATEGORIES),
            'data_quality':dict(recent_statements=True, debt_verified=True,
                                fcf_verified=True, pre_profit=False, narrative_only=False),
            'buffett':dict(badge='GOLD', structuralBreak=False, shortThesisRisk='LOW',
                           qualityPass=True, compounderPass=True, crowdingRisk='LOW')}

def context_input():
    layer = dict(applicable=True, market_regime='RISK_ON', market_risk_scalar=1,
                 sentiment_regime='NEUTRAL', sentiment_cap=1,
                 source_ids=['s1'], sentiment_source_ids=['s1'])
    return {'as_of':'2000-01-03T22:00:00+01:00',
            'layers':{n:deepcopy(layer) for n in ['GLOBAL','REGION','STYLE','SECTOR','INDUSTRY']},
            'divergence':dict(state='ALIGNED_POSITIVE', cap=1, source_ids=['s1']),
            'weekly_report':dict(status='COMPLETE', published_at='2000-01-03T08:00:00+01:00',
                                 valid_until='2000-01-10T08:00:00+01:00', data_coverage=0.8,
                                 missing_critical_layers=[], material_shock=False)}

def risk_input():
    return dict(capital_total=100000, capital_currency='USD', currency='USD',
                risk_fraction=0.01, effective_risk_scalar=1, entry=100,
                support=92, atr14=2, stop_protector=90, target=125,
                roundtrip_cost_per_share=0.5, existing_shares=0, current_price=100,
                exceptional_setup=False, liquid=True, fully_confirmed=True,
                fundamental_score=85)

def tunnel_input():
    bar = dict(close=100, Z_low=90, Z_high=95, Z_color='GREEN', G=89,
               G_color='GREEN', slope_G=1, B_blue_low=80, B_blue_high=140,
               B_pink_low=75, B_pink_high=150, closed=True)
    prev=deepcopy(bar); prev.update(close=94, MACD_hist=1)
    setup=deepcopy(bar); setup.update(MACD_hist=2, vol_rel=1.5)
    return dict(ht=deepcopy(bar), setup=setup, previous=prev,
                EPS=0, SLOPE_MIN=0, VOL_MIN_FACTOR=1.3, shorts_requested=False)

def dca_input():
    return dict(score=85, thesis_intact=True, price=80, ytd_high=100,
                above_daily_wma200=True, weekly_recovery_confirmed=False,
                fibo_retracement=0.6, reversal_confirmed=True, volume_confirmed=True,
                tunnel_compatible=True, market_regimes=['RISK_ON'],
                sentiment_regimes=['NEUTRAL'], sentiment_complete=True,
                effective_risk_scalar=1, divergence_state='ALIGNED_POSITIVE',
                blocking_divergence=False, final_weight=0.08,
                contrarian=True, plan_predefined=True, structural_compatible=True,
                aggressive_multiplier=2, overextended=False)


def mtf_input(setup_type='REACCELERATION'):
    return dict(setup_type=setup_type, bar_closed=True, htf_confirmed=True,
        ma_types=dict(operating='EMA',structural_htf='SMA'),
        operating=dict(close=105,fast5=104,mid13=102,slow34=100),
        htf=dict(close=110,fast30=108,mid50=104,slow200=95),
        recent_bull_cross=True,breakout_confirmed=True,volume_confirmed=True,
        support_state='CONFIRMED',seller_exhaustion='CONFIRMED',
        pivot_bias=dict(bias='ALCISTA',event='RECUPERA_PIVOT',source='PREVIOUS_CONFIRMED_DAILY_HLC'))

def analysis_input():
    s=score_input()
    return dict(schema_version='1.0', synthetic=True, analysis_at='2000-01-03T22:00:00+01:00',
        instrument=dict(ticker='SYNTH', exchange='SYNTHETIC', country='US', currency='USD',
                        kind='STOCK', price=100, quote_at='2000-01-03T21:00:00+00:00',
                        identity_verified=True),
        data_quality=dict(price_current=True, fundamentals_current=True, news_checked=True),
        fundamentals=s, valuation=dict(status='SYNTHETIC_TEST_ONLY'), buffett=s['buffett'],
        structural_trend=dict(sma200_daily=100), context_stack=context_input(),
        market_regime=dict(status='DERIVED_BY_LAYER'), sentiment=dict(status='EXTERNAL_INPUT'),
        technical=dict(entry_plan=True, mtf=mtf_input(), regime_compatible=True, blocking_divergence=False, obstacles=[],
                       aggressive_entry=False, liquid=True, setup_grade='A_PLUS',
                       stop_thesis=92, stop_thesis_basis='DAILY_CLOSE', source_ids=['s1'],
                       event_risk_reviewed=True, correlation_reviewed=True),
        tunnel=tunnel_input(), risk=risk_input(), dca=None,
        position=dict(status='NONE', shares=0, currency='USD'),
        review=dict(mode='INITIAL', material_changes=[]),
        sources=[dict(id='s1', kind='DATO_REPORTADO', reference='urn:synthetic:fixture',
                      retrieved_at='2000-01-03T22:00:00+01:00',
                      as_of='2000-01-03T21:00:00+00:00')])
