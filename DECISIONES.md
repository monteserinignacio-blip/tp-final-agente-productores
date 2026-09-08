# DECISIONES.md — historia de iteración, análisis económico y gobierno/riesgo

Este documento junta las 3 partes que pide la consigna del Trabajo Final además del
contrato y las corridas: la historia honesta de cómo se armó el agente (qué se
probó, qué falló, qué cambió y por qué), el análisis económico de costos, y la
sección de gobierno y riesgo.

## 1 · Historia de iteración

### 1.1 — Punto de partida: Entrega 1

Este TP Final **no arranca de cero**: extiende "Agente de Productores — ficha para
reunión" (Entrega 1, [repo original](https://github.com/monteserinignacio-blip/agentes-productores)),
un agente que ya buscaba por Cliente y por Agente Productor cruzando un Excel local,
Firestore y Google News. La consigna pide "la versión seria" de un agente ya hecho —
se decidió tomar ese, no armar uno nuevo, porque es un caso de uso real del trabajo
diario (coordinación de un equipo comercial con Agentes Productores).

### 1.2 — Decisión: agregar un 3er modo (Comercial), no reescribir todo

La mejora concreta pedida para el TP Final fue agregar una tercera forma de buscar
—por **Comercial**— pensada para una reunión interna de equipo (no con un cliente),
mirando un dashboard separado (una app hecha en Google AI Studio) que ya mostraba
por comercial: sus Agentes Productores a cargo, pendientes, recordatorios,
aperturas en curso y calificaciones. Se tradujo esa pantalla a un tercer modo del
mismo agente, reusando toda la lógica de cruce de colecciones ya construida en la
Entrega 1 (`_contiene`, agrupamiento por coincidencia parcial, manejo de 0/2+
resultados).

### 1.3 — Decisión: seguir 100% en código, sin API de LLM en runtime

Se evaluó explícitamente usar un LLM en tiempo de ejecución (para, por ejemplo,
redactar el resumen de cada ficha) y **se descartó a propósito**. Las tres búsquedas
son consultas estructuradas contra fuentes fijas (Firestore + Google News) con una
salida en formato fijo — no hay ambigüedad de lenguaje natural que resolver, ni
texto libre que generar. Meter un LLM ahí agregaría costo, latencia y un riesgo de
alucinación (que invente un número de cuenta o una etapa) sin agregar ninguna
capacidad real. Es la misma postura que en la Entrega 1: un buen agente no se define
por cuánta API de IA usa, sino por resolver el problema real de la forma más simple
y confiable posible. Ver §2 (Análisis económico) para la comparación de costo
concreta.

### 1.4 — Iteración sobre el esquema real de Firestore

La documentación inicial de la app (hecha en Google AI Studio) decía una cosa sobre
cómo se relacionan las colecciones, pero al pedirle a la propia app que describiera
su esquema real y cruzarlo contra capturas de pantalla del CRM, aparecieron 2
discrepancias que hubo que resolver con el usuario antes de escribir código:

1. **Etapas de Calificación.** Se asumió inicialmente un set de etapas distinto;
   mirando el CRM real junto con Chicho se confirmó que son exactamente 4:
   **Prospecto / Pre Riesgos / Riesgos / Calificada** — con la aclaración de que hoy
   (2026-09) no hay ningún caso real cargado en "Pre Riesgos", pero la etapa existe
   igual y el código la contempla (no se hardcodeó "las 3 etapas que tienen datos
   hoy", que hubiera sido un error sutil).
2. **"Pendiente asignado" en modo Cliente.** Se había planeado mostrar, en la ficha
   de un cliente, si tenía algún pendiente del CRM asociado. Se descartó: los
   `pendientes` del CRM no tienen un vínculo estructurado (por ID) a un cliente
   puntual, solo texto libre — buscar por texto libre hubiera generado falsos
   positivos (un pendiente que menciona "Juan" por casualidad, sin ser de ese
   cliente). Se documenta como limitación declarada de v1, no como bug.

### 1.5 — El problema de `companies.producer` (ambigüedad de cruce)

Este fue el punto de diseño más delicado. La documentación de la app dice que la
columna `producer` de Calificaciones se cruza contra el nombre del **Comercial**
(`comerciales.nombre`). Pero los datos reales (capturas de la pestaña
Calificaciones, columna "Prod.") muestran nombres con forma de **Agente Productor**
("Diego Ruggeri", "Tarallo", "Mattioli"), no los ~5 comerciales conocidos del
dashboard.

Como es un campo de texto libre y las dos fuentes (documentación vs. datos reales)
se contradicen, **se decidió no asumir una sola interpretación**: el agente matchea
`producer` contra el nombre del Agente Productor buscado (modo Productor) y, en modo
Comercial, contra el nombre del comercial **o** contra cualquiera de los Agentes
Productores a su cargo (lo que matchee primero, sin preferencia declarada por uno u
otro). Esto quedó documentado explícitamente como restricción declarada en
`prompts/system_prompt.md` (§4.2) y en el docstring de `src/agent.py`, no como un
supuesto silencioso — es exactamente el tipo de cosa que, si se elige mal y no se
avisa, termina mostrándole a un comercial datos de otro comercial.

### 1.6 — Decisión: correr local, no desplegar en internet

Se evaluó desplegar el agente en un hosting público (Render, con Basic Auth como
protección) para que corriera "en un link", replicando el patrón de la Entrega 2.
Se preparó el despliegue completo (`render.yaml`, usuario/contraseña vía variables
de entorno) pero, al pensarlo con más cuidado, se decidió **no usarlo**: el agente
expone datos reales y sensibles de clientes (cuentas, situación crediticia,
pendientes internos), y agregar una superficie de internet pública —aunque esté
protegida con usuario/contraseña— es un riesgo innecesario para un trabajo de la
facultad, cuando correrlo en `http://127.0.0.1:5000` (solo accesible desde la propia
compu) cumple el mismo objetivo real: "que no dependa de chatear con un asistente de
IA para operarlo". El archivo `render.yaml`/`DEPLOY.md` queda en el repo documentado
como opción evaluada y descartada, no como parte del entregable final.

### 1.7 — Ajustes tras probar con datos reales (las 3+ corridas)

Al correr las primeras búsquedas reales (ver `corridas/`) aparecieron 2 pedidos de
ajuste:

1. **Pendientes y recordatorios ya resueltos.** La primera versión mostraba todos
   los pendientes/recordatorios de un comercial, marcando "(hecho)" o "(pendiente)".
   Al verlo con datos reales (un comercial con varios ítems ya resueltos mezclados
   con los activos), se decidió que no aporta valor ver los ya resueltos en una
   ficha pensada para actuar antes de una reunión — se cambió para mostrar solo los
   que siguen sin resolver (`completado = false`), en Pendientes y en Recordatorios
   (este último ya se filtraba así en modo Productor; solo faltaba emparejar modo
   Comercial). Ver `corridas/corrida_3_comercial_nacho.md`, que muestra el resultado
   de este ajuste ya aplicado sobre datos reales.
2. **Aperturas en modo Cliente.** Se planteó la duda de si "cuentas en proceso de
   Apertura" debía verse también en modo Cliente (hoy solo existe en modo
   Comercial). Al revisar una corrida real de Cliente se confirmó que no hacía
   falta el cambio — quedó fuera de alcance de v1 por decisión del usuario, no por
   limitación técnica.
3. **Hallazgo de calidad de datos (no es un bug del agente).** La corrida real de
   modo Productor sobre "polera" (`corridas/corrida_2_productor_polera.md`) mostró
   2 pares de cuentas con nombres de cliente casi idénticos pero no exactamente
   iguales ("SANCHEZ, ELIAS DEMETRIO" / "ELIAS SANCHEZ DEMETRIO", y "MARTINEZ RIAL,
   MANUEL" repetido dos veces). El agente no decide si son la misma persona
   cargada dos veces con formato distinto — los muestra tal cual, tal como manda la
   restricción anti-alucinación (§4.2 del contrato). Es una señal real de calidad de
   datos del CRM que vale la pena que el equipo revise, no algo que el agente deba
   "arreglar" adivinando.

## 2 · Análisis económico

### 2.1 — Costo real de este agente: prácticamente $0 por corrida

El agente **no llama a ningún LLM en tiempo de ejecución** (ver §1.3) — cada corrida
es código determinístico: unas pocas lecturas a Firestore (5 a 8 colecciones según
el modo, todas dentro del free tier de Firestore para el volumen de este equipo) más
una búsqueda RSS gratuita a Google News (solo en modo Cliente). El único costo real
es el tiempo de cómputo de esas consultas, del orden de milisegundos.

| Concepto | Costo por corrida |
|---|---|
| Llamadas a API de LLM | **$0** (no se usa ningún LLM en runtime) |
| Lecturas a Firestore | ~5-8 documentos/colecciones — dentro del free tier de Firestore para este volumen |
| Búsqueda de noticias (Google News RSS) | $0 (RSS público) |
| Hosting | $0 (corre local, en la compu del usuario — ver §1.6) |

Proyección: aunque el equipo comercial corriera este agente **50 veces por semana**
(un uso intensivo, mucho más de lo real hoy), el costo semanal y anual en LLM sigue
siendo **$0**, porque no hay ningún llamado a un modelo de por medio.

### 2.2 — Comparación hipotética: ¿cuánto costaría si usara un LLM?

Para justificar la decisión de no usar un LLM (§1.3), vale la pena estimar cuánto
costaría la alternativa. Si cada corrida usara un LLM chico y barato para, por
ejemplo, redactar o interpretar la ficha (aun sin agregar ninguna capacidad real),
con los datos de cada ficha como contexto de entrada (CRM + noticias, unos ~2.000
tokens de entrada) y una salida de ~500 tokens:

| Modelo (precio de referencia, sep. 2026) | Input | Output | Costo estimado / corrida* |
|---|---|---|---|
| Claude Haiku 4.5 — $1,00 / MTok in, $5,00 / MTok out | 2.000 tok | 500 tok | ≈ $0,0045 |
| GPT-5.6 Luna (gama económica de OpenAI) — $0,20 / MTok in, $1,20 / MTok out | 2.000 tok | 500 tok | ≈ $0,0010 |

*Cálculo: `(tokens_input/1.000.000 × precio_input) + (tokens_output/1.000.000 × precio_output)`.
Fuentes: [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[OpenAI pricing](https://openai.com/api/pricing/) (precios vigentes a la fecha de
este documento — pueden cambiar).

Con el volumen actual del equipo (varias decenas de corridas por semana entre los 5
comerciales), eso da un costo hipotético de LLM de entre **~$0,20 y ~$0,90 por
semana** (~$10-45 por año) — no es un monto alto en términos absolutos, pero es
**estrictamente peor que $0** para resolver un problema que no necesita generación
de lenguaje: es una consulta estructurada con salida de formato fijo. Justifica la
decisión de §1.3: el "modelo más chico que hace bien la tarea" acá es, literalmente,
ningún modelo — código determinístico.

### 2.3 — Dónde sí tendría sentido un LLM (para referencia futura)

Si en una futura versión se quisiera, por ejemplo, redactar un resumen ejecutivo en
prosa combinando varias fichas, o interpretar pedidos en lenguaje natural ambiguo
("¿cómo viene todo con los clientes de Fran?"), ahí sí un LLM aportaría algo que el
código no puede: comprensión de lenguaje natural. Hoy no hace falta, porque el modo
de búsqueda (Cliente/Productor/Comercial) lo elige la persona explícitamente (§3.0
del contrato) — no hay ambigüedad de lenguaje que resolver.

## 3 · Gobierno y riesgo

### 3.1 — Sistemas que toca el agente

| Sistema | Acceso | Modo |
|---|---|---|
| Firestore (CRM real de la empresa) | Lectura — 7 colecciones (`clientes`, `agentesProductores`, `comerciales`, `companies`, `aperturas`, `reminders`, `pendientes`) | **Solo lectura, nunca escribe** (§4.4 del contrato) |
| Google News (RSS público) | Lectura pública, sin autenticación | Solo modo Cliente |

No toca correo, no toca ningún sistema de pagos o transferencias, no envía mensajes
a nadie, no dispara ninguna acción hacia afuera del propio proceso.

### 3.2 — Permisos y credenciales

Usa una cuenta de servicio de Firebase (`firebase-service-account.json`) con
permiso de **lectura** sobre el proyecto de Firestore. El archivo de credenciales:
- Nunca se sube al repo (excluido por `.gitignore`).
- Vive solo en la compu del usuario, donde también corre el agente (ver §1.6 —
  decisión de no desplegarlo en internet, justamente para no tener que replicar esta
  credencial en un servidor de terceros).

### 3.3 — Modos de falla y qué se revisa antes de confiar en la salida

| Falla posible | Qué pasa | Mitigación |
|---|---|---|
| 0 coincidencias | El agente lo dice explícitamente ("no se encontró...") — nunca inventa un resultado | Ver corrida de prueba "Inexistente" en `smoke_test.py` |
| 2+ coincidencias con el mismo nombre buscado | Se listan todas las fichas por separado — nunca se elige una | Restricción 4.3 del contrato |
| `companies.producer` ambiguo (§1.5) | Puede matchear el nombre equivocado si dos Agentes Productores o comerciales tienen nombres muy parecidos | Restricción declarada — una persona valida el cruce antes de comunicarlo (L2, §4.5) |
| Dato de calidad dudosa en el CRM (ver hallazgo §1.7.3) | El agente muestra el dato tal cual, sin "corregirlo" | Es información para que el equipo revise el CRM, no algo que el agente deba decidir |
| Firestore no disponible / credencial vencida | El agente devuelve un error explícito (`Config.validate()`), no un resultado vacío silencioso | Se ve en la interfaz web como mensaje de error |

### 3.4 — Qué se revisa antes de confiar en el resultado, y quién firma

Según el nivel de supervisión (L0-L4, vocabulario del curso, tabla completa en
`prompts/system_prompt.md` §4.5):

- **L0/L1** (corre solo, queda registrado): la búsqueda de texto y el armado de la
  ficha. No requiere revisión previa — es una consulta de lectura, reversible y sin
  efecto sobre el CRM.
- **L2** (una persona revisa antes de usarlo en una decisión): **todo dato de
  Calificación o línea de crédito antes de comunicárselo a un cliente**, y
  cualquier cruce vía `producer` (§1.5/§3.3) antes de asumir a qué Agente Productor
  o Comercial corresponde. Quien revisa es el mismo comercial o coordinador que usa
  la ficha antes de la reunión — no hay una segunda persona formal de por medio en
  v1, pero la restricción de "no comunicar sin revisar" queda declarada en el
  contrato (§4.5).
- **L3/L4**: no aplican — el agente no dispara ninguna acción hacia afuera ni
  modifica el CRM (es 100% de solo lectura, §4.4). Cualquier cambio real en el CRM
  (dar de alta una calificación, cerrar un pendiente) lo sigue haciendo una persona,
  a mano, en el sistema real — fuera del alcance de este agente.

### 3.5 — Quién firma

El responsable de la corrida (el comercial o coordinador que la ejecuta) es quien
firma el uso del dato en cualquier decisión o comunicación hacia un cliente — el
agente no reemplaza esa responsabilidad, solo ahorra el tiempo de juntar la
información de 5-8 fuentes distintas a mano.
