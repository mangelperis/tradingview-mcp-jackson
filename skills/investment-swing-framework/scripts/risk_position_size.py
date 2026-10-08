"""Whole-share long sizing. All money inputs must be in the quotation currency."""
from decimal import Decimal, ROUND_FLOOR
from common import cli, decimal, integer, InputError

D=Decimal

def floor(value): return int(value.to_integral_value(rounding=ROUND_FLOOR))

def calculate(data):
    for forbidden in ('risk_money','risk_budget','scaled_risk','shares','scalar_application_count'):
        if forbidden in data: raise InputError(f'{forbidden}: supply raw inputs, not a previously scaled result')
    currency=data.get('currency')
    if currency not in ('USD','EUR') or data.get('capital_currency')!=currency:
        raise InputError('Explicit portfolio conversion to USD/EUR quotation currency required')
    capital=decimal(data.get('capital_total'),'capital_total',0)
    if capital<=0: raise InputError('capital_total must be positive')
    fraction=decimal(data.get('risk_fraction',0.01),'risk_fraction',0,0.02)
    if fraction>D('0.01'):
        if not all(data.get(k) is True for k in ('exceptional_setup','liquid','fully_confirmed')):
            raise InputError('Risk above 1% requires an exceptional, liquid, confirmed setup')
        if integer(data.get('fundamental_score',0),'fundamental_score',0,100)<80:
            raise InputError('Risk above 1% requires fundamental high conviction')
    scalar=decimal(data.get('effective_risk_scalar'),'effective_risk_scalar',0,1)
    entry=decimal(data.get('entry'),'entry',0)
    stop=decimal(data.get('stop_protector'),'stop_protector',0)
    support=decimal(data.get('support'),'support',0)
    atr=decimal(data.get('atr14'),'atr14',0)
    if entry<=0 or atr<=0 or stop>=entry or support>=entry:
        raise InputError('Require positive entry/ATR and support/stop below entry')
    if stop>support-atr: raise InputError('Protective stop must be at least 1 ATR below structural support')
    target=decimal(data.get('target',entry+2*(entry-stop)),'target',0)
    if target<=entry: raise InputError('Long target must exceed entry')
    costs=decimal(data.get('roundtrip_cost_per_share',0),'roundtrip_cost_per_share',0)
    existing=decimal(data.get('existing_shares',0),'existing_shares',0)
    mark=decimal(data.get('current_price',entry),'current_price',0)
    if mark<=0: raise InputError('current_price must be positive')
    R=entry-stop
    base=capital*fraction
    budget=base*scalar  # Single and only application of scalar.
    existing_risk=existing*max(mark-stop,D(0))
    remaining=max(budget-existing_risk,D(0))
    by_risk=floor(remaining/R)
    existing_value=existing*mark
    by_weight=max(0,floor((capital*D('0.10')-existing_value)/entry))
    liquidity=data.get('liquidity_max_shares')
    by_liquidity=integer(liquidity,'liquidity_max_shares') if liquidity is not None else by_risk
    shares=max(0,min(by_risk,by_weight,by_liquidity))
    value=D(shares)*entry
    rr=(target-entry-costs)/R
    result=dict(currency=currency,base_risk_money=base,effective_risk_scalar=scalar,
        risk_money=budget,existing_stop_risk=existing_risk,remaining_risk_money=remaining,
        risk_per_share=R,R=R,shares_by_risk=by_risk,shares_by_weight=by_weight,
        shares=shares,position_value=value,existing_position_value=existing_value,
        final_position_value=existing_value+value,position_weight=(existing_value+value)/capital,
        new_stop_risk=D(shares)*R,total_stop_risk=existing_risk+D(shares)*R,
        estimated_new_loss_with_costs=D(shares)*(R+costs),
        T1=entry+R,T2=entry+2*R,rr_net=rr,rr_sufficient=rr>=2,
        minimum_net_target=entry+2*R+costs,scalar_application_count=1,
        stop_buffer_atr=(support-stop)/atr,
        cost_efficiency_multiple=(target-entry)/costs if costs>0 else None,
        protective_stop_guaranteed=False)
    return {k:float(v) if isinstance(v,Decimal) else v for k,v in result.items()}

if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
