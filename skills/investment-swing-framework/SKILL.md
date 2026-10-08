---
name: investment-swing-framework
description: Use when the user requests fundamental and technical analysis, swing-trading research, watchlist reviews, momentum stock discovery/scans, earnings reanalysis, entry timing, stops, position sizing, DCA, position management, or XTB single-leg long options on USD/EUR stocks and ETFs. Triggers include Analiza NVS, Seguimiento, Entrar o esperar, opciones, call, put, Ampliar posicion, Se ha roto la tesis, and Aplica el marco completo.
---

# Investment Swing Framework

Aplicar un motor disciplinado de investigación y gestión, no una señal libre de compra. Separar calidad fundamental, posibilidad de nueva entrada y gestión de posiciones existentes. No ejecutar órdenes.

## Autoridad y carga progresiva

Respetar esta precedencia, también ante contradicciones entre ejemplos y reglas:

`estrategia_inversion > reglas_riesgo_tecnico > entrada_tecnica_mtf > regla_tunel > tendencia_mercado > sentimiento_posicionamiento > automatizacion_sentimiento_semanal > informes temporales`.

Subordinar Buffett a estrategia; usar configuración solo para comprobar integración. No considerar un hook pendiente como contenido canónico recuperado. Consultar [estado de fuentes](references/source-status.md) y verificar [manifest](references/source-manifest.json). Las referencias conservan el cuerpo base de las fuentes disponibles y documentan explícitamente la enmienda técnica MTF autorizada el 2026-09-29.

| Fase | Cargar |
|---|---|
| Siempre | [estrategia](references/estrategia_inversion.md), [datos](references/data-contract.md), [salida](references/output-contract.md) |
| Descubrimiento momentum solicitado | [prefiltro de momentum](references/momentum_prefilter.md) |
| Estado o seguimiento | [estado](references/state-contract.md) |
| Fundamental | [Buffett](references/buffet_value_invest.md) |
| Contexto | [tendencia](references/tendencia_mercado.md), [sentimiento](references/sentimiento_posicionamiento.md) |
| Técnica y riesgo | [riesgo](references/reglas_riesgo_tecnico.md), [entrada MTF](references/entrada_tecnica_mtf.md), [Pine de referencia](references/tradingview_mtf_swing_pivot.pine), [Túnel](references/regla_tunel.md) |
| Opciones XTB solicitadas | [opciones long single-leg](references/options_xtb_long.md) |
| ETF | [adaptación ETF](references/etf-contract.md) |
| Informe semanal | [hook de automatización](references/automatizacion_sentimiento_semanal.md) |
| Integración/mantenimiento | [configuración](references/configuracion_proyecto_actualizada.md), [mantenimiento](references/maintenance.md) |

## Fase 0 condicional — discovery de momentum

Solo para peticiones explícitas de escanear/descubrir acciones líderes por momentum o calcular ese diagnóstico para un ticker, cargar [Momentum Leadership Prefilter](references/momentum_prefilter.md) y ejecutar `scripts/momentum_prefilter.py` con OHLC diarios verificados. Su resultado es `DISCOVERY_ONLY`: `PASS` prioriza investigación, `FAIL` excluye solo de ese scanner, `INSUFFICIENT` conserva pendientes y `NOT_APPLICABLE` excluye clases fuera de alcance. **Nunca** alterar score fundamental, entrada técnica, `effective_risk_scalar`, riesgo ni gestión de posiciones. No ejecutar por defecto en `Analiza`, `Seguimiento`, `Reanaliza` o DCA. Para un ticker solicitado analizar normalmente aunque el prefiltro sea `FAIL`.

## Flujo obligatorio

1. **Resolver instrumento.** Confirmar ticker, bolsa, país de cotización, USD/EUR y tipo. No resolver ambigüedades por parecido. Obtener precio, hora de la cotización y hora de análisis en Europe/Madrid. Si no puede verificarse, emitir DATO PENDIENTE y bloquear ejecución.
2. **Resolver estado externo.** Distinguir candidato de posición OPEN/NONE. Leer estado disponible antes de suponer títulos, coste o análisis previo. No incrustar cartera ni conversaciones dentro de reglas. Un estado desconocido impide autorizar compras.
3. **Recabar datos actuales.** Usar navegación/herramientas disponibles; priorizar IR, filings, bolsas y organismos oficiales. Verificar resultados, guidance, ingresos, márgenes, EPS, deuda/caja/vencimientos, FCF, dilución, recompras, dividendos y noticias materiales. No atribuir frescura a una cifra por copiarla de una conversación. Citar fuentes y periodos; marcar ausencias, nunca completarlas de memoria.
4. **Calcular Fase 1.** Justificar las siete categorías exclusivamente fundamentales con la estrategia. Ejecutar `fundamental_score.py`; aplicar Buffett, datos insuficientes y vetos. No asignar puntos por precio técnico, medias, RSI, volumen, patrón, Túnel, VIX o sentimiento.
5. **Cerrar gate fundamental.** Con score <70 o veto duro, no desarrollar una nueva entrada ni generar entrada/stop/T1/T2/tamaño para comprar. Permitir diagnóstico estructural y gestión protectora de una posición existente; no equiparar NO_TRADE a venta automática. Con score >=70 sin veto, continuar.
6. **Revisar tendencia.** Recabar diarias 20/50/200 y semanales 20/50/200, indicando SMA/WMA exacta, periodo, ajustes y vela cerrada. Revisar estructura y gráficos 1/5 años. Distancia alcista >=20% sobre SMA200 diaria: SOBRE-EXTENSION, sin cambiar score.
7. **Resolver contexto jerárquico.** GLOBAL > REGION > STYLE > SECTOR > INDUSTRY > INSTRUMENT. Verificar pertenencia y proxies; no sustituir industria por índice amplio. Separar régimen de mercado de sentimiento. Ejecutar `context_caps.py`; mostrar divergencia, capa débil y scalar limitante.
8. **Validar sentimiento.** Usar informe externo vigente solo con cobertura >=70%, capas críticas completas y sin shock material posterior. Ausente/caducado/incompleto: DATO PENDIENTE, cap 1.00, efecto NONE, nunca evidencia positiva. PANIC_LIQUIDATION mantiene WAIT. No programar trabajo futuro desde este hook.
9. **Desarrollar técnica.** Usar `entrada_tecnica_mtf.md` como motor de autorización: estructura HTF confirmada, setup 5/13/34, soporte, Pivot Bias, pivots confirmados, breakout/volumen y tipo de setup. Ejecutar `technical_entry_context.py`. No usar Donchian. El Túnel es overlay de zonas, obstáculos, agotamiento y deterioro: `AllowedLongContext=false` no es un veto universal. Ejecutar `tunnel_context.py` solo sobre observables reales; no fabricar bandas.
10. **Fijar riesgo.** Separar stop de tesis por cierre diario, protector fuera de estructura >=1 ATR(14), y táctico. Ejecutar `risk_position_size.py`. Aplicar el scalar una sola vez al presupuesto; después limitar títulos por 10% agregado y liquidez. Reducir tamaño, no comprimir el stop. Exigir R/R neto >=2; T2=2R bruto no garantiza ese neto si hay costes.
10A. **Opciones XTB, solo si se solicitan.** Validar primero la tesis del subyacente. Limitar V1 a BUY_CALL/BUY_PUT single-leg confirmados por el ticket actual; no proponer sell-to-open ni multi-leg. Exigir DTE >=14 y >= horizonte+5, preview actual de PRIMA/VOLUMEN, perdida maxima verificable y `RR_floor >=2`. Ejecutar `options_long.py`. No asumir multiplicador 100: inferirlo solo del preview actual cuando premium, precio y volumen sean coherentes.
11. **DCA o posición.** Ejecutar `decision_rules.py` para DCA y `position_management.py` para P/L, riesgo y BE/trailing. DCA agresivo exige todas las condiciones; un multiplicador 1.5-2 no vuelve a multiplicar el scalar ni el tamaño aprobado. No vender solo porque una nueva entrada esté bloqueada.
12. **Reanalizar sin deriva.** Buscar cambios materiales primero. Conservar desglose y score previos salvo evidencia nueva identificada; mostrar delta, categorías, motivo y fuentes. Emitir TITULO_CANONICO_ACTUALIZADO solo si cambia score/decisión por cambio material. Un seguimiento sin historial verificado se identifica como nueva línea base.
13. **Validar y publicar.** Construir input según contrato; ejecutar pipeline y validator. Corregir errores; con datos incompletos publicar salida bloqueada y pendientes, no ENTRADA VALIDA. No confundir validación lógica con autenticación de fuentes o rentabilidad comprobada.

## Gates que no pueden rebajarse

- Structural break o short thesis HIGH: NO_TRADE aunque el score aritmético sea alto. Buffett no añade puntos.
- Acciones: scalar <=0.25 bloquea nuevas entradas; con scalar <=0.50 exigir A_PLUS y liquidez. Los caps se combinan por mínimo, nunca multiplicándolos.
- ROTATION_OUT material/bloqueante, capitulación no confirmada, pánico, riesgo/costes pendientes, contexto material ausente, setup MTF inválido o R/R insuficiente: esperar.
- Prohibir entrada agresiva sobreextendida y exposición agregada nueva >10%. Distinguir `risk.shares` teórico de `computed.approved_shares`: solo este último supera todos los gates.
- Cortos desactivados por defecto. Una petición explícita habilita diagnóstico Túnel corto, no reutiliza el motor de sizing largo ni ejecuta una orden.
- ETFs amplios: solo investigación de asignación mientras falte la estrategia macro. No conceder score de empresa a un ETF por analogía.
- Opciones XTB V1: solo single-leg long confirmado por ticket actual. DTE <14, accion BUY no confirmada, perdida maxima no verificable, RR_floor <2 o estrategia sell/multi-leg bloquean la operativa de opciones.

## Ejecución de código

Requerir Python 3.10+ y biblioteca estándar. Resolver la raíz instalada de esta Skill; ejecutar desde ella o prefijar sus rutas resueltas. Mantener `runtime/` externo al paquete/versionado. No instalar librerías ni necesitar credenciales.

```bash
python scripts/audit_bundle.py
python scripts/technical_entry_context.py runtime/mtf.json
python scripts/options_long.py runtime/options.json
python scripts/run_analysis.py runtime/input.json --operational --output runtime/analysis.json
python scripts/validate_analysis.py runtime/analysis.json --operational
```

Cada calculadora acepta un objeto JSON por archivo o stdin; consultar `--help`. El contrato especifica sus campos. Los scripts no recaban cotizaciones ni autentican fuentes: esas obligaciones siguen siendo del agente. Si no hay runtime, no afirmar que se ejecutaron validadores; señalar VALIDACION AUTOMATICA PENDIENTE y no autorizar ejecución.

## Salida obligatoria

Usar [output-contract.md](references/output-contract.md), con título, hora, instrumento, resumen ejecutivo, score/desglose, evidencia fundamental, contexto, scalar, gates y pendientes. Añadir técnica solo tras gate; para OPEN incluir títulos, coste, P/L, peso, invalidación y acción. Si el usuario solicita opciones, añadir el bloque XTB V1 solo despues de validar el subyacente y el preview actual. Terminar exactamente con `DECISION FINAL: ...`. Citar datos y separar DATO REPORTADO / CONSENSO / CALCULO / INFERENCIA / DATO PENDIENTE. No mostrar JSON completo salvo diagnóstico.

## Verificación y extensión

Consultar [trazabilidad de requisitos](references/requirements-map.md), [verificación](references/verification.md) y [escenarios de comportamiento](scripts/tests/behavioral-scenarios.md). Ejecutar antes de distribuir cambios:

```bash
python -m unittest discover -s scripts/tests -p 'test_*.py' -v
python scripts/audit_bundle.py
```
