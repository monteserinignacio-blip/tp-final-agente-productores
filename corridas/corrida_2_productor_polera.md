# Corrida real 2 — Modo Agente Productor

- **Fecha:** 2026-09-08
- **Modo:** Agente Productor
- **Búsqueda (input real, tipeado por el usuario):** `polera`
- **Interfaz:** web (`http://127.0.0.1:5000`), corrida contra Firestore real (no datos de prueba)

## Salida tal cual la mostró el agente

```
AGENTE PRODUCTOR: POLERA

CUENTAS ASIGNADAS:
  • SANCHEZ, ELIAS DEMETRIO — Cuenta 3694
  • ELIAS SANCHEZ DEMETRIO — Cuenta 58095
  • MARTINEZ RIAL, MANUEL — Cuenta 3769
  • VARGAS DIANA NOEMI — Cuenta 59164
  • MARTINEZ RIAL, MANUEL — Cuenta 58063

CUENTAS EN CALIFICACIÓN:
  Sin empresas en proceso de calificación.

RECORDATORIOS:
  • Apertura de Fernando Courreges (AP: POLERA) — 2026-09-02
```

## Nota de supervisión (L1/L2, ver `prompts/system_prompt.md` §4.5)

Se ven 5 cuentas asignadas a este productor, dos de ellas con nombre casi idéntico
("SANCHEZ, ELIAS DEMETRIO" y "ELIAS SANCHEZ DEMETRIO") y dos más también repetidas
("MARTINEZ RIAL, MANUEL" aparece dos veces con números de cuenta distintos). El
agente no decide si es el mismo cliente cargado dos veces con formato de nombre
distinto o dos clientes distintos — eso lo tiene que revisar una persona (L2) antes
de usar el dato en una decisión; el agente solo reporta lo que hay en la fuente, tal
cual (Restricción 4.2).
