"""Unit-explicit valuation arithmetic. Missing inputs remain null, never invented."""
from common import cli, number

def calculate(data):
    pe=data.get('pe'); growth=data.get('eps_growth_pct')
    if pe is not None: pe=number(pe,'pe')
    if growth is not None: growth=number(growth,'eps_growth_pct')
    interpretable=pe is not None and pe>0 and growth is not None and growth>0 and data.get('growth_reliable') is True
    fcf=data.get('fcf'); cap=data.get('market_cap'); price=data.get('price'); high=data.get('ytd_high')
    for key in ('fcf','market_cap','price','ytd_high','enterprise_value'):
        if data.get(key) is not None: number(data[key],key)
    return dict(PEG=pe/growth if interpretable else None,
      PEG_status='INTERPRETABLE' if interpretable else 'PEG no interpretable',
      fcf_yield=fcf/cap if fcf is not None and cap is not None and cap>0 else None,
      ev_fcf=data['enterprise_value']/fcf if data.get('enterprise_value') is not None and fcf is not None and fcf>0 else None,
      P20=high*0.8 if high is not None and high>0 else None,
      drawdown_from_ytd_high=price/high-1 if price is not None and high is not None and high>0 else None)

if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
