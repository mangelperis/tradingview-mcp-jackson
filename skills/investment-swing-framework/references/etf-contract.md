# Acciones, ETFs temáticos y ETFs amplios

## Acciones individuales

Aplicar los siete bloques de score y Buffett con métricas del emisor. Con scalar<=.25 no autorizar nueva posición. No confundir riesgo técnico con deterioro de negocio.

## ETFs temáticos

Mantener NARROW_THEME_OVERLAY. Analizar composición actual, concentración, liquidez/spread, AUM, costes, réplica, tracking, domicilio y principal factor/riesgo sectorial. Usar holdings/look-through verificables para fundamentales cuando existan, indicando cobertura y fecha. No atribuir deuda o FCF de la gestora al fondo.

Las fuentes disponibles no contienen una rúbrica automática completa para transformar cada métrica ETF a los siete bloques. No inventarla. Fundamentar la adaptación dentro del marco; si no puede justificarse una evaluación comparable o valoración alternativa robusta, declarar DATO PENDIENTE y bloquear gate. La capacidad aritmética del script no demuestra que los puntos elegidos sean válidos.

Buffett GRAY solo puede superar su cap con alternative_valuation robusta documentada. No afirmar un badge GOLD de una empresa para un ETF. Revisar sector e industria dominantes; no tratar un tema concentrado como mercado amplio.

## ETFs diversificados y mercado amplio

Permitir BROAD_MARKET_RESEARCH, diagnóstico de tendencia y señal de investigación de asignación. `estrategia_asignacion_macro.md` no está disponible: el pipeline bloquea nueva ejecución de ETF_BROAD por diseño, incluso con todos los campos favorables.

No desbloquear pasando execution_enabled=true. Hace falta integrar y revisar la fuente canónica de asignación y sus tests. Las posiciones existentes pueden gestionarse sin confundir este bloqueo de nueva asignación con venta obligatoria.
