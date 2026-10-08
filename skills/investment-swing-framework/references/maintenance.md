# Mantenimiento y portabilidad

## Runtime

Python3.10+ y biblioteca estándar. No APIs ni dependencias de red en scripts. Comandos desde la raíz instalada; desde otro directorio, resolver esa raíz y prefijar scripts/fixtures. No hay ruta absoluta de una máquina requerida.

```bash
python scripts/audit_bundle.py
python -m unittest discover -s scripts/tests -p 'test_*.py' -v
mkdir -p runtime
python scripts/run_analysis.py scripts/tests/fixtures/analysis.synthetic.json --output runtime/analysis.synthetic.json
python scripts/validate_analysis.py runtime/analysis.synthetic.json
```

La fixture es de test y falla intencionadamente con --operational. El directorio runtime está ignorado por Git; eliminarlo antes de volver a empaquetar. El entorno que ejecute la Skill debe proporcionar navegador/datos actuales y ejecución de Python. Sin alguno, degradar con pendientes; no fingir ejecución.

## Cambios de reglas

1. Incorporar la nueva fuente original e identificar su autoridad; no sobreescribir referencias con un informe temporal.
2. Revisar conflictos contra estrategia. Documentar interpretaciones, no aceptar el documento más reciente como autoridad superior por su fecha.
3. Escribir un test que falle para la nueva regla y comprobar el fallo.
4. Modificar el módulo mínimo, ejecutar toda la suite y comprobar CLI.
5. Actualizar source-manifest.json: hash original, hash empaquetado, adaptaciones/version y dependencia resuelta. Las implementaciones externas de referencia, como Pine, van en `implementation_references` con hash exacto y no adquieren autoridad fundamental por estar empaquetadas. No actualizar hashes simplemente para ocultar cambios no revisados.
6. Ejecutar audit_bundle y el validador oficial de Skills. Empaquetar con el script oficial del entorno como skill.zip, excluyendo cachés, runtime, secretos y archivos temporales.

El auditor detecta cambios de referencias respecto del manifest; no es una firma criptográfica ni prueba de autoría. No se realiza autoactualización silenciosa de reglas.

## Git

Versionar SKILL, agents, references, scripts/tests y manifest. No versionar cartera, informes semanales, claves, .env, salida runtime, cachés ni cuentas de broker. El paquete puede colocarse en un repositorio; esta entrega no crea ni publica un repositorio remoto.

## Alcance de pruebas

La suite comprueba aritmética, invariantes, gates, casos adversos y portabilidad de CLI. No constituye backtest, prueba de rentabilidad, calidad de datos en vivo ni validación de cumplimiento con otro modelo. Los escenarios de agente están separados con estado NO EJECUTADO.
