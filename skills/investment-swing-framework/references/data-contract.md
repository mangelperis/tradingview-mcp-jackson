# Contrato de datos v1.1

## Índice

1. Semántica y formatos
2. Instrumento y calidad
3. Fundamentales y Buffett
4. Valoración y tendencia
5. Contexto y sentimiento
6. Túnel y técnica
7. Riesgo
8. DCA y posición
9. Seguimiento y fuentes
10. Pipeline y validación
11. Contrato de opciones XTB V1
12. Prefiltro momentum independiente

## 1. Semántica y formatos

Python 3.10+, biblioteca estándar. Todas las interfaces de cálculo reciben/devuelven un objeto JSON. No mezclar una entrada cruda con un resultado derivado. Números JSON finitos; no NaN/Infinity, strings numéricos, booleanos como números o claves duplicadas. Porcentajes de riesgo/cobertura/peso son fracciones: 1%=0.01, 70%=0.70. El crecimiento EPS del PEG es porcentaje: 15 significa 15%.

Las fechas son ISO 8601 con offset. `analysis_at` se presenta en Europe/Madrid usando el offset de esa fecha; fuentes y cotizaciones conservan su zona o UTC. Comparar instantes, no strings locales. Rechazar fuentes o precios posteriores a `analysis_at`. No sustituir una fecha ausente por la hora de descarga.

Separar etiquetas: DATO REPORTADO, CONSENSO, CALCULO, INFERENCIA, DATO PENDIENTE. Valores pendientes son `null` con motivo, nunca cero fingido. Una ausencia puede bloquear solo el módulo afectado; no afirmar una entrada válida cuando afecta un gate.

El input superior contiene `schema_version`, `synthetic`, `analysis_at`, `instrument`, `data_quality`, `fundamentals`, `valuation`, `buffett`, `structural_trend`, `context_stack`, `market_regime`, `sentiment`, `technical`, `tunnel`, `risk`, `position`, `review`, `dca`, `sources`. Las opciones XTB V1 usan un input separado para `options_long.py` y no contaminan el envelope principal de acciones.

## 2. Instrumento y calidad

`instrument`: ticker oficial sin duplicar sufijo de país, exchange, country (país de cotización), currency USD/EUR, kind STOCK/ETF_THEMATIC/ETF_BROAD, price, quote_at, identity_verified. Añadir ISIN/MIC, share_class, ADR_ratio y primary_listing cuando sean relevantes. No confundir emisor suizo con ADR que cotiza en US.

`data_quality`: `price_current`, `fundamentals_current`, `news_checked` son booleanos demostrados por fuentes, no defaults optimistas. Adjuntar `pending` y `freshness_audit` cuando haya retrasos. Un precio de cierre puede ser actual para el último cierre, pero no denominarlo precio en directo.

Recabar market cap, resultados/guidance, revenue, margen, beneficio/EPS, deuda/caja/vencimientos, FCF, acciones diluidas/dilución, buybacks/dividendos, litigios/regulación y consenso. Cada métrica se describe con valor, unidad, periodo, tipo epistemológico y source_ids. No mezclar TTM, FY y NTM sin etiqueta.

## 3. Fundamentales y Buffett

Entrada de `fundamental_score.py` = objeto `fundamentals`:

```json
{
  "categories": {
    "business_quality": 18, "profitability": 13, "balance_sheet": 13,
    "free_cash_flow": 13, "growth": 8, "valuation": 16, "governance": 4
  },
  "data_quality": {"recent_statements": true, "debt_verified": true, "fcf_verified": true},
  "buffett": {"badge": "GOLD", "structuralBreak": false, "shortThesisRisk": "LOW"}
}
```

El fragmento anterior es sintético y solo ilustra tipos; no contiene un análisis operativo completo. Justificar categorías en `category_evidence`: score, rationale, source_ids y riesgos; el código no convierte automáticamente ratios en puntos no definidos por la fuente.

Máximos exactos: 20,15,15,15,10,20,5. Rechazar categorías extra y puntos técnicos. Datos críticos recientes/deuda/FCF no verificados -> cap59. `pre_profit && narrative_only` -> cap59 salvo `sector_exception` documentada. Buffett AMBER69, RED59, GRAY59 salvo valoración alternativa robusta documentada.

`buffett` superior debe coincidir con `fundamentals.buffett`. Campos: badge, qualityPass, compounderPass, structuralBreak, crowdingRisk, shortThesisRisk, FV, BuyUnder, weekly200Context, actionability, alternative_valuation. HIGH de tesis corta o ruptura estructural fuerzan veto. GOLD/GREEN requieren qualityPass=true en el validator.

Una alternativa o excepción documentada contiene `robust: true`, `method`, `rationale`, `source_ids` no vacíos; no basta un booleano. Leer Buffett para cálculo/interpretación de FV y BuyUnder. Cotizar bajo WMA200 semanal es solo research trigger.

Resultado: raw_score, score tras caps, decision, categories, caps, hard_overrides, pending y phase2_allowed. Un score85 con veto puede tener decision NO_TRADE; esto es distinto de un score67 mal etiquetado APTO.

## 4. Valoración y tendencia

`valuation_metrics.py`: recibir pe, price, eps_growth_pct, growth_reliable, fcf, market_cap, enterprise_value y ytd_high. Solo calcular ratios con denominadores interpretables. PEG = PE / crecimiento porcentual fiable positivo; si no, PEG no interpretable y EV/FCF cuando sea significativo. No extrapolar beneficios negativos para obtener PEG atractivo.

`structural_trend`: como mínimo daily_sma20, daily_sma50, sma200_daily, daily_wma200 cuando DCA la necesite, weekly20, weekly50, weekly200, high_low_structure. Incluir tipo exacto de media, precio ajustado/no ajustado, ventana y fechas. `overextended` usa precio >=1.20*sma200_daily; no resta puntos.

Cálculos sin series: no inventar DMA/WMA/EMA, pivots confirmados, ATR, OBV o volumen relativo. Declarar pendiente. Una captura permite una lectura aproximada etiquetada, no cifras exactas ocultas.

## 5. Contexto y sentimiento

Entrada `context_caps.py` = `context_stack`:

- `as_of` debe ser idéntico a analysis_at.
- `layers` es mapa GLOBAL, REGION, STYLE, SECTOR, INDUSTRY, INSTRUMENT.
- Cada capa aplicable: `applicable:true`, proxy/identidad, market_regime, market_risk_scalar, source_ids, sentiment_regime, sentiment_cap, sentiment_source_ids; opcionales risk_appetite_score, contrarian_opportunity_score, reversal_confirmation.
- Capa no aplicable requiere `applicable:false, reason`. No usar esta exención para ocultar sector o industria desconocidos. INSTRUMENT puede omitirse como cap porque el score y la técnica ya tienen sus gates.
- `divergence`: state, cap, source_ids, reversal_confirmation cuando corresponda.
- `weekly_report`: status COMPLETE/VALID/PARTIAL, published_at, valid_until, data_coverage (0-1), missing_critical_layers, material_shock (false verificado).

Informe ausente, caducado, futuro, shock no comprobado/true, cobertura <.70 o capas críticas ausentes invalida todos sus caps de sentimiento. Mercado se evalúa independientemente. No convertir informe inválido en compra ni usarlo para borrar un riesgo de mercado vigente.

Caps de mercado máximos documentados: RISK_ON1, CONSTRUCTIVE1, CAUTION.75, RISK_OFF.50, CAPITULATION_UNCONFIRMED0. Un valor de entrada menor se conserva.

Caps de divergencia: ALIGNED_POSITIVE1, INDEX_STRONG_SECTOR_WEAK.50, INDEX_WEAK_SECTOR_STRONG.75, SECTOR_STRONG_INDUSTRY_WEAK.50, SECTOR_WEAK_INDUSTRY_STRONG.50 (hasta .75 solo con reversión confirmada), ROTATION_OUT.25, ROTATION_IN1, MIXED.75. ALIGNED_NEGATIVE e INSUFFICIENT no tienen un bonus ni cap inventado: se usa1 neutral antes de combinar evidencia válida.

```text
layer_effective_cap = min(market_risk_scalar, sentiment_cap)
broad_context_cap = min(GLOBAL, REGION)
relative_context_cap = min(STYLE, SECTOR, INDUSTRY, divergence_cap)
effective_risk_scalar = min(broad_context_cap, relative_context_cap)
```

Ausencia neutral1 nunca cuenta como confirmación positiva. Mostrar `weakest_context_layer` entre capas evidenciadas y `risk_limiter` por separado si limita DIVERGENCE. `positive_risk_adjustment` siempre FORBIDDEN: los caps nunca amplifican riesgo base.

`market_regime` y `sentiment` superiores son resúmenes narrativos; las decisiones numéricas proceden exclusivamente de computed.context. No volver a multiplicar esos resúmenes por el scalar.

## 6. Túnel y técnica

Entrada de `tunnel_context.py`: `ht`, `setup`, `previous`, EPS, SLOPE_MIN, VOL_MIN_FACTOR (1.3 por defecto canónico), shorts_requested false.

Cada vela/estado requiere close, Z_low, Z_high, Z_color, G, G_color, slope_G, B_blue_low/high, B_pink_low/high y closed. Setup/previous contienen MACD_hist; setup contiene vol_rel. Aportar las bandas inferiores específicas exigidas por ExhaustionDown cuando estén disponibles; de lo contrario el resultado es null/DATO PENDIENTE.

Son observables del indicador, no OHLC de los que el script reconstruya bandas. Devolver trend_state_HT/SETUP, AllowedLongContext, AllowedShortContext, CondPullbackPrev, CondBreakUpNow, ImpulseStrength, UpperObstacle_HT, LowerObstacle_HT, ExhaustionUp/Down y tunnel_risk_flags. Leer la fuente para semántica exacta.

`technical`: entry_plan, side LONG, `mtf`, regime_compatible, blocking_divergence, obstacles (lista revisada; [] significa revisada sin obstáculos), aggressive_entry, liquid, setup_grade, stop_thesis, stop_thesis_basis DAILY_CLOSE, event_risk_reviewed, correlation_reviewed, source_ids. `mtf` es obligatorio para una nueva entrada y se valida con `technical_entry_context.py`; no aceptar `AllowedLongContext` del Túnel como autorización universal.

Score<70 o veto: technical.entry_plan=false y risk=null. Pueden existir observaciones estructurales o stops de protección dentro de position, pero no un nuevo plan de compra.

## 7. Riesgo

Entrada `risk_position_size.py` = `risk`, en una sola moneda USD/EUR:

```text
capital_total, capital_currency, currency
risk_fraction, effective_risk_scalar
entry, support, atr14, stop_protector, target
roundtrip_cost_per_share
existing_shares, current_price
exceptional_setup, liquid, fully_confirmed, fundamental_score
liquidity_max_shares (opcional)
```

capital_total es patrimonio total convertido a moneda de la operación con FX fechado. `current_price` coincide con instrument.price; existing_shares incluye todos los títulos ya abiertos. Sin capital/FX no fabricar tamaño. El stop largo debe estar bajo entrada y <=support-ATR14, ATR14>0.

Riesgo estándar .01. Un valor >.01 y <=.02 exige score>=80, excepcional, líquido y plenamente confirmado. Los caps solo reducen ese presupuesto.

```text
base_risk_money = capital_total * risk_fraction
risk_money = base_risk_money * effective_risk_scalar   # una sola vez
R = entry - stop_protector
existing_risk = existing_shares * max(current_price - stop_protector, 0)
available_risk = max(risk_money - existing_risk, 0)
risk_shares = floor(available_risk / R)
concentration_shares = floor(max(0, .10*capital_total-existing_shares*current_price)/entry)
shares = min(risk_shares, concentration_shares, optional_liquidity_cap)
```

T1=entry+R; T2=entry+2R. RRnet=(target-entry-roundtrip_cost_per_share)/R. MinNetTarget=entry+2R+costes. Usar costes roundtrip estimados (comisiones, spread, slippage prudente) sin fingir garantía. `estimated_new_loss_with_costs` se informa además del R canónico.

No realimentar `risk_money`, `risk_budget`, `scaled_risk`, `shares` o scalar_application_count como input: se rechaza para evitar doble cálculo. El resultado incluye scalar_application_count=1 y el validator reconstruye el presupuesto desde capital/fraction/scalar; no confía solo en el contador.

Los stops no garantizan precio de ejecución frente a gaps. Revisar riesgo de evento/correlación por separado. Un holding antiguo que haya superado10% por apreciación no se vende automáticamente; el motor devuelve cero capacidad de ampliación.

## 8. DCA y posición

`decision_rules.py` recibe directamente el objeto DCA, sin envoltorio (ver interfaz CLI real con --help y ejemplo sintético). Campos DCA: score, thesis_intact, price, ytd_high, above_daily_wma200, weekly_recovery_confirmed, fibo_retracement, reversal_confirmed, volume_confirmed, tunnel_compatible, market_regimes, sentiment_regimes, sentiment_complete, effective_risk_scalar, divergence_state, blocking_divergence, final_weight, contrarian, plan_predefined, structural_compatible, aggressive_multiplier, overextended (false verificado para DCA agresivo).

P20=ytd_high*.80; aggressive_multiplier en [1.5,2]. DCA agresivo requiere todos los gates documentados; condiciones desconocidas no equivalen a true. La selección del ticket base es externa; no multiplicar shares final. En el pipeline, score/precio/scalar/contexto/Túnel/peso se derivan de los módulos comunes para evitar contradicciones.

`position`: status NONE/OPEN, shares entero, avg_price, currency, current_price derivado del instrumento, capital_total, stop_protector, stop_thesis, daily_close, daily_close_confirmed, atr14, roundtrip_cost_per_share, t1_taken; opcionales weekly_low, ma20, higher_low, channel_base, next_level, next_event, thesis. Ver `state-contract.md` y `position_management.py` para nombres exactos. P/L y riesgo con datos faltantes son pendientes.

BE solo tras T1 y con precio a >=.5ATR del stop de equilibrio. Trailing son candidatos estructurales, no modificaciones automáticas de órdenes. No interpretar mecha como cierre diario invalidante.

## 9. Seguimiento y fuentes

`review`: mode INITIAL/FOLLOWUP, prior (score, decision y desglose/hora externos), material_changes (lista de objetos con categoría, reason y source_ids). El script detecta cambio de score/decisión sin justificación material. La persona/agente identifica el cambio económico; no lo inventa Python.

`sources`: lista con id único, reference (URL/filing/file reference real), retrieved_at, as_of, kind. Distinguir hora de observación, publicación y recuperación. Cualquier campo terminado en source_ids debe apuntar a IDs existentes. Añadir period/location para trazabilidad. No inventar URLs ni citas a archivos ausentes.

Prioridad: IR, filings, bolsas, organismos oficiales, bancos centrales, CFTC/Cboe/FINRA/ICI/FRED, apoyo financiero secundario. La prioridad depende de la métrica; no una lista que fuerce una fuente irrelevante.

## 10. Pipeline y validación
11. Contrato de opciones XTB V1
12. Prefiltro momentum independiente

`run_analysis.py input.json --output analysis.json` genera un envelope: schema_version, input intacto, computed (fundamental/context/technical_entry/tunnel/risk/dca/position/review/eligibility/approved_shares) y presentation. `validate_analysis.py analysis.json` recalcula y compara ambos. Los costes deben indicarse explícitamente en el pipeline; cero solo si es una estimación justificada. La calculadora aislada permite cero como convención matemática, pero no autoriza una entrada por sí sola.

Datos crudos coherentes pero entrada bloqueada: valid=true, execution_valid=false. Resultado manipulado o invariante rota: valid=false, exit1. JSON mal formado/entrada no procesable: exit2 en calculadoras/pipeline.

`--operational` rechaza fixtures synthetic=true; no verifica en Internet la autenticidad de fuentes, exactitud de juicios, frescura real ni adecuación financiera. `approved_shares=0` cuando algún gate falla, aunque el tamaño teórico sea positivo.

La única fixture completa está en `scripts/tests/fixtures/analysis.synthetic.json`, identificada SYNTHETIC, fuente urn:synthetic:fixture y fechas de prueba. No copiarla como un análisis real ni eliminar su etiqueta para aprobar validación.


### Entrada técnica MTF

`technical.mtf` representa observables, no una señal libre:

```text
setup_type: RECOVERY_ENTRY | REACCELERATION | TREND_CONTINUATION | BREAKOUT_ENTRY
bar_closed: bool
htf_confirmed: bool
ma_types:
  operating: EMA por defecto; admitir tipo declarado compatible
  structural_htf: SMA por defecto; admitir tipo declarado compatible
operating:
  close
  fast5
  mid13
  slow34
htf:
  close
  fast30
  mid50
  slow200
recent_bull_cross: bool
breakout_confirmed: bool
volume_confirmed: bool
support_state: NONE | TESTING | FORMING | CONFIRMED | BROKEN
seller_exhaustion: NONE | POSSIBLE | CONFIRMED
pivot_bias:
  bias: ALCISTA | BAJISTA | NEUTRAL | N/D
  event: RECUPERA_PIVOT | PIERDE_PIVOT | - | N/D
  source: PREVIOUS_CONFIRMED_DAILY_HLC
```

Perfil TradingView de referencia: EMA 5/13/34, SMA 30/50/200, HTF confirmado, pivots de swing confirmados strength=3, cruce 5/13 con ventana 3, RVOL 1.3x. `30/50/200` es implementación swing adicional; conservar el diagnóstico general 20/50/200. No introducir Donchian.

El Pivot Bias usa el H/L/C diario previo confirmado y es `TIMING_ONLY`. No convierte por sí mismo `technical_entry.valid` en true.


## 11. Contrato de opciones XTB V1

`options_long.py` consume un objeto independiente. No usar este payload para modificar el score fundamental.

Campos requeridos:

```text
option_type: CALL | PUT
order_mode: PREMIUM | VOLUME
broker_action: BUY_CALL | BUY_PUT
underlying_price
strike
target_price
option_price
volume
premium_total
broker_max_loss
broker_break_even
capital_total
base_risk_pct
effective_risk_scalar
direct_costs_total
dte
planned_holding_days
quote_current: bool
underlying_thesis_valid: bool
bearish_requested: bool
```

Campo opcional: `broker_volume_limit`, solo si el ticket actual lo publica. No hardcodear un limite observado en otro contrato.

Semantica:

- `premium_total` y `broker_max_loss` son importes monetarios totales del preview, no precio por unidad.
- `option_price` es el precio unitario mostrado en la cadena/ticket.
- `volume` es el volumen mostrado por XTB para ese preview.
- El script infiere un multiplicador efectivo solo para ese preview; no lo persiste como constante de broker.
- `quote_current=true` debe estar sustentado por la captura/ticket actual; no es default.
- Para PUT direccional, `bearish_requested=true` es obligatorio.
- IV, Greeks, OI, bid/ask y exercise style no se inventan. Si se aportan desde otra fuente, son diagnostico externo al calculador V1.


## 12. Prefiltro momentum independiente — DISCOVERY_ONLY

`momentum_prefilter.py` tiene un contrato **separado** del JSON de `run_analysis.py`. No insertar su salida en `analysis_engine`, `fundamental_score`, MTF, contexto, stop/riesgo, gestión, DCA ni `output-contract.md`. Solo se ejecuta para escaneo momentum/watchlist o cuando el usuario solicita expresamente su diagnóstico.

Input: `analysis_at` ISO-offset; `instrument` (`ticker`, `exchange`, `kind=STOCK`, `currency=USD/EUR`, `identity_verified`); `market_data` (`price_basis=SPLIT_ADJUSTED`, `expected_last_completed_session` ISO date, `bars` >=252 OHLC diarios completos ordenados); `source` (`reference`, `kind=DAILY_OHLC`, `as_of` ISO date, `retrieved_at` ISO-offset). Los checks y métricas no son input libre: se calculan internamente. La fuente y calendario son verificaciones externas al cálculo sin red.

Output: `module`, `role=DISCOVERY_ONLY`, `ticker`, `as_of_session`, `status=PASS|FAIL|INSUFFICIENT|NOT_APPLICABLE`, `checks`, `metrics`, `failed_conditions`, `pending`, `source_reference`. `PASS/FAIL` solo con cinco comprobaciones calculables. `INSUFFICIENT/NOT_APPLICABLE` con métricas/checks nulos. Error de formato/valores imposibles => exit 2; falta de evidencia => exit 0 con `INSUFFICIENT`. Consultar [reglas exactas de ventanas y origen](momentum_prefilter.md).
