"""
Orquestador — Agente de Productores v2 (buscador unificado: Cliente /
Agente Productor / Comercial), 100% código, sin llamadas a un LLM en
tiempo de ejecución (ver DECISIONES.md, Análisis económico).

Esquema real de Firestore (confirmado por la app de Google AI Studio que
alimenta este CRM — ver DECISIONES.md para la fuente completa):

- `comerciales`      id, nombre, email, activo, fechaAlta
- `agentesProductores` id, nombre, comercialId, provincia, ciudad, email,
  telefono, fechaUltimoContacto, activo, tipoStatus
- `clientes`         id, nombre, numeroCuenta, agenteProductorId,
  comercialId, activo, observaciones
  (si comercialId no está seteado, se hereda el del Agente Productor)
- `companies`        (= pestaña "Calificaciones") id, businessName,
  groupName, producer (texto libre), currentStage
  ('Prospecto'|'Pre Riesgos'|'Riesgos'|'Calificada'), checklist (array de
  {id, name, isPresent, updatedAt}), qualifiedData (map)
- `aperturas`        id, cliente (texto), agenteProductorId, comercialId,
  entidades (array), estado ('ENVIADA'|'DOCUMENTACION FALTANTE'|
  'REVISION'|'PLA'|'FINALIZADA'), fechaSolicitud, fechaApertura,
  accountNumbers (map)
- `reminders`        id, comercialId, agenteProductorId, clienteId, fecha,
  mensaje, completado, hora
- `pendientes`       id, comercialId, agenteProductorId, descripcion,
  completado, createdAt, projectId, milestoneId, taskId

Punto de diseño importante — `companies.producer` (restricción declarada,
ver prompts/system_prompt.md §4.2 y DECISIONES.md): la documentación de la
app dice que `producer` se cruza contra `comerciales.nombre`, pero los
datos reales (captura de la pestaña Calificaciones, columna "Prod.")
muestran nombres con forma de Agente Productor ("Diego Ruggeri", "Marial
Arevalo"), no los 5 comerciales conocidos. Como es texto libre y las dos
fuentes se contradicen, este agente NO asume una interpretación: matchea
`producer` contra el nombre del Agente Productor buscado (modo Productor)
o contra el nombre del comercial + los nombres de sus Agentes Productores
a cargo (modo Comercial) — lo que matchee, sin preferencia. Ver
DECISIONES.md para el detalle de esta decisión.
"""
from .config import Config
from .connectors import firestore_crm, news

ETAPAS_CALIFICACION = ["Prospecto", "Pre Riesgos", "Riesgos", "Calificada"]
ESTADOS_APERTURA = ["ENVIADA", "DOCUMENTACION FALTANTE", "REVISION", "PLA", "FINALIZADA"]

QUALIFIED_DATA_LABELS = {
    "multi": "Cupo Multilateral / Línea total",
    "cpd": "Cupo Cheques de Pago Diferido",
    "prestamoON": "Cupo Préstamos / Obligaciones Negociables",
    "ctaBM": "Cuenta Banco Macro",
    "ctaMB": "Cuenta Mercado Abierto",
    "vencimiento": "Vencimiento de la calificación",
    "vencimientoEECC": "Vencimiento de balances/EECC",
    "diasPVto": "Días restantes al vencimiento",
    "currency": "Moneda",
}


def _contiene(texto, query: str) -> bool:
    return bool(query) and query.lower() in str(texto or "").lower()


def _match_bidireccional(a, b) -> bool:
    a, b = str(a or "").strip().lower(), str(b or "").strip().lower()
    if not a or not b:
        return False
    return a in b or b in a


def _index_por_id(docs: list[dict]) -> dict:
    return {d.get("id"): d for d in docs if d.get("id")}


# --- Calificaciones (companies) ---

def _resumen_calificacion(c: dict) -> dict:
    etapa = c.get("currentStage", "")
    checklist = c.get("checklist", []) or []
    if etapa in ("Prospecto", "Pre Riesgos", "Riesgos"):
        total = len(checklist)
        presentes = sum(1 for item in checklist if item.get("isPresent"))
        faltantes = [item.get("name", "") for item in checklist if not item.get("isPresent")]
        if faltantes:
            detalle = f"Documentación: {presentes}/{total}. Faltante: " + ", ".join(faltantes)
        else:
            detalle = f"Documentación completa ({presentes}/{total})." if total else "Sin checklist cargado."
    elif etapa == "Calificada":
        qd = c.get("qualifiedData", {}) or {}
        if qd:
            partes = []
            moneda = qd.get("currency", "")
            for campo, label in QUALIFIED_DATA_LABELS.items():
                if campo in ("currency",) or campo not in qd:
                    continue
                valor = qd[campo]
                if campo in ("multi", "cpd", "prestamoON") and moneda:
                    partes.append(f"{label}: {valor} {moneda}")
                else:
                    partes.append(f"{label}: {valor}")
            detalle = "; ".join(partes) if partes else "Calificada, sin detalle de línea cargado."
        else:
            detalle = "Calificada, sin detalle de línea cargado."
    else:
        detalle = f"Etapa no reconocida: '{etapa}' — revisar dato en origen (no es una de las 4 esperadas)."
    return {
        "cliente": c.get("businessName", ""),
        "grupo": c.get("groupName", ""),
        "etapa": etapa,
        "detalle": detalle,
        "producer": c.get("producer", ""),
    }


# --- Modo A: Cliente ---

def buscar_por_cliente(nombre_query: str) -> dict:
    clientes = firestore_crm.fetch_collection("clientes")
    coincidencias = [c for c in clientes if _contiene(c.get("nombre"), nombre_query)]

    if not coincidencias:
        return {"modo": "cliente", "query": nombre_query, "encontrado": False, "resultados": []}

    aps = firestore_crm.fetch_collection("agentesProductores")
    comerciales = firestore_crm.fetch_collection("comerciales")
    companies = firestore_crm.fetch_collection("companies")
    ap_by_id = _index_por_id(aps)
    comercial_by_id = _index_por_id(comerciales)

    # Agrupar por nombre exacto (normalizado): mismo nombre = mismo cliente
    # con varias cuentas; nombres distintos = fichas separadas (ambigüedad).
    grupos: dict[str, list[dict]] = {}
    for c in coincidencias:
        clave = str(c.get("nombre", "")).strip().lower()
        grupos.setdefault(clave, []).append(c)

    resultados = []
    for clave, docs in grupos.items():
        nombre_cliente = docs[0].get("nombre", "")

        cuentas = []
        for d in docs:
            ap = ap_by_id.get(d.get("agenteProductorId"))
            comercial_id = d.get("comercialId") or (ap.get("comercialId") if ap else None)
            comercial = comercial_by_id.get(comercial_id)
            cuentas.append({
                "numeroCuenta": d.get("numeroCuenta", "") or "— (sin número asignado)",
                "agente_productor": ap.get("nombre", "") if ap else "— (sin asignar)",
                "comercial": comercial.get("nombre", "") if comercial else "— (sin asignar)",
            })

        calificaciones = [
            _resumen_calificacion(c) for c in companies
            if _match_bidireccional(c.get("businessName"), nombre_cliente)
        ]

        noticias = news.search_news(nombre_cliente)

        resultados.append({
            "cliente": nombre_cliente,
            "cuentas": cuentas,
            "calificaciones": calificaciones,
            "noticias": noticias,
        })

    return {"modo": "cliente", "query": nombre_query, "encontrado": True, "resultados": resultados}


# --- Modo B: Agente Productor ---

def buscar_por_productor(nombre_query: str) -> dict:
    aps = firestore_crm.fetch_collection("agentesProductores")
    coincidencias = [p for p in aps if _contiene(p.get("nombre"), nombre_query)]

    if not coincidencias:
        return {"modo": "productor", "query": nombre_query, "encontrado": False, "resultados": []}

    clientes = firestore_crm.fetch_collection("clientes")
    companies = firestore_crm.fetch_collection("companies")
    reminders = firestore_crm.fetch_collection("reminders")

    resultados = []
    for p in coincidencias:
        pid = p.get("id")
        pnombre = p.get("nombre", "")

        cuentas_asignadas = [
            {"cliente": c.get("nombre", ""), "numeroCuenta": c.get("numeroCuenta", "") or "—"}
            for c in clientes if c.get("agenteProductorId") == pid
        ]

        en_calificacion = [
            {"cliente": c.get("businessName", ""), "etapa": c.get("currentStage", "")}
            for c in companies if _match_bidireccional(c.get("producer"), pnombre)
        ]

        recordatorios = [
            {"descripcion": r.get("mensaje", ""), "fecha": r.get("fecha", "")}
            for r in reminders if r.get("agenteProductorId") == pid and not r.get("completado")
        ]

        resultados.append({
            "productor": {"nombre": pnombre, "id": pid},
            "cuentas_asignadas": cuentas_asignadas,
            "en_calificacion": en_calificacion,
            "recordatorios": recordatorios,
        })

    return {"modo": "productor", "query": nombre_query, "encontrado": True, "resultados": resultados}


# --- Modo C: Comercial ---

def buscar_por_comercial(nombre_query: str) -> dict:
    comerciales = firestore_crm.fetch_collection("comerciales")
    coincidencias = [c for c in comerciales if _contiene(c.get("nombre"), nombre_query)]

    if not coincidencias:
        return {"modo": "comercial", "query": nombre_query, "encontrado": False, "resultados": []}

    aps = firestore_crm.fetch_collection("agentesProductores")
    pendientes = firestore_crm.fetch_collection("pendientes")
    reminders = firestore_crm.fetch_collection("reminders")
    aperturas = firestore_crm.fetch_collection("aperturas")
    companies = firestore_crm.fetch_collection("companies")
    ap_by_id = _index_por_id(aps)

    resultados = []
    for com in coincidencias:
        cid = com.get("id")
        cnombre = com.get("nombre", "")

        aps_del_comercial = [ap for ap in aps if ap.get("comercialId") == cid]
        aps_nombres = [ap.get("nombre", "") for ap in aps_del_comercial]

        # Solo lo que sigue pendiente — lo ya marcado como hecho no se muestra
        # (decisión tomada tras probar con datos reales, ver DECISIONES.md).
        pendientes_com = [
            {"descripcion": pe.get("descripcion", "")}
            for pe in pendientes if pe.get("comercialId") == cid and not pe.get("completado")
        ]
        recordatorios_com = [
            {"mensaje": r.get("mensaje", ""), "fecha": r.get("fecha", "")}
            for r in reminders if r.get("comercialId") == cid and not r.get("completado")
        ]

        aperturas_com = []
        for a in aperturas:
            if a.get("comercialId") != cid:
                continue
            if a.get("estado") == "FINALIZADA":
                continue
            ap = ap_by_id.get(a.get("agenteProductorId"))
            aperturas_com.append({
                "cliente": a.get("cliente", ""),
                "agente_productor": ap.get("nombre", "") if ap else "—",
                "estado": a.get("estado", ""),
            })

        # producer (texto libre) matchea contra el nombre del comercial O
        # contra cualquiera de sus Agentes Productores — ver nota de diseño
        # al principio del archivo y en DECISIONES.md.
        textos_propios = [cnombre] + aps_nombres
        calificaciones_com = [
            {
                "cliente": c.get("businessName", ""),
                "agente_productor_o_texto": c.get("producer", ""),
                "etapa": c.get("currentStage", ""),
            }
            for c in companies
            if any(_match_bidireccional(c.get("producer"), t) for t in textos_propios)
        ]

        resultados.append({
            "comercial": {"nombre": cnombre, "id": cid},
            "agentes_productores": aps_nombres,
            "pendientes": pendientes_com,
            "recordatorios": recordatorios_com,
            "aperturas": aperturas_com,
            "calificaciones": calificaciones_com,
        })

    return {"modo": "comercial", "query": nombre_query, "encontrado": True, "resultados": resultados}


# --- Dispatcher + formato en texto plano ---

MODOS = {"cliente": buscar_por_cliente, "productor": buscar_por_productor, "comercial": buscar_por_comercial}


def buscar(modo: str, nombre_query: str) -> dict:
    if modo not in MODOS:
        raise ValueError(f"Modo inválido: '{modo}'. Debe ser uno de: {', '.join(MODOS)}")
    return MODOS[modo](nombre_query)


def _texto_cliente(datos: dict) -> str:
    if not datos["encontrado"]:
        return f"No se encontró ningún cliente que coincida con '{datos['query']}'."
    bloques = []
    for r in datos["resultados"]:
        partes = [f"CLIENTE: {r['cliente']}"]
        partes.append("\nCUENTAS:")
        for c in r["cuentas"]:
            partes.append(f"  • Cuenta {c['numeroCuenta']} — Productor: {c['agente_productor']} — Comercial: {c['comercial']}")
        partes.append("\nCALIFICACIÓN:")
        if r["calificaciones"]:
            for c in r["calificaciones"]:
                partes.append(f"  • Etapa: {c['etapa']}. {c['detalle']}")
        else:
            partes.append("  Sin proceso de calificación.")
        if r["noticias"]:
            partes.append(f"\n⚠ NOTICIAS: {len(r['noticias'])} noticia(s) pública(s).")
            for n in r["noticias"]:
                partes.append(f"  • {n['title']} ({n['source']}, {n['date']})")
        else:
            partes.append("\nNoticias públicas: sin noticias.")
        bloques.append("\n".join(partes))
    return ("\n\n" + "-" * 60 + "\n\n").join(bloques)


def _texto_productor(datos: dict) -> str:
    if not datos["encontrado"]:
        return f"No se encontró ningún agente productor que coincida con '{datos['query']}'."
    bloques = []
    for r in datos["resultados"]:
        partes = [f"AGENTE PRODUCTOR: {r['productor']['nombre']}"]
        partes.append("\nCUENTAS ASIGNADAS:")
        if r["cuentas_asignadas"]:
            for c in r["cuentas_asignadas"]:
                partes.append(f"  • {c['cliente']} — Cuenta {c['numeroCuenta']}")
        else:
            partes.append("  Sin cuentas asignadas.")
        partes.append("\nCUENTAS EN CALIFICACIÓN:")
        if r["en_calificacion"]:
            for c in r["en_calificacion"]:
                partes.append(f"  • {c['cliente']} — Etapa: {c['etapa']}")
        else:
            partes.append("  Sin empresas en proceso de calificación.")
        partes.append("\nRECORDATORIOS:")
        if r["recordatorios"]:
            for rec in r["recordatorios"]:
                partes.append(f"  • {rec['descripcion']} — {rec['fecha']}")
        else:
            partes.append("  Sin recordatorios pendientes.")
        bloques.append("\n".join(partes))
    return ("\n\n" + "-" * 60 + "\n\n").join(bloques)


def _texto_comercial(datos: dict) -> str:
    if not datos["encontrado"]:
        return f"No se encontró ningún comercial que coincida con '{datos['query']}'."
    bloques = []
    for r in datos["resultados"]:
        partes = [f"COMERCIAL: {r['comercial']['nombre']}"]
        partes.append("\nAGENTES PRODUCTORES ASOCIADOS:")
        partes.append("  " + ", ".join(r["agentes_productores"]) if r["agentes_productores"] else "  Sin agentes productores asignados.")
        partes.append("\nPENDIENTES (sin resolver):")
        if r["pendientes"]:
            for pe in r["pendientes"]:
                partes.append(f"  • {pe['descripcion']}")
        else:
            partes.append("  Sin pendientes.")
        partes.append("\nRECORDATORIOS (sin resolver):")
        if r["recordatorios"]:
            for rec in r["recordatorios"]:
                partes.append(f"  • {rec['mensaje']} — {rec['fecha']}")
        else:
            partes.append("  Sin recordatorios.")
        partes.append("\nAPERTURAS (≠ Finalizada):")
        if r["aperturas"]:
            for a in r["aperturas"]:
                partes.append(f"  • {a['cliente']} — Productor: {a['agente_productor']} — Estado: {a['estado']}")
        else:
            partes.append("  Sin aperturas en curso.")
        partes.append("\nCALIFICACIONES:")
        if r["calificaciones"]:
            for c in r["calificaciones"]:
                partes.append(f"  • {c['cliente']} — ({c['agente_productor_o_texto']}) — Etapa: {c['etapa']}")
        else:
            partes.append("  Sin empresas en proceso de calificación.")
        bloques.append("\n".join(partes))
    return ("\n\n" + "-" * 60 + "\n\n").join(bloques)


TEXTO = {"cliente": _texto_cliente, "productor": _texto_productor, "comercial": _texto_comercial}


def buscar_texto(modo: str, nombre_query: str) -> str:
    return TEXTO[modo](buscar(modo, nombre_query))
