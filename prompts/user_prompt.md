# USER PROMPT — Agente de Productores v2 (pedido puntual, parametrizado)

Buscá **{MODO}** = "{NOMBRE}" y armá la ficha correspondiente, aplicando las fuentes, la
jerarquía de confiabilidad, el proceso de validación y el formato definidos en tu system
prompt.

`{MODO}` es uno de: `Cliente` / `Agente Productor` / `Comercial`.
`{NOMBRE}` es el texto de búsqueda (nombre completo o parcial).

Si hay más de una coincidencia, mostrá una ficha por cada una — no elijas por mí. Si algún
dato obligatorio no está disponible en su fuente, decilo explícitamente en el campo
correspondiente en lugar de omitirlo.

---

### Ejemplos de uso concreto

- Buscá Cliente = "Carafi" y armá la ficha correspondiente.
- Buscá Agente Productor = "Longobardi" y armá la ficha correspondiente.
- Buscá Comercial = "Nacho" y armá la ficha correspondiente.
