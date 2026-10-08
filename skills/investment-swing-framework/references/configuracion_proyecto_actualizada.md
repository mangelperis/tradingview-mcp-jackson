# Referencia canónica: configuracion_proyecto_actualizada.md

> Fuente permanente proporcionada por el usuario; cuerpo conservado sin cambios.

## Índice de la fuente

- Jerarquía obligatoria
- Lectura antes de cada análisis
- Contexto índice–sector–industria
- Reglas por universo
- Informe ausente o caducado
- Salida mínima añadida

---

# Configuración del proyecto — Integración de sentimiento

Usar este bloque en la configuración permanente del proyecto.

## Jerarquía obligatoria

```text
estrategia_inversion.md
  > reglas_riesgo_tecnico.md
    > entrada_tecnica_mtf.md
      > regla_tunel.md
      > tendencia_mercado.md
        > sentimiento_posicionamiento.md
          > automatizacion_sentimiento_semanal.md
            > sentimiento_semanal_actual.md
              > otros informes temporales y escenarios externos
```

`buffet_value_invest.md` sigue siendo un submódulo fundamental de `estrategia_inversion.md`.

## Lectura antes de cada análisis

1. Resolver ticker, bolsa, país, moneda, precio y datos actuales.
2. Aplicar el score fundamental y sus overrides.
3. Resolver el `context_stack`: global, región, estilo/factor, sector, industria y activo.
4. Calcular `market_regime[layer]` y `market_risk_scalar[layer]` con `tendencia_mercado.md`.
5. Leer `sentimiento_semanal_actual.md`.
6. Validar `REPORT_STATUS`, `VALID_UNTIL`, `DATA_COVERAGE`, cobertura por capas y shocks posteriores.
7. Calcular:

```text
layer_effective_cap[layer] = min(
    market_risk_scalar[layer],
    sentiment_cap[layer]
)

broad_context_cap = min(valid GLOBAL and REGION caps)
relative_context_cap = min(valid STYLE, SECTOR and INDUSTRY caps, divergence_cap)
effective_risk_scalar = min(broad_context_cap, relative_context_cap)
```

8. Aplicar el scalar una sola vez al presupuesto monetario de riesgo.

## Contexto índice–sector–industria

Para acciones y ETFs temáticos:

```text
context_stack = GLOBAL -> REGION -> STYLE -> SECTOR -> INDUSTRY -> INSTRUMENT
```

- No usar el índice amplio como sustituto del sector.
- Resolver pertenencia actual y clasificación oficial.
- Detectar `INDEX_STRONG_SECTOR_WEAK`, `ROTATION_OUT`, `ROTATION_IN` y divergencias sector–industria.
- La capa más débil material limita nuevas entradas.
- Datos ausentes tienen efecto neutral `1,00`, pero no cuentan como confirmación favorable.
- Una oportunidad contrarian se evalúa en la capa deprimida y requiere reversión confirmada.

Ejemplo: AMD debe contrastarse con mercado de EE. UU., Nasdaq/growth, tecnología y semiconductores; no basta con que Nasdaq esté cerca de máximos.


## Reglas por universo

### Acciones individuales — `SINGLE_NAME_OVERLAY`

- El sentimiento no autoriza entradas.
- Score >=70, `technical_entry.valid`, stop estructural y R/R >=2 siguen siendo obligatorios. El Túnel actúa como overlay; `AllowedLongContext` no es veto universal.
- `contrarian_opportunity_score` solo prioriza investigación.
- Con `effective_risk_scalar <= 0,25`, pausar nuevas entradas.
- Euforia no obliga a vender; pánico no obliga a comprar.

### ETFs temáticos — `NARROW_THEME_OVERLAY`

- Uso contextual.
- Revisar concentración, liquidez, crowding y factor dominante.
- No tratar como índice amplio si pocos componentes explican la mayor parte del riesgo.

### Índices y ETFs amplios — `BROAD_MARKET_RESEARCH`

- El módulo puede emitir `allocation_signal`.
- `execution_enabled = false` mientras no exista `estrategia_asignacion_macro.md`.
- `PANIC_LIQUIDATION` => `WAIT`.
- Acumulación gradual solo con `contrarian_opportunity_score >=70` y `reversal_confirmation = CONFIRMED`.

## Informe ausente o caducado

```text
SENTIMIENTO_SEMANAL: DATO PENDIENTE
sentiment_cap = 1.00
sentiment_effect = NONE
positive_risk_adjustment = forbidden
```

Este comportamiento es neutral y no equivale a contexto favorable.

## Salida mínima añadida

```text
SENTIMIENTO_SEMANAL:
INFORME_FECHA:
CONTEXT_STACK:
CONTEXT_DIVERGENCE_STATE:
WEAKEST_CONTEXT_LAYER:
MARKET_REGIME_BY_LAYER:
SENTIMENT_REGIME_BY_LAYER:
RISK_APPETITE_SCORE_BY_LAYER:
CONTRARIAN_OPPORTUNITY_SCORE_BY_LAYER:
REVERSAL_CONFIRMATION_BY_LAYER:
RELATIVE_CONTEXT_CAP:
EFFECTIVE_RISK_SCALAR:
IMPACTO_EJECUCION:
```
