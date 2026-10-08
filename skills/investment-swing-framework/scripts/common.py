"""Strict JSON I/O and numeric primitives; Python 3.10+, standard library only."""
import argparse
import json
import math
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

class InputError(ValueError):
    pass

def number(value, name, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise InputError(f'{name}: finite numeric value required')
    n=float(value)
    if not math.isfinite(n): raise InputError(f'{name}: non-finite number')
    if minimum is not None and n < minimum: raise InputError(f'{name}: below {minimum}')
    if maximum is not None and n > maximum: raise InputError(f'{name}: above {maximum}')
    return n

def decimal(value, name, minimum=None, maximum=None):
    number(value,name,minimum,maximum)
    return Decimal(str(value))

def integer(value, name, minimum=0, maximum=None):
    n=number(value,name,minimum,maximum)
    if n != int(n): raise InputError(f'{name}: integer required')
    return int(n)

def stamp(value, name):
    if not isinstance(value,str): raise InputError(f'{name}: ISO8601 timestamp required')
    try: d=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as exc: raise InputError(f'{name}: invalid timestamp') from exc
    if d.tzinfo is None: raise InputError(f'{name}: UTC offset required')
    return d

def evidence(value):
    return isinstance(value,list) and bool(value) and all(isinstance(i,str) and i.strip() for i in value)

def documented(value):
    return isinstance(value,dict) and value.get('robust') is True and bool(value.get('rationale')) and evidence(value.get('source_ids'))

def reject_constant(value):
    raise InputError(f'Invalid JSON constant: {value}')

def unique_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise InputError(f'Duplicate JSON key: {k}')
        out[k]=v
    return out

def read_json(path=None):
    text=Path(path).read_text(encoding='utf-8') if path and path!='-' else sys.stdin.read()
    value=json.loads(text,parse_constant=reject_constant,object_pairs_hook=unique_pairs)
    if not isinstance(value,dict): raise InputError('Top-level JSON object required')
    return value

def write_json(value,path=None):
    text=json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n'
    if path: Path(path).write_text(text,encoding='utf-8')
    else: sys.stdout.write(text)

def cli(function, description):
    p=argparse.ArgumentParser(description=description)
    p.add_argument('input',nargs='?',default='-',help='JSON file or stdin (-)')
    p.add_argument('--output',help='Output JSON path (default stdout)')
    a=p.parse_args()
    try: write_json(function(read_json(a.input)),a.output)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        write_json({'valid':False,'error':str(exc)})
        return 2
    return 0
