"""Existing holdings: P/L, risk, close-based invalidation and management conditions."""
from common import cli, number

def calculate(data):
    shares=number(data.get('shares'),'shares',0)
    avg=data.get('avg_price'); price=number(data.get('current_price'),'current_price',0)
    if avg is not None: avg=number(avg,'avg_price',0)
    capital=data.get('capital_total'); stop=data.get('stop_protector')
    thesis=data.get('stop_thesis'); close=data.get('daily_close'); atr=data.get('atr14')
    for key in ('capital_total','stop_protector','stop_thesis','daily_close','atr14','weekly_low','ma20','higher_low','channel_base'):
        if data.get(key) is not None: number(data[key],key,0)
    costs=number(data.get('roundtrip_cost_per_share',0),'roundtrip_cost_per_share',0)
    be=avg+costs if avg is not None else None
    be_allowed=(data.get('t1_taken') is True and be is not None and atr is not None and atr>0
                and price>=be and price-be>=0.5*atr)
    invalidated=(thesis is not None and close is not None and data.get('daily_close_confirmed') is True and close<thesis)
    if data.get('structuralBreak') is True: invalidated=True
    trailing={}
    if data.get('weekly_low') is not None and atr is not None:
        trailing['weekly_low_minus_half_atr']=data['weekly_low']-0.5*atr
    for key in ('ma20','higher_low','channel_base'):
        if data.get(key) is not None: trailing[key]=data[key]
    # These are candidates, not a silently selected or lowered protective stop.
    return dict(unrealized_pl=shares*(price-avg) if avg is not None else None,
      unrealized_pl_fraction=price/avg-1 if avg is not None and avg>0 else None,
      market_value=shares*price,weight=shares*price/capital if capital is not None and capital>0 else None,
      remaining_stop_risk=shares*max(price-stop,0) if stop is not None else None,
      thesis_invalidated=invalidated,break_even_price=be,break_even_allowed=be_allowed,
      trailing_candidates=trailing,stop_fill_guaranteed=False,
      next_level=data.get('next_level'),next_event=data.get('next_event'))

if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
