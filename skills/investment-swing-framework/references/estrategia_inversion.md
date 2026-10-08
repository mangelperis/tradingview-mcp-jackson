# Referencia canónica: estrategia_inversion.md

> Fuente permanente proporcionada por el usuario; cuerpo conservado sin cambios.

## Índice de la fuente

- 0. Jerarquía normativa
- 1. Flujo obligatorio en dos fases
- 2. Score fundamental 0–100
- 3. Integración del módulo Buffett
- 4. Tendencia estructural y sobre-extensión
- 5. DCA modulado
- 6. Metodología técnico-táctica
- 7. Reglas maestras de riesgo
- 8. Régimen de mercado, sentimiento y contexto jerárquico
- 9. Datos frescos y evidencia
- 10. Escenarios obligatorios
- 11. Formato obligatorio de salida

---

# Inversiones — Marco canónico unificado

Este archivo es la **autoridad principal** del proyecto. Define el flujo de decisión, el score fundamental, los umbrales de clasificación y el contrato de salida de cada análisis.

## 0. Jerarquía normativa

En caso de contradicción, prevalece este orden:

```text
estrategia_inversion.md
  > reglas_riesgo_tecnico.md
    > regla_tunel.md
      > tendencia_mercado.md
        > sentimiento_posicionamiento.md
          > automatizacion_sentimiento_semanal.md
            > informes temporales de sentimiento, escenarios externos y notas de mercado
```

`buffet_value_invest.md` es un submódulo fundamental especializado. Su badge y sus filtros deben integrarse en el score general, pero no sustituyen la decisión final de este documento.

Reglas de interpretación:

- Una fuente temporal nunca modifica por sí sola una regla permanente.
- El informe semanal de sentimiento vigente es contexto temporal; si falta o caduca, se marca `DATO PENDIENTE` y no se aplica ajuste positivo.
- Un indicador técnico nunca compensa una ruptura fundamental grave.
- Un activo con score inferior a 70 no pasa a estrategia técnica de entrada.
- Todos los precios, entradas, stops y objetivos se expresan únicamente en la **moneda de cotización del activo**.
- Fechas y horas: **Europe/Madrid**.

---

## 1. Flujo obligatorio en dos fases

### Fase 1 — Filtro fundamental y contexto

Evaluar:

1. Calidad del negocio y ventaja competitiva.
2. Márgenes, rentabilidad sobre capital y estabilidad operativa.
3. Balance, deuda, liquidez y vencimientos.
4. Flujo de caja libre y conversión de beneficio en caja.
5. Crecimiento histórico y esperado.
6. Valoración frente a historia propia, sector y calidad del activo.
7. Riesgos estructurales, regulatorios, legales y de gobierno corporativo.
8. Tendencia estructural frente a DMA/SMA/WMA200.
9. Régimen de mercado como contexto, sin alterar el score fundamental.
10. Overlay vigente de sentimiento, posicionamiento y flujos, sin alterar el score fundamental.

Resultado obligatorio:

| Score | Decisión |
|---:|---|
| 0–59 | **NO TRADE** |
| 60–69 | **WATCHLIST** |
| 70–79 | **APTO** |
| 80–100 | **ALTA CONVICCIÓN** |

Overrides:

- `structuralBreak = true` ⇒ **NO TRADE**, independientemente del score aritmético.
- Datos críticos insuficientes ⇒ marcar `DATO PENDIENTE` y aplicar el cap correspondiente.
- Score 60–69 permite seguimiento, no una nueva entrada.
- Solo `APTO` o `ALTA CONVICCIÓN` permite pasar a Fase 2.

### Fase 2 — Estrategia técnica y ejecución

Solo se activa con score ≥70.

Debe revisar:

- Tendencia diaria y semanal.
- DMA/WMA20, 50 y 200.
- RSI, MACD, ATR, volumen y OBV.
- Soportes, resistencias, gaps y patrones clásicos.
- Elliott y Fibonacci como mapa de contexto, nunca como señal aislada.
- Entrada MTF mediante `entrada_tecnica_mtf.md`: estructura HTF, 5/13/34 operativo, soporte, Pivot Bias, pivots confirmados, volumen y tipos de setup.
- Tunnel Domènec como overlay de tendencia, zonas, obstáculos, agotamiento y deterioro; `AllowedLongContext` no es un veto universal de entrada.
- Régimen de mercado mediante `tendencia_mercado.md`.
- Sentimiento, posicionamiento y flujos mediante `sentimiento_posicionamiento.md` y el informe semanal vigente.
- Riesgo y ejecución mediante `reglas_riesgo_tecnico.md`.

Una entrada nueva requiere simultáneamente:

1. `technical_entry.valid = true` según `entrada_tecnica_mtf.md`.
2. Soporte/recuperación, re-aceleración, continuación o breakout estructural válidos para el tipo de setup.
3. Confirmación por cierre y volumen cuando el setup lo exija.
4. Stop estructural válido.
5. `R/R neto ≥2,0`.
6. Régimen de mercado compatible.
7. `effective_risk_scalar > 0,25` para una nueva entrada individual.
8. Sin divergencia jerárquica bloqueante ni obstáculo material antes del objetivo económico.

`AllowedLongContext` del Túnel es diagnóstico/confluencia: por sí solo no autoriza ni bloquea universalmente una entrada. Un obstáculo o agotamiento del Túnel sí puede degradar o bloquear por razones económicas/estructurales.

Los cortos están desactivados por defecto. Solo se analizan o plantean si el usuario los solicita explícitamente y el contexto es excepcionalmente claro.

---

## 2. Score fundamental 0–100

El score es fundamental. No sumar puntos técnicos al número.

### 2.1. Calidad del negocio — 0 a 20

- 17–20: moat claro, ingresos resistentes, poder de precios, reinversión rentable.
- 12–16: negocio bueno pero cíclico, concentrado o con moat moderado.
- 6–11: ventaja limitada, dependencia elevada de ciclo, cliente o producto.
- 0–5: tesis especulativa, deterioro competitivo o modelo no probado.

### 2.2. Rentabilidad y márgenes — 0 a 15

Evaluar ROIC/ROCE, margen bruto, operativo y neto frente a historia y sector.

- 13–15: retornos altos y márgenes estables o crecientes.
- 9–12: rentabilidad correcta con volatilidad controlada.
- 4–8: márgenes débiles, cíclicos o en compresión.
- 0–3: destrucción de valor o pérdidas persistentes sin camino creíble.

### 2.3. Balance y deuda — 0 a 15

- 13–15: caja neta o deuda fácilmente cubierta; vencimientos manejables.
- 9–12: apalancamiento razonable para el sector.
- 4–8: deuda elevada, cobertura de intereses justa o refinanciación relevante.
- 0–3: riesgo de liquidez, covenant, dilución o deuda no sostenible.

Referencia general para no financieras: deuda neta/EBITDA ≤2–2,5× es favorable, ajustando por sector y estabilidad de caja.

### 2.4. Flujo de caja libre — 0 a 15

- 13–15: FCF positivo, recurrente y con buena conversión.
- 9–12: FCF positivo pero irregular o condicionado por ciclo/capex.
- 4–8: conversión débil o FCF temporalmente negativo con explicación válida.
- 0–3: consumo estructural de caja, dependencia de financiación o dilución.

Calcular siempre que sea posible:

```text
FCF yield = FCF normalizado / capitalización bursátil
```

### 2.5. Crecimiento — 0 a 10

- 9–10: crecimiento rentable, diversificado y sostenible.
- 6–8: crecimiento moderado con visibilidad razonable.
- 3–5: crecimiento bajo, irregular o dependiente de recuperación.
- 0–2: contracción estructural o expectativas sin evidencia.

### 2.6. Valoración — 0 a 20

Comparar P/E, forward P/E, EV/EBITDA o EV/EBIT, FCF yield y valoración histórica/sectorial.

- 17–20: descuento claro con fundamentos intactos y margen de seguridad.
- 12–16: valoración razonable para calidad y crecimiento.
- 6–11: valoración exigente o descuento insuficiente.
- 0–5: valoración extrema, sin anclaje o dependiente de supuestos agresivos.

PEG, dentro de esta categoría:

```text
PEG = P/E / crecimiento anual esperado del EPS (%)
```

- PEG ≤1: favorable.
- PEG >1 y ≤1,5: neutral.
- PEG >1,5: exigente.
- Sin P/E positivo o crecimiento fiable: `PEG no interpretable`.

El PEG no se usa de forma aislada ni añade puntos fuera de los 20 de valoración.

### 2.7. Gobierno y riesgos estructurales — 0 a 5

- 5: gobierno sólido, incentivos alineados y riesgos controlados.
- 3–4: riesgos manejables o habituales del sector.
- 1–2: litigios, regulación, concentración o asignación de capital preocupante.
- 0: fraude, ruptura estructural, insolvencia potencial o gobierno inaceptable.

### 2.8. Caps por datos insuficientes

- Sin estados financieros recientes o sin deuda/FCF verificables: score máximo 59.
- Empresa pre-beneficios con valoración basada solo en narrativa: score máximo 59, salvo marco sectorial específico y evidencia excepcional.
- PEG no interpretable no limita por sí solo el score; obliga a usar FCF, EV/Ventas, EV/EBITDA, márgenes y camino a rentabilidad.

---

## 3. Integración del módulo Buffett

El badge Buffett funciona como control de calidad y valoración:

| Resultado Buffett | Integración en el score general |
|---|---|
| GOLD + compounder + sin ruptura estructural | Compatible con 80–100 |
| GREEN + compounder + sin ruptura estructural | Compatible con 70–89 |
| AMBER | Score máximo 69 |
| RED | Score máximo 59 |
| GRAY | Score máximo 59, salvo valoración alternativa robusta y explícita |
| `structuralBreak = true` | **NO TRADE obligatorio** |

Cotizar bajo WMA200 semanal es un **trigger de investigación**, no una autorización automática de compra. La entrada sigue requiriendo estabilización y Fase 2 válida.

---

## 4. Tendencia estructural y sobre-extensión

Evaluar siempre:

- Precio frente a DMA/SMA200 diaria.
- Dirección de la DMA/SMA200.
- Precio frente a WMA/SMA200 semanal.
- Estructura de máximos y mínimos.

Lectura:

- Precio sobre DMA200 ascendente: fortaleza estructural.
- Precio bajo DMA200 descendente: debilidad estructural; no perseguir rebotes sin base.
- Compounder bajo WMA200 semanal: posible oportunidad de investigación, no señal de entrada.

### Alerta de sobre-extensión

Si el precio está ≥20% por encima de la DMA/SMA200:

- Marcar **SOBRE-EXTENSIÓN**.
- No proponer compras agresivas.
- Priorizar espera, pullback, gestión de posición o parciales.
- Si además Elliott sugiere onda 5 y el Túnel marca agotamiento, elevar el riesgo de corrección.

---

## 5. DCA modulado

Aplicable a fondos, ETFs y acciones de calidad con tesis vigente.

### DCA normal

- Mantener aportación base si la tendencia estructural es compatible.
- Reducir o pausar si se rompe soporte mayor o aparece deterioro fundamental.
- No usar DCA para evitar reconocer una tesis rota.

### DCA agresivo — 1,5× a 2× ticket base

Solo si se cumplen **todas**:

1. Score ≥70.
2. Precio ≥WMA200 diaria o recuperación semanal confirmada sobre soporte mayor.
3. Precio en zona Fibonacci 0,50–0,618 del tramo relevante.
4. Precio ≤P20, donde `P20 = máximo YTD ×0,80`.
5. Señal de giro confirmada con volumen.
6. Contexto del Túnel compatible con largos.
7. Régimen de mercado no bloqueado por `RISK_OFF` o `CAPITULATION_UNCONFIRMED`.
8. Ninguna capa material de `sentiment_regime[layer]` está en `CROWDED_LONG`, `DISTRIBUTION`, `RISK_OFF_DELEVERAGING`, `PANIC_LIQUIDATION` o `INSUFFICIENT_DATA`, y no existe `ROTATION_OUT` sin reversión confirmada.
9. `effective_risk_scalar > 0,25`.
10. Exposición total tras la compra ≤10% del capital.

Si falta una condición, no etiquetar la aportación como DCA agresivo.

---

## 6. Metodología técnico-táctica

### 6.1. Marcos temporales

- Semanal: tendencia estructural y soportes mayores.
- Diario: contexto principal y validación swing.
- 4H: construcción del setup y afinado.
- 5–60m: solo optimización del precio; nunca invalida por sí solo la tesis swing.

### 6.2. Indicadores mínimos

- DMA/WMA20, 50 y 200.
- RSI(14).
- MACD.
- ATR(14).
- Volumen relativo y OBV.
- Soportes, resistencias y gaps.

### 6.3. Patrones

Considerar banderas, banderines, triángulos, canales, HCH/HCH invertido, dobles o triples techos/suelos, taza con asa, cuñas, redondeos y bump-and-run.

Gating obligatorio:

- Patrón coherente con la tendencia.
- Confirmación por cierre.
- Volumen de ruptura preferiblemente ≥1,3× la media de 20 sesiones.
- Stop estructural válido.
- `R/R neto ≥2,0`.

### 6.4. Entrada MTF, Elliott, Fibonacci y Túnel

- `entrada_tecnica_mtf.md`: motor de autorización técnica de nuevas entradas largas tras score >=70. Perfil de referencia TradingView: EMA 5/13/34 en setup y SMA 30/50/200 en HTF; 30/50/200 no reemplaza el diagnóstico canónico 20/50/200.
- Elliott 1–5 + ABC: mapa probabilístico, nunca señal aislada.
- Fibonacci 0,382–0,618: zona de corrección, no compra automática.
- Extensiones 1,272–1,618: objetivos contextuales, subordinados a R y resistencias.
- Túnel: overlay de tendencia, corrección, obstáculos y agotamiento; no decide por sí solo autorización de entrada, stop final ni salida.

---

## 7. Reglas maestras de riesgo

El detalle operativo reside en `reglas_riesgo_tecnico.md`. Estas reglas no pueden ser rebajadas por otros módulos:

- Máximo 10% del capital por posición.
- Riesgo estándar 1% del portfolio por operación.
- Hasta 2% solo en setup de alta convicción, líquido y plenamente validado.
- Stop de tesis swing por cierre diario bajo nivel clave.
- Stop protector fuera de estructura con buffer mínimo aproximado de 1×ATR.
- Entradas planificadas con orden Limit; Stop solo para ruptura confirmada o protección.
- `R/R neto mínimo = 2,0`.
- T1=1R: tomar 25–40%.
- T2=2R: tomar 25–50% adicional.
- Break-even solo tras T1 y si no queda dentro de 0,5×ATR de ruido.
- Resto con trailing por mínimo semanal −0,5×ATR o DMA/WMA20.
- No permitir que un ganador consolidado vuelva a pérdida neta.

---

## 8. Régimen de mercado, sentimiento y contexto jerárquico

`tendencia_mercado.md` calcula `market_regime` y `market_risk_scalar` con precio, breadth, volatilidad, crédito, distribución y reacción a noticias. No autoriza una operación por sí solo.

`sentimiento_posicionamiento.md` calcula por separado:

- `risk_appetite_score`: disposición observable a asumir riesgo.
- `contrarian_opportunity_score`: oportunidad potencial tras saturación y agotamiento.
- `reversal_confirmation`: `NONE`, `EARLY`, `CONFIRMED` o `INSUFFICIENT`.
- `sentiment_cap`: techo contextual de riesgo.

Acoplamiento obligatorio:

```text
market_risk_scalar = salida amplia de tendencia_mercado.md
sentiment_cap = salida amplia del informe semanal vigente

broad_context_cap = min(
    market_risk_scalar,
    sentiment_cap
)

relative_context_cap = min(
    valid_style_sector_industry_layer_caps,
    divergence_cap
)

effective_risk_scalar = min(
    broad_context_cap,
    relative_context_cap
)
```

Reglas:

- El módulo y la capa contextual más restrictivos prevalecen.
- El sentimiento no modifica el score fundamental.
- El sentimiento no altera directamente `market_regime`; evita dependencias circulares.
- Un `risk_appetite_score` alto no equivale a compra.
- Un miedo extremo no equivale a compra; `PANIC_LIQUIDATION` mantiene nuevas entradas bloqueadas.
- `contrarian_opportunity_score` solo prioriza investigación en acciones individuales.
- Con `effective_risk_scalar <= 0,25` se pausan nuevas entradas individuales. Una divergencia `ROTATION_OUT` puede producir este bloqueo aunque el índice amplio siga cerca de máximos.
- En índices amplios y ETFs diversificados, `allocation_signal` es solo investigación mientras `execution_enabled = false`.
- Si el informe semanal falta, está caducado o tiene cobertura insuficiente, registrar `SENTIMIENTO_SEMANAL: DATO PENDIENTE`; no fabricar una señal favorable.

El régimen y el overlay modifican tamaño máximo y agresividad, nunca el score fundamental ni una ruptura de tesis.

---

### 8.1. Contexto jerárquico obligatorio

Antes de valorar una entrada en una acción o ETF temático, resolver una cadena de contexto con referencias oficiales o proxies líquidos y documentados:

```text
context_stack = {
  global_anchor,
  regional_broad_index,
  style_or_factor_index,
  sector_index,
  industry_index,
  instrument
}
```

No todas las capas son obligatorias. Se incluye una capa solo cuando sea material para el activo y exista una referencia razonable. Si falta una capa, marcar `DATO PENDIENTE`; usar cap neutral `1,00` y prohibir cualquier inferencia positiva basada en su ausencia.

Ejemplo orientativo para AMD:

```text
global_anchor = renta variable global / condiciones financieras globales
regional_broad_index = S&P 500
style_or_factor_index = Nasdaq 100 o índice growth relevante
sector_index = tecnología de EE. UU.
industry_index = semiconductores / PHLX Semiconductor Index o referencia equivalente
instrument = AMD
```

Cada capa válida produce:

```text
market_regime[layer]
market_risk_scalar[layer]
risk_appetite_score[layer]
contrarian_opportunity_score[layer]
reversal_confirmation[layer]
sentiment_regime[layer]
sentiment_cap[layer]
layer_effective_cap[layer] = min(
    market_risk_scalar[layer],
    sentiment_cap[layer]
)
```

El contexto relativo se calcula con las capas de estilo, sector e industria aplicables:

```text
relative_context_cap = min(
    valid_layer_effective_caps,
    divergence_cap
)
```

Estados mínimos de divergencia:

```text
ALIGNED_POSITIVE
ALIGNED_NEGATIVE
INDEX_STRONG_SECTOR_WEAK
INDEX_WEAK_SECTOR_STRONG
SECTOR_STRONG_INDUSTRY_WEAK
SECTOR_WEAK_INDUSTRY_STRONG
ROTATION_OUT
ROTATION_IN
MIXED
INSUFFICIENT
```

Reglas:

- Índice amplio fuerte con sector o industria deteriorándose no es confirmación alcista para la acción; clasificar `INDEX_STRONG_SECTOR_WEAK` o `ROTATION_OUT`.
- Sector fuerte con índice amplio débil puede indicar liderazgo relativo, pero no elimina el riesgo de mercado general.
- Industria débil dentro de un sector fuerte prevalece para empresas altamente expuestas a esa industria.
- La fortaleza aislada del activo no eleva el cap de su sector o industria. Solo permite estudiar una excepción idiosincrática con fundamentos y setup propios.
- El miedo extremo de un sector o industria solo activa investigación contrarian. No autoriza entrada sin `reversal_confirmation = CONFIRMED` y el resto de gates canónicos.
- La capa más débil limita el tamaño de una nueva entrada; no obliga a vender automáticamente una posición existente con tesis intacta.

Referencia para `divergence_cap`:

| Estado | Cap máximo |
|---|---:|
| Alineación positiva | 1,00 |
| Mixto sin deterioro material | 0,75 |
| Índice fuerte, sector/industria débil | 0,50 |
| Índice débil, sector líder | 0,75; el cap amplio sigue prevaleciendo |
| Rotación clara fuera del sector | 0,25 |
| Sector/industria en liquidación no confirmada | 0,00–0,25 |
| Datos insuficientes | 1,00 neutral; sin validación positiva |


## 9. Datos frescos y evidencia

Antes de emitir una recomendación:

- Usar el precio actual disponible.
- Revisar resultados, guidance, deuda, FCF y noticias materiales recientes.
- Comparar valoración con datos actuales, no con cifras obsoletas si existen otras más recientes.
- Citar las fuentes principales.
- Marcar claramente estimaciones, datos pendientes y rangos de incertidumbre.
- Las probabilidades de informes de mercado fechados deben verificarse antes de reutilizarse.
- Leer `sentimiento_semanal_actual.md` cuando exista; comprobar `VALID_UNTIL`, `DATA_COVERAGE`, cobertura por capas y shocks posteriores antes de aplicar cualquier cap. Resolver el `context_stack` del activo y usar la capa más débil material.

---

## 10. Escenarios obligatorios

Para score ≥70, presentar al menos:

### Base

- Disparador.
- Zona de entrada.
- Stop de tesis y stop protector.
- T1, T2 y trailing.

### Aceleración

- Resistencia cuya ruptura confirma continuación.
- Volumen requerido.
- Condición para añadir o mantener.

### Fallo / invalidación

- Nivel o evento que rompe la tesis.
- Acción: cancelar entrada, reducir o cerrar.
- Condición necesaria antes de reconsiderar.

---

## 11. Formato obligatorio de salida

1. **Fecha y hora:** Europe/Madrid.
2. **Precio actual:** moneda de cotización.
3. **Score fundamental:** total y desglose 0–100.
4. **Métricas:** P/E, forward P/E, PEG, FCF yield, deuda y márgenes.
5. **Valoración:** historia propia y sector.
6. **Tendencia estructural:** DMA/WMA20/50/200 y sobre-extensión.
7. **Decisión:** NO TRADE / WATCHLIST / APTO / ALTA CONVICCIÓN.
8. **Fase técnica:** solo si score ≥70.
9. **Setup MTF y Túnel:** tipo de setup, estado HTF, 5/13/34, soporte, Pivot Bias, breakout/volumen y overlay de Túnel.
10. **Mercado, sector y sentimiento:** `context_stack`, régimen y scores por capa, `context_divergence_state`, `weakest_context_layer`, fecha del informe y `effective_risk_scalar`.
11. **Plan:** entrada, stop, T1, T2, trailing, tamaño y escenarios.
12. **Riesgos y próximos catalizadores.**

No duplicar niveles en otra moneda. No introducir restricciones o costes de una plataforma concreta salvo petición expresa del usuario.


## 6.5. Extension de opciones XTB V1 - single-leg long

Cuando el usuario solicite opciones, conservar intacto el score fundamental y la tesis del subyacente. La opcion es un vehiculo de ejecucion posterior, nunca una fuente de puntos ni una forma de saltarse Fase 1/Fase 2.

Alcance V1 autorizado:

- `LONG_CALL` solo con ticket actual `BUY_CALL` confirmado.
- `LONG_PUT` solo con ticket actual `BUY_PUT` confirmado y solicitud bajista explicita; la politica general de cortos/bajistas sigue desactivada por defecto.
- Uso protector de una long put puede analizarse para una posicion existente, pero no tiene sizing automatico de hedge en V1.

Bloquear sell-to-open, estrategias multi-leg, covered calls, cash-secured puts, spreads, collars, straddles/strangles, iron condors/butterflies, calendars/diagonals y naked short hasta nueva autorizacion.

Para una opcion direccional swing exigir ademas:

1. tesis del subyacente valida;
2. DTE >=14 dias;
3. DTE >= planned_holding_days + 5;
4. preview actual del broker con precio, strike, expiracion, break-even, volumen/prima y perdida maxima;
5. max_loss_total dentro del presupuesto de riesgo despues de aplicar una sola vez `effective_risk_scalar`;
6. objetivo del subyacente mas alla del break-even;
7. `RR_floor >=2.0` calculable con payoff intrinseco al objetivo y multiplicador efectivo verificado/inferido del preview actual;
8. cierre antes de expiracion por defecto.

No asumir multiplicador contractual 100. Inferirlo solo para el preview actual mediante prima/(precio_opcion*volumen) cuando los tres datos existen y son coherentes con la perdida maxima mostrada.

No usar DCA para opciones long. Ver `options_xtb_long.md`.
