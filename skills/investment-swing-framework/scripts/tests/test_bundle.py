import importlib
import re
import sys
import unittest
from pathlib import Path
EXPECTED_CANONICAL_HASHES = {'buffet_value_invest.md': ('9e04e6869840e2880ed35644a8f3eaca949890f90f8d7dc85537b5ce0df23ddb', '9f2a475685a1ce6c285736aae98000259132b8f88f2f6d469d17f766e7ee069d'), 'configuracion_proyecto_actualizada.md': ('303c22df7e97ea5985059ec26ff233250a2d9276b4f3e8f491641e283b320c4d', '73bc2d348380f6b19eaefd5b0bc476ed92959214d46739ca2f1d26f5583e005f'), 'estrategia_inversion.md': ('3e8c000e7e6570d1b367cfce3f1a3ce8c90e8fc0eeead65b28aa1df0fb353c57', '7dbde9586bfe17af1b5af6952e8af6c70f7740109303230510bda0135f5369ae'), 'regla_tunel.md': ('978f59b7647490ca9b979aa01e1a4f397965f575604a3ff25d46a8557181faa3', 'de680c6c777fa3b130e34a52f2f8a668ae4b4239118f0adc9aaacb376c843db3'), 'reglas_riesgo_tecnico.md': ('e44af693ab1d381b2a938babc534c5d6eea7cf40176fd9d978219020557b9ef1', 'c894748dd857e2afca1fe28ebc752686b3b3d1b1f7927334fb1657f3597cdc92'), 'tendencia_mercado.md': ('54ac87fa8b08a83021e534007333f2668317ab84e8fb07dc93852fc99a0b2bcf', 'ccbec8fbaa2d0a1a7268d1e30e0ca4946ad2fa18ef138a23dbeae747f9284e31')}
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))

class BundleTests(unittest.TestCase):
    def test_control_plane_compact_and_complete(self):
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertLess(len(text.splitlines()),500)
        self.assertNotIn('[TODO',text)
        self.assertIn('validate_analysis.py',text)
    def test_reference_dependencies_present(self):
        for name in ('estrategia_inversion.md','reglas_riesgo_tecnico.md','regla_tunel.md',
                     'tendencia_mercado.md','buffet_value_invest.md','sentimiento_posicionamiento.md',
                     'automatizacion_sentimiento_semanal.md','data-contract.md','output-contract.md','state-contract.md',
                     'options_xtb_long.md'):
            self.assertTrue((ROOT/'references'/name).is_file(),name)
    def test_missing_modules_explicit_not_fabricated(self):
        for name in ('sentimiento_posicionamiento.md','automatizacion_sentimiento_semanal.md'):
            path=ROOT/'references'/name
            self.assertTrue(path.exists(),name)
            self.assertIn('DATO PENDIENTE',path.read_text(encoding='utf-8'))
    def test_no_operational_weekly_or_holdings_files(self):
        self.assertFalse((ROOT/'references'/'sentimiento_semanal_actual.md').exists())
        self.assertFalse((ROOT/'state.json').exists())
    def test_integrity_audit(self):
        self.assertTrue((ROOT/'scripts'/'audit_bundle.py').exists())
        r=importlib.import_module('audit_bundle').audit(ROOT)
        self.assertTrue(r['valid'],r)
    def test_integrity_detects_change(self):
        self.assertTrue((ROOT/'scripts'/'audit_bundle.py').exists())
        import tempfile,shutil
        with tempfile.TemporaryDirectory() as tmp:
            copy=Path(tmp)/'skill'; shutil.copytree(ROOT,copy)
            path=copy/'references'/'estrategia_inversion.md'
            path.write_text(path.read_text(encoding='utf-8')+'\nmutated\n',encoding='utf-8')
            self.assertFalse(importlib.import_module('audit_bundle').audit(copy)['valid'])
    def test_control_plane_links_resolve(self):
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        for target in re.findall(r'\]\(((?:references|scripts|agents)/[^)#]+)(?:#[^)]*)?\)',text):
            self.assertTrue((ROOT/target).exists(),target)

if __name__=='__main__': unittest.main()



class MomentumBundleSafetyTests(unittest.TestCase):
    def test_momentum_module_is_required(self):
        import shutil, tempfile
        from audit_bundle import audit
        with tempfile.TemporaryDirectory() as tmp:
            dst=Path(tmp)/'skill'
            shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','.worktrees','.superpowers','runtime','__pycache__'))
            (dst/'scripts/momentum_prefilter.py').unlink()
            result=audit(dst)
            self.assertFalse(result['valid'],result)
            self.assertTrue(any('momentum_prefilter.py' in issue for issue in result['errors']))

    def test_momentum_reference_hash_tamper_detected(self):
        import shutil, tempfile
        from audit_bundle import audit
        with tempfile.TemporaryDirectory() as tmp:
            dst=Path(tmp)/'skill'
            shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','.worktrees','.superpowers','runtime','__pycache__'))
            ref=dst/'references/momentum_prefilter.md'
            ref.write_text(ref.read_text(encoding='utf-8')+'\nmutated\n',encoding='utf-8')
            result=audit(dst)
            self.assertFalse(result['valid'],result)
            self.assertTrue(any('momentum_prefilter.md' in issue for issue in result['errors']))

    def test_manifest_keeps_six_canonical_sources(self):
        import json
        data=json.loads((ROOT/'references/source-manifest.json').read_text())
        expected = EXPECTED_CANONICAL_HASHES
        observed = {r['name']:(r['original_sha256'],r['bundled_sha256']) for r in data['sources']}
        self.assertEqual(observed,expected)
        self.assertEqual(len(observed),6)
        self.assertEqual({r['name'] for r in data['missing_dependencies']},
                         {'sentimiento_posicionamiento.md','automatizacion_sentimiento_semanal.md','estrategia_asignacion_macro.md'})
        self.assertTrue(all(r['status']=='DATO PENDIENTE' for r in data['missing_dependencies']))

    def test_allow_momentum_discovery_reference_role(self):
        import json
        from audit_bundle import audit
        data=json.loads((ROOT/'references/source-manifest.json').read_text())
        self.assertEqual(data['version'],'1.3.0')
        found = [x for x in data['implementation_references'] if x.get('role')=='momentum_discovery_reference']
        self.assertEqual(len(found),1)
        self.assertEqual(found[0]['path'],'references/momentum_prefilter.md')
        self.assertTrue(audit(ROOT)['valid'])
