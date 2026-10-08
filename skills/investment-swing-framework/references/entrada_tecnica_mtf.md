# Entrada técnica MTF — soporte, re-aceleración y breakout

## 0. Autoridad y objetivo

Este módulo formaliza la autorización técnica de nuevas entradas largas después del gate fundamental. Está subordinado a `estrategia_inversion.md` y `reglas_riesgo_tecnico.md`, y prevalece sobre `regla_tunel.md` únicamente para decidir si existe un setup técnico candidato.

```text
estrategia_inversion.md
  > reglas_riesgo_tecnico.md
    > entrada_tecnica_mtf.md
      > regla_tunel.md
```

El objetivo es detectar antes una base, recuperación o re-aceleración swing sin esperar a que el Túnel complete toda su secuencia. No promete anticipar suelos ni convierte un rebote en tendencia confirmada.

`AllowedLongContext` y `LongSetupContext` del Túnel pasan a ser diagnóstico/confluencia. No son gates universales. El Túnel conserva valor para obstáculos, zonas, agotamiento y deterioro.

No usar Donchian en este módulo.

## 1. Perfil TradingView de referencia

La implementación de referencia está en [`tradingview_mtf_swing_pivot.pine`](tradingview_mtf_swing_pivot.pine). Es una referencia operativa, no una fuente fundamental ni una regla de rentabilidad.

Perfil por defecto del Pine:

```text
TF operativo 4H -> HTF 1D
TF operativo 1D -> HTF 1W
HTF confirmado: true
media operativa: EMA 5 / 13 / 34
media estructural HTF: SMA 30 / 50 / 200
pivotStrength: 3
ventana tras cruce 5/13: 3 barras
RVOL mínimo: 1.3x sobre media 20
ATR: 14
buffer protector diagnóstico: >=1.0 ATR
invalidación swing: por cierre
```

La elección `30/50/200` es un **perfil de implementación para swing**, no reemplaza las medias 20/50/200 que el marco general sigue reportando. Cuando se use otra familia de media configurada en TradingView, declarar el tipo exacto; no comparar EMA/WMA/SMA como si fueran la misma serie.

## 2. Separación de funciones

### 2.1 Estructura HTF — 30/50/200

Usar el HTF para clasificar régimen, no para disparar por sí solo una orden.

```text
htfBullishStack = MA30 > MA50 > MA200
htfBearishStack = MA30 < MA50 < MA200
htfBullishRegime = MA50 > MA200 AND close_HTF > MA200
htfLongCompatible = htfBullishRegime AND close_HTF > MA50
htfBearishStructural = htfBearishStack AND close_HTF < MA200
```

Estados de referencia:

```text
STRONG:      stack alcista y close > MA30
PULLBACK:    stack alcista y MA50 < close <= MA30
CORRECTION:  MA50 > MA200 y MA200 < close <= MA50
DETERIORATION: close < MA200 sin stack bajista completo
BEARISH_STRUCTURAL: MA30 < MA50 < MA200 y close < MA200
BULLISH/NEUTRAL: resto
```

Usar vela HTF cerrada por defecto. Un HTF live puede mostrarse como diagnóstico, pero no debe presentarse como confirmación no-repaint.

### 2.2 Setup operativo — 5/13/34

Usar 5/13/34 para momentum y reconstrucción del setup:

```text
operatingBullishStack = MA5 > MA13 > MA34
priceAboveOperating = close > MA5 AND close > MA13 AND close > MA34
recentBullCross = cruce MA5 sobre MA13 dentro de la ventana configurada
```

Un `TREND_CONTINUATION` no exige un cruce 5/13 reciente si el orden ya está establecido. Un `REACCELERATION` sí lo exige.

## 3. Pivots de swing y breakout

Usar pivots confirmados de precio como estructura. En la referencia TradingView:

```text
pivotHigh = ta.pivothigh(high, 3, 3)
pivotLow  = ta.pivotlow(low, 3, 3)
```

El pivot solo existe operacionalmente tras las barras derechas necesarias para confirmarlo. No retrotraer conocimiento al momento visual del swing.

Breakout largo:

```text
close > confirmedPivotHigh
AND close_prev <= confirmedPivotHigh
AND barra operativa cerrada
```

Cuando `requireVolumeConfirmation=true`, exigir:

```text
RVOL = volumen / SMA20(volumen) >= 1.3
```

La referencia de invalidación estructural del breakout es el último pivot low confirmado; el stop protector sigue estando subordinado a `reglas_riesgo_tecnico.md` y usa buffer ATR.

## 4. Pivot Bias diario — timing, no autorización

El Pivot Bias usa exclusivamente H/L/C del último día confirmado:

```text
DailyPivot = (prevDayHigh + prevDayLow + prevDayClose) / 3
close > DailyPivot -> ALCISTA
close < DailyPivot -> BAJISTA
```

Eventos:

```text
RECUPERA_PIVOT = crossover(close, DailyPivot) confirmado al cierre
PIERDE_PIVOT   = crossunder(close, DailyPivot) confirmado al cierre
```

Reglas:

- Usar `lookahead_off` y congelar los datos del día previo al comenzar una nueva sesión.
- Tratar el Pivot Bias como **timing intradía/4H**, no como soporte estructural.
- Un gap de apertura no crea artificialmente RECUPERA/PIERDE: exigir continuidad de sesión según el script.
- Bloquear eventos Pivot en un día de split cuando la fuente reporte el corporate action.
- No derivar stop, target o tamaño únicamente del Pivot.
- `ALCISTA` o `RECUPERA_PIVOT` aportan confluencia positiva; nunca autorizan una entrada por sí solos.

## 5. Soporte y agotamiento vendedor

El soporte swing procede de estructura de precio, no del floor-pivot diario.

```text
support_state in {NONE, TESTING, FORMING, CONFIRMED, BROKEN}
seller_exhaustion in {NONE, POSSIBLE, CONFIRMED}
```

Evidencia admisible para soporte/agota­miento:

- swing low o zona horizontal diaria/4H;
- failed breakdown con cierre recuperando la zona;
- higher low;
- recuperación de soporte previo;
- contracción de volumen vendedor;
- expansión de volumen en vela de recuperación;
- mejora de OBV;
- divergencia RSI/MACD como apoyo, nunca como señal aislada;
- recuperación de Pivot Bias como timing adicional.

No crear un score técnico agregado. Mantener cada evidencia separada.

## 6. Tipos de setup

### 6.1 `TREND_CONTINUATION`

```text
HTF confirmado
AND htfLongCompatible
AND MA5 > MA13 > MA34
AND precio sobre 5/13/34
AND breakout de pivot confirmado
AND volumen confirmado cuando sea exigido
AND soporte no roto
```

No exigir crossover 5/13 reciente.

### 6.2 `REACCELERATION`

```text
TREND_CONTINUATION conditions
AND crossover 5/13 reciente
```

Usar cuando un pullback/compression vuelve a ordenar momentum.

### 6.3 `BREAKOUT_ENTRY`

```text
HTF confirmado
AND htfLongCompatible
AND stack operativo alcista
AND breakout de pivot confirmado
AND volumen confirmado
AND soporte no roto
```

El breakout es estructural por pivot confirmado, no Donchian.

### 6.4 `RECOVERY_ENTRY`

Extensión del framework para buscar mejor asimetría antes de una alineación HTF completa. **El Pine de referencia no emite este trigger como `longTrigger`; se razona externamente con los observables del gráfico.**

Exigir simultáneamente:

```text
HTF confirmado
AND NOT htfBearishStructural
AND support_state = CONFIRMED
AND seller_exhaustion = CONFIRMED
AND Pivot Bias positivo o RECUPERA_PIVOT
AND reparación operativa: MA5 > MA13 y close > MA34
AND crossover 5/13 reciente
AND volumen confirmado
```

Este setup tiene más riesgo de fallo que continuación/re-aceleración. No describirlo como tendencia alcista confirmada si el HTF sigue `CORRECTION`, `DETERIORATION` o `NEUTRAL`.

## 7. Túnel como overlay

Calcular el Túnel cuando existan sus observables, pero no usar:

```text
AllowedLongContext = false
```

como veto universal.

Usos que se conservan:

- `UpperObstacle_HT`: añadirlo a la revisión de obstáculos; si impide el objetivo con `R/R neto >=2`, bloquear o esperar.
- `LowerObstacle_HT`: contexto de soporte/estructura.
- `ExhaustionUp`: bloquear entrada agresiva o elevar riesgo de entrada tardía.
- `ExhaustionDown`: evidencia secundaria de agotamiento, nunca compra automática.
- `LongStructureWarning`: alerta de deterioro.
- zonas/cintas: confluencia, no objetivos automáticos.

Si faltan datos del Túnel, marcarlo como overlay pendiente; no convertir su ausencia en autorización favorable ni en veto automático si la revisión estructural de obstáculos está completa por otras fuentes.

## 8. Gate técnico final

Después de score >=70 y antes del sizing:

```text
technical_entry.valid = true
AND stop estructural válido
AND R/R neto >= 2.0
AND régimen/contexto jerárquico compatible
AND effective_risk_scalar > 0.25 para acción individual
AND sin divergencia bloqueante
AND sin obstáculo material antes del objetivo económico
```

`technical_entry.valid` lo calcula `scripts/technical_entry_context.py` a partir de observables declarados; no aceptar un booleano libre sin datos subyacentes.

DCA agresivo conserva sus reglas canónicas actuales en esta iteración, incluido el requisito de Túnel cuando corresponda. No reutilizar automáticamente este cambio para relajar DCA.

## 9. Salida mínima

```text
SETUP_TECNICO:
SETUP_TYPE:
TF_SETUP:
TF_HTF:
HTF_DATA: CONFIRMED/LIVE
OPERATING_MA: tipo + 5/13/34
STRUCTURAL_HTF_MA: tipo + 30/50/200
HTF_STATE:
OPERATING_STACK:
SUPPORT_STATE:
SELLER_EXHAUSTION:
PIVOT_BIAS:
PIVOT_EVENT:
BREAKOUT_LEVEL:
BREAKOUT_CONFIRMED:
RVOL:
TUNNEL_OVERLAY:
TUNNEL_OBSTACLE:
TECHNICAL_ENTRY_VALID:
FAILED_TECHNICAL_CONDITIONS:
```

No mostrar `RECOVERY_ENTRY` como `ENTRADA VALIDA` hasta pasar también riesgo, contexto, obstáculos y R/R.
