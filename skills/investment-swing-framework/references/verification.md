# Verificacion de entrega

## Resultados ejecutados

- Suite: **126 tests superados, 0 fallos**, duracion observada 1.628 s.
- Runtime probado: Python 3.13.5. El codigo usa sintaxis compatible con Python 3.10+; no se ejecuto una matriz de versiones.
- Validador oficial de Skills: `Skill is valid!`.
- Auditor de integridad: seis referencias verificadas contra sus SHA-256; sin errores.
- CLI desde un directorio distinto: pipeline, validator y auditor superados.
- Calculadoras obligatorias por stdin: superadas.
- Fixture sintetica con `--operational`: rechazada, como corresponde.
- Presupuesto monetario manipulado: rechazado por recomputacion independiente.
- Compilacion de todos los scripts y comprobacion de texto UTF-8: superadas.

## Comandos reproducibles

```bash
python -m unittest discover -s scripts/tests -p 'test_*.py' -v
python scripts/audit_bundle.py
mkdir -p runtime
python scripts/run_analysis.py scripts/tests/fixtures/analysis.synthetic.json --output runtime/example.json
python scripts/validate_analysis.py runtime/example.json
```

La ultima validacion sin --operational es exclusivamente de test. Anadir --operational a esta fixture debe devolver exit1; no eliminar su etiqueta synthetic para hacerla pasar.

## Cobertura

Score, limites y cada override; neutralidad de datos ausentes; scalar1/.75/.5/.25/0 y aplicacion unica; divergencias y panico; exposicion agregada10%; RR/costes/ATR; Tunnel por observables; DCA; sobreextension; gestion de existentes; cierre diario vs mecha; BE/trailing; fuentes; seguimiento material; manipulacion de resultados; integridad de referencias y enlaces del control plane.

## Limites de la comprobacion

No se han realizado backtests, pruebas con capital real, autenticacion de fuentes de mercado, evaluacion de rentabilidad ni pruebas de comportamiento con otro agente. Los escenarios de agente tienen estado NO EJECUTADO en su documento. Los datos de test son sinteticos y no representan recomendaciones.

Faltan los originales permanentes de sentimiento y automatizacion semanal, y la politica de asignacion macro para habilitar ese universo. Los hooks y bloqueos estan implementados y comprobados; no se presenta contenido inventado como fuente recuperada.


## Invariantes MTF añadidos

- `AllowedLongContext=false` no bloquea por sí solo una entrada si `technical_entry.valid=true` y los demás gates pasan.
- Un `UpperObstacle_HT` conocido antes del objetivo económico sigue bloqueando/posponiendo.
- Pivot Bias alcista sin soporte/agota­miento/setup no autoriza.
- `REACCELERATION` exige cruce 5/13 reciente; `TREND_CONTINUATION` no.
- HTF no confirmado o vela operativa abierta bloquean confirmación.
- `RECOVERY_ENTRY` puede preceder a alineación HTF completa, pero no cuando existe `BEARISH_STRUCTURAL`.
- Donchian no forma parte del contrato.


## Opciones XTB V1

Verificar al menos:

- preview equivalente a option_price 0.251, volume 3.98 y premium 99.90 infiere multiplier ~100 sin hardcodearlo;
- DTE 3 bloquea;
- DTE 17 con holding 5 supera el gate temporal;
- max_loss por encima del risk budget bloquea;
- limite de volumen del ticket se respeta solo si se aporta;
- PUT direccional sin solicitud bajista explicita bloquea;
- SELL_CALL/SELL_PUT o cualquier accion distinta a BUY correspondiente bloquea;
- RR_floor <2 bloquea;
- datos de IV/Greeks/OI ausentes no se fabrican.
