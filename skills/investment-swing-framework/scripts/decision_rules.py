"""DCA and structural extension rules, separate from fundamental scoring."""
from common import cli, number, integer

def overextended(price,sma200):
    if price is None or sma200 is None: return None
    p=number(price,'price',0); s=number(sma200,'sma200',0)
    if s<=0: return None
    # A boundary comparison avoids floating-point 19.999999999996 percent.
    return p>=s*1.2

def evaluate_dca(data):
    score=integer(data.get('score',0),'score',0,100)
    price=number(data.get('price'),'price',0)
    high=data.get('ytd_high')
    p20=number(high,'ytd_high',0)*0.8 if high is not None else None
    scalar=number(data.get('effective_risk_scalar',0),'effective_risk_scalar',0,1)
    weight=number(data.get('final_weight',0),'final_weight',0)
    fibo=data.get('fibo_retracement')
    if fibo is not None: number(fibo,'fibo_retracement',0)
    regimes=data.get('sentiment_regimes',[])
    market=data.get('market_regimes',[])
    blockers={'CROWDED_LONG','DISTRIBUTION','RISK_OFF_DELEVERAGING','PANIC_LIQUIDATION','INSUFFICIENT_DATA'}
    checks={
      'fundamental':score>=70,
      'thesis_intact':data.get('thesis_intact') is True,
      'major_structure':data.get('above_daily_wma200') is True or data.get('weekly_recovery_confirmed') is True,
      'fibo_zone':fibo is not None and 0.5<=fibo<=0.618,
      'p20':p20 is not None and price<=p20,
      'confirmed_reversal':data.get('reversal_confirmed') is True,
      'volume':data.get('volume_confirmed') is True,
      'tunnel':data.get('tunnel_compatible') is True,
      'market_regime':bool(market) and not set(market)&{'RISK_OFF','CAPITULATION_UNCONFIRMED','INSUFFICIENT'},
      'sentiment':data.get('sentiment_complete') is True and bool(regimes) and not set(regimes)&blockers,
      'scalar':scalar>0.25,
      'rotation':data.get('divergence_state')!='ROTATION_OUT' or data.get('reversal_confirmed') is True,
      'divergence':data.get('blocking_divergence') is False,
      'exposure':weight<=0.1,
      'predefined_plan':data.get('plan_predefined') is True,
      'not_overextended':data.get('overextended') is False,
    }
    failed=[k for k,v in checks.items() if not v]
    multiplier=number(data.get('aggressive_multiplier',1.5),'aggressive_multiplier',1.5,2)
    if not checks['fundamental'] or not checks['thesis_intact'] or not checks['exposure']:
        decision='NO_DCA'
    elif not failed: decision='DCA_AGRESIVO'
    elif scalar<=0.25 or set(regimes)&{'PANIC_LIQUIDATION'} or data.get('blocking_divergence') is True:
        decision='ESPERAR'
    elif not all(checks[k] for k in ('confirmed_reversal','volume','tunnel','market_regime','predefined_plan')):
        decision='ESPERAR'
    elif data.get('structural_compatible') is not True: decision='ESPERAR'
    elif scalar<1 or not checks['sentiment']: decision='DCA_REDUCIDO'
    else: decision='DCA_NORMAL'
    return dict(decision=decision,P20=p20,checks=checks,failed_conditions=failed,
                aggressive_multiplier=multiplier if decision=='DCA_AGRESIVO' else None,
                authorizes_order=False)

def review_delta(review,current):
    previous=review.get('prior')
    changes=review.get('material_changes',[])
    material=[c for c in changes if isinstance(c,dict) and c.get('reason') and c.get('source_ids')]
    changed=bool(previous) and (previous.get('score')!=current['score'] or previous.get('decision')!=current['decision'])
    return dict(mode=review.get('mode','INITIAL'),score_anterior=previous.get('score') if previous else None,
      decision_anterior=previous.get('decision') if previous else None,
      score_actual=current['score'],decision_actual=current['decision'],
      material_change=bool(material),changed=changed,
      categorias_modificadas=sorted({k for c in material for k in c.get('categories',[])}),
      motivo=[c['reason'] for c in material],
      unexplained_change=review.get('mode')=='FOLLOWUP' and changed and not material,
      emit_updated_title=review.get('mode')=='FOLLOWUP' and changed and bool(material))

if __name__=='__main__': raise SystemExit(cli(evaluate_dca,__doc__))
