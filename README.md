# Agente de Productores v2 — buscador unificado (Cliente / Agente Productor / Comercial)

Trabajo Final — materia *Programación de y con Agentes de IA* (MBA UCEMA), prof.
Alfredo B. Roisenzvit. Autor: Ignacio "Chicho" Monteserin.

Este repo es la versión completa y "seria" de un agente que ya existía
([Entrega 1](https://github.com/monteserinignacio-blip/agentes-productores) de la
misma materia): antes de una reunión con un cliente, con un agente productor, o
antes de una reunión interna de equipo, arma en segundos una ficha con toda la
información dispersa en el CRM real (Firestore) y en noticias públicas — sin que
nadie tenga que ir a buscarla a mano en 5-8 lugares distintos.

## Qué hace

Tres modos de búsqueda, elegidos explícitamente por quien usa el agente (nunca
adivinados por texto):

- **Cliente** → cuentas activas, Agente Productor y Comercial asignado,
  calificación crediticia (etapa + documentación faltante o línea calificada),
  noticias públicas recientes.
- **Agente Productor** → cuentas asignadas, cuentas en proceso de calificación,
  recordatorios pendientes.
- **Comercial** (para una reunión interna de equipo) → Agentes Productores a
  cargo, pendientes y recordatorios sin resolver, aperturas en curso (≠
  Finalizada), calificaciones de su cartera.

Es **100% código determinístico — no llama a ningún LLM en tiempo de ejecución**.
Es una decisión de diseño explícita, no una limitación: ver `DECISIONES.md` §1.3 y
§2 (análisis económico) para el porqué.

## Estructura del repo

```
prompts/
  system_prompt.md   # el contrato completo (Rol/Contexto/Tarea/Restricciones/Formato/Ejemplos)
  user_prompt.md      # plantilla de la consulta que dispara cada búsqueda
corridas/
  corrida_1_...md      # 4 corridas reales (una de cada modo, más un segundo caso de Comercial)
  corrida_2_...md
  corrida_3_...md
  corrida_4_...md
src/
  agent.py             # la lógica de las 3 búsquedas (el "cerebro" del agente)
  webapp.py            # interfaz web (Flask) — corre local en http://127.0.0.1:5000
  cli.py               # interfaz de terminal, alternativa a la web
  connectors/          # Firestore y Google News
  templates/index.html # la interfaz visual (3 pestañas)
smoke_test.py          # prueba de humo con datos inventados (no toca Firestore real)
DECISIONES.md           # historia de iteración + análisis económico + gobierno y riesgo
render.yaml, DEPLOY.md  # despliegue público — evaluado y descartado, ver DECISIONES.md §1.6
```

## Cómo correrlo

Requiere Python 3 instalado y un archivo de credenciales de Firebase
(`firebase-service-account.json`, no incluido en el repo por seguridad — ver
`.gitignore`) en la raíz del proyecto.

```
pip install -r requirements.txt
python smoke_test.py      # prueba con datos inventados, no toca Firestore real
python run_web.py         # levanta la interfaz web en http://127.0.0.1:5000
```

Corre **local, no en internet** — decisión deliberada, ver `DECISIONES.md` §1.6.

## Documentación completa

- **`prompts/system_prompt.md`** — el contrato completo: rol, contexto, tarea
  detallada por modo, restricciones (jerarquía de fuentes, anti-alucinación, manejo
  de ambigüedad, alcance de solo lectura, niveles de supervisión L0-L4), formato de
  salida fijo, y ejemplos correcto/incorrecto.
- **`corridas/`** — 4 corridas reales contra el CRM real (Cliente, Agente
  Productor, y 2 casos de Comercial), con nota de qué debería revisar una persona
  antes de confiar en cada dato.
- **`DECISIONES.md`** — la historia honesta de cómo se construyó esto: qué se
  asumió mal al principio, qué se corrigió al confirmar el esquema real de
  Firestore con el usuario, la decisión de no usar un LLM en runtime (con el
  análisis de costo que la justifica), la decisión de correr local en vez de
  desplegarlo en internet, y la sección de gobierno y riesgo (qué sistemas toca,
  qué puede fallar, qué revisa una persona antes de confiar en el resultado).
