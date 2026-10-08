"""Conservative validator for XTB-style single-leg long options. No market data or orders."""
from common import cli, number, integer, InputError

OPTION_TYPES={'CALL','PUT'}
ORDER_MODES={'PREMIUM','VOLUME'}
ACTIONS={'BUY_CALL','BUY_PUT'}


def calculate(data):
    if not isinstance(data,dict):
        raise InputError('Options input must be an object')
    option_type=data.get('option_type')
    if option_type not in OPTION_TYPES: raise InputError('option_type must be CALL or PUT')
    order_mode=data.get('order_mode')
    if order_mode not in ORDER_MODES: raise InputError('order_mode must be PREMIUM or VOLUME')
    action=data.get('broker_action')
    expected_action='BUY_CALL' if option_type=='CALL' else 'BUY_PUT'

    underlying=number(data.get('underlying_price'),'underlying_price',0)
    strike=number(data.get('strike'),'strike',0)
    target=number(data.get('target_price'),'target_price',0)
    option_price=number(data.get('option_price'),'option_price',0)
    volume=number(data.get('volume'),'volume',0)
    premium=number(data.get('premium_total'),'premium_total',0)
    broker_loss=number(data.get('broker_max_loss'),'broker_max_loss',0)
    breakeven=number(data.get('broker_break_even'),'broker_break_even',0)
    capital=number(data.get('capital_total'),'capital_total',0)
    base_risk=number(data.get('base_risk_pct'),'base_risk_pct',0,0.02)
    scalar=number(data.get('effective_risk_scalar'),'effective_risk_scalar',0,1)
    costs=number(data.get('direct_costs_total',0),'direct_costs_total',0)
    dte=integer(data.get('dte'),'dte',1)
    holding=integer(data.get('planned_holding_days'),'planned_holding_days',1)

    checks={}
    checks['broker_buy_action_confirmed']=action==expected_action
    checks['quote_current']=data.get('quote_current') is True
    checks['underlying_thesis_valid']=data.get('underlying_thesis_valid') is True
    if option_type=='PUT':
        checks['bearish_request_explicit']=data.get('bearish_requested') is True
    checks['dte_min_14']=dte>=14
    checks['dte_buffer']=dte>=holding+5
    checks['target_direction']=target>underlying if option_type=='CALL' else target<underlying
    checks['target_beyond_breakeven']=target>breakeven if option_type=='CALL' else target<breakeven

    broker_limit=data.get('broker_volume_limit')
    if broker_limit is not None:
        limit=number(broker_limit,'broker_volume_limit',0)
        checks['broker_volume_limit']=volume<limit

    inferred_multiplier=premium/(option_price*volume)
    checks['effective_multiplier_positive']=inferred_multiplier>0

    expected_be=strike+option_price if option_type=='CALL' else strike-option_price
    be_tol=max(0.02,option_price*0.10)
    checks['breakeven_consistent']=abs(expected_be-breakeven)<=be_tol

    loss_tol=max(1.0,premium*0.05)
    checks['broker_loss_consistent']=abs(broker_loss-premium)<=loss_tol

    max_loss=max(broker_loss,premium+costs)
    risk_budget=capital*base_risk*scalar
    checks['risk_scalar_open']=scalar>0.25
    checks['max_loss_within_budget']=max_loss<=risk_budget+1e-12
    checks['premium_within_10pct_cap']=premium<=capital*0.10+1e-12

    if option_type=='CALL':
        intrinsic=max(target-strike,0)*volume*inferred_multiplier
    else:
        intrinsic=max(strike-target,0)*volume*inferred_multiplier
    profit_floor=intrinsic-max_loss
    rr_floor=profit_floor/max_loss if max_loss>0 else None
    checks['rr_floor_2x']=rr_floor is not None and rr_floor>=2.0

    failed=[k for k,v in checks.items() if not v]
    return {
        'valid':not failed,
        'status':'OPTIONS_ENTRY_VALID' if not failed else 'OPTIONS_BLOCKED',
        'option_type':option_type,
        'order_mode':order_mode,
        'failed_conditions':failed,
        'checks':checks,
        'effective_multiplier':inferred_multiplier,
        'risk_budget':risk_budget,
        'max_loss_total':max_loss,
        'intrinsic_floor_at_target':intrinsic,
        'profit_floor_at_target':profit_floor,
        'rr_floor':rr_floor,
        'dte':dte,
        'planned_holding_days':holding,
        'expiry_management':'CLOSE_BEFORE_EXPIRY',
        'advanced_chain_metrics_required':False,
        'advanced_chain_metrics_role':'DIAGNOSTIC_ONLY_IF_SEPARATELY_VERIFIED',
        'authorizes_order':False
    }


if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
