"""Deterministic MTF long-entry context. Tunnel is overlay/confluence, not the authorizer."""
from common import cli, number

SETUPS={'RECOVERY_ENTRY','REACCELERATION','TREND_CONTINUATION','BREAKOUT_ENTRY'}
MA_TYPES_OPERATING={'SMA','EMA','SMMA (RMA)','WMA','VWMA','EVWAP','VRMA'}
MA_TYPES_HTF={'SMA','EMA','WMA'}


def _ma_block(block, names, label):
    if not isinstance(block,dict):
        raise ValueError(label+' must be an object')
    return {name:number(block.get(name),f'{label}.{name}') for name in names}


def calculate(data):
    if not isinstance(data,dict): raise ValueError('MTF input must be an object')
    setup_type=data.get('setup_type')
    if setup_type not in SETUPS: raise ValueError('Unsupported setup_type')
    op=_ma_block(data.get('operating'),('close','fast5','mid13','slow34'),'operating')
    htf=_ma_block(data.get('htf'),('close','fast30','mid50','slow200'),'htf')
    ma_types=data.get('ma_types') or {}
    op_type=ma_types.get('operating','EMA'); htf_type=ma_types.get('structural_htf','SMA')
    if op_type not in MA_TYPES_OPERATING: raise ValueError('Unsupported operating MA type')
    if htf_type not in MA_TYPES_HTF: raise ValueError('Unsupported HTF MA type')

    bar_closed=data.get('bar_closed') is True
    htf_confirmed=data.get('htf_confirmed') is True
    op_stack=op['fast5']>op['mid13']>op['slow34']
    op_above=op['close']>op['fast5'] and op['close']>op['mid13'] and op['close']>op['slow34']
    op_repair=op['fast5']>op['mid13'] and op['close']>op['slow34']

    htf_bull_stack=htf['fast30']>htf['mid50']>htf['slow200']
    htf_bear_stack=htf['fast30']<htf['mid50']<htf['slow200']
    htf_bull_regime=htf['mid50']>htf['slow200'] and htf['close']>htf['slow200']
    htf_long_compatible=htf_bull_regime and htf['close']>htf['mid50']
    htf_bearish_structural=htf_bear_stack and htf['close']<htf['slow200']
    if htf_bull_stack and htf['close']>htf['fast30']: htf_state='STRONG'
    elif htf_bull_stack and htf['close']<=htf['fast30'] and htf['close']>htf['mid50']: htf_state='PULLBACK'
    elif htf['mid50']>htf['slow200'] and htf['close']<=htf['mid50'] and htf['close']>htf['slow200']: htf_state='CORRECTION'
    elif htf_bearish_structural: htf_state='BEARISH_STRUCTURAL'
    elif htf['close']<htf['slow200']: htf_state='DETERIORATION'
    elif htf_bull_regime: htf_state='BULLISH'
    else: htf_state='NEUTRAL'

    recent_cross=data.get('recent_bull_cross') is True
    breakout=data.get('breakout_confirmed') is True
    volume=data.get('volume_confirmed') is True
    support=data.get('support_state')
    if support not in ('NONE','TESTING','FORMING','CONFIRMED','BROKEN',None):
        raise ValueError('Unsupported support_state')
    exhaustion=data.get('seller_exhaustion')
    if exhaustion not in ('NONE','POSSIBLE','CONFIRMED',None):
        raise ValueError('Unsupported seller_exhaustion')
    pb=data.get('pivot_bias') or {}
    pivot_bias=pb.get('bias','N/D'); pivot_event=pb.get('event','-')
    if pivot_bias not in ('ALCISTA','BAJISTA','NEUTRAL','N/D'): raise ValueError('Unsupported pivot bias')
    if pivot_event not in ('RECUPERA_PIVOT','PIERDE_PIVOT','-','N/D'): raise ValueError('Unsupported pivot event')
    pivot_positive=pivot_bias=='ALCISTA' or pivot_event=='RECUPERA_PIVOT'

    common=bar_closed and htf_confirmed and support!='BROKEN'
    if setup_type=='TREND_CONTINUATION':
        checks={'closed':bar_closed,'htf_confirmed':htf_confirmed,'htf_long':htf_long_compatible,
                'operating_stack':op_stack,'price_above_operating':op_above,
                'breakout':breakout,'volume':volume,'support_not_broken':support!='BROKEN'}
    elif setup_type=='REACCELERATION':
        checks={'closed':bar_closed,'htf_confirmed':htf_confirmed,'htf_long':htf_long_compatible,
                'operating_stack':op_stack,'price_above_operating':op_above,'recent_5_13_cross':recent_cross,
                'breakout':breakout,'volume':volume,'support_not_broken':support!='BROKEN'}
    elif setup_type=='BREAKOUT_ENTRY':
        checks={'closed':bar_closed,'htf_confirmed':htf_confirmed,'htf_long':htf_long_compatible,
                'operating_stack':op_stack,'breakout':breakout,'volume':volume,
                'support_not_broken':support!='BROKEN'}
    else: # RECOVERY_ENTRY: framework extension for earlier swing recovery; not a Pine longTrigger.
        checks={'closed':bar_closed,'htf_confirmed':htf_confirmed,'not_structural_bear':not htf_bearish_structural,
                'support_confirmed':support=='CONFIRMED','seller_exhaustion':exhaustion=='CONFIRMED',
                'pivot_timing_positive':pivot_positive,'operating_repair':op_repair,
                'recent_5_13_cross':recent_cross,'volume':volume}

    failed=[k for k,v in checks.items() if not v]
    reference_profile=(op_type=='EMA' and htf_type=='SMA')
    return dict(valid=not failed,setup_type=setup_type,failed_conditions=failed,checks=checks,
                operating_bullish_stack=op_stack,price_above_operating=op_above,
                htf_bullish_stack=htf_bull_stack,htf_bearish_structural=htf_bearish_structural,
                htf_bullish_regime=htf_bull_regime,htf_long_compatible=htf_long_compatible,
                htf_state=htf_state,pivot_timing_positive=pivot_positive,
                reference_profile=reference_profile,
                tradingview_reference=dict(operating=f'{op_type} 5/13/34',structural_htf=f'{htf_type} 30/50/200',
                                           pivot_bias_role='TIMING_ONLY',donchian=False),
                authorizes_order=False)


if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
