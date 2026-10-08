"""Build and validate a structured envelope. Data retrieval remains the calling agent's job."""
import argparse
from common import read_json, write_json
from analysis_engine import build
from validate_analysis import validate

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',nargs='?',default='-'); p.add_argument('--output')
    p.add_argument('--operational',action='store_true')
    a=p.parse_args()
    try:
        result=build(read_json(a.input)); check=validate(result,operational=a.operational)
        if not check['valid']:
            write_json(check,a.output); return 1
        result['validation']=check
        write_json(result,a.output); return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        write_json({'valid':False,'error':str(exc)},a.output); return 2
if __name__=='__main__': raise SystemExit(main())
