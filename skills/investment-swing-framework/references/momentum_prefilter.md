# Momentum Leadership Prefilter v1 — DISCOVERY_ONLY

## Propósito, activación y autoridad

Utilizar únicamente al buscar/escanear **acciones líderes por momentum** para crear o priorizar una watchlist, o cuando se solicite expresamente el diagnóstico de momentum de un ticker. No activar automáticamente para `Analiza`, `Seguimiento`, `Reanaliza`, DCA, compras, gestión de posiciones o cualquier decisión individual.

`DISCOVERY_ONLY` significa selección para **investigación**, no una señal de trading. El prefiltro no pertenece a la jerarquía normativa `estrategia_inversion > reglas_riesgo_tecnico > entrada_tecnica_mtf > regla_tunel > tendencia_mercado > sentimiento_posicionamiento > automatizacion_sentimiento_semanal > informes temporales`. No modifica fundamentales, Buffett, valoración, `score`, `TITULO_CANONICO`, gates de Fase 2, `effective_risk_scalar`, técnica 5/13/34, HTF 30/50/200, stops estructurales/ATR, R/R, DCA ni posiciones. Tampoco modifica `computed.approved_shares`.

- `PASS`: priorizar el análisis fundamental del candidato; **no** inferir `APTO`, `ENTRADA VALIDA` ni posición nueva.
- `FAIL`: omitirlo de **este** scanner; jamás convertirlo en `NO_TRADE` o vetar un ticker solicitado individualmente.
- `INSUFFICIENT`: evidencia no comparable, incompleta, no verificada o caducada; no confundir con fallo del patrón.
- `NOT_APPLICABLE`: clase de instrumento o moneda fuera del alcance.

Un `PASS` con fundamentales <70 mantiene WATCHLIST/NO_TRADE según reglas. `PASS` con `structuralBreak=true` sigue `NO_TRADE`; con sobreextensión >=20% sobre SMA200 diario no habilita entrada agresiva. `PASS` en posición `OPEN` no ordena vender, mantener o añadir. No sustituir `entrada_tecnica_mtf` ni los gates de riesgo con un resultado del prefiltro.

## SOURCE-DERIVED frente a IMPLEMENTATION CONVENTIONS

**SOURCE-DERIVED — inspiración:** la publicación en X `https://x.com/Gaurav_Cx10/status/2106493661387076056` propone: proximidad <=10% al máximo de 52 semanas, subida >=30% en tres meses, EMAs 11/21 ascendentes y velas estrechas. Es una heurística externa, **not validated** como alpha/backtest de esta implementación, y **no** constituye autoridad canónica. Los términos de pendiente y compresión no están suficientemente definidos en esa idea para ejecutar un cálculo reproducible sin elegir convenciones adicionales.

**IMPLEMENTATION CONVENTIONS — elecciones propias v1:** 252 sesiones, 63 sesiones, pendiente sobre cinco sesiones, EMA SMA-seeded, mediana True Range 5/20 con umbral inclusivo 0.80; ninguna de estas elecciones implica ventaja estadística demostrada.

| Check | Métrica independiente, velas diarias CERRADAS y split-adjusted | Condición |
|---|---|---|
| `NEAR_52W_HIGH` | `close[t] / max(high[t-251:t]) - 1` | `>= -0.10` |
| `MOMENTUM_63_SESSIONS` | `close[t] / close[t-63] - 1` | `>= 0.30` |
| `EMA11_SLOPE` | EMA11(t) vs EMA11(t-5) | aumento estricto |
| `EMA21_SLOPE` | EMA21(t) vs EMA21(t-5) | aumento estricto |
| `TIGHT_RANGE` | mediana(TR últimas 5) / mediana(TR últimas 20) | `<= 0.80` con denominador `>0` |

TR = `max(high-low, abs(high-prev_close), abs(low-prev_close))`; en primera observación, TR=high-low. **Las últimas cinco sesiones se incluyen en la ventana de 20**. EMA con primera semilla SMA(periodo), en el índice periodo-1, y suavizado `alpha=2/(periodo+1)`. Ventanas inclusivas y cinco condiciones booleanas; **no crear momentum score**.

## Contrato y semántica de evidencia

Invocar `python scripts/momentum_prefilter.py INPUT.json [--output OUTPUT.json]` o stdin según `common.cli`. Python >=3.10 y biblioteca estándar. Un instrumento por llamada, sin red, API, datos de brokers, scraping, ejecución de órdenes ni datos de cartera.

Entrada separada del envelope de `analysis_engine.py`:

```json
{
  "analysis_at": "2026-10-08T11:08:00+02:00",
  "instrument": {
    "ticker": "TEST.US", "exchange": "NYSE", "kind": "STOCK",
    "currency": "USD", "identity_verified": true
  },
  "market_data": {
    "price_basis": "SPLIT_ADJUSTED",
    "expected_last_completed_session": "2026-10-07",
    "bars": [
      {"date": "2025-10-08", "open": 100, "high": 102, "low": 99, "close": 101}
    ]
  },
  "source": {
    "reference": "urn:synthetic:example", "kind": "DAILY_OHLC",
    "as_of": "2026-10-07", "retrieved_at": "2026-10-08T11:00:00+02:00"
  }
}
```

Este ejemplo es **sintético e INSUFFICIENT**: solo contiene una vela. Para `PASS`/`FAIL`, exigir >=252 observaciones diarias completadas, ordenadas, únicas, H/L/O/C finitos y coherentes, procedencia documentada, hora de análisis y recuperación con offset, `source.as_of = expected_last_completed_session = date(última barra)`, OHLC **ajustado coherentemente por splits**, sin datos futuros ni total-return reinvertido. Los campos son declaraciones del recolector, no prueba de autenticidad; verificar externamente el calendario de bolsa, cobertura de sesiones, corporate actions y frescura. El módulo offline comprueba consistencia, **no** verifica fuente, bolsa ni autenticidad.

`NOT_APPLICABLE`: emisor verificado no STOCK o no USD/EUR, sin exigir barras. `INSUFFICIENT`: identidad no confirmada, precio sin ajuste, fuente ausente, historia <252, cierre no coincidente, barra incompleta o mediana TR20 cero. `PASS` o `FAIL` requieren TODAS las métricas válidas; `FAIL` conserva métricas y lista de condiciones fallidas. `INSUFFICIENT`/`NOT_APPLICABLE` muestran `checks` y `metrics` nulos y `pending` explícitos. Tipos falsos, NaN, cadenas numéricas, datos futuros, fechas duplicadas, orden incorrecto o velas imposibles son errores de entrada (`valid=false`, exit 2); una clasificación válida sale con código 0.

Salida: `module=MOMENTUM_LEADERSHIP_PREFILTER_V1`, `role=DISCOVERY_ONLY`, `ticker`, `as_of_session`, `status`, mapa `checks` de cinco claves, `metrics` con `high_52w`, `distance_52w_high`, `return_63_sessions`, `ema11_now/lag5`, `ema21_now/lag5`, `median_tr5/20`, `tight_range_ratio`, `failed_conditions`, `pending`, `source_reference`. No emitir score, entrada, stop, objetivo, tamaño, recomendación ni scalar.

## Uso en scanner

1. Obtener un universo de acciones USD/EUR e historial OHLC diario verificable con origen y sesión completada para cada acción.
2. Ejecutar la CLI una vez por acción. Agrupar `PASS` para investigación fundamental; distinguir `FAIL`, `INSUFFICIENT` y `NOT_APPLICABLE`. No inventar historial si no existe.
3. Mostrar tabla: ticker, distancia a máximo 52w, retorno 63 sesiones, EMA11 subiendo, EMA21 subiendo, compresión TR5/TR20, estado y fecha del cierre.
4. Aplicar `estrategia_inversion.md` y posteriores gates completos únicamente cuando corresponda. No imponer este prefiltro sobre análisis individuales ni sobre posiciones OPEN.

No reclamar evidencia de rentabilidad, backtest, alpha o superioridad del filtro. Es un mecanismo de priorización de investigación.
