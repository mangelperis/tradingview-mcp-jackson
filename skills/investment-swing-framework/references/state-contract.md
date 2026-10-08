# Contrato de estado externo v1.0

## Separación

La Skill contiene reglas; no tiene cartera mutable. Otra capa puede proporcionar JSON/YAML o un archivo de Project con estado. No requiere un proveedor concreto, cuenta privada, memoria de este chat ni API hardcodeada. Los scripts reciben JSON; YAML es una interfaz documental, no requiere PyYAML en runtime.

```yaml
schema_version: "1.0"
as_of: null
portfolio:
  total_capital: null
  currency: null
positions:
  TICKER:
    instrument_id: null
    shares: null
    avg_price: null
    currency: null
    status: UNKNOWN
    updated_at: null
analysis_history:
  TICKER:
    score: null
    decision: null
    categories: null
    date: null
    thesis: null
    evidence_refs: []
watchlist:
  TICKER:
    target_zone: null
    thesis: null
    updated_at: null
special_instrument_rules:
  TICKER:
    listing: null
    currency: null
    reason: null
```

Este esquema no contiene datos personales ni un activo real. UNKNOWN se resuelve antes de convertir a `position.status=NONE/OPEN`. No deducir cero acciones por ausencia de estado; solo NONE verificado permite nueva entrada calculada.

## Identidad, precedencia y cambios

Usar ISIN+bolsa+clase como identidad cuando exista; un ticker puede cambiar, repetirse por bolsas o recibir un split. Mantener currency/ADR ratio y ajuste de cantidad/coste verificados. No usar cotización USD para una posición EUR sin conversión trazable.

Una corrección explícita y más reciente del usuario prevalece sobre snapshots antiguos. Entre snapshots comparar as_of, procedencia y coherencia; si hay conflicto no resuelto marcar DATO PENDIENTE. Ningún estado puede relajar reglas permanentes.

Clasificar cada objeto como REGLA PERMANENTE / ESTADO / DATO ACTUAL / INFORME TEMPORAL / INFERENCIA. No copiar conversaciones completas como reglas. La lista de acciones seguidas no implica posiciones abiertas.

## Adaptación al pipeline

Mapear posición seleccionada a `position`; patrimonio/FX a `risk`; historial previo a `review.prior`. Consultar contratos de datos y helpers de tests para campos exactos. El builder deriva current_price desde instrumento, no desde avg_price.

Para ampliación, contar todo el holding en existing_shares. Aplicar10% al valor final agregado y presupuesto de riesgo restante a la misma tesis. No ocultar exposición mediante varios tickets o brokers. Si capital o FX faltan, mostrar fórmula/pendiente, no número aprobado.

## Seguimientos y persistencia

Conservar score/desglose/tesis anteriores salvo cambio material evidenciado. Guardar opcionalmente un nuevo snapshot fuera de la Skill; no afirmar que se persistieron datos sin una herramienta de escritura realmente ejecutada. Nunca sobreescribir fuentes canónicas al guardar una posición.

Al recuperar historial, distinguir decisiones fundamentales y operativas. NO_TRADE no es una operación de venta; AÑADIR no es una orden ejecutada. Registrar fills solo a partir de confirmaciones externas.
