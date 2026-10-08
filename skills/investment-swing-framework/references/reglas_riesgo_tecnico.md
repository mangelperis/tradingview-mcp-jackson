# Referencia canónica: reglas_riesgo_tecnico.md

> Fuente permanente proporcionada por el usuario; cuerpo conservado sin cambios.

## Índice de la fuente

- 1. Principios no negociables
- 2. Dimensionamiento de posición
- 3. Diseño del stop
- 4. Relación riesgo/beneficio
- 5. Option walls
- 6. Órdenes y ejecución
- 7. Gestión de beneficios
- 8. Régimen de mercado y cap de sentimiento
- 9. Promediado y DCA
- 10. Presupuesto de stops y reintentos
- 11. Correlación y concentración
- 12. Plan de trade obligatorio
- 13. Marco Taleb del stop

---

# Reglas de Riesgo Técnicas

Este archivo es el módulo especializado de riesgo y ejecución. Está subordinado a `estrategia_inversion.md` y no puede modificar el score fundamental ni autorizar una operación con score inferior a 70.

Su función es convertir una tesis ya aprobada en un plan de entrada, tamaño, invalidación y gestión de beneficios. Consume `market_risk_scalar` de `tendencia_mercado.md` y `sentiment_cap` del informe vigente, pero no recalcula ninguno de ellos.

---

## 1. Principios no negociables

- Máximo 10% del capital por posición.
- Riesgo estándar por operación: 1% del portfolio.
- Riesgo máximo excepcional: 2% solo en setup de alta convicción, líquido y completamente validado.
- `R/R neto mínimo = 2,0`.
- El stop se coloca donde muere la tesis, no donde empieza el ruido.
- Se reduce el tamaño antes de acercar artificialmente el stop.
- El stop de tesis swing se valida por cierre diario.
- El stop protector usa estructura y ATR; no se pega al mínimo intradía.
- Los cortos están desactivados por defecto salvo petición explícita.
- Todos los cálculos se expresan en la moneda de cotización del activo.

---

## 2. Dimensionamiento de posición

### 2.1. Fórmula base

```text
riesgo_base_monetario = capital_total × porcentaje_riesgo

effective_risk_scalar = min(
    market_risk_scalar,
    sentiment_cap
)

riesgo_monetario = riesgo_base_monetario × effective_risk_scalar
riesgo_por_accion = |entrada - stop_protector|
numero_acciones = floor(riesgo_monetario / riesgo_por_accion)
valor_posicion = numero_acciones × entrada
```

Aplicar después el límite:

```text
valor_posicion ≤ capital_total × 0,10
```

El tamaño final es el menor entre:

1. Tamaño permitido por riesgo.
2. Tamaño permitido por concentración.
3. Tamaño permitido por liquidez y spread.
4. Tamaño permitido por `effective_risk_scalar`.

El scalar se aplica una sola vez al presupuesto monetario de riesgo. No volver a multiplicar el número de acciones ni el valor de posición por el mismo scalar.

### 2.2. Regla de hierro

El tamaño se calcula usando el stop técnico real, no un stop imaginario más cercano.

Si el tamaño resultante es demasiado pequeño o el objetivo razonable no ofrece `R/R neto ≥2,0`, la operación se descarta.

### 2.3. Riesgo por convicción

| Contexto | Riesgo máximo |
|---|---:|
| APTO, setup normal | 1,0% |
| ALTA CONVICCIÓN, setup A+ | hasta 1,5% |
| Excepcional, muy líquido y plenamente confirmado | hasta 2,0% |
| VIX 20–28 o mercado deteriorado | multiplicar por 0,75 |
| VIX >28 o backwardation | máximo 0,5×; normalmente no operar |

Nunca aumentar riesgo para compensar una entrada tardía o una pérdida anterior.

---

## 3. Diseño del stop

### 3.1. Stop de tesis swing

La tesis se invalida cuando se produce un **cierre diario** bajo el nivel estructural definido, salvo evento extremo que justifique salida inmediata.

Niveles válidos:

- Soporte horizontal relevante.
- Último mínimo creciente significativo.
- Base de canal.
- Neckline o borde de patrón confirmado.
- Zona Fibonacci con reacción validada.
- Zona de corrección del Túnel, solo como confluencia.
- DMA/WMA relevante cuando coincide con estructura.
- Put wall confirmada por precio y volumen.

Una mecha intradía aislada no invalida por sí sola una tesis swing.

### 3.2. Stop protector o de catástrofe

Debe proteger frente a gaps, noticias severas o caída desordenada.

Referencia:

```text
stop_protector_largo = soporte_estructural - buffer_ATR
buffer_ATR ≥ 1,0 × ATR(14)
```

Puede ampliarse a 1,2–1,5×ATR cuando:

- El activo es volátil.
- El soporte es una zona amplia.
- El régimen general es adverso.
- Existen gaps frecuentes.

Si el stop correcto obliga a exceder el riesgo máximo, reducir tamaño o cancelar.

### 3.3. Stop táctico

Reservado a breakouts, noticias o setups intradía muy líquidos.

- Debe tener estructura mayor favorable.
- Usa mínimo/máximo de vela de señal más buffer de volatilidad.
- No sustituye el stop swing cuando la tesis es diaria.
- Limitar el número de intentos.

### 3.4. Prohibiciones

- No bajar el stop para evitar que se ejecute.
- No convertir una operación fallida en inversión de largo plazo.
- No usar stops dentro del ruido normal del activo.
- No definir primero el tamaño y después forzar el stop para que encaje.

---

## 4. Relación riesgo/beneficio

### 4.1. Cálculo

Para largos:

```text
R = entrada - stop_protector
reward_neto = objetivo - entrada - costes_directos_estimados
RR_neto = reward_neto / R
```

Requisito:

```text
RR_neto ≥ 2,0
```

Los costes directos incluyen comisiones, tasas, spread y deslizamiento esperable cuando sean materiales.

### 4.2. Filtro económico

El beneficio esperado medio de una operación ganadora debe ser al menos 3–4× los costes directos estimados.

Una operación puede tener `R/R ≥2` y aun así descartarse si los costes consumen una parte excesiva del recorrido esperado.

### 4.3. Obstáculos

Antes de aceptar un objetivo, revisar:

- Resistencias diarias y semanales.
- Gaps pendientes.
- Call walls.
- Cintas del Túnel.
- Máximos previos y zonas de oferta.

Si un obstáculo importante aparece antes de 2R, ajustar la entrada, ampliar el objetivo solo con evidencia o cancelar.

`AllowedLongContext` no es un gate de riesgo ni de autorización. El Túnel aporta obstáculos y agotamiento; la existencia del setup técnico se resuelve en `entrada_tecnica_mtf.md`.

---

## 5. Option walls

Cuando exista open interest relevante:

- Put wall: soporte potencial, nunca garantía.
- Call wall: resistencia potencial, nunca garantía.

Reglas:

- Entrada larga tras reacción en put wall: exigir giro, cierre y volumen.
- Ruptura de call wall: exigir cierre confirmado por encima y volumen.
- En largos, el stop se coloca por debajo de la call wall rota si esta pasa a actuar como soporte, con buffer estructural/ATR.
- Nunca colocar el stop largo por encima de la resistencia recién superada.
- Si no existe mercado de opciones fiable, ignorar este módulo.

---

## 6. Órdenes y ejecución

### 6.1. Tipo de orden

- **Limit**: opción por defecto para pullbacks y entradas planificadas.
- **Stop**: solo para breakout confirmado o protección clara.
- **Market**: evitar por defecto; usar solo cuando el riesgo de no salir sea superior al deslizamiento esperado.

### 6.2. Confirmación

- Swing: cierre diario.
- Setup intermedio: cierre 4H.
- Intradía: cierre del timeframe operativo, siempre subordinado a diario/4H.

### 6.3. Horarios

- Expresar todas las horas en Europe/Madrid.
- Evitar nuevas aperturas en la última hora del viernes salvo setup A+.
- Evitar operar inmediatamente antes de resultados o eventos binarios salvo estrategia específica.

### 6.4. Liquidez

Descartar o reducir tamaño cuando:

- Spread amplio.
- Volumen medio insuficiente.
- Profundidad pobre.
- Gaps frecuentes.
- El tamaño previsto puede alterar la ejecución.

---

## 7. Gestión de beneficios

### 7.1. T1

```text
T1 = entrada + 1R
```

Al alcanzar T1:

- Tomar 25–40% de la posición.
- Evaluar movimiento a break-even.
- No ampliar riesgo inicial.

### 7.2. Break-even

Solo se mueve el stop a break-even después de haber tomado parcial en T1.

No moverlo si queda dentro del ruido:

```text
distancia(precio_actual, break_even) < 0,5 × ATR(14)
```

En ese caso:

- Mantener stop estructural.
- Subirlo a un nivel técnico válido.
- O reducir más posición.

El break-even debe incluir costes directos materiales.

### 7.3. T2

```text
T2 = entrada + 2R
```

Al alcanzar T2:

- Tomar 25–50% adicional.
- Mantener el resto solo si la estructura continúa sana.

### 7.4. Trailing

Para el remanente:

- Mínimo semanal −0,5×ATR.
- DMA/WMA20.
- Último mínimo creciente diario.
- Base de canal ascendente.

Usar el nivel que mejor preserve tendencia sin quedar dentro del ruido.

### 7.5. Regla de ganador consolidado

Después de T1 y una gestión correcta, no permitir que la posición completa vuelva a pérdida neta.

No cerrar ganadores antes de T1 por ruido intradía salvo:

- Cambio fundamental grave.
- Profit warning.
- Fraude o evento legal severo.
- Ruptura estructural evidente.
- Evento macro extremo.

---

## 8. Régimen de mercado y cap de sentimiento

Entradas requeridas:

```text
market_risk_scalar = salida amplia vigente de tendencia_mercado.md
sentiment_cap = salida amplia vigente de sentimiento_posicionamiento.md

broad_context_cap = min(market_risk_scalar, sentiment_cap)
relative_context_cap = min(
    valid_style_sector_industry_layer_caps,
    divergence_cap
)

effective_risk_scalar = min(
    broad_context_cap,
    relative_context_cap
)
```

| `effective_risk_scalar` | Ejecución en acciones individuales |
|---:|---|
| 1,00 | Riesgo canónico permitido |
| 0,75 | Riesgo reducido; priorizar pullbacks |
| 0,50 | Medio riesgo; solo setup A+ y líquido |
| 0,25 | Pausar nuevas entradas individuales |
| 0,00 | Bloqueo total de nuevas entradas |

Reglas:

- `PANIC_LIQUIDATION` no es compra automática; esperar reversión.
- Una oportunidad contrarian alta no eleva el scalar ni autoriza una acción individual.
- `CROWDED_LONG` y `DISTRIBUTION` reducen nuevas entradas tardías, pero no obligan a vender una posición sana.
- Si el informe semanal falta o caduca, marcar `DATO PENDIENTE`; usar `sentiment_cap = 1,00` como efecto neutral, nunca como confirmación positiva.
- No aplicar el scalar dos veces.
- El VIX, el sentimiento o el crowding no convierten un activo débil en comprable; solo regulan exposición y timing.

---

### 8.1. Cap jerárquico por índice, sector e industria

Para acciones individuales y ETFs temáticos, el tamaño no puede basarse solo en el índice amplio. Resolver las capas aplicables del `context_stack` y usar la más restrictiva.

| Divergencia | Lectura de riesgo | `divergence_cap` máximo |
|---|---|---:|
| Índice e industria alineados al alza | Contexto favorable | 1,00 |
| Índice fuerte, sector débil | Rotación fuera del sector | 0,50 |
| Índice fuerte, industria en liquidación | Riesgo específico alto | 0,25 |
| Índice débil, sector fuerte | Liderazgo relativo, pero mercado adverso | 0,75 |
| Sector fuerte, industria débil | Debilidad específica de la cadena | 0,50 |
| Sector débil, industria mejorando | Rotación interna temprana | 0,50–0,75 según confirmación |
| Pánico sectorial sin reversión | No anticipar suelo | 0,00–0,25 |
| Datos insuficientes | Efecto neutral, no confirmatorio | 1,00 |

Reglas:

- Aplicar `effective_risk_scalar` una sola vez al riesgo monetario.
- No compensar una industria débil aumentando convicción por fortaleza del índice amplio.
- Una excepción idiosincrática no puede elevar el scalar; solo justifica mantener el análisis si score, catalyst y setup siguen válidos.
- Para una posición existente, una divergencia negativa activa revisión y reducción opcional; no genera salida automática sin invalidación de tesis o estructura.


## 9. Promediado y DCA

- No promediar una pérdida sin plan definido antes de la primera entrada.
- Cada tramo debe tener nivel, tamaño y invalidación.
- El stop final de tesis no se desplaza para acomodar nuevos tramos.
- DCA agresivo solo cuando se cumplen todas las condiciones de `estrategia_inversion.md`.
- DCA agresivo exige `effective_risk_scalar > 0,25`, `reversal_confirmation = CONFIRMED` cuando la tesis es contrarian y ausencia de regímenes de bloqueo definidos en `sentimiento_posicionamiento.md`.
- `structuralBreak = true` bloquea cualquier DCA.

---

## 10. Presupuesto de stops y reintentos

### 10.1. Límite por idea

- Máximo 2 stops completos seguidos para el mismo activo y tesis.
- Tras el segundo, suspender reentradas hasta una revisión completa.
- Pérdida acumulada máxima por idea en un trimestre: 3–4% del portfolio.

### 10.2. Reentrada

Solo si aparece nueva evidencia:

- Nueva base.
- Recuperación de soporte.
- Ruptura confirmada con volumen.
- Mejora fundamental.
- Cambio de régimen de mercado.

No reentrar solo porque el precio ha vuelto al nivel anterior.

---

## 11. Correlación y concentración

Antes de abrir:

- Revisar exposición sectorial e industrial, además del índice o factor común que domina cada posición.
- Revisar factores comunes: tipos, petróleo, semiconductores, crédito, divisa del negocio o geografía.
- No añadir una posición altamente correlacionada si eleva el riesgo agregado sin mejorar el retorno esperado. Varias acciones de una industria en `ROTATION_OUT` cuentan como una sola concentración de riesgo.
- El límite del 10% por activo no sustituye el control de concentración temática.

---

## 12. Plan de trade obligatorio

Cada operación debe incluir:

1. Tesis breve.
2. Score y decisión fundamental.
3. Setup técnico MTF (`entrada_tecnica_mtf.md`) y overlay del Túnel.
4. `context_stack`, regímenes por capa, divergencia, capa más débil, fecha del informe y `effective_risk_scalar`.
5. Entrada y tipo de orden.
6. Stop de tesis.
7. Stop protector y ATR usado.
8. Tamaño calculado con el scalar aplicado una sola vez.
9. Riesgo monetario y porcentaje del portfolio.
10. T1, T2 y trailing.
11. `R/R neto`.
12. Costes directos estimados.
13. Escenarios base, aceleración y fallo.
14. Condición de cancelación.
15. Próximo catalizador o fecha de revisión.

---

## 13. Marco Taleb del stop

El stop no elimina el riesgo; transforma una cola potencialmente extrema en una serie más frecuente de pérdidas limitadas.

Consecuencias:

- Stops demasiado ceñidos elevan frecuencia de pérdida y costes.
- Reentradas repetidas alrededor de la misma barrera destruyen expectativa.
- La prioridad es evitar ruina y preservar acceso a grandes ganadores.
- Ajustar tamaño es preferible a comprimir el stop.
- La estrategia completa debe mantener expectativa positiva después de costes y stops fallidos.


## 5.1. Opciones XTB V1 - riesgo de single-leg long

Esta seccion aplica solo cuando el usuario solicita opciones y el ticket actual confirma BUY_CALL o BUY_PUT. No habilita sell-to-open ni multi-leg.

Preferir sizing por `PRIMA`. Para una opcion long:

```text
risk_base = capital_total * base_risk_pct
options_risk_budget = risk_base * effective_risk_scalar
max_loss_total = max(abs(broker_max_loss), premium_total + direct_costs_total)
```

Requerir `max_loss_total <= options_risk_budget`. El scalar se aplica una sola vez. Mantener 1% como riesgo estandar y 2% como maximo excepcional; la prima total tampoco puede superar 10% del capital.

Si el usuario trabaja por `VOLUMEN`, exigir el premium total o la perdida maxima del preview del broker. No hardcodear limites de volumen observados en un ticket concreto.

No asumir multiplicador 100. Inferir `effective_multiplier = premium_total/(option_price*volume)` solo para el contrato/precio actual y bloquear si la mecanica del preview no es coherente.

Para una opcion direccional nueva exigir DTE >=14 y DTE >= planned_holding_days+5. Con DTE menor, no usar el modo V1 de swing.

El R/R se valida de forma conservadora con el valor intrinseco del contrato al objetivo del subyacente:

```text
CALL intrinsic = max(target - strike,0) * volume * effective_multiplier
PUT  intrinsic = max(strike - target,0) * volume * effective_multiplier
profit_floor = intrinsic - max_loss_total
RR_floor = profit_floor / max_loss_total
```

Exigir `RR_floor >=2.0`. Si no puede calcularse por datos incompletos, marcar DATO PENDIENTE y no autorizar la opcion.

V1 usa `CLOSE_BEFORE_EXPIRY`. Ejercicio/assignment requiere verificacion aparte de la mecanica del broker. No promediar a la baja opciones long ni mover la tesis del subyacente para justificar theta perdido.
