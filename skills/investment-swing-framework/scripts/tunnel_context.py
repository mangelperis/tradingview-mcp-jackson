"""Interpret supplied Tunnel observables; never reconstruct undisclosed indicator bands."""
from common import cli, number, InputError

UP={'IMPULSE_UP','PULLBACK_UP'}
DOWN={'IMPULSE_DOWN','PULLBACK_DOWN'}
REQUIRED=('close','Z_low','Z_high','Z_color','G','G_color','slope_G')

def state(bar,eps,slope):
    if not isinstance(bar,dict) or any(bar.get(k) is None for k in REQUIRED): return 'INSUFFICIENT'
    for k in ('close','Z_low','Z_high','G','slope_G'): number(bar[k],k)
    if bar['Z_low']>bar['Z_high']: raise InputError('Tunnel correction-zone bounds are reversed')
    p=bar['close']; lo=bar['Z_low']-eps; hi=bar['Z_high']+eps
    up=bar['Z_color']=='GREEN' and bar['G_color']=='GREEN' and bar['slope_G']>slope
    down=bar['Z_color']=='RED' and bar['G_color']=='RED' and bar['slope_G'] < -slope
    if up:
        return 'IMPULSE_UP' if p>hi else ('BROKEN_UP' if p<lo else 'PULLBACK_UP')
    if down:
        return 'IMPULSE_DOWN' if p<lo else ('BROKEN_DOWN' if p>hi else 'PULLBACK_DOWN')
    return 'NEUTRAL'

def calculate(data):
    eps=number(data.get('EPS',0),'EPS',0)
    slope=number(data.get('SLOPE_MIN',0),'SLOPE_MIN',0)
    vol_min=number(data.get('VOL_MIN_FACTOR',1.3),'VOL_MIN_FACTOR',0)
    ht=data.get('ht',{}); setup=data.get('setup',{}); prev=data.get('previous',{})
    hs=state(ht,eps,slope); ss=state(setup,eps,slope)
    complete=hs!='INSUFFICIENT' and ss!='INSUFFICIENT'
    closed=all(x.get('closed') is True for x in (ht,setup,prev))
    allowed_long=complete and hs in UP and ss in UP
    allowed_short=complete and hs in DOWN and ss in DOWN
    pending=[]; flags=[]
    if not complete: pending.append('TUNNEL_OBSERVABLES')
    if not closed: flags.append('UNCONFIRMED_BAR_OR_HT'); pending.append('CLOSED_BARS')
    pullback=False; breakout=False; impulse=False; downbreak=False; downimpulse=False
    upper=None; lower=None; exhaust_up=None; exhaust_down=None
    if complete:
        p=number(setup['close'],'setup.close')
        breakout=p>setup['Z_high']+eps; downbreak=p<setup['Z_low']-eps
        if all(prev.get(k) is not None for k in ('close','Z_low','Z_high')):
            pullback=prev['Z_low']-eps<=prev['close']<=prev['Z_high']+eps
        else: pending.append('PREVIOUS_CORRECTION_ZONE')
        if all(v is not None for v in (setup.get('MACD_hist'),prev.get('MACD_hist'),setup.get('vol_rel'))):
            macd=number(setup['MACD_hist'],'MACD_hist'); old=number(prev['MACD_hist'],'previous.MACD_hist')
            vol=number(setup['vol_rel'],'vol_rel',0)
            impulse=macd>old and vol>=vol_min
            downimpulse=macd<old and vol>=vol_min
        else: pending.append('IMPULSE_INPUTS')
        highs=[ht[k] for k in ('Z_high','G','B_blue_high','B_pink_high') if ht.get(k) is not None]
        lows=[ht[k] for k in ('Z_low','G','B_blue_low','B_pink_low') if ht.get(k) is not None]
        for value in highs+lows: number(value,'obstacle')
        upper=min([v for v in highs if v>p],default=None)
        lower=max([v for v in lows if v<p],default=None)
        if any(ht.get(k) is None for k in ('B_blue_high','B_pink_high','B_blue_low','B_pink_low')):
            pending.append('HT_RIBBONS')
        if all(setup.get(k) is not None for k in ('B_pink_low','B_pink_high')):
            exhaust_up=setup['B_pink_low']<=p<=setup['B_pink_high'] and setup['slope_G']<=slope
        else: pending.append('EXHAUSTION_UP_INPUTS')
        # The source does not define how the lower pink ribbon is generated.
        # Require observed lower bounds rather than guessing a symmetric formula.
        if all(setup.get(k) is not None for k in ('lower_pink_low','lower_pink_high')):
            exhaust_down=setup['lower_pink_low']<=p<=setup['lower_pink_high'] and setup['slope_G']>=-slope
        else: pending.append('EXHAUSTION_DOWN_INPUTS')
        if ss=='BROKEN_UP' or hs=='BROKEN_UP' or p<setup['G']-eps: flags.append('LONG_STRUCTURE_WARNING')
    if complete and not allowed_long and not allowed_short: flags.append('TIMEFRAME_CONFLICT_OR_NEUTRAL')
    if exhaust_up: flags.append('EXHAUSTION_UP_NO_AGGRESSIVE_ENTRY')
    return dict(trend_state_HT=hs,trend_state_SETUP=ss,AllowedLongContext=allowed_long,
      AllowedShortContext=allowed_short,CondPullbackPrev=pullback,CondBreakUpNow=breakout,
      ImpulseStrength=impulse,UpperObstacle_HT=upper,LowerObstacle_HT=lower,
      ExhaustionUp=exhaust_up,ExhaustionDown=exhaust_down,
      LongSetupContext=closed and allowed_long and pullback and breakout and impulse,
      ShortSetupContext=data.get('shorts_requested') is True and closed and allowed_short and pullback and downbreak and downimpulse,
      closed_bars=closed,tunnel_risk_flags=flags,pending=pending)

if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
