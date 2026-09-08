# Corrida real 3 — Modo Comercial

- **Fecha:** 2026-09-08
- **Modo:** Comercial
- **Búsqueda (input real, tipeado por el usuario):** `Nacho`
- **Interfaz:** web (`http://127.0.0.1:5000`), corrida contra Firestore real (no datos de prueba)

## Salida tal cual la mostró el agente

```
COMERCIAL: NACHO

AGENTES PRODUCTORES ASOCIADOS:
  GONZALO GAVIÑA ALVARADO, BoPartners, Santiago Bottegoni, Fran Radaelli, DW, CARAFI,
  MORAD, FADVANCE, Ceci Danese, PEDRO CARAFI, LONGOBARDI, SAGUIER, STELLUTO,
  Options Securities

PENDIENTES (sin resolver):
  • Back to back MCM(2)
  • [PROYECTO: ETN's] Apertura de Cuenta en Fobl - V Badel [Ref: fffe55af-c0ee-48f0-947e-4b693e99469a]
  • [PROYECTO: ETN's] Firma Documentos Carlos Walton [Ref: 6ccfafa0-8e6e-4c4e-baf2-3e0a7bec31d6]
  • [PROYECTO: ETN's] Apertura Cuenta Mariva Bursatil 2 en MCM [Ref: fc0de797-8fc6-444a-adc8-a5109922c8b1]
  • Entender bien cuando se cobra el 0.5 y cuando cuenta como exchange. (ej semi liquido y liquido)
  • [PROYECTO: ETN's] Revision documentos en los legales. [Ref: 4bd3264f-5618-4fc0-b863-87a6fb02eac2]
  • [PROYECTO: ETN's] Cambio Boleto para que diga: Boleto [Ref: b3ce6821-d036-483b-af86-cb3da2eb2a21]

RECORDATORIOS (sin resolver):
  • Pasar propuesta cuenta 5MM brokerage Santander (equity + t bills) (AP: Options Securities) — 2026-09-08
  • Quien paga los Upfronts? al cliente no se lo cobra. Cobro USD 25 fijos, venian
    cobrando Service Charge USD 2 (aumentamos 1000%? hace ruido) (AP: ANDES) — 2026-09-08

APERTURAS (≠ Finalizada):
  • ARX Arcillex — Productor: Options Securities — Estado: REVISION
  • Luis Mario Sikorski — Productor: CARAFI — Estado: PLA
  • Stelutto — Productor: STELLUTO — Estado: REVISION
  • Cofaloza LTD — Productor: Fran Radaelli — Estado: ENVIADA
  • Pondrey SA — Productor: Santiago Bottegoni — Estado: REVISION
  • Jorge Podesta — Productor: LONGOBARDI — Estado: REVISION

CALIFICACIONES:
  • Tecnolab SA — (LVA) — Etapa: Calificada
```

## Nota de supervisión (L2, ver `prompts/system_prompt.md` §4.5)

Esta corrida es la que valida en datos reales el ajuste pedido durante el TP: antes,
los pendientes y recordatorios ya marcados como "hecho" se mostraban igual (con la
etiqueta "(hecho)"); ahora el agente los filtra y solo deja los que siguen sin
resolver — se ve reflejado en que todos los ítems listados están efectivamente
abiertos. Antes de comunicarle algo de "Pendientes" o "Recordatorios" a un cliente o
de decidir sobre una apertura, una persona tiene que revisarlo igual (L2) — el agente
no prioriza ni interpreta la urgencia de cada ítem, solo filtra por `completado`.
