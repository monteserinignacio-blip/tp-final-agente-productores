# Corrida real 1 — Modo Cliente

- **Fecha:** 2026-09-08
- **Modo:** Cliente
- **Búsqueda (input real, tipeado por el usuario):** `autos sustentables del sur`
- **Interfaz:** web (`http://127.0.0.1:5000`), corrida contra Firestore real (no datos de prueba)

## Salida tal cual la mostró el agente

```
AUTOS SUSTENTABLES DEL SUR SA

⚠ Se encontraron 5 noticia(s) públicas — revisar antes de la reunión.

CUENTAS:
  • Cuenta 58253 — Agente Productor: ARIEL ROMERO — Comercial: Sergio
  • Cuenta 3812 — Agente Productor: ARIEL ROMERO — Comercial: Fran

CALIFICACIÓN:
  Sin proceso de calificación.

NOTICIAS PÚBLICAS:
  • Geely reclama una "revisión" del cupo para poder importar modelos electrificados
    — El Economista - Últimas noticias económicas y financieras — Thu, 04 Dec 2025 08:00:00 GMT
  • Algunas marcas podrían bajarse del cupo de autos híbridos y eléctricos por una
    reglamentación clave que sigue demorada — infobae.com — Wed, 14 May 2025 07:00:00 GMT
  • El Gobierno todavía no resolvió los reclamos de los importadores de autos híbridos
    y eléctricos — infobae.com — Sat, 26 Apr 2025 07:00:00 GMT
  • Estos son los autos electrificados autorizados a llegar a la Argentina sin
    impuestos — El Economista - Últimas noticias económicas y financieras — Mon, 28 Jul 2025 07:00:00 GMT
  • Cuántos autos híbridos y eléctricos de cada modelo se importarán en 2025 con el
    cupo sin arancel — infobae.com — Tue, 29 Jul 2025 07:00:00 GMT
```

## Nota de supervisión (L2, ver `prompts/system_prompt.md` §4.5)

Este cliente tiene 2 cuentas activas y noticias públicas recientes sobre el sector
(cupos de importación de autos híbridos/eléctricos) — antes de una reunión, un
comercial debería revisar esas noticias para entender si afectan la situación del
cliente. El agente no interpreta la noticia ni decide si es relevante: solo la trae
a la vista, tal como pide el contrato (Restricción 4.2, anti-alucinación).
