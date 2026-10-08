# Trazabilidad de los requisitos de creación

| Secciones del prompt | Implementación |
|---|---|
| 1 activación y objetivo | SKILL frontmatter y workflow |
| 2 fuentes y precedencia | fuentes canónicas, source-status, manifest, auditor |
| 3-5 modularidad/control plane/pipeline | SKILL, references, scripts, analysis_engine/run_analysis |
| 6-7 identidad y datos actuales | SKILL fases1-3, data-contract, validator |
| 8-9 score y overrides | fundamental_score + tests de rangos, caps y vetos |
| 10 Buffett | referencia original y overlay sin bonus |
| 11 tendencia y sobreextensión | strategy, decision_rules.overextended y gate agresivo |
| 12-13 contexto y caps | context_caps, minimums, neutralidad, tests scalar1/.75/.5/.25/0 |
| 14 sentimiento | fallback neutral, comprobación del informe y hooks pendientes |
| 15 gate técnico | analysis_engine, validator y tests de bloqueo |
| 15–16 Entrada técnica/Túnel | entrada_tecnica_mtf + technical_entry_context como gate; Túnel como overlay sobre observables originales |
| 17 riesgo | risk_position_size: presupuesto, scalar una vez,10% agregado |
| 18 stops | risk_position_size + position_management; cierre vs mecha |
| 19 RR/targets/BE/trailing | cálculo canónico con costes + gestión |
| 20 DCA | decision_rules + pipeline, P20, gates conjuntos |
| 21 existentes | position_management, estado y output separados de nueva entrada |
| 22 reanálisis | review_delta, validator, historial externo |
| 23 estado vs reglas | state-contract y .gitignore |
| 24 datos | data-contract y fixture sintética tipada |
| 25 salida | output-contract, presentation derivada y cierre obligatorio |
| 26-28 scripts/invariantes/testing | scripts y tests unitarios, integración, regresión e integridad |
| 29 temporalidad | ninguna cartera/cotización/informe operativo en paquete |
| 30 portabilidad | Python estándar, rutas relativas, CLI archivo/stdin |
| 31 epistemología | fuente/tipo/periodo, DATO PENDIENTE y auditoría limitada |
| 32-33 implementación/entrega | inicializador, suite, validación oficial, skill.zip |

Las condiciones cualitativas requieren juicio evidenciado del agente; no se presentan como descubrimientos automáticos de Python. Las dependencias originales ausentes se detallan en source-status, sin contenido fabricado.


## Enmienda técnica 2026-09-29

- TradingView MTF Swing + Pivot: referencia congelada en `tradingview_mtf_swing_pivot.pine`.
- Perfil de referencia: EMA 5/13/34, SMA 30/50/200, 4H->1D y 1D->1W, HTF confirmado, pivot strength 3, RVOL 1.3x, invalidación por cierre.
- Pivot Bias diario: timing únicamente, H/L/C previo confirmado, sin lookahead favorable.
- `AllowedLongContext` deja de ser autorización/veto universal de nuevas entradas.
- Donchian: descartado; no forma parte del motor.
- DCA agresivo: sin relajación en esta enmienda.


## Extension OPTIONS-XTB-V1

- `OPT-XTB-01`: solo BUY_CALL/BUY_PUT single-leg confirmado por ticket actual.
- `OPT-XTB-02`: no sell-to-open ni multi-leg.
- `OPT-XTB-03`: DTE >=14 y >= planned_holding_days+5.
- `OPT-XTB-04`: sizing por prima/volumen con perdida maxima verificable; no asumir multiplier 100.
- `OPT-XTB-05`: aplicar effective_risk_scalar una sola vez y max_loss dentro del risk budget.
- `OPT-XTB-06`: target mas alla del break-even y RR_floor >=2.
- `OPT-XTB-07`: close-before-expiry por defecto; assignment/exercise fuera de V1.
- `OPT-XTB-08`: no DCA de long premium.


## Extension Momentum Leadership Prefilter v1 (2026-10-08)

- `MOM-DISC-01`: ejecutor independiente `scripts/momentum_prefilter.py`/`references/momentum_prefilter.md`; no cambio de `analysis_engine` ni scores; `test_prefilter_is_not_operational_input`.
- `MOM-DISC-02`: datos OHLC ajustados por splits y >=252 cierres completos, identidad/frescura/fuente; pruebas `ContractTests`.
- `MOM-DISC-03`: 52w(252), retorno63, SMA-seeded EMA11/21, mediana TR5/TR20; `ArithmeticTests` y `test_boundaries_and_flat_series`.
- `MOM-DISC-04`: estados `PASS/FAIL/INSUFFICIENT/NOT_APPLICABLE`, sin momentum score ni señal de operativa; `ClassificationTests`.
- `MOM-DISC-05`: carga solo en scanner/diagnóstico explícito, nunca veto en ticker individual o posición; `DiscoveryRoutingTests` + escenarios NO EJECUTADOS.
- `MOM-DISC-06`: trazabilidad como referencia de implementación sin elevar autoridad; `test_manifest_keeps_six_canonical_sources`, `audit_bundle.py`, validación de Skill y empaquetado limpio.
