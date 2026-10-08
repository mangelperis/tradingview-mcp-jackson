# Opciones XTB long single-leg - V1

> Extension autorizada por el usuario para el Investment Swing Framework.
> Alcance deliberadamente conservador: solo productos y mecanicas observadas/confirmadas en la interfaz XTB aportada por el usuario.

## 1. Principio de autoridad

Las opciones no crean una tesis nueva ni mejoran el score fundamental. Primero se valida el subyacente con el framework normal. Solo despues se estudia si una opcion long single-leg es un vehiculo adecuado para expresar esa tesis.

Esta extension no sustituye `estrategia_inversion.md`, `reglas_riesgo_tecnico.md` ni `entrada_tecnica_mtf.md`.

## 2. Alcance operativo V1

Admitir exclusivamente:

- `LONG_CALL`: compra de una call single-leg cuando el ticket actual del broker confirma una accion `BUY_CALL`.
- `LONG_PUT`: compra de una put single-leg solo cuando el ticket actual del broker confirma una accion `BUY_PUT` y el usuario ha solicitado explicitamente una tesis bajista.

Uso protector de una put sobre una posicion existente puede analizarse como cobertura, pero V1 no automatiza el sizing del hedge ni lo etiqueta como entrada direccional.

No admitir ni proponer como operativas V1:

- sell-to-open de calls o puts;
- covered calls;
- cash-secured puts;
- bull/bear spreads;
- collars;
- straddles/strangles;
- iron condors/butterflies;
- calendars/diagonals;
- ratio spreads;
- cualquier estrategia multi-leg;
- opciones naked short.

Si el broker ofrece alguna de estas funciones en el futuro, tratarla como `DATO PENDIENTE` hasta que el usuario la confirme y se incorpore una regla especifica.

## 3. Datos confirmados por la interfaz XTB aportada

La evidencia de interfaz aportada permite trabajar con:

- vencimientos disponibles;
- strikes;
- precios de calls y puts listados;
- precio actual del subyacente;
- break-even mostrado por contrato seleccionado;
- perdida maxima y beneficio maximo cuando el preview puede calcularlos;
- orden expresada por `PRIMA` o por `VOLUMEN`;
- limite de volumen comunicado por el propio ticket cuando aplique.

No hardcodear un maximo global de volumen. Un mensaje como `Volume must be lower than 50` se interpreta como restriccion del ticket actual, no como regla universal del broker.

No asumir un multiplicador contractual fijo de 100. Cuando `option_price`, `volume` y `premium_total` estan presentes, puede inferirse un `effective_multiplier`:

```text
effective_multiplier = premium_total / (option_price * volume)
```

Usarlo solo para ese preview si es coherente con la perdida maxima mostrada por XTB. No reutilizarlo en otro contrato sin nueva verificacion.

## 4. Datos que V1 no inventa

La captura no demuestra de forma suficiente:

- bid/ask separado;
- open interest;
- volumen negociado de la cadena;
- IV;
- IV rank/percentile;
- delta, gamma, theta o vega;
- estilo de ejercicio;
- reglas exactas de assignment/exercise;
- settlement;
- sell-to-open;
- multi-leg.

Si estos datos aparecen por otra fuente fiable pueden mostrarse como diagnostico, pero no son necesarios para la logica V1 ni pueden fabricar una autorizacion ausente.

## 5. Gate del subyacente

### LONG_CALL

Requerir antes de mirar el contrato:

- score fundamental >=70 y sin veto;
- contexto no bloqueante;
- setup tecnico MTF valido;
- riesgo/evento/correlacion revisados;
- objetivo del subyacente definido;
- tesis alcista vigente.

La opcion no rescata una entrada que el subyacente no autoriza.

### LONG_PUT

El proyecto mantiene cortos/bajistas desactivados por defecto. Requerir:

- solicitud bajista explicita del usuario;
- tesis bajista del subyacente validada de forma separada;
- ticket actual que confirme `BUY_PUT`.

Sin solicitud explicita, una put puede analizarse solo como cobertura de una posicion existente.

## 6. Gate temporal - DTE

V1 esta orientado a swing, no a 0DTE/ultra-short-dated.

Para una entrada direccional estandar exigir simultaneamente:

```text
DTE >= 14 dias calendario
DTE >= planned_holding_days + 5
```

Con DTE <14: `OPTIONS_DTE_TOO_SHORT` y no autorizar la entrada V1. Esta regla es deliberadamente conservadora para evitar que theta/gamma de muy corto plazo dominen una tesis swing.

La fecha de expiracion debe ser posterior al horizonte del catalizador/objetivo que justifica la operacion. Si el catalizador principal ocurre despues del vencimiento, bloquear.

## 7. Prima, volumen y multiplicador efectivo

Preferir `PRIMA` para sizing porque la perdida maxima de una opcion long esta acotada por el debit pagado mas costes.

Aun cuando el usuario seleccione `VOLUMEN`, exigir que el preview de XTB proporcione `premium_total` o `broker_max_loss` antes de validar riesgo monetario.

Campos minimos:

```text
order_mode = PREMIUM | VOLUME
option_price
volume
premium_total
broker_max_loss
broker_break_even
broker_action = BUY_CALL | BUY_PUT
```

Si `volume` o `premium_total` son derivados automaticamente por XTB, capturar ambos valores del preview final. No inferir el coste total a partir de un multiplicador memorizado.

## 8. Riesgo monetario

Aplicar el scalar una sola vez:

```text
risk_base = capital_total * base_risk_pct
options_risk_budget = risk_base * effective_risk_scalar
```

Limites:

- `base_risk_pct <= 0.02`; 1% sigue siendo el estandar y 2% excepcional.
- `max_loss_total <= options_risk_budget`.
- `premium_total <= 10%` del capital, aunque normalmente el gate de riesgo sea mas restrictivo.
- `max_loss_total = max(broker_max_loss_abs, premium_total + direct_costs_total)`.

Si la perdida maxima mostrada por el broker y el debit total no son coherentes dentro de una tolerancia razonable, bloquear y revisar el contrato.

## 9. Break-even y R/R conservador

Primero comprobar que el objetivo del subyacente supera el break-even en la direccion correcta:

```text
CALL: target_price > broker_break_even
PUT:  target_price < broker_break_even
```

Cuando se hayan verificado `volume` y `effective_multiplier`, calcular un floor de payoff a expiracion:

```text
CALL intrinsic_at_target = max(target_price - strike, 0) * volume * effective_multiplier
PUT  intrinsic_at_target = max(strike - target_price, 0) * volume * effective_multiplier

profit_floor_at_target = intrinsic_at_target - max_loss_total
RR_floor = profit_floor_at_target / max_loss_total
```

Para `OPTIONS_ENTRY_VALID` exigir `RR_floor >= 2.0`.

Este floor no intenta valorar theta/vega/IV antes del vencimiento. Es deliberadamente conservador. Si faltan los datos para calcularlo, devolver `OPTIONS_CANDIDATE` / `DATO PENDIENTE`, nunca `OPTIONS_ENTRY_VALID`.

## 10. Gestion

- No hacer DCA/promediado automatico de opciones long.
- No desplazar la tesis del subyacente para justificar una prima perdida.
- La opcion puede cerrarse antes que el subyacente si el tiempo restante deja de ser compatible con la tesis.
- V1 usa por defecto `CLOSE_BEFORE_EXPIRY`.
- No planificar ejercicio, assignment o conversion a acciones salvo verificacion expresa de la mecanica del broker para ese contrato.
- Una perdida de 100% de la prima sigue contando como perdida total del trade; dimensionar para que sea asumible desde el inicio.

## 11. Estado de salida

```text
OPTIONS_NOT_REQUESTED
OPTIONS_CANDIDATE
OPTIONS_ENTRY_VALID
OPTIONS_BLOCKED
```

Mostrar siempre:

- CALL/PUT;
- strike y expiracion;
- DTE;
- precio del subyacente;
- precio de opcion;
- modo PRIMA/VOLUMEN;
- volume y premium_total;
- multiplier efectivo verificado/inferido para ese preview;
- break-even;
- objetivo del subyacente;
- perdida maxima;
- presupuesto de riesgo;
- RR_floor si es calculable;
- gates fallidos;
- datos pendientes.

Nunca presentar una opcion concreta como valida si el ticket actual no confirma la accion BUY correspondiente o si los datos del preview no permiten verificar la perdida maxima.
