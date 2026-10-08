# Referencia canónica: regla_tunel.md

> Fuente permanente proporcionada por el usuario; cuerpo conservado sin cambios.

## Índice de la fuente

- 0. Convenciones
- 1. Variables observables
- 2. Estados de tendencia
- 3. Alineación multi-timeframe
- 4. Obstáculos del timeframe superior
- 5. Contexto de setup largo
- 6. Diagnóstico corto
- 7. Agotamiento
- 8. Alertas de invalidación
- 9. Cintas y gestión de posición
- 10. Integración con Elliott y Fibonacci
- 11. Pseudocódigo completo
- 12. Contrato de salida para análisis

---

# Tunnel Domènec — Motor formal de contexto

Este documento define cómo interpretar las salidas del Tunnel Domènec dentro del marco `Inversiones`.

No es un sistema autónomo de trading. Está subordinado a:

```text
estrategia_inversion.md > reglas_riesgo_tecnico.md > regla_tunel.md
```

El Túnel puede:

- Clasificar tendencia y corrección.
- Confirmar o negar contexto para largos.
- Identificar obstáculos y agotamiento.
- Aportar niveles de confluencia.

El Túnel no puede:

- Autorizar una entrada con score fundamental <70.
- Definir por sí solo el stop final.
- Sustituir T1=1R y T2=2R por cintas.
- Invalidar una tesis swing por una vela intradía aislada.
- Activar cortos salvo petición explícita.

---

## 0. Convenciones

- `t`: índice de vela del timeframe de setup.
- `TF_SETUP`: diario o 4H por defecto.
- `TF_HT`: semanal o diario como contexto superior.
- `TF_TIMING`: 5–60m, solo para afinar precio.
- `map_to_HT(t)`: vela de `TF_HT` que contiene a `t`.
- `EPS`: tolerancia mínima.
- `SLOPE_MIN`: pendiente mínima significativa.
- `VOL_MIN_FACTOR`: volumen relativo mínimo; referencia 1,3.

Principio temporal:

```text
TF_HT define el régimen
TF_SETUP define el setup
TF_TIMING solo optimiza la ejecución
```

Una señal en `TF_TIMING` no invalida por sí sola una tesis basada en diario/semanal.

---

## 1. Variables observables

### 1.1. Precio y volumen

Para cada timeframe `TF`:

- `close_TF[t]`
- `high_TF[t]`
- `low_TF[t]`
- `volume_TF[t]`
- `ATR_TF[t]`
- `vol_rel_TF[t]`
- `MACD_hist_TF[t]`

### 1.2. Zona de corrección

- `Z_low_TF[t]`
- `Z_high_TF[t]`
- `Z_color_TF[t] ∈ {GREEN, RED, NONE}`

### 1.3. Genial Line

- `G_TF[t]`
- `G_color_TF[t] ∈ {GREEN, RED}`
- `slope_G_TF[t]`

### 1.4. Cintas

- `B_blue_low_TF[t]`
- `B_blue_high_TF[t]`
- `B_pink_low_TF[t]`
- `B_pink_high_TF[t]`
- `B_yellow_low_TF[t]` y `B_yellow_high_TF[t]`, si existen.

Las cintas son zonas de trayectoria, resistencia, soporte o agotamiento. No son automáticamente take-profits.

---

## 2. Estados de tendencia

```text
trend_state_TF[t] ∈ {
  IMPULSE_UP,
  PULLBACK_UP,
  BROKEN_UP,
  IMPULSE_DOWN,
  PULLBACK_DOWN,
  BROKEN_DOWN,
  NEUTRAL
}
```

### 2.1. Funciones auxiliares

```text
BetweenInclusive(x, a, b) := (x >= a) and (x <= b)

EnvUp_TF(t) :=
    Z_color_TF[t] == GREEN and
    G_color_TF[t] == GREEN and
    slope_G_TF[t] > SLOPE_MIN

EnvDown_TF(t) :=
    Z_color_TF[t] == RED and
    G_color_TF[t] == RED and
    slope_G_TF[t] < -SLOPE_MIN
```

### 2.2. Clasificación

```text
P  = close_TF[t]
ZL = Z_low_TF[t]
ZH = Z_high_TF[t]

if EnvUp_TF(t) and P > ZH + EPS:
    state = IMPULSE_UP

else if EnvUp_TF(t) and BetweenInclusive(P, ZL - EPS, ZH + EPS):
    state = PULLBACK_UP

else if EnvUp_TF(t) and P < ZL - EPS:
    state = BROKEN_UP

else if EnvDown_TF(t) and P < ZL - EPS:
    state = IMPULSE_DOWN

else if EnvDown_TF(t) and BetweenInclusive(P, ZL - EPS, ZH + EPS):
    state = PULLBACK_DOWN

else if EnvDown_TF(t) and P > ZH + EPS:
    state = BROKEN_DOWN

else:
    state = NEUTRAL
```

`BROKEN_UP` significa que el entorno previamente alcista ha perdido su zona. No implica venta automática: activa una alerta de revisión en el timeframe que corresponda.

---

## 3. Alineación multi-timeframe

Para `t` en `TF_SETUP`:

```text
t_ht = map_to_HT(t)
state_HT = trend_state_HT[t_ht]
state_SETUP = trend_state_SETUP[t]
```

### 3.1. Contexto largo

```text
AllowedLongContext(t) :=
    state_HT in {IMPULSE_UP, PULLBACK_UP} and
    state_SETUP in {IMPULSE_UP, PULLBACK_UP}
```

Interpretación:

- `true`: el Túnel aporta confluencia favorable para largos.
- `false`: el Túnel no confirma su propio contexto largo, pero no bloquea universalmente un setup válido de `entrada_tecnica_mtf.md`.
- No equivale a orden de compra ni a autorización final.

### 3.2. Contexto corto

```text
AllowedShortContext(t) :=
    state_HT in {IMPULSE_DOWN, PULLBACK_DOWN} and
    state_SETUP in {IMPULSE_DOWN, PULLBACK_DOWN}
```

Por defecto:

```text
SHORTS_ENABLED = false
```

`AllowedShortContext` se conserva como diagnóstico. Solo puede convertirse en setup operativo si el usuario solicita cortos expresamente y `SHORTS_ENABLED = true`.

### 3.3. Conflicto de timeframes

Si `TF_HT` y `TF_SETUP` del Túnel no están alineados:

- Marcar conflicto del overlay y clasificar transición, rango o rebote contra tendencia.
- No convertir el timeframe inferior del Túnel en confirmación superior.
- El motor MTF externo decide la existencia del setup; un `RECOVERY_ENTRY` puede existir antes de alineación completa si cumple sus gates y no hay deterioro estructural bloqueante.

---

## 4. Obstáculos del timeframe superior

### 4.1. Obstáculo superior

```text
UpperObstacle_HT(t) :=
    menor valor > close_SETUP[t] entre:
      Z_high_HT[t_ht],
      G_HT[t_ht],
      B_blue_high_HT[t_ht],
      B_pink_high_HT[t_ht]
```

### 4.2. Obstáculo inferior

```text
LowerObstacle_HT(t) :=
    mayor valor < close_SETUP[t] entre:
      Z_low_HT[t_ht],
      G_HT[t_ht],
      B_blue_low_HT[t_ht],
      B_pink_low_HT[t_ht]
```

### 4.3. Uso

```text
HasLongObstacle(t, target_price) :=
    UpperObstacle_HT(t) != None and
    UpperObstacle_HT(t) < target_price
```

Un obstáculo antes de 2R obliga a:

- Mejorar la entrada.
- Reducir expectativa.
- Esperar ruptura confirmada.
- O cancelar el setup.

Las cintas no sustituyen el objetivo por R.

---

## 5. Contexto de setup largo

La salida del módulo es un **contexto candidato**, no una orden.

### 5.1. Corrección previa

```text
CondPullbackPrev :=
    BetweenInclusive(
        close_SETUP[t - 1],
        Z_low_SETUP[t - 1] - EPS,
        Z_high_SETUP[t - 1] + EPS
    )
```

### 5.2. Salida alcista

```text
CondBreakUpNow :=
    close_SETUP[t] > Z_high_SETUP[t] + EPS
```

### 5.3. Fuerza

```text
ImpulseStrength :=
    MACD_hist_SETUP[t] > MACD_hist_SETUP[t - 1] and
    vol_rel_SETUP[t] >= VOL_MIN_FACTOR
```

El volumen puede relajarse solo si existe una razón explícita: activo de bajo volumen estructural, cierre semanal aún no disponible o ruptura confirmada por otra evidencia fuerte.

### 5.4. Contexto candidato

```text
LongSetupContext(t) :=
    AllowedLongContext(t) and
    CondPullbackPrev and
    CondBreakUpNow and
    ImpulseStrength
```

Para que el marco general autorice entrada, `LongSetupContext` no es obligatorio por sí solo. La autorización se resuelve en `entrada_tecnica_mtf.md`; cuando el Túnel sea favorable, además deben seguir cumpliéndose:

- Score fundamental ≥70.
- Nivel estructural claro.
- Stop válido según `reglas_riesgo_tecnico.md`.
- Objetivo razonable con `R/R neto ≥2,0`.
- Sin obstáculo superior invalidante.
- Régimen de mercado compatible.

### 5.5. Salida del módulo

El módulo devuelve:

```text
{
  trend_state_HT,
  trend_state_SETUP,
  AllowedLongContext,
  CondPullbackPrev,
  CondBreakUpNow,
  ImpulseStrength,
  UpperObstacle_HT,
  zone_reference,
  tunnel_risk_flags
}
```

No devuelve una orden final, número de acciones, stop definitivo ni take-profits definitivos.

---

## 6. Diagnóstico corto

Solo si `SHORTS_ENABLED = true`:

```text
CondBreakDownNow := close_SETUP[t] < Z_low_SETUP[t] - EPS

DownImpulseStrength :=
    MACD_hist_SETUP[t] < MACD_hist_SETUP[t - 1] and
    vol_rel_SETUP[t] >= VOL_MIN_FACTOR

ShortSetupContext(t) :=
    AllowedShortContext(t) and
    CondPullbackPrev and
    CondBreakDownNow and
    DownImpulseStrength
```

Incluso activado, el contexto corto no sustituye las reglas de riesgo, liquidez y R/R.

---

## 7. Agotamiento

### 7.1. Agotamiento alcista

```text
ExhaustionUp(t) :=
    BetweenInclusive(
        close_SETUP[t],
        B_pink_low_SETUP[t],
        B_pink_high_SETUP[t]
    ) and
    slope_G_SETUP[t] <= SLOPE_MIN
```

Refuerzos:

- Divergencia bajista RSI/MACD.
- Volumen climático.
- Precio ≥20% sobre DMA/SMA200.
- Elliott compatible con onda 5.
- Rechazo repetido en resistencia semanal.

Efectos:

- Prohibir nuevas compras agresivas.
- Revisar parciales y trailing.
- No cerrar automáticamente toda la posición si la estructura diaria sigue intacta.

### 7.2. Agotamiento bajista

```text
ExhaustionDown(t) :=
    precio en cinta rosa inferior and
    slope_G_SETUP[t] >= -SLOPE_MIN
```

Es una alerta de posible agotamiento, no una compra automática.

---

## 8. Alertas de invalidación

### 8.1. Alerta de deterioro largo

```text
LongStructureWarning(t) :=
    trend_state_SETUP[t] == BROKEN_UP or
    trend_state_HT[t_ht] == BROKEN_UP or
    close_SETUP[t] < G_SETUP[t] - EPS
```

Uso:

- En 4H: alerta temprana.
- En diario: revisión de tesis.
- En semanal: deterioro estructural mayor.

No ejecutar salida automática por una pérdida intradía de `G` o `Z_low`.

La salida final se rige por:

1. Nivel estructural definido antes de entrar.
2. Cierre diario de invalidación.
3. Stop protector con buffer ATR.
4. Evento fundamental grave, si aparece.

### 8.2. Alerta de deterioro corto

Simétrica, solo si cortos están habilitados.

---

## 9. Cintas y gestión de posición

### Cinta azul

- Primer obstáculo o zona de aceleración.
- Puede coincidir con T1, pero no lo define.
- Si aparece antes de 1R, el setup puede ser ineficiente.

### Cinta rosa

- Zona potencial de extensión o agotamiento.
- Puede justificar parcial adicional o trailing más estricto.
- No obliga a cerrar si tendencia, volumen y estructura siguen fuertes.

### Regla de objetivos

```text
T1 = 1R
T2 = 2R
```

Las cintas se usan para validar si esos objetivos son realistas.

### Break-even

El Túnel no mueve el stop a break-even.

Solo `reglas_riesgo_tecnico.md` puede hacerlo, después de T1 y fuera del ruido de 0,5×ATR.

---

## 10. Integración con Elliott y Fibonacci

- `PULLBACK_UP` puede ser compatible con onda 2 o 4.
- `IMPULSE_UP` puede ser compatible con onda 1, 3 o 5.
- `ExhaustionUp` eleva la probabilidad de onda 5 madura o inicio ABC.
- Fibonacci 0,382–0,618 delimita una zona de corrección, no una señal autónoma.
- El conteo más conservador prevalece para riesgo.

Confluencia fuerte:

```text
PULLBACK_UP
+ Fibo 0,50–0,618
+ soporte diario/semanal
+ giro con volumen
+ recuperación de zona de corrección
```

---

## 11. Pseudocódigo completo

```text
Para cada nueva vela t en TF_SETUP:

    actualizar precio, volumen, ATR, MACD y salidas del Túnel
    t_ht = map_to_HT(t)

    state_SETUP = calcular_trend_state(TF_SETUP, t)
    state_HT = calcular_trend_state(TF_HT, t_ht)

    allowed_long = AllowedLongContext(t)
    allowed_short = AllowedShortContext(t)

    long_context = LongSetupContext(t)
    short_context = SHORTS_ENABLED and ShortSetupContext(t)

    calcular UpperObstacle_HT y LowerObstacle_HT
    calcular ExhaustionUp y ExhaustionDown
    calcular alertas de deterioro

    devolver contexto estructurado

    # El núcleo externo decide:
    # - si score >= 70
    # - si existe entrada válida
    # - stop definitivo
    # - tamaño
    # - T1/T2
    # - orden y ejecución
```

---

## 11.1 Papel subordinado en autorización

El Túnel se conserva como overlay. `AllowedLongContext`, `CondPullbackPrev`, `CondBreakUpNow` e `ImpulseStrength` son diagnóstico/confluencia. No deben convertirse en un veto universal si `entrada_tecnica_mtf.md` identifica un setup válido.

`UpperObstacle_HT`, `ExhaustionUp` y alertas de deterioro sí pueden afectar ejecución cuando impiden `R/R neto >=2`, indican sobreextensión/agotamiento o deterioran la estructura. La ausencia de datos del Túnel no es evidencia favorable.

---

## 12. Contrato de salida para análisis

El resumen del Túnel debe incluir:

- `trend_state_HT`.
- `trend_state_SETUP`.
- `AllowedLongContext`.
- `AllowedShortContext` como diagnóstico.
- Posición del precio: impulso, zona de corrección, cinta azul o cinta rosa.
- `ExhaustionUp/Down`.
- Obstáculo superior e inferior relevante.
- Señal de salida de corrección confirmada o no.
- Alertas de deterioro.
- Conclusión: favorable, neutral, contradictorio o agotado.

Nunca presentar una lectura del Túnel como garantía ni como sustituto del filtro fundamental.
