"""Pure analysis orchestration. No network, broker orders or mutable portfolio state."""
from copy import deepcopy
from common import number, integer, stamp, InputError
from fundamental_score import calculate as score
from context_caps import calculate as context
from risk_position_size import calculate as size
from tunnel_context import calculate as tunnel
from technical_entry_context import calculate as technical_entry
from decision_rules import evaluate_dca, overextended, review_delta
from position_management import calculate as manage

def build(data):
    x=deepcopy(data)
    f_input=deepcopy(x.get('fundamentals',{}))
    # The top-level Buffett view and fundamental input must not contradict each other.
    if x.get('buffett') is not None and f_input.get('buffett')!=x['buffett']:
        raise InputError('Top-level and fundamental Buffett assessments disagree')
    f=score(f_input)
    cx=deepcopy(x.get('context_stack',{}))
    if cx.get('as_of')!=x.get('analysis_at'): raise InputError('Context as_of must equal analysis_at')
    c=context(cx)
    inst=x.get('instrument',{}); tech=x.get('technical') or {}
    t=tunnel(x.get('tunnel') or {}) if f['phase2_allowed'] and x.get('tunnel') is not None else None
    te=technical_entry(tech.get('mtf') or {}) if f['phase2_allowed'] and tech.get('entry_plan') is True else None
    r=None; risk_error=None
    if f['phase2_allowed'] and x.get('risk'):
        ri=deepcopy(x['risk'])
        ri['effective_risk_scalar']=c['effective_risk_scalar']
        ri['fundamental_score']=f['score']
        try:
            if 'roundtrip_cost_per_share' not in ri:
                raise InputError('Cost estimate pending: provide roundtrip_cost_per_share explicitly')
            r=size(ri)
        except (ValueError,TypeError,KeyError) as exc: risk_error=str(exc)
    ext=overextended(inst.get('price'),x.get('structural_trend',{}).get('sma200_daily'))
    reasons=[]
    def gate(ok,reason):
        if not ok: reasons.append(reason)
    gate(f['phase2_allowed'],'FUNDAMENTAL_GATE')
    gate(inst.get('identity_verified') is True,'INSTRUMENT_IDENTITY_PENDING')
    gate(x.get('position',{}).get('status') in ('NONE','OPEN'),'POSITION_STATE_PENDING')
    gate(inst.get('currency') in ('USD','EUR'),'UNSUPPORTED_CURRENCY')
    gate(inst.get('kind') in ('STOCK','ETF_THEMATIC','ETF_BROAD'),'INSTRUMENT_KIND_PENDING')
    dq=x.get('data_quality',{})
    gate(all(dq.get(k) is True for k in ('price_current','fundamentals_current','news_checked')),'CURRENT_DATA_PENDING')
    gate(c['market_complete'],'MATERIAL_MARKET_CONTEXT_PENDING')
    gate(c['context_divergence_state']!='INSUFFICIENT','DIVERGENCE_REVIEW_PENDING')
    scalar=c['effective_risk_scalar']
    gate(scalar>0.25 if inst.get('kind')=='STOCK' else scalar>0,'RISK_SCALAR_BLOCK')
    gate(not c['panic_block'],'PANIC_LIQUIDATION_WAIT')
    gate(not c['capitulation_block'],'CAPITULATION_UNCONFIRMED_WAIT')
    gate(c['context_divergence_state']!='ROTATION_OUT','ROTATION_OUT_BLOCK')
    gate(tech.get('blocking_divergence') is False,'BLOCKING_DIVERGENCE_OR_PENDING')
    gate(tech.get('side','LONG')=='LONG','SHORT_EXECUTION_NOT_IMPLEMENTED')
    # Broad-market allocation cannot be activated by one unverified boolean.
    gate(inst.get('kind')!='ETF_BROAD','MACRO_ALLOCATION_POLICY_PENDING_RESEARCH_ONLY')
    gate(tech.get('entry_plan') is True,'NO_NEW_ENTRY_PLAN')
    gate(bool(te) and te['valid'],'TECHNICAL_SETUP_NOT_CONFIRMED')
    gate(tech.get('regime_compatible') is True,'REGIME_INCOMPATIBLE_OR_PENDING')
    gate(tech.get('event_risk_reviewed') is True,'EVENT_RISK_PENDING')
    gate(tech.get('correlation_reviewed') is True,'CORRELATION_REVIEW_PENDING')
    gate(tech.get('stop_thesis_basis')=='DAILY_CLOSE','SWING_INVALIDATION_REQUIRES_DAILY_CLOSE')
    gate(r is not None,'RISK_PLAN_MISSING_OR_INVALID')
    if scalar<=0.5:
        gate(tech.get('setup_grade')=='A_PLUS' and tech.get('liquid') is True,'HALF_RISK_REQUIRES_A_PLUS_LIQUID')
    if tech.get('aggressive_entry') is True:
        gate(ext is False,'AGGRESSIVE_OVEREXTENDED_OR_UNKNOWN')
        gate(x.get('buffett',{}).get('crowdingRisk')!='HIGH','AGGRESSIVE_CROWDING')
        if t and t.get('ExhaustionUp') is True:
            gate(False,'AGGRESSIVE_TUNNEL_EXHAUSTION')
    if r:
        gate(r['rr_sufficient'],'RR_INSUFFICIENT')
        gate(r['shares']>0,'POSITION_SIZE_ZERO')
        gate(r['position_weight']<=0.1+1e-12,'POSITION_OVER_10_PERCENT')
        obstacles=tech.get('obstacles')
        gate(isinstance(obstacles,list),'OBSTACLE_REVIEW_PENDING')
        all_obstacles=list(obstacles or [])
        if t and t['UpperObstacle_HT'] is not None: all_obstacles.append(t['UpperObstacle_HT'])
        ri=x['risk']; target=ri.get('target',r['T2'])
        gate(not any(number(v,'obstacle')>ri['entry'] and v<target for v in all_obstacles),'UPPER_OBSTACLE_BEFORE_TARGET')
        thesis=tech.get('stop_thesis')
        gate(thesis is not None and ri['stop_protector']<=number(thesis,'stop_thesis')<ri['entry'],'INVALID_THESIS_STOP')
    eligible=not reasons
    entry='VALIDA' if eligible else ('CONDICIONADA' if f['phase2_allowed'] else 'NO')
    if not f['phase2_allowed']: execution=None
    elif eligible: execution='ENTRADA_VALIDA'
    elif tech.get('aggressive_entry') and ext: execution='PRECIO_SOBRE_EXTENDIDO'
    elif 'RR_INSUFFICIENT' in reasons: execution='RR_INSUFICIENTE'
    elif c['panic_block'] or c['capitulation_block']: execution='REGIMEN_ADVERSO'
    elif c['context_divergence_state']=='ROTATION_OUT' or tech.get('blocking_divergence'): execution='DIVERGENCIA_CONTEXTUAL'
    else: execution='ESPERAR_CONFIRMACION'
    dca=None
    if x.get('dca'):
        di=deepcopy(x['dca']); di.update(score=f['score'],price=inst.get('price'),
          thesis_intact=di.get('thesis_intact') is True and not f['hard_overrides'],
          effective_risk_scalar=scalar,overextended=ext,sentiment_complete=c['sentiment_complete'],
          sentiment_regimes=[v.get('sentiment_regime') for v in c['layers'].values() if v.get('applicable') is True],
          market_regimes=[v.get('market_regime') for v in c['layers'].values() if v.get('applicable') is True],
          divergence_state=c['context_divergence_state'],
          blocking_divergence=tech.get('blocking_divergence') is not False,
          tunnel_compatible=bool(t) and t['AllowedLongContext'] and t['closed_bars'],
          final_weight=r['position_weight'] if r else di.get('final_weight',0))
        dca=evaluate_dca(di)
    position=x.get('position',{})
    action=None
    if position.get('status')=='OPEN':
        action='NO ANADIR'
        if eligible and dca and dca['decision'] in ('DCA_AGRESIVO','DCA_NORMAL','DCA_REDUCIDO'):
            action='ANADIR'
        if x.get('buffett',{}).get('structuralBreak') is True: action='CERRAR'
    management=None
    if position.get('status')=='OPEN':
        mi=deepcopy(position); mi['current_price']=inst.get('price')
        mi['structuralBreak']=x.get('buffett',{}).get('structuralBreak')
        management=manage(mi)
        if management['thesis_invalidated']: action='CERRAR'
    review=review_delta(x.get('review',{}),f)
    ticker=inst.get('ticker','DATO_PENDIENTE'); country=inst.get('country','DATO_PENDIENTE')
    title=f'{ticker}.{country}-{f["score"]}-{f["decision"]}'
    presentation=dict(score=f['score'],decision=f['decision'],entry=entry,execution=execution,
      technical_entry_present=f['phase2_allowed'] and tech.get('entry_plan') is True,
      position_action=action,canonical_title=title)
    return {'schema_version':'1.0','input':x,'computed':dict(fundamental=f,context=c,tunnel=t,risk=r,
      risk_error=risk_error,overextended=ext,technical_entry=te,dca=dca,review=review,position=management,
      approved_shares=r['shares'] if eligible and r else 0,
      eligibility=dict(valid=eligible,reasons=reasons),operational=not x.get('synthetic',False)),
      'presentation':presentation}
