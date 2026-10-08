"""Recompute every derived field and validate cross-module invariants before reporting."""
import argparse
from common import read_json, write_json, stamp, number, evidence
from analysis_engine import build


def validate(envelope,operational=False):
    errors=[]; warnings=[]
    def fail(code,detail): errors.append({'code':code,'detail':detail})
    try:
        x=envelope['input']; expected=build(x)
        if envelope.get('schema_version')!='1.0': fail('SCHEMA_VERSION','Expected 1.0')
        for section in ('computed','presentation'):
            if envelope.get(section)!=expected[section]:
                fail('DERIVED_MISMATCH',f'{section} differs from independently recomputed values')
        f=expected['computed']['fundamental']; c=expected['computed']['context']
        r=expected['computed']['risk']; tech=x.get('technical') or {}; inst=x.get('instrument',{})
        now=stamp(x.get('analysis_at'),'analysis_at')
        if stamp(inst.get('quote_at'),'quote_at')>now: fail('FUTURE_PRICE','Quote is after analysis timestamp')
        if not inst.get('ticker') or not inst.get('exchange') or not inst.get('country'):
            fail('IDENTITY_FIELDS','Ticker, exchange and listing country are required')
        if inst.get('currency') not in ('USD','EUR'): fail('CURRENCY','Only USD/EUR quotations supported')
        if number(inst.get('price'),'price',0)<=0: fail('PRICE','Quoted price must be positive')
        if x.get('position',{}).get('currency') not in (None,inst.get('currency')):
            fail('POSITION_CURRENCY','Position and quoted instrument currency must match')
        if not f['phase2_allowed'] and (tech.get('entry_plan') is True or x.get('risk') is not None):
            fail('TECHNICAL_BELOW_GATE','Do not develop a new entry plan while fundamental gate is closed')
        if expected['computed']['review']['unexplained_change']:
            fail('UNEXPLAINED_REANALYSIS','Score/decision changed with no evidenced material change')
        b=x.get('buffett',{})
        if b.get('badge') in ('GOLD','GREEN') and b.get('qualityPass') is not True:
            fail('BUFFETT_BADGE_QUALITY','GOLD/GREEN requires minimum qualityPass')
        if r:
            ri=x['risk']; position=x.get('position',{})
            if ri.get('currency')!=inst.get('currency'): fail('RISK_CURRENCY','Risk plan and instrument currencies differ')
            if abs(float(ri.get('effective_risk_scalar',-1))-c['effective_risk_scalar'])>1e-12:
                fail('STALE_SCALAR','Risk input scalar must equal recomputed context scalar')
            if ri.get('fundamental_score',f['score'])!=f['score']: fail('STALE_SCORE','Risk input score mismatch')
            if ri.get('existing_shares',0)!=position.get('shares',0): fail('EXISTING_POSITION_OMITTED','Risk plan must include all existing shares')
            if ri.get('current_price')!=inst.get('price'): fail('MARK_PRICE_MISMATCH','Use current instrument price for concentration')
            if r['shares']>0 and r['position_weight']>0.1+1e-12: fail('CONCENTRATION','New/add-on position exceeds 10%')
        if operational and x.get('synthetic') is True: fail('SYNTHETIC_INPUT','Test fixture cannot be used operationally')
        sources=x.get('sources',[])
        ids={s.get('id') for s in sources if isinstance(s,dict)}
        if not sources or len(ids)!=len(sources) or any(not isinstance(i,str) or not i.strip() for i in ids): fail('SOURCES','Unique nonempty source IDs required')
        for source in sources:
            if not source.get('reference'): fail('SOURCE_REFERENCE','Missing source reference')
            if stamp(source.get('retrieved_at'),'source.retrieved_at')>now: fail('FUTURE_SOURCE','Source retrieved after analysis')
            if stamp(source.get('as_of'),'source.as_of')>now: fail('FUTURE_SOURCE','Source observation after analysis')
        def walk(value,path='input'):
            if isinstance(value,dict):
                for k,v in value.items():
                    if k.endswith('source_ids') and v is not None:
                        if not isinstance(v,list) or any(i not in ids for i in v): fail('SOURCE_ID',path+'.'+k)
                    walk(v,path+'.'+k)
            elif isinstance(value,list):
                for item in value: walk(item,path)
            elif isinstance(value,float): number(value,path)
        walk(x)
        if not c['weekly_report_valid']: warnings.append('SENTIMIENTO_SEMANAL: DATO PENDIENTE; neutral is not positive evidence')
        if not c['market_complete']: warnings.append('Material market context incomplete; new entry blocked')
        if expected['computed']['risk_error']: warnings.append(expected['computed']['risk_error'])
        if x.get('synthetic'): warnings.append('SYNTHETIC TEST ONLY: no live-data or source-authenticity verification')
        if x.get('position',{}).get('status')=='OPEN':
            position=x['position']
            for field in ('avg_price','currency'):
                if position.get(field) is None: warnings.append('POSITION DATO PENDIENTE: '+field)
        return dict(valid=not errors,errors=errors,warnings=warnings,
                    execution_valid=not errors and expected['computed']['eligibility']['valid'],
                    operational=operational and not errors and not x.get('synthetic',False))
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as exc:
        fail('MALFORMED_OR_INVALID_INPUT',str(exc))
        return dict(valid=False,errors=errors,warnings=warnings,execution_valid=False,operational=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',nargs='?',default='-'); p.add_argument('--operational',action='store_true')
    p.add_argument('--output'); a=p.parse_args()
    try: result=validate(read_json(a.input),operational=a.operational)
    except (ValueError,OSError) as exc: result={'valid':False,'errors':[str(exc)]}
    write_json(result,a.output)
    return 0 if result['valid'] else 1
if __name__=='__main__': raise SystemExit(main())
