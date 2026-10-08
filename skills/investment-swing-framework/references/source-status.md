# Estado de fuentes y dependencias

## Fuentes permanentes disponibles

Se recuperaron seis documentos originales proporcionados por el usuario: `estrategia_inversion.md`, `reglas_riesgo_tecnico.md`, `regla_tunel.md`, `tendencia_mercado.md`, `buffet_value_invest.md` y `configuracion_proyecto_actualizada.md`. El cuerpo base se conserva; se añade navegación. `estrategia_inversion.md`, `reglas_riesgo_tecnico.md` y `regla_tunel.md` incorporan además la enmienda técnica MTF autorizada por el usuario el 2026-09-29, registrada en el manifest. En el documento Buffett se elimina solo el frontmatter de la fuente independiente. Los hashes de original y versión empaquetada están en `source-manifest.json`.

Los contratos y scripts son implementación derivada del prompt de creación y de esas fuentes, no nuevas fuentes financieras. Su autoridad es subordinada. No hay cotizaciones ni estado real incorporados. No se han utilizado informes semanales para reconstruir un módulo permanente ausente.

## DATO PENDIENTE

| Dependencia | Disponibilidad | Efecto |
|---|---|---|
| sentimiento_posicionamiento.md original | No localizado; hook explícito | No generar de cero risk_appetite_score, contrarian_opportunity_score o sentiment_cap con una fórmula inventada. Aceptar informe externo verificable o neutralizar. |
| automatizacion_sentimiento_semanal.md original | No localizado; hook explícito | Contrato para recibir informes; no scheduler, tarea persistente ni producción automática del informe. |
| estrategia_asignacion_macro.md | No localizado; dependencia opcional del universo amplio | Asignación en ETFs amplios permanece research-only. Para habilitarla hace falta integrar la fuente y añadir tests, no cambiar un booleano. |
| Fórmula de las bandas originales del Túnel | No definida como generador en la fuente formal | Recibir observables originales del indicador. El script interpreta estados; no fabrica bandas ni periodos. |
| Datos actuales, estado, consenso, FX e informe vigente | Inputs externos por ejecución | Nunca quedan congelados en la Skill. DATO PENDIENTE cuando no pueden verificarse. |

Los dos hooks de sentimiento solo reiteran el fallback ya definido por el prompt y la estrategia; no pretenden sustituir el contenido original que falta.

## Decisiones técnicas explícitas

- El score es entero. El modelo justifica cada categoría; Python suma y valida, no evalúa cualitativamente una empresa.
- Los vetos conservan `raw_score` y `score` tras caps, y fuerzan `decision=NO_TRADE`; no se falsea el score a 59 solo para que el veto parezca un corte aritmético.
- Para compras adicionales, el riesgo de los títulos existentes hasta el stop se resta del presupuesto de la misma idea. Es una convención conservadora de implementación; no duplica el scalar.
- El tamaño se calcula con capital y cotización en la misma moneda. Una cartera EUR con entrada USD requiere conversión externa fechada; no se supone paridad.
- `RR_neto=(objetivo-entrada-costes_por_accion)/R` sigue la fórmula canónica. Se informa además de pérdida con costes. No se cambia silenciosamente el denominador.
- `ALIGNED_NEGATIVE` no tiene un cap numérico independiente documentado. Se usa el cap evidenciado y los de sus capas; el valor neutral 1.00 no significa permiso ni contexto favorable.
- Ningún flag de frescura del JSON demuestra por sí mismo que un dato se obtuvo del mercado. El agente tiene que verificarlo y citarlo.


## Referencia de implementación TradingView

`tradingview_mtf_swing_pivot.pine` es una copia exacta del script Pine v6 proporcionado por el usuario el 2026-09-29 para alinear terminología y observables técnicos. No es una fuente financiera ni reemplaza las reglas fundamentales. Su perfil por defecto usa EMA 5/13/34, SMA 30/50/200, HTF confirmado, pivots strength 3, RVOL 1.3x y Pivot Bias basado en H/L/C diario previo confirmado. El propio script declara 30/50/200 como elección de implementación, no redefinición canónica.

La Skill amplía esos observables con `RECOVERY_ENTRY` para razonamiento temprano de soporte/agota­miento. Ese setup no es un `longTrigger` emitido por el Pine y debe etiquetarse como lógica del framework.


## Perfil de opciones XTB V1

`options_xtb_long.md` es una referencia de implementacion autorizada por el usuario a partir de la interfaz XTB aportada. Limita el alcance a opciones long single-leg confirmadas por el ticket actual, sizing por PRIMA/VOLUMEN, break-even/perdida maxima y DTE. No convierte observaciones de una captura en constantes globales: el limite de volumen y el multiplicador se verifican por preview; IV, Greeks, OI, sell-to-open y multi-leg permanecen fuera de V1 salvo nueva evidencia/autorizacion.


## Momentum Leadership Prefilter v1 — extension 2026-10-08

La referencia derivada `momentum_prefilter.md` y el cálculo `momentum_prefilter.py` implementan una **fase de descubrimiento condicional `DISCOVERY_ONLY`**: proximidad a máximo 52w, retorno63, EMA11/21 ascendente y contracción True Range. La idea externa proporcionada por el usuario en `https://x.com/Gaurav_Cx10/status/2106493661387076056` es **inspiración**, no séptima fuente canónica ni evidencia de alpha validado. Ventanas, EMA SMA-seeded y TR5/TR20 con umbral 0,80 son convenciones de implementación y no un backtest.

El manifest registra un `implementation_references` adicional con SHA-256 exacto. Conservar los seis registros originales de `sources` sin cambiar sus hashes; las dependencias originales pendientes siguen pendientes. Este prefiltro no forma parte del input ni del código de `analysis_engine`, y no puede cambiar score, fases, contexto, técnica, stops, sizing, DCA o gestión. El agente debe verificar externamente procedencia, ajuste por splits, calendario de sesiones y frescura del OHLC.
