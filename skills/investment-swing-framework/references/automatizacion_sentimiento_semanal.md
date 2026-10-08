# Hook pendiente: automatizacion_sentimiento_semanal.md

**DATO PENDIENTE: procedimiento permanente original no localizado.** No hay scheduler ni automatización persistente implementados.

La Skill consume un informe dinámico a través de `context_stack.weekly_report` y los campos de sentimiento de cada capa. No escribe sobre los documentos del Project, no promete actualizaciones futuras y no incorpora un informe fechado al núcleo.

El proveedor externo es responsable de recabar datos, producir el informe, establecer vigencia y detectar shocks materiales. El consumidor comprueba cobertura >=70%, marcas temporales, capas críticas y fuentes; ante fallo aplica neutralidad sin evidencia favorable. La fecha máxima de validez no se inventa.

No activar generación programada ni fórmulas de scores hasta recibir el procedimiento original y las capacidades externas necesarias.
