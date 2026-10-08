"""Canonical fundamental arithmetic. Category assessment remains evidence-based judgment."""
from common import cli, integer, documented, InputError

CATEGORY_MAX = dict(business_quality=20, profitability=15, balance_sheet=15,
                    free_cash_flow=15, growth=10, valuation=20, governance=5)

def classify(score):
    score=integer(score,'score',0,100)
    if score<60: return 'NO_TRADE'
    if score<70: return 'WATCHLIST'
    if score<80: return 'APTO'
    return 'ALTA_CONVICCION'

def calculate(data):
    categories=data.get('categories',{})
    if set(categories)!=set(CATEGORY_MAX):
        raise InputError('categories: require exactly the seven fundamental categories; no technical points')
    points={k:integer(categories[k],k,0,m) for k,m in CATEGORY_MAX.items()}
    raw=sum(points.values()); caps=[]; pending=[]; overrides=[]
    quality=data.get('data_quality',{})
    for k in ('recent_statements','debt_verified','fcf_verified'):
        if quality.get(k) is not True:
            caps.append({'rule':k,'cap':59}); pending.append(k)
    if quality.get('pre_profit') is True and quality.get('narrative_only') is True:
        if not documented(quality.get('sector_exception')):
            caps.append({'rule':'PRE_PROFIT_NARRATIVE','cap':59})
    b=data.get('buffett',{})
    badge=b.get('badge','GRAY')
    if badge not in ('GOLD','GREEN','AMBER','RED','GRAY'):
        raise InputError('Unrecognized Buffett badge')
    if badge=='AMBER': caps.append({'rule':'BUFFETT_AMBER','cap':69})
    if badge=='RED': caps.append({'rule':'BUFFETT_RED','cap':59})
    if badge=='GRAY' and not documented(b.get('alternative_valuation')):
        caps.append({'rule':'BUFFETT_GRAY','cap':59})
    # Missing structural assessment is not silently converted into an intact thesis.
    if b.get('structuralBreak') is True: overrides.append('STRUCTURAL_BREAK')
    elif b.get('structuralBreak') is not False:
        caps.append({'rule':'STRUCTURAL_ASSESSMENT_PENDING','cap':59}); pending.append('structuralBreak')
    short=b.get('shortThesisRisk','NA')
    if short not in ('LOW','MODERATE','HIGH','NA'): raise InputError('Invalid shortThesisRisk')
    if short=='HIGH': overrides.append('SHORT_THESIS_HIGH')
    if short=='NA': pending.append('shortThesisRisk')
    score=min([raw]+[c['cap'] for c in caps])
    decision='NO_TRADE' if overrides else classify(score)
    return dict(raw_score=raw,score=score,decision=decision,categories=points,
                caps=caps,hard_overrides=overrides,pending=pending,
                phase2_allowed=score>=70 and not overrides)

if __name__=='__main__': raise SystemExit(cli(calculate,__doc__))
