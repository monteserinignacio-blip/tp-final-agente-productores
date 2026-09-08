# Corrida real 4 — Modo Comercial (segundo caso)

- **Fecha:** 2026-09-08
- **Modo:** Comercial
- **Búsqueda (input real, tipeado por el usuario):** `Ceci`
- **Interfaz:** web (`http://127.0.0.1:5000`), corrida contra Firestore real (no datos de prueba)

## Salida tal cual la mostró el agente

```
COMERCIAL: CECI

AGENTES PRODUCTORES ASOCIADOS:
  CROVETTO, RECONDO, AREVALO MATIAS, LOBO, LANTIA CAPITAL, DEMARCHI, DINICOLA,
  CRESIUM, WORCAP, TARALLO, CASARINI, CABSA, MATTIOLI, INCAPTIAL, RUGGERI, MG ALFA,
  TSA

PENDIENTES (sin resolver):
  • Ver con Fran Carpetas completas Erca y Metal Noet

RECORDATORIOS (sin resolver):
  • Gestion Empresarial. Va a usar la linea Coop Agricola Misiones o liberamos la
    cuenta? (AP: Ceci Danese) — 2026-09-04
  • Seguimiento de contacto (AP: INCAPTIAL) — 2026-09-07
  • Ver como viene la calificacion y la respuesta de Ignacio Martinez (AP: CASARINI) — 2026-09-08
  • El 18/02 vence bonificacion del mantenimiento de la cuenta (AP: DINICOLA, FRANCO) — 2027-02-01
  • Seguimiento de contacto (AP: CRESIUM) — 2026-09-30
  • Cuando lo capital me avise que MACRO les aprobo la linea para ON (AP: INCAPTIAL) — 2026-09-08
  • Seguimiento de contacto (AP: RUGGERI) — 2026-09-07
  • Seguimiento de contacto (AP: Erica O'Connor) — 2026-09-28
  • Ver si me contacta para coordinar llamado (AP: MG ALFA) — 2026-09-10

APERTURAS (≠ Finalizada):
  • Le Parc S.A. — Productor: INCAPTIAL — Estado: ENVIADA

CALIFICACIONES:
  • Industrias ERCA S.A — (Diego Ruggeri) — Etapa: Prospecto
  • RCM SA — (Tarallo) — Etapa: Prospecto
  • Ricardo Venturino SA — (Mattioli) — Etapa: Calificada
  • Vepez SA — (Crovetto) — Etapa: Calificada
  • Riboldi SA — (Mattioli) — Etapa: Calificada
  • Moretti e Hijos SA — (Casarini) — Etapa: Calificada
  • Tropfen SA — (Emi Recondo) — Etapa: Calificada
  • Sembrar Agropecuaria SA — (Guille Casarini) — Etapa: Calificada
  • C Menendez y CIA SA — (LOBO) — Etapa: Prospecto
  • Agro de Souza SRL — (Demarchi) — Etapa: Calificada
  • Gualeguay Cereales SA — (Mattioli) — Etapa: Calificada
  • Grobocopatel Hnos SA — (Emi Recondo) — Etapa: Riesgos
  • Biogas Bella Ville — (TSA) — Etapa: Prospecto
  • DQD SAS — (LANTIA CAPITAL) — Etapa: Calificada
  • Multijacto SA — (Casarini) — Etapa: Riesgos
  • PLANTEL S.A. — (Crovetto) — Etapa: Riesgos
  • Arinco SA — (TSA) — Etapa: Prospecto
  • Colibri SA — (Guille Casarini) — Etapa: Calificada
```

## Nota de supervisión (L2, ver `prompts/system_prompt.md` §4.5)

Se agrega esta segunda corrida de modo Comercial (además de "Nacho") porque trae
una cartera de Calificaciones mucho más grande (18 empresas en distintas etapas) —
sirve para verificar que el agrupamiento por etapa y el cruce `producer` ↔ nombre de
Agente Productor (restricción declarada en `prompts/system_prompt.md` §4.2 y en
DECISIONES.md) funciona también con volumen real, no solo con el caso chico de
prueba. Antes de usar cualquiera de estas calificaciones en una conversación con un
cliente, una persona la valida contra el CRM (L2) — el agente no decide prioridad ni
urgencia entre las 18 empresas.
