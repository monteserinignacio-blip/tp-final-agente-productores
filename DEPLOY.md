# Cómo publicar el agente en internet (paso a paso)

Esto tiene 2 partes: primero subir el código a un repositorio público en GitHub (lo
pide la consigna del TP), después desplegarlo en Render para que tenga un link de
internet real. Los dos pasos usan la MISMA carpeta `tp-final-agente-productores` que
ya tenés en tu escritorio.

⚠️ **El link va a mostrar datos reales de clientes.** Por eso el Paso 3 activa usuario
y contraseña — no lo saltees.

## Paso 1 — Crear el repo en GitHub

1. Andá a [github.com/new](https://github.com/new), nombralo por ejemplo
   `tp-final-agente-productores`, dejalo **público**, no tildes ningún checkbox
   (README/gitignore/licencia) — ya los tenemos en la carpeta.
2. En una terminal (PowerShell), parado en la carpeta del proyecto:
   ```
   cd Desktop\tp-final-agente-productores
   git init
   git add .
   git commit -m "Trabajo final: agente de productores v2"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/tp-final-agente-productores.git
   git push -u origin main
   ```
   (reemplazá `TU-USUARIO` por tu usuario de GitHub, el mismo que usaste para
   `agentes-productores`).
3. Verificá en el navegador que el repo público NO tenga `firebase-service-account.json`
   ni ningún `.env` con datos reales — el `.gitignore` ya los excluye, pero conviene
   mirarlo una vez.

Este es el link que subís a la actividad "Trabajo final" del campus.

## Paso 2 — Crear cuenta en Render (gratis, sin tarjeta)

1. Andá a [render.com](https://render.com) → "Get Started" → registrate con tu
   cuenta de GitHub (así Render ya puede ver tus repos, no hace falta conectar nada
   aparte).

## Paso 3 — Definir usuario y contraseña (antes de desplegar)

Elegí un usuario y una contraseña para proteger el link (se los vas a pasar a Render
como variables de entorno en el paso siguiente — no se escriben en ningún archivo del
repo). Ejemplo: usuario `chicho`, contraseña algo que no uses en otro lado.

## Paso 4 — Desplegar

1. En el dashboard de Render: **New +** → **Blueprint**.
2. Elegí el repo `tp-final-agente-productores` que acabás de subir. Render va a leer
   el archivo `render.yaml` que ya está en la carpeta y va a precargar casi toda la
   configuración solo.
3. Te va a pedir 2 variables que dejé en blanco a propósito (`sync: false` en el
   `render.yaml`): completá `BASIC_AUTH_USER` y `BASIC_AUTH_PASS` con lo que elegiste
   en el Paso 3.
4. Antes de darle "Deploy", andá a la pestaña **Environment** del servicio → sección
   **Secret Files** → **Add Secret File**:
   - Filename: `/etc/secrets/firebase-service-account.json`
   - Contents: pegá el contenido completo de tu `firebase-service-account.json` (abrilo
     con el Bloc de notas, copiá todo, pegalo ahí).
   Esto es lo que reemplaza tener el archivo en tu compu — Render lo guarda de forma
   segura, nunca queda en el repo público.
5. Deploy. La primera vez tarda unos minutos (instala dependencias). Cuando termina,
   Render te da un link tipo `https://agente-productores-v2.onrender.com`.

## Paso 5 — Probar

Abrí el link. El navegador te va a pedir usuario/contraseña (los del Paso 3) antes de
mostrar nada — si no te los pide, algo quedó mal configurado en el Paso 4.3, revisalo
antes de compartir el link con nadie.

**Nota sobre la velocidad:** el plan gratis de Render "duerme" el servicio después de
15 minutos sin uso. La primera búsqueda después de un rato de inactividad puede tardar
~30-60 segundos en responder (se está "despertando") — es normal, no está roto.

## Si algo falla

- **"Application Error" al abrir el link**: revisá los "Logs" del servicio en Render —
  casi siempre es un typo en las variables de entorno o el Secret File mal nombrado.
- **Pide usuario/contraseña pero no los acepta**: revisá que `BASIC_AUTH_USER` /
  `BASIC_AUTH_PASS` en Render coincidan exactamente (mayúsculas, espacios) con lo que
  estás tipeando.
- **Anduvo local pero no en Render**: lo más probable es el Secret File del paso 4.4 —
  confirmá que el path sea exactamente `/etc/secrets/firebase-service-account.json`.
