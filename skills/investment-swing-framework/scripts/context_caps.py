"""Hierarchical caps: neutral missing evidence, no multiplication between layers."""
from common import cli, number, stamp, evidence, InputError

LAYERS=('GLOBAL','REGION','STYLE','SECTOR','INDUSTRY','INSTRUMENT')
MARKET_MAX={'RISK_ON':1.0,'CONSTRUCTIVE':1.0,'CAUTION':0.75,
            'RISK_OFF':0.5,'CAPITULATION_UNCONFIRMED':0.0}
# ALIGNED_NEGATIVE has no independent numeric cap in the sources.
# Its supplied cap and the market layers constrain risk; 1.0 is not positive evidence.
DIVERGENCE_MAX={'ALIGNED_POSITIVE':1.0,'ALIGNED_NEGATIVE':1.0,
 'INDEX_STRONG_SECTOR_WEAK':0.5,'INDEX_WEAK_SECTOR_STRONG':0.75,
 'SECTOR_STRONG_INDUSTRY_WEAK':0.5,'SECTOR_WEAK_INDUSTRY_STRONG':0.5,
 'ROTATION_OUT':0.25,'ROTATION_IN':1.0,'MIXED':0.75,'INSUFFICIENT':1.0}

def report_status(report, as_of):
    if not isinstance(report,dict): return False,['WEEKLY_REPORT_MISSING']
    reasons=[]
    if report.get('status') not in ('COMPLETE','VALID','PARTIAL'): reasons.append('REPORT_STATUS')
    try:
        published=stamp(report.get('published_at'),'published_at')
        until=stamp(report.get('valid_until'),'valid_until')
        now=stamp(as_of,'as_of')
        if published>now or until<=now or until<=published: reasons.append('REPORT_NOT_CURRENT')
    except ValueError: reasons.append('REPORT_TIMESTAMPS_PENDING')
    coverage=report.get('data_coverage')
    if coverage is None: reasons.append('REPORT_COVERAGE_PENDING')
    elif number(coverage,'data_coverage',0,1)<0.70: reasons.append('REPORT_COVERAGE_BELOW_70')
    if report.get('missing_critical_layers'): reasons.append('REPORT_CRITICAL_LAYERS_MISSING')
    if report.get('material_shock') is not False: reasons.append('REPORT_SHOCK_CHECK_PENDING_OR_TRUE')
    return not reasons,reasons

def calculate(data):
    stamp(data.get('as_of'),'as_of')
    valid_report,pending=report_status(data.get('weekly_report'),data['as_of'])
    raw_layers=data.get('layers',{})
    if not isinstance(raw_layers,dict) or set(raw_layers)-set(LAYERS):
        raise InputError('layers: use GLOBAL, REGION, STYLE, SECTOR, INDUSTRY, INSTRUMENT')
    layers={}; market_missing=[]; applicable=[]; sentiment_missing=[]
    for name in LAYERS:
        item=raw_layers.get(name)
        if item is not None and item.get('applicable') is False:
            if not item.get('reason'): raise InputError(f'{name}: inapplicability requires reason')
            layers[name]={'applicable':False,'layer_effective_cap':1.0}; continue
        if item is None:
            layers[name]={'applicable':None,'market_valid':False,'sentiment_valid':False,
                          'market_risk_scalar':1.0,'sentiment_cap':1.0,'layer_effective_cap':1.0,
                          'market_regime':'INSUFFICIENT','sentiment_regime':'INSUFFICIENT_DATA'}
            if name!='INSTRUMENT': market_missing.append(name)
            continue
        applicable.append(name)
        scalar=item.get('market_risk_scalar'); regime=item.get('market_regime')
        if scalar is not None: number(scalar,f'{name}.market_risk_scalar',0,1)
        mvalid=scalar is not None and regime in MARKET_MAX and evidence(item.get('source_ids'))
        m=min(float(scalar),MARKET_MAX[regime]) if mvalid else 1.0
        if not mvalid: market_missing.append(name)
        cap=item.get('sentiment_cap')
        if cap is not None: number(cap,f'{name}.sentiment_cap',0,1)
        svalid=(valid_report and cap is not None and evidence(item.get('sentiment_source_ids'))
                and item.get('sentiment_regime') not in (None,'INSUFFICIENT_DATA'))
        s=float(cap) if svalid else 1.0
        if not svalid: sentiment_missing.append(name)
        layers[name]=dict(applicable=True,market_valid=mvalid,sentiment_valid=svalid,
                         market_regime=regime if mvalid else 'INSUFFICIENT',
                         market_risk_scalar=m,sentiment_regime=item.get('sentiment_regime') if svalid else 'INSUFFICIENT_DATA',
                         sentiment_cap=s,layer_effective_cap=min(m,s),
                         risk_appetite_score=item.get('risk_appetite_score') if svalid else None,
                         contrarian_opportunity_score=item.get('contrarian_opportunity_score') if svalid else None,
                         reversal_confirmation=item.get('reversal_confirmation','INSUFFICIENT') if svalid else 'INSUFFICIENT')
    div=data.get('divergence',{})
    state=div.get('state','INSUFFICIENT')
    if state not in DIVERGENCE_MAX: raise InputError('Unrecognized divergence state')
    requested=div.get('cap',1.0); number(requested,'divergence.cap',0,1)
    divvalid=state!='INSUFFICIENT' and evidence(div.get('source_ids'))
    maxcap=DIVERGENCE_MAX[state]
    # Canonical range 0.50-0.75: only confirmed internal rotation can use 0.75.
    if state=='SECTOR_WEAK_INDUSTRY_STRONG' and div.get('reversal_confirmation')=='CONFIRMED': maxcap=0.75
    divergence_cap=min(float(requested),maxcap) if divvalid else 1.0
    if not divvalid: pending.append('DIVERGENCE_PENDING')
    broad=min([layers[k]['layer_effective_cap'] for k in ('GLOBAL','REGION')]+[1.0])
    relative=min([layers[k]['layer_effective_cap'] for k in ('STYLE','SECTOR','INDUSTRY')]+[divergence_cap])
    effective=min(broad,relative)
    candidates=[k for k in LAYERS[:-1] if layers[k].get('market_valid') or layers[k].get('sentiment_valid')]
    weakest=min(candidates,key=lambda k:layers[k]['layer_effective_cap']) if candidates else 'INSUFFICIENT'
    weakest_cap=layers[weakest]['layer_effective_cap'] if candidates else 1.0
    limiter='DIVERGENCE' if divergence_cap<weakest_cap else weakest
    panic=any(v.get('sentiment_regime')=='PANIC_LIQUIDATION' for v in layers.values())
    capitulation=any(v.get('market_regime')=='CAPITULATION_UNCONFIRMED' for v in layers.values())
    market_complete=bool(applicable) and not market_missing
    sentiment_complete=bool(applicable) and valid_report and not sentiment_missing
    positive=(market_complete and sentiment_complete and divvalid and state=='ALIGNED_POSITIVE')
    return dict(layers=layers,broad_context_cap=broad,relative_context_cap=relative,
      divergence_cap=divergence_cap,context_divergence_state=state if divvalid else 'INSUFFICIENT',
      effective_risk_scalar=effective,weakest_context_layer=weakest,risk_limiter=limiter,
      weekly_report_valid=valid_report,sentiment_complete=sentiment_complete,
      sentiment_effect='CAP_ONLY' if valid_report else 'NONE',positive_risk_adjustment='FORBIDDEN',
      positive_evidence=positive,market_complete=market_complete,
      context_status='INSUFFICIENT' if not market_complete or not divvalid else ('ALINEADO' if state.startswith('ALIGNED') else 'DIVERGENTE'),
      panic_block=panic,capitulation_block=capitulation,
      missing_market_layers=market_missing,missing_sentiment_layers=sentiment_missing,
      pending=pending)

if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
