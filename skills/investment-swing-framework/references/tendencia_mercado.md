# Referencia canónica: tendencia_mercado.md

> Fuente permanente proporcionada por el usuario; cuerpo conservado sin cambios.

## Índice de la fuente

- 0. Cómo usar esta guía
- 1. Patrones de suelo / final de tramo bajista
- 2. Patrones de techo / distribución
- 3. Patrones de confirmación de nuevo tramo alcista
- 4. Patrones de amplitud (breadth) y rotación
- 5. Patrones de volatilidad (VIX y su estructura)
- 6. Patrones de rallies engañosos y trampas
- 7. Checklist mínimo antes de tomar decisiones

---

# Tendencia de mercado

> Objetivo: disponer de un catálogo breve de patrones y señales que ayuden a **entender en qué fase está el mercado** (caída, distribución, capitulación, inicio de tramo alcista, etc.) y cómo reaccionan los precios ante las noticias.

Este archivo es un módulo de **régimen de mercado** subordinado a `estrategia_inversion.md` y `reglas_riesgo_tecnico.md`. No modifica el score fundamental, no autoriza entradas por sí solo y no redefine stops, objetivos ni tamaño base.

Calcula el régimen exclusivamente con evidencia de mercado: precio, breadth, volatilidad, crédito, distribución/acumulación y reacción ante noticias. No consume ni modifica `sentiment_regime`; la combinación se realiza después en el marco canónico para evitar dependencias circulares.

Su salida debe poder calcularse para el mercado agregado y para cada capa material del activo:

```text
context_layer ∈ {GLOBAL, REGION, STYLE, SECTOR, INDUSTRY}
market_regime[layer] ∈ {RISK_ON, CONSTRUCTIVE, CAUTION, RISK_OFF, CAPITULATION_UNCONFIRMED}
market_risk_scalar[layer] ∈ {1.00, 0.75, 0.50, 0.00}
```

La salida agregada `market_regime` se conserva para compatibilidad. En análisis de acciones y ETFs temáticos se añaden las capas aplicables y se identifica `weakest_market_layer`.

Referencia de aplicación:

| Régimen | Condiciones orientativas | `market_risk_scalar` máximo |
|---|---|---:|
| RISK_ON | índices sobre DMA200, breadth sano, VIX ≤20 y contango | 1,00 |
| CONSTRUCTIVE | tendencia positiva con deterioro limitado | 0,75–1,00 |
| CAUTION | VIX 20–28, breadth débil o distribución creciente | 0,75 |
| RISK_OFF | VIX >28, backwardation o ruptura amplia de DMA200 | 0,50; normalmente esperar |
| CAPITULATION_UNCONFIRMED | pánico sin giro ni follow-through | 0,00 para nuevas entradas |

Una capitulación, un FTD o un thrust son evidencia de contexto. La entrada sigue requiriendo score ≥70, setup técnico válido, `R/R neto ≥2,0` y el cap externo de sentimiento cuando exista.

Acoplamiento externo, no calculado aquí:

```text
layer_effective_cap[layer] = min(
    market_risk_scalar[layer],
    sentiment_cap[layer]
)

effective_risk_scalar = min(
    broad_context_cap,
    relative_context_cap
)
```

---

## 0. Cómo usar esta guía

- No son señales infalibles; sirven para **poner en contexto** movimientos de precio, volumen, volatilidad y noticias.
- Siempre combinar con:
  - Tendencia de los índices vs DMA200.
  - Volatilidad (VIX).
  - Breadth (anchura del mercado: cuántos valores acompañan).
  - Macro y “tono” de las noticias.

---

## 1. Patrones de suelo / final de tramo bajista

### 1.1. Patrón clásico de final de tramo bajista (tu definición)

**Secuencia típica:**

1. Noticia claramente negativa.
2. Interpretación muy negativa por parte del mercado.
3. Pánico de venta generalizado (gaps, barridas, volumen extremo).
4. Mano fuerte compra ese pánico y el día acaba con **vela de giro** (por ejemplo:
   - Martillo / hammer.
   - Reversal alcista (cierre en la parte alta del rango).
   - 90% down-day seguido pronto de 90% up-day).

**Contexto donde tiene más peso:**

- Tras **varias semanas/meses de caídas**.
- Índices alejados por debajo de la DMA50 y acercándose o tocando la DMA200.
- Noticias malas pero no “sistémicas” (dato macro, guidance flojo, etc.).

**Interpretación:**

- Las noticias negativas sirven de **excusa final** para que el inversor rezagado venda.
- La demanda de mano fuerte absorbe esa oferta y deja “vacío” de vendedores a corto plazo.
- Señal de posible **fin de tramo bajista**, no necesariamente de inicio inmediato de bull market secular.

---

### 1.2. Capitulation (capitulación)

**Definición:**

- Episodio de **pánico vendedor masivo**, donde incluso inversores normalmente pacientes “tirán la toalla” y venden a cualquier precio.
- Suele ir acompañado de caídas muy pronunciadas y volumen extremo en poco tiempo.

**Señales típicas:**

- Caídas diarias muy grandes en índices principales (−3 % a −5 % o más).
- Volumen claramente superior a la media de las últimas semanas.
- Amplitud extrema:
  - >90 % de valores bajando (90% down day).
  - Máximos/mínimos de 52 semanas disparados a la baja.
- VIX disparado (picos bruscos) y/o curva de VIX entrando en backwardation.
- Cobertura masiva de puts, spreads de crédito ampliándose fuerte.

**Interpretación:**

- Puede marcar el **final de la fase aguda** de la caída.
- Tras una capitulación, es frecuente una fase de:
  - **Consolidación lateral** (base) o
  - Inicio de tramo alcista más sostenible.

---

### 1.3. Suelo de agotamiento sin pánico (“grinding bottom”)

**Características:**

- No hay día de pánico brutal, sino:
  - Larga fase de caídas y rebotes fallidos.
  - Volumen decreciente.
  - Pérdida de interés general (“nadie quiere hablar de bolsa”).

**Señales:**

- Volatilidad baja o moderada, pero precios en zona deprimida.
- Noticias malas que ya “no hacen caer más”.
- Divergencias alcistas en indicadores de momentum (RSI, MACD, etc.).

**Interpretación:**

- El mercado “se seca” en la parte baja.
- El suelo se forma más por **ausencia de vendedores** que por entrada masiva de compradores.

---

## 2. Patrones de techo / distribución

### 2.1. Días de distribución (CAN SLIM / O’Neil)

**Definición:**

- Jornada en la que un índice principal:
  - Cae en precio (cierre negativo),
  - Con **volumen mayor que el día anterior**,
  - Dentro de una tendencia previa alcista.

**Uso:**

- 4–6 días de distribución en pocas semanas en el S&P/Nasdaq = alerta de inicio de **fase de distribución**.
- Aparecen sobre todo **cerca de máximos** de un ciclo, no en mitad de un desplome.

**Interpretación:**

- Mano fuerte vende en días de liquidez, mientras el público aún compra.
- Acumulación de distribution days = alto riesgo de techo importante.

---

### 2.2. Clímax comprador / Exhaustion gap

**Señales típicas:**

- Tras una subida muy fuerte y prolongada:
  - Gap alcista grande al abrir (exhaustion gap).
  - Velas diarias con rangos enormes.
  - Volumen parabolicamente alto.
- A menudo, la subida ese día se revierte y cierra lejos de máximos.

**Interpretación:**

- Último empujón de compra por FOMO.
- Si tras ese clímax el precio no consigue seguir subiendo y entra en rango o cae, suele marcar **techo de ciclo** o de tramo.

---

### 2.3. Buenas noticias que ya no suben el precio (“good news, bad tape”)

**Patrón:**

- Publicación de resultado/dato claramente positivo.
- Gap o subida fuerte al principio.
- Venta agresiva durante la sesión → cierre plano o en rojo.

**Interpretación:**

- Señal de que el mercado ya había descontado lo positivo y está usando las buenas noticias para vender.
- Muy típico en **fases finales de tendencia alcista** y en grandes líderes del ciclo.

---

## 3. Patrones de confirmación de nuevo tramo alcista

### 3.1. Follow-Through Day (FTD) – William O’Neil

**Definición:**

- Sistema para detectar el paso de **corrección → nueva tendencia alcista**.
- Condiciones estándar:
  - Tras un mínimo reciente de mercado (corrección clara),
  - Se produce un día, normalmente **entre el 4.º y el 10.º día** después de ese mínimo,
  - En el que el índice (S&P o Nasdaq):
    - Sube **≥ 1,7 % – 2 %**,
    - Con **volumen significativamente mayor** que el día anterior.

**Interpretación:**

- Señal de que mano fuerte entra con decisión.
- No garantiza éxito, pero ayuda a distinguir:
  - Rebote técnico débil
  - De inicio probable de rally más sostenible.

**Uso táctico:**

- No entrar agresivo sólo por el FTD; usarlo como condición **necesaria pero no suficiente**.
- Confirmar con:
  - Más días de subida ordenada.
  - Mejoras en breadth (más valores uniéndose al movimiento).

---

### 3.2. Zweig Breadth Thrust (ZBT)

**Definición:**

- Indicador de amplitud desarrollado por Marty Zweig.
- Calcula un ratio de **acciones que suben / total de acciones** (en la NYSE u otro universo amplio).
- Luego hace una **media de 10 días** de ese ratio.
- Se considera thrust cuando:
  - Esa media sube desde **<40 %** a **>61,5 %** en **≤10 días**.

**Interpretación:**

- Señal rara pero potente de **cambio de régimen**:
  - De mercado bajista o lateral
  - A posible inicio de bull market significativo.
- Indica paso brusco de “poca participación” a “muchos valores subiendo a la vez”.

---

## 4. Patrones de amplitud (breadth) y rotación

### 4.1. % de valores por encima de DMA50 / DMA200

**Indicadores típicos:**

- % de acciones del S&P 500 por encima de su **DMA50**.
- % de acciones del S&P 500 por encima de su **DMA200**.

**Interpretación estándar:**

- DMA50:
  - <30–40 % → mercado frágil; correcciones más probables.
  - >60 % → rally sano; muchos valores acompañan.
- DMA200:
  - >60–70 % → tendencia de fondo sólida.
  - <40 % → deterioro estructural de mercado (posibles mercados bajistas o fuertes correcciones).

---

### 4.2. 90% down days / 90% up days

**Definición:**

- **90% down day**:
  - ≥90 % del volumen total es en valores que caen.
- **90% up day**:
  - ≥90 % del volumen total es en valores que suben.

**Contextos clave:**

- Serie de 90% down days → pánico y ventas forzadas.
- 90% up day **después** de 90% down day(s) → posible señal de giro con entrada de mano fuerte.

---

### 4.3. Rotación sectorial

**Patrones a vigilar:**

- En fases finales de ciclo:
  - **Defensivos (utilities, consumo básico, salud)** empiezan a comportarse mejor que el índice.
- En inicios de tramo alcista:
  - **Cíclicos (industriales, financieras, small caps)** empiezan a mejorar tras haber quedado muy castigados.

**Interpretación:**

- La rotación ofrece pistas de si el movimiento es:
  - Sólo rebote técnico de líderes previos,
  - O verdadero cambio de fase macro/cíclica.

---

### 4.4. Jerarquía índice, estilo, sector e industria

La rotación puede quedar oculta en un índice amplio. Un Nasdaq 100 cerca de máximos no implica que semiconductores, software o biotecnología estén en un régimen favorable.

Para cada activo resolver:

```text
regional_broad_index
style_or_factor_index
sector_index
industry_index
```

Aplicar las mismas familias de evidencia en cada capa cuando existan datos adecuados:

- Precio frente a DMA50/DMA200 y estructura de máximos/mínimos.
- Breadth interno de los componentes de esa capa.
- Días de distribución/acumulación.
- Volumen y flujos agregados del índice o proxy.
- Reacción ante noticias relevantes para esa capa.
- Volatilidad o dispersión específica cuando esté disponible.

Clasificación de divergencias de mercado:

```text
MARKET_ALIGNED
INDEX_STRONG_SECTOR_WEAK
INDEX_WEAK_SECTOR_STRONG
SECTOR_STRONG_INDUSTRY_WEAK
SECTOR_WEAK_INDUSTRY_STRONG
ROTATION_OUT
ROTATION_IN
MIXED
INSUFFICIENT
```

Criterios orientativos:

- `INDEX_STRONG_SECTOR_WEAK`: índice amplio en `RISK_ON/CONSTRUCTIVE`, pero sector en `CAUTION/RISK_OFF` con breadth y flujos deteriorándose.
- `ROTATION_OUT`: debilidad sectorial persistente, pérdida de participación y salida de flujos mientras otras áreas del índice absorben el liderazgo.
- `INDEX_WEAK_SECTOR_STRONG`: mercado general débil, pero sector con breadth, flujos y reacción relativa superiores.
- `SECTOR_STRONG_INDUSTRY_WEAK`: la fortaleza del sector no alcanza al grupo industrial del activo.
- `ROTATION_IN`: mejora simultánea de breadth, flujos y reacción ante noticias desde niveles deprimidos.

La divergencia no cambia el score fundamental. Produce contexto y un cap que será combinado externamente con sentimiento y riesgo.


## 5. Patrones de volatilidad (VIX y su estructura)

### 5.1. Niveles absolutos del VIX

**Zonas típicas:**

- <15: complacencia, volatilidad muy baja.
- 15–20: normalidad.
- 20–28: corrección, susto moderado.
- >28–30: miedo alto / posible capitulación.
- >40: pánico extremo.

**Interpretación:**

- En fases finales de caídas:
  - Picos de VIX >28–30 suelen coincidir con capitulaciones o momentos de máximo miedo.
- En fases de distribución:
  - VIX sube poco a poco mientras índice hace techo.

---

### 5.2. Estructura temporal del VIX (contango / backwardation)

**Conceptos:**

- **Contango**:
  - Futuros de VIX de largo plazo más caros que el VIX spot/corto plazo.
  - Estructura típica en mercados tranquilos.
- **Backwardation**:
  - VIX spot/corto plazo más alto que VIX de vencimientos lejanos.
  - Indica estrés inmediato.

**Patrones útiles:**

- **Contango pronunciado + VIX bajo**:
  - Señal de complacencia; riesgo de que cualquier shock provoque subida violenta de volatilidad.
- **Backwardation + VIX alto**:
  - Señal de miedo agudo; suele asociarse a episodios de corrección o capitulación.
  - Si se normaliza (vuelve a contango) tras noticias negativas, puede coincidir con suelos.

---

## 6. Patrones de rallies engañosos y trampas

### 6.1. Relief rally / short-covering rally

**Características:**

- Gran subida en 1–3 días tras malas noticias:
  - A menudo impulsada por cobertura de cortos.
- Breadth limitada:
  - Pocas acciones lideran, muchas siguen débiles.
- Volumen no tan alto como en las caídas previas.

**Interpretación:**

- Descarga parcial de presión bajista, pero **no cambio estructural**.
- Alta probabilidad de retestear mínimos en las semanas siguientes.

---

### 6.2. Dead cat bounce (“rebote de gato muerto”)

**Señales:**

- Tras un desplome fuerte:
  - Rebote rápido de varios días/semanas.
  - Se queda por debajo de la DMA50 o de máximos locales previos.
- Luego:
  - Vuelve a aparecer presión vendedora y se marcan nuevos mínimos.

**Interpretación:**

- Rara vez empieza un bull market con una estructura así.
- Sirve para **salir mejor** de posiciones débiles, no para entrar fuerte.

---

### 6.3. Bull trap / breakout falso

**Patrón:**

- Precio rompe una resistencia relevante (máximos previos, canal, etc.).
- Muchos traders entran en el breakout.
- En pocos días:
  - El precio vuelve a meterse por debajo del nivel roto.
  - Puede acelerar la caída (stops ejecutados).

**Interpretación:**

- Falso inicio de tramo alcista.
- Frecuente en mercados en corrección donde las buenas noticias se usan para distribuir.

---

## 7. Checklist mínimo antes de tomar decisiones

Antes de abrir o ampliar posiciones, revisar:

1. **Tendencia índice principal (S&P/Nasdaq)**
   - ¿Por encima o por debajo de DMA50 y DMA200?

2. **Volatilidad**
   - VIX en zona <20, 20–28 o >28.
   - ¿Curva de VIX en contango o backwardation?

3. **Breadth**
   - % de valores por encima de DMA50/200 (fortaleza o debilidad estructural).
   - ¿Hay señales tipo Zweig Breadth Thrust o 90% up/down days?

4. **Patrón de días recientes**
   - ¿Ves más días de distribución o de acumulación?
   - ¿Las buenas noticias se venden (“good news, bad tape”)?

5. **Contexto macro y noticias**
   - ¿Estamos justo antes/después de datos clave (inflación, empleo, Fed)?
   - ¿Las noticias negativas desencadenan pánico o apenas mueven mercado?

6. **Contexto jerárquico**
   - ¿El índice amplio, el índice de estilo, el sector y la industria están alineados?
   - ¿Existe `ROTATION_OUT` o `ROTATION_IN`?
   - ¿Cuál es `weakest_market_layer`?

7. **Overlay de sentimiento vigente**
   - ¿El informe está vigente y con cobertura suficiente por capa?
   - ¿`risk_appetite_score[layer]` mejora o se deteriora?
   - ¿`contrarian_opportunity_score[layer]` está confirmado por `reversal_confirmation[layer]`?
   - ¿Existe divergencia entre flujos/posicionamiento y la evidencia de mercado?

El overlay no cambia `market_regime`. Se conserva como eje separado para calcular después `effective_risk_scalar`.

Si varios de estos puntos apuntan a:
- **Capitulación + señales de thrust / follow-through** → elevar el régimen desde `CAPITULATION_UNCONFIRMED` hacia `CONSTRUCTIVE` solo por evidencia de mercado; desplegar capital solo en activos con score ≥70, setup confirmado y `effective_risk_scalar > 0,25`.
- **Distribución + VIX al alza + buenas noticias vendidas** → clasificar como `CAUTION` o `RISK_OFF`, reducir `market_risk_scalar` y no ampliar riesgo.
- **Pánico con oportunidad contrarian alta pero sin giro** → mantener `CAPITULATION_UNCONFIRMED`; el miedo extremo no autoriza compra.
- **Sentimiento favorable con mercado deteriorado** → prevalece el scalar más restrictivo.

Contrato de salida:

```text
market_regime
market_risk_scalar
market_evidence_date
market_regime_by_layer
market_risk_scalar_by_layer
market_divergence_state
weakest_market_layer
breadth_state
volatility_state
credit_state
distribution_state
event_reaction
market_confidence
```

