"""Verify packaged reference integrity and control-plane links; no network access."""
import argparse
import hashlib
import json
import re
from pathlib import Path

REQUIRED = (
    'SKILL.md', 'agents/openai.yaml',
    'references/estrategia_inversion.md', 'references/reglas_riesgo_tecnico.md',
    'references/regla_tunel.md', 'references/tendencia_mercado.md',
    'references/buffet_value_invest.md', 'references/configuracion_proyecto_actualizada.md',
    'references/sentimiento_posicionamiento.md',
    'references/automatizacion_sentimiento_semanal.md',
    'references/data-contract.md', 'references/output-contract.md', 'references/state-contract.md',
    'references/entrada_tecnica_mtf.md', 'references/tradingview_mtf_swing_pivot.pine',
    'references/options_xtb_long.md', 'references/momentum_prefilter.md', 'references/source-manifest.json',
    'scripts/fundamental_score.py', 'scripts/context_caps.py', 'scripts/technical_entry_context.py',
    'scripts/options_long.py', 'scripts/risk_position_size.py', 'scripts/momentum_prefilter.py', 'scripts/validate_analysis.py',
)


def audit(root=None):
    """Return errors instead of changing a missing or modified reference."""
    root=Path(root or Path(__file__).resolve().parents[1]).resolve()
    errors=[]; checked=[]; pending=[]
    def safe(relative):
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Unsafe relative path: '+str(relative))
        resolved=(root/path).resolve()
        if not resolved.is_relative_to(root):
            raise ValueError('Path escapes skill root: '+str(relative))
        return resolved
    for relative in REQUIRED:
        if not (root/relative).is_file(): errors.append('Missing required file: '+relative)
    try:
        control=(root/'SKILL.md').read_text(encoding='utf-8')
        if len(control.splitlines())>=500: errors.append('SKILL.md must remain below 500 lines')
        if '[TODO' in control: errors.append('Unfinished control-plane template')
        if not control.startswith('---\n'): errors.append('Missing YAML frontmatter')
        if 'name: investment-swing-framework' not in control: errors.append('Unexpected skill name')
        for target in re.findall(r'\]\(((?:references|scripts|agents)/[^)#]+)(?:#[^)]*)?\)',control):
            if not safe(target).is_file(): errors.append('Unresolved control-plane link: '+target)
        manifest=json.loads((root/'references'/'source-manifest.json').read_text(encoding='utf-8'))
        entries=manifest.get('sources',[])
        if len(entries)!=6: errors.append('Expected six supplied permanent sources; review manifest when extending')
        paths=set()
        for source in entries:
            relative=source.get('path',''); path=safe(relative)
            if relative in paths: errors.append('Duplicate manifest path: '+relative)
            paths.add(relative)
            if not path.is_file(): errors.append('Source missing: '+relative); continue
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            if actual!=source.get('bundled_sha256'): errors.append('Reference hash mismatch: '+relative)
            else: checked.append(relative)
            if not re.fullmatch('[0-9a-f]{64}',source.get('original_sha256','')):
                errors.append('Missing original source hash: '+relative)
        for ref in manifest.get('implementation_references',[]):
            relative=ref.get('path',''); path=safe(relative)
            if not path.is_file(): errors.append('Implementation reference missing: '+relative); continue
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            if actual!=ref.get('bundled_sha256'): errors.append('Implementation reference hash mismatch: '+relative)
            if ref.get('role') not in ('tradingview_implementation_reference','broker_options_profile_reference','momentum_discovery_reference'): errors.append('Unexpected implementation reference role: '+relative)
        for entry in manifest.get('missing_dependencies',[]):
            if entry.get('status')!='DATO PENDIENTE': errors.append('Missing dependency status must be explicit')
            pending.append(entry.get('name'))
        for name in ('sentimiento_posicionamiento.md','automatizacion_sentimiento_semanal.md'):
            if name in pending and 'DATO PENDIENTE' not in (root/'references'/name).read_text(encoding='utf-8'):
                errors.append('Missing dependency masquerades as supplied source: '+name)
        for path in root.rglob('*'):
            if path.is_symlink(): errors.append('Symlink not allowed in portable bundle: '+str(path.relative_to(root)))
            if path.is_file() and path.name in ('sentimiento_semanal_actual.md','state.json','positions.json','.env'):
                errors.append('Mutable or private operational input included: '+str(path.relative_to(root)))
        if sum(p.stat().st_size for p in root.rglob('*') if p.is_file())>25*1024*1024:
            errors.append('Uncompressed skill exceeds conservative 25 MB budget')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        errors.append(str(exc))
    return dict(valid=not errors,errors=errors,verified_sources=checked,pending_dependencies=pending,
                scope='Local integrity, not source authenticity, live-data freshness or financial suitability')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',nargs='?',help='Skill root; default resolved relative to this script')
    args=parser.parse_args(); result=audit(args.root)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['valid'] else 1

if __name__=='__main__': raise SystemExit(main())
