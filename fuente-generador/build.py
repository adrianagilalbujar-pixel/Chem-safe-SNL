# -*- coding: utf-8 -*-
"""Genera el sitio estático CHEM SAFE (index, fichas y etiquetas). Versión 2 (rediseño).

Uso, desde la raíz del repositorio:
    python fuente-generador/build.py .
"""
import os, re, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import *

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

SECTIONS = [
    ("s1", "Identificación"),
    ("s2", "Identificación de peligros"),
    ("s3", "Composición"),
    ("s4", "Primeros auxilios"),
    ("s5", "Manipulación y almacenamiento"),
    ("s6", "Equipos de protección personal"),
    ("s7", "Propiedades físicas y químicas"),
    ("s8", "Estabilidad, reactividad y compatibilidad"),
    ("s9", "Emergencias, derrames y eliminación"),
]

# Pictogramas GHS: id -> (código, nombre)
PICTO = {
    "ghs02": ("GHS02", "Inflamable"),
    "ghs03": ("GHS03", "Comburente"),
    "ghs05": ("GHS05", "Corrosión"),
    "ghs06": ("GHS06", "Toxicidad aguda"),
    "ghs07": ("GHS07", "Nocivo / irritante"),
    "ghs08": ("GHS08", "Peligro para la salud"),
    "ghs09": ("GHS09", "Peligro para el medio ambiente"),
}

# Filtros de la portada: id -> (texto del botón, función de pertenencia)
FILTERS = [
    ("all", "Todas"),
    ("ghs05", "Corrosivas"),
    ("ghs07", "Nocivas / irritantes"),
    ("none", "Sin clasificación"),
]

def svg(body, sw="1.8"):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')

ICONS = {
    "i1": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M14 10h4M14 14h4M6 16c.8-1.4 2-2 3-2s2.2.6 3 2"/>',
    "i2": '<path d="M12 3 2.5 20h19z"/><path d="M12 10v4.5M12 17.2v.1"/>',
    "i3": '<path d="M9 3h6M10 3v6l-5.5 9.2A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-2.8L14 9V3"/><path d="M7.5 15h9"/>',
    "i4": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M12 7.5v9M7.5 12h9"/>',
    "i5": '<path d="M3 8l9-5 9 5v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M8 20v-7h8v7M8 16.5h8"/>',
    "i6": '<path d="M3 11a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v3a4 4 0 0 1-4 4h-1.5a3 3 0 0 1-2.5-1.5 2 2 0 0 0-3 0A3 3 0 0 1 8.5 18H7a4 4 0 0 1-4-4z"/><path d="M3 11l1.5-5.5M21 11l-1.5-5.5"/>',
    "i7": '<path d="M10 14.8V5a2 2 0 0 1 4 0v9.8a4 4 0 1 1-4 0z"/><path d="M12 9v7"/>',
    "i8": '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
    "i9": '<path d="M12 3s5 4.4 5 9.2A5 5 0 0 1 7 12.2C7 9 9 7.5 9 7.5s.5 2 2 2c0 0 1.5-2 1-6.5z"/>',
    "ref": '<path d="M5 4h11l3 3v13H5z"/><path d="M9 10h6M9 14h6M9 18h3"/>',
    "flask": '<path d="M9 3h6M10 3v6l-5.5 9.2A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-2.8L14 9V3"/><path d="M12 12.5l2 1v2.5l-2 1-2-1v-2.5z"/>',
    "warn": '<path d="M12 3 2.5 20h19z"/><path d="M12 10v4.5M12 17.2v.1"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.1"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "print": '<path d="M7 9V3h10v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
    "tag": '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="8" cy="8" r="1.5"/>',
    "qr": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v1M14 20h1M17 17h4v4h-4"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "tap": '<path d="M9 11V5a2 2 0 0 1 4 0v5l4.5.9a2 2 0 0 1 1.6 2.3L18 19a3 3 0 0 1-3 2h-3.6a3 3 0 0 1-2.4-1.2L5.5 15a1.7 1.7 0 0 1 2.6-2.2L9 14"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
}

def icon(k, sw="1.8"):
    return svg(ICONS[k], sw)

def cites(refs):
    if not refs:
        return ""
    out = "".join(f'<a href="#ref{n.strip()}">[{n.strip()}]</a>' for n in refs.split(","))
    return f' <sup class="cite">{out}</sup>'

def fmt(t):
    """Convierte marcas [n] en citas enlazadas."""
    return re.sub(r"\s?\[(\d+(?:\s*,\s*\d+)*)\]", lambda m: cites(m.group(1)), t)

def src(refs, extra=""):
    return f'<p class="src">Fuentes:{cites(refs)}{(" " + extra) if extra else ""}</p>'

def strip_tags(t):
    return re.sub(r"<[^>]+>", "", t)

STATE = {"ok": ("✓", "Compatible documentado"), "bad": ("✕", "Incompatible documentado"), "nd": ("?", "Información insuficiente o no determinada")}

THEME_INIT = ('<script>document.documentElement.classList.add("js");try{var t=localStorage.getItem("chemsafe-theme");if(t==="dark"||t==="light")'
              'document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>')

def head(title, depth, extra_css=None, accent=None, accent_soft=None, desc=None):
    pre = "../" * depth
    style = f' style="--accent:{accent};--accent-soft:{accent_soft}"' if accent else ""
    links = f'<link rel="stylesheet" href="{pre}assets/css/styles.css">'
    if extra_css:
        links += f'\n<link rel="stylesheet" href="{pre}assets/css/{extra_css}">'
    desc = desc or "CHEM SAFE: fichas educativas de seguridad química consultables mediante código QR."
    return (f'<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{html.escape(title)}</title>\n'
            f'<meta name="description" content="{html.escape(desc)}">\n'
            f'<meta name="theme-color" content="#0f1f1b">\n'
            f'<link rel="icon" href="{pre}assets/img/favicon.svg" type="image/svg+xml">\n{links}\n{THEME_INIT}\n</head>\n<body{style}>\n')

def topbar(depth, current=""):
    pre = "../" * depth
    def nav(href, label, key, opt=False):
        cur = ' aria-current="page"' if key == current else ""
        cls = ' class="opt"' if opt else ""
        return f'<a href="{pre}{href}"{cur}{cls}>{label}</a>'
    return (f'<header class="topbar"><div class="wrap">'
            f'<a class="school" href="{pre}index.html" title="Colegio San Luis Maristas"><img src="{pre}assets/img/logo-maristas.png" alt="Logo del Colegio San Luis Maristas" width="38" height="38"></a>'
            f'<a class="brand" href="{pre}index.html"><span class="mark">{icon("flask", "2")}</span><span>CHEM SAFE<small>Colegio San Luis Maristas</small></span></a>'
            f'<nav aria-label="Principal">{nav("index.html", "Inicio", "home")}{nav("index.html#sustancias", "Sustancias", "subs", True)}'
            f'{nav("index.html#compatibilidad", "Compatibilidad", "x", True)}{nav("etiquetas.html", "Etiquetas", "labels")}</nav>'
            f'<button class="theme-btn" type="button" data-theme-toggle aria-label="Cambiar entre modo claro y oscuro">'
            f'<span class="moon">{icon("moon")}</span><span class="sun">{icon("sun")}</span></button>'
            f'</div></header>')

def footer(depth):
    pre = "../" * depth
    return ('<footer class="site"><div class="wrap">'
            f'<div class="fbrand"><img src="{pre}assets/img/logo-maristas.png" alt="" width="28" height="28">CHEM SAFE</div>'
            '<p>Colegio San Luis Maristas · Prototipo escolar con fines educativos. Las fichas <strong>no reemplazan la Ficha de Datos de Seguridad (FDS) '
            'oficial</strong> del producto específico que tienes en el laboratorio. Ante una emergencia, avisa al docente y llama a los servicios de emergencia.</p>'
            f'<p>Versión {VERSION} · Actualizado el {UPDATED}</p>'
            '</div></footer>')

def picto_img(p, pre="../", size=None):
    code, name = PICTO[p]
    wh = f' width="{size}" height="{size}"' if size else ""
    return f'<img src="{pre}assets/img/{p}.svg" alt="Pictograma {code}: {name}"{wh}>'

def picto_figs(s):
    return "".join(f'<figure class="pict">{picto_img(p)}<figcaption>{PICTO[p][0]}<br>{PICTO[p][1]}</figcaption></figure>' for p in s["pictos"])

def hazard_icon(cls):
    if cls == "none":
        return svg('<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>', "2.2")
    return svg(ICONS["warn"], "2.2")

def sec(n, inner, featured=False):
    sid, title = SECTIONS[n - 1]
    cls = "sec featured reveal" if featured else "sec reveal"
    return (f'<section class="{cls}" id="{sid}" aria-labelledby="{sid}-h"><h2 id="{sid}-h"><span class="num">{icon(f"i{n}")}</span>'
            f'<span class="ttl"><small>Sección {n}</small>{title}</span></h2>\n{inner}\n</section>\n')

def dl(rows):
    return '<dl class="dl">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl>"

def ul(items):
    return "<ul>" + "".join(f"<li>{fmt(i)}</li>" for i in items) + "</ul>"

def legend():
    return ('<div class="legend" role="list">' + "".join(
        f'<span role="listitem"><span class="st {k}" aria-hidden="true">{STATE[k][0]}</span>{STATE[k][1]}</span>' for k in ("ok", "bad", "nd")) + "</div>")

def matrix_html(rows):
    out = [legend(), '<div class="matrix">']
    for st, fam, why, refs in rows:
        out.append(f'<div class="mrow {st}"><span class="st {st}" aria-hidden="true">{STATE[st][0]}</span>'
                   f'<div><span class="lbl">{STATE[st][1]}</span><span class="fam">{fam}</span></div>'
                   f'<div class="why">{fmt(why)}{cites(refs)}</div></div>')
    out.append("</div>")
    return "".join(out)

def cross_get(a, b):
    key = (a, b) if (a, b) in CROSS else (b, a)
    return CROSS[key]

def cross_table(highlight=None):
    subs = SUBSTANCES
    t = ['<div class="xwrap"><div class="xcard"><div class="scroll-x"><table class="xmatrix" aria-label="Compatibilidad entre las sustancias de CHEM SAFE"><thead><tr><th></th>']
    for s in subs:
        hl = ' class="hl"' if s["slug"] == highlight else ""
        t.append(f'<th scope="col"{hl}>{s["formula"]}</th>')
    t.append("</tr></thead><tbody>")
    for r in subs:
        hl = ' class="hl"' if r["slug"] == highlight else ""
        t.append(f'<tr><th scope="row"{hl}>{r["formula"]}</th>')
        for c in subs:
            if r["slug"] == c["slug"]:
                t.append('<td class="diag" aria-label="misma sustancia">—</td>')
                continue
            st, note, detail = cross_get(r["slug"], c["slug"])
            pair = f'{r["name"]} + {c["name"]}'
            t.append(f'<td class="{st}"><button type="button" data-pair="{html.escape(pair)}" data-state="{st}" '
                     f'data-label="{html.escape(STATE[st][1])}" data-detail="{html.escape(detail)}" '
                     f'aria-label="{html.escape(pair)}: {html.escape(note)}">'
                     f'<span class="st {st}" aria-hidden="true">{STATE[st][0]}</span><span class="lbl-sm">{note}</span></button></td>')
        t.append("</tr>")
    t.append("</tbody></table></div></div>")
    t.append(f'<div class="xdetail" aria-live="polite"><div class="hint">{icon("tap")}<span>Toca una celda de la matriz para ver por qué esa pareja es '
             'compatible, incompatible o no tiene información.</span></div></div></div>')
    t.append('<p class="xnote">Las celdas resumen incompatibilidades listadas en las FDS citadas en cada ficha. Cuando no hay información documentada, '
             'la celda queda como «sin información»: <strong>no se asume compatibilidad</strong>.</p>')
    return "".join(t)

def ficha(s):
    i = SUBSTANCES.index(s)
    prev_s = SUBSTANCES[i - 1] if i > 0 else None
    next_s = SUBSTANCES[i + 1] if i < len(SUBSTANCES) - 1 else None
    desc = f'Ficha educativa de seguridad de {s["name"]} ({s["formula_plain"]}, CAS {s["cas"]}): peligros, EPP, primeros auxilios y compatibilidad.'
    h = head(f'{s["name"]} ({s["formula_plain"]}) · CHEM SAFE', 1, accent=s["accent"], accent_soft=s["accent_soft"], desc=desc)
    h += '<div class="progress" aria-hidden="true"></div>' + topbar(1)

    # Encabezado
    picts = "".join(picto_img(p, size=64) for p in s["pictos"])
    h += (f'<div class="hero"><div class="ghost-f" aria-hidden="true">{s["formula"]}</div><div class="wrap">'
          f'<p class="crumbs"><a href="../index.html">Inicio</a> / <a href="../index.html#sustancias">Sustancias</a> / {s["name"]}</p>'
          f'<h1>{s["name"]}</h1><div class="hero-row">'
          f'<span class="formula">{s["formula"]}</span>'
          f'<span class="chip">CAS {s["cas"]}</span>'
          f'<span class="hazard-badge {"none" if s["hazard_class"]=="none" else ""}">{hazard_icon(s["hazard_class"])}{s["hazard"]}</span>'
          f'</div>' + (f'<div class="hero-picts">{picts}</div>' if picts else "") + '</div></div>')
    h += '<main class="wrap">'
    h += ('<div class="facts" aria-label="Información general">'
          f'<div class="fact"><div class="k">Fórmula</div><div class="v">{s["formula"]}</div></div>'
          f'<div class="fact"><div class="k">Número CAS</div><div class="v">{s["cas"]}</div></div>'
          f'<div class="fact"><div class="k">Masa molar</div><div class="v">{s["molar"]}</div></div>'
          f'<div class="fact"><div class="k">Palabra de advertencia</div><div class="v">{s["signal"] or "Ninguna"}</div></div></div>')
    h += (f'<div class="notice">{icon("info")}<div><strong>Ficha educativa</strong>Esta ficha no reemplaza la FDS oficial del producto específico. '
          'Los riesgos dependen de la concentración y de la presentación del compuesto.</div></div>')

    # Índice
    h += '<div class="layout"><nav class="toc" id="menu" aria-label="Secciones de la ficha"><p class="ttl">En esta ficha</p><ol>'
    for n, (sid, t) in enumerate(SECTIONS, 1):
        h += f'<li><a href="#{sid}"><span class="ico">{icon(f"i{n}")}</span><span class="n">{n}</span><span>{t}</span></a></li>'
    h += (f'<li><a href="#referencias"><span class="ico">{icon("ref")}</span><span class="n">✎</span><span>Referencias</span></a></li></ol>'
          f'<button class="btn ghost print" type="button" data-print>{icon("print")}Imprimir ficha</button></nav><div class="content">')

    # 1 Identificación
    cas_refs = s.get("cas_refs", "1" if s["slug"] == "hidroxido-de-sodio" else "2")
    h += sec(1, dl([
        ("Nombre", f'<strong class="formula-big">{s["name"]}</strong>'),
        ("Fórmula química", f'<span class="formula-big">{s["formula"]}</span>'),
        ("Nomenclatura sistemática", s["sistematica"]),
        ("Nomenclatura tradicional", s["tradicional"]),
        ("Otros nombres", s.get("otros") or "—"),
        ("Número CAS", f'{s["cas"]}{cites(cas_refs)}'),
        ("Número CE", s["ec"]),
        ("Identificador PubChem", f'CID {s["cid"]}'),
        ("Masa molar", s["molar"]),
        ("Usos habituales", ul(s["usos"]) + cites(s["usos_refs"])),
    ]))

    # 2 Peligros
    hz = s["hazards"]
    if s["pictos"]:
        body = f'<div class="picts">{picto_figs(s)}<span class="signal">{s["signal"]}</span></div>'
        body += ('<div class="scroll-x"><table class="t"><thead><tr><th>Clase y categoría</th><th>Código</th><th>Indicación de peligro</th></tr></thead><tbody>'
                 + "".join(f"<tr><td>{a}</td><td><strong>{b}</strong></td><td>{c}</td></tr>" for a, b, c in hz["clasif"])
                 + f'</tbody></table></div><p class="src">Clasificación según el SGA/GHS{cites(hz["class_refs"])}. '
                 'Los pictogramas mostrados son dibujos simplificados; los oficiales están publicados por UNECE.</p>')
    else:
        body = ('<div class="picts"><div class="nopict">Sin pictogramas de peligro GHS. Las FDS consultadas lo indican como sustancia '
                f'no clasificada{cites(hz["class_refs"])}.</div><span class="signal none">Sin palabra de advertencia</span></div>')
    body += f'<h3>Riesgos para la salud</h3>{ul(hz["salud"])}{src(hz["salud_refs"])}'
    body += f'<h3>Riesgos físicos</h3>{ul(hz["fisicos"])}{src(hz["fisicos_refs"])}'
    body += f'<h3>Riesgos ambientales</h3><p>{fmt(hz["ambiente"])}</p>'
    body += f'<h3>Advertencias principales</h3><p>{fmt(hz["advertencias"])}</p>'
    body += f'<div class="notice">{icon("warn")}<div><strong>Concentración y presentación</strong>{fmt(s["concentration_note"])}</div></div>'
    h += sec(2, body)

    # 3 Composición
    body = ('<div class="scroll-x"><table class="t"><thead><tr><th>Componente</th><th>Fórmula</th><th>Pureza o concentración</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{fmt(c)}{cites(d)}</td></tr>" for a, b, c, d in s["comp_rows"])
            + "</tbody></table></div>" + ul(s["comp_notes"]) + src(s["comp_refs"]))
    h += sec(3, body)

    # 4 Primeros auxilios
    fa = s["fa"]
    body = dl([("Exposición ocular", fmt(fa["ojos"])), ("Contacto con la piel", fmt(fa["piel"])), ("Inhalación", fmt(fa["inhalacion"])),
               ("Ingestión", fmt(fa["ingestion"])), ("Síntomas relevantes", fmt(fa["sintomas"]))])
    body += f'<div class="alert">{icon("warn")}<div><strong>Asistencia médica urgente:</strong> {fmt(fa["urgente"])}</div></div>'
    body += src(fa["refs"], "Estas medidas son generales; sigue siempre las indicaciones de la FDS del producto y las de tu docente.")
    h += sec(4, body)

    # 5 Manipulación y almacenamiento
    st = s["storage"]
    body = f'<h3>Condiciones de almacenamiento</h3>{ul(st["cond"])}<h3>Precauciones de manipulación</h3>{ul(st["manip"])}'
    body += dl([("Materiales de recipientes", fmt(st["envases"])), ("Condiciones que deben evitarse", fmt(st["evitar"])),
                ("Recomendaciones de segregación", fmt(st["segreg"]))])
    body += src(st["refs"])
    h += sec(5, body)

    # 6 EPP
    p = s["ppe"]
    body = dl([("Protección ocular", fmt(p["ojos"])), ("Protección de manos", fmt(p["manos"])), ("Protección corporal", fmt(p["cuerpo"])),
               ("Ventilación y controles", fmt(p["vent"]))]) + f'<h3>Recomendaciones preventivas</h3>{ul(p["reco"])}'
    body += src(p["refs"])
    h += sec(6, body)

    # 7 Propiedades
    cards = []
    for k, v, c, r, ok in s["props"]:
        cls = "pcard" if ok else "pcard nd"
        cond = f'<div class="c">{c}</div>' if c else ""
        cards.append(f'<div class="{cls}"><div class="k">{k}</div><div class="v">{v}</div>{cond}<div class="c">{cites(r).strip()}</div></div>')
    body = '<div class="cards">' + "".join(cards) + "</div>"
    body += '<p class="src">Los valores provienen de FDS de fabricantes y pueden variar ligeramente según el grado y la concentración. Donde hay diferencias entre fuentes se muestra el intervalo.</p>'
    h += sec(7, body)

    # 8 Compatibilidad
    body = (f'<div class="alert">{icon("warn")}<div><strong>Importante.</strong> No se asume compatibilidad por falta de información. '
            'Nunca mezcles sustancias «para comprobar» si son compatibles.</div></div>')
    body += dl([("Estabilidad química", fmt(s["stability"])), ("Reactividad conocida", fmt(s["reactivity"])),
                ("Condiciones que deben evitarse", fmt(s["conditions"])), ("Riesgos de reacciones peligrosas", fmt(s["danger_reactions"])),
                ("Productos de descomposición peligrosos", fmt(s["decomposition"])),
                ("Almacenamiento separado", fmt(s["separate"]))])
    body += src(s["stab_refs"])
    body += "<h3>Matriz visual de compatibilidad</h3>" + matrix_html(s["matrix"])
    body += "<h3>Entre las sustancias de CHEM SAFE</h3>" + cross_table(highlight=s["slug"])
    h += sec(8, body, featured=True)

    # 9 Emergencias
    e = s["emerg"]
    body = (f'<h3>Riesgos ante derrames</h3><p>{fmt(e["derrames"])}</p><h3>Precauciones iniciales</h3>{ul(e["precauciones"])}'
            f'<h3>Riesgos en caso de incendio</h3><p>{fmt(e["incendio"])}</p><h3>Medidas generales de emergencia</h3><p>{fmt(e["medidas"])}</p>'
            f'<h3>Gestión segura de residuos</h3><p>{fmt(e["residuos"])}</p>' + src(e["refs"]))
    h += sec(9, body)

    # Referencias
    h += (f'<section class="sec reveal" id="referencias" aria-labelledby="ref-h"><h2 id="ref-h"><span class="num">{icon("ref")}</span>'
          '<span class="ttl"><small>Fuentes</small>Referencias</span></h2>'
          f'<p class="meta"><span>Versión de la ficha: <strong>{VERSION}</strong></span><span>Última actualización: <strong>{s.get("updated", UPDATED)}</strong></span></p>'
          '<ol class="refs">')
    for n, (txt, url) in enumerate(s["refs"], 1):
        h += f'<li id="ref{n}"><span class="id">[{n}]</span> {html.escape(txt)} <a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(url)}</a></li>'
    h += (f'</ol><div class="notice">{icon("info")}<div><strong>Datos confirmados y datos no disponibles</strong>Los valores se tomaron de las fuentes listadas. '
          'Lo que no aparece en ellas se marca como «No determinado en las fuentes consultadas». '
          'Las consultas directas a PubChem, ECHA y OSHA están pendientes de verificación por el equipo antes de la entrega final.</div></div>'
          f'<p class="noprint"><button class="btn ghost" type="button" data-print>{icon("print")}Imprimir esta ficha</button></p></section>')

    # Navegación entre fichas
    h += '<nav class="pager" aria-label="Otras fichas">'
    if prev_s:
        h += f'<a class="prev" href="{prev_s["slug"]}.html"><small>← Anterior</small><b>{prev_s["name"]}</b></a>'
    if next_s:
        h += f'<a class="next" href="{next_s["slug"]}.html"><small>Siguiente →</small><b>{next_s["name"]}</b></a>'
    h += '</nav></div></div></main>'
    h += f'<button class="totop" type="button" aria-label="Volver arriba">{icon("up", "2.2")}</button>'
    h += footer(1) + '<script src="../assets/js/app.js"></script>\n</body>\n</html>\n'
    return h

def hex_bg():
    return ('<svg class="hex" aria-hidden="true" width="100%" height="100%"><defs><pattern id="hx" width="56" height="97" patternUnits="userSpaceOnUse" '
            'patternTransform="scale(.9)"><path d="M28 0l28 16v32L28 64 0 48V16zM28 64v33M0 97V81M56 97V81" fill="none" stroke="currentColor" stroke-width="1"/>'
            '</pattern></defs><rect width="100%" height="100%" fill="url(#hx)"/></svg>')

def index():
    nrefs = sum(len(s["refs"]) for s in SUBSTANCES)
    h = head("CHEM SAFE · Fichas de seguridad química con QR", 0)
    h += topbar(0, "home")
    h += (f'<section class="home-hero">{hex_bg()}<div class="wrap grid"><div>'
          f'<span class="eyebrow">{icon("qr")}Laboratorio · Colegio San Luis Maristas</span>'
          '<h1>Escanea la etiqueta.<br><em>Conoce el riesgo.</em></h1>'
          '<p class="lead">CHEM SAFE reúne fichas digitales de seguridad para las sustancias de nuestro laboratorio. '
          'Cada frasco lleva un código QR que abre su ficha en el celular.</p>'
          f'<div class="cta"><a class="btn" href="#sustancias">Ver sustancias {icon("arrow")}</a>'
          f'<a class="btn ghost" href="etiquetas.html">{icon("tag")}Etiquetas con QR</a></div>'
          f'<div class="stats"><div><b>{len(SUBSTANCES)}</b><span>sustancias</span></div><div><b>{len(SECTIONS)}</b><span>secciones por ficha</span></div>'
          f'<div><b>{nrefs}</b><span>fuentes citadas</span></div></div></div>')
    # tarjeta de muestra decorativa
    ex = SUBSTANCES[min(3, len(SUBSTANCES) - 1)]
    h += (f'<div class="preview" aria-hidden="true"><div class="card"><div class="row"><div style="flex:1">'
          f'<div class="fm" style="color:{ex["accent"]}">{ex["formula"]}</div><div style="font-weight:800;font-size:1.1rem">{ex["name"]}</div>'
          f'<div class="bar m"></div><div class="bar s"></div></div><div class="qrbox"></div></div>'
          f'<div style="display:flex;gap:8px;margin-top:16px">{"".join(picto_img(p, "", 44) for p in ex["pictos"])}</div>'
          f'<div class="bar"></div><div class="bar m"></div><div class="bar s"></div></div><div class="card"><div class="bar"></div><div class="bar s"></div></div></div>'
          '</div></section>')
    h += '<main class="wrap">'

    # Sustancias
    h += ('<section class="block" id="sustancias"><div class="block-head"><div><h2>Sustancias</h2>'
          '<p>Busca por nombre, fórmula o número CAS, o filtra por tipo de peligro.</p></div></div>'
          f'<div class="toolbar"><label class="search"><span class="sr-only">Buscar sustancia</span>{icon("search")}'
          '<input type="search" id="q" placeholder="Buscar: sulfúrico, HCl, 7722-84-1…" autocomplete="off"></label>'
          '<div class="filters" role="group" aria-label="Filtrar por peligro">')
    for fid, lab in FILTERS:
        pressed = "true" if fid == "all" else "false"
        h += f'<button type="button" data-filter="{fid}" aria-pressed="{pressed}">{lab}</button>'
    h += '</div></div><div class="subs">'
    for s in SUBSTANCES:
        tags = " ".join(s["pictos"]) if s["pictos"] else "none"
        search = html.escape(" ".join([s["name"], s["formula_plain"], strip_tags(s["formula"]), s["cas"], s.get("otros", ""), s["tradicional"]]).lower())
        cls = "ok" if s["hazard_class"] == "none" else "bad"
        pics = "".join(picto_img(p, "", 36) for p in s["pictos"])
        h += (f'<a class="sub reveal" style="--accent:{s["accent"]};--accent-soft:{s["accent_soft"]}" href="fichas/{s["slug"]}.html" '
              f'data-tags="{tags}" data-search="{search}">'
              f'<span class="f">{s["formula"]}</span><span class="nm">{s["name"]}</span><span class="cas">CAS {s["cas"]}</span>'
              f'<span class="pics">{pics}</span>'
              f'<span class="foot"><span class="pill {cls}">{hazard_icon(s["hazard_class"])}{s["hazard"]}</span>'
              f'<span class="go">Ficha {icon("arrow", "2")}</span></span></a>')
    h += '</div><p class="empty" id="empty">No hay sustancias que coincidan con la búsqueda.</p></section>'

    # Cómo se usa
    h += ('<section class="block"><div class="block-head"><div><h2>Cómo se usa</h2><p>Tres pasos, desde el frasco hasta la ficha.</p></div></div><ol class="how">'
          f'<li class="reveal"><div class="ic">{icon("eye")}</div><strong>Identifica</strong><span>Lee el nombre y la fórmula de la etiqueta.</span></li>'
          f'<li class="reveal"><div class="ic">{icon("qr")}</div><strong>Escanea</strong><span>Apunta la cámara del celular al código QR.</span></li>'
          f'<li class="reveal"><div class="ic">{icon("i2")}</div><strong>Consulta</strong><span>Revisa peligros, EPP, primeros auxilios y compatibilidad.</span></li></ol></section>')

    # Compatibilidad
    h += ('<section class="block" id="compatibilidad"><div class="block-head"><div><h2>Compatibilidad entre sustancias</h2>'
          f'<p>Matriz de las {len(SUBSTANCES)} sustancias de CHEM SAFE. Los estados se basan en incompatibilidades documentadas en FDS; '
          'lo que no está documentado queda como «sin información».</p></div></div>' + legend() + cross_table() + '</section>')

    # Etiquetas
    h += ('<section class="cta-band reveal"><div><h2>Etiquetas para imprimir</h2>'
          '<p>Genera las etiquetas con código QR (100 × 62 mm) una vez que el sitio esté publicado y verificado.</p></div>'
          f'<a class="btn" href="etiquetas.html">{icon("tag")}Ir a las etiquetas</a></section>')
    h += '</main>' + footer(0) + '<script src="assets/js/app.js"></script>\n</body>\n</html>\n'
    return h

def etiquetas():
    h = head("Etiquetas · CHEM SAFE", 0, extra_css="labels.css")
    h += topbar(0, "labels")
    h += ('<main class="wrap"><section class="block" style="padding-top:40px"><div class="block-head"><div><span class="eyebrow">'
          f'{icon("tag")}Impresión</span><h2 style="margin-top:14px">Etiquetas con código QR</h2>'
          '<p>Los códigos QR solo se generan cuando escribes la URL pública del sitio y confirmas que los enlaces funcionan.</p></div></div>')
    h += ('<section class="controls" aria-label="Configuración"><ol class="steps">'
          '<li><label class="lb" for="base-url">URL pública del sitio (GitHub Pages)</label>'
          '<div class="row"><input id="base-url" type="url" inputmode="url" placeholder="https://tu-usuario.github.io/chem-safe/" autocomplete="off">'
          '<button class="btn" id="apply" type="button">Generar QR</button></div><p id="status" role="status"></p></li>'
          '<li><p class="lb">Abre cada enlace que codifican los QR</p><ul id="links"></ul></li>'
          '<li><label class="ck"><input type="checkbox" id="confirm" disabled><span>Abrí cada enlace y cada uno muestra la ficha correcta.</span></label>'
          f'<button class="btn" id="print" type="button" disabled>{icon("print")}Imprimir etiquetas</button></li></ol></section>')
    h += '<div class="sheet" aria-label="Vista previa de etiquetas">'
    for s in SUBSTANCES:
        pic = ("".join(f'<img src="assets/img/{p}.svg" alt="Pictograma {PICTO[p][0]}: {PICTO[p][1]}">' for p in s["pictos"][:2])
               if s["pictos"] else '<div class="nopic">Sin pictograma</div>')
        sig = f'<b>{s["signal"]}</b>' if s["signal"] else "<b>Sin clasificación</b>"
        h += (f'<article class="label" style="--accent:{s["accent"]}"><div class="info"><p class="nm">{s["name"]}</p>'
              f'<p class="fm">{s["formula"]}</p>'
              f'<p class="nom"><b>Sistemática:</b> {s["sistematica"]}<br><b>Tradicional:</b> {s["tradicional"]}</p>'
              '<div class="school-mark"><img src="assets/img/logo-maristas.png" alt="" width="20" height="20"><span>Colegio San Luis Maristas</span></div></div>'
              f'<div class="side"><div class="qr" data-qr="{s["slug"]}"></div><div class="scan">Escanea para ver la ficha</div></div>'
              f'<div class="foot"><div class="pics">{pic}</div><div class="w">{sig}{s["label_warning"]}</div></div></article>')
    h += '</div></section></main>' + footer(0)
    h += ('<script src="assets/js/qrcode.js"></script>\n<script src="assets/js/config.js"></script>\n'
          '<script src="assets/js/labels.js"></script>\n<script src="assets/js/app.js"></script>\n</body>\n</html>\n')
    return h

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def check():
    """Comprueba que todas las parejas de la matriz cruzada existan y que las citas apunten a referencias reales."""
    slugs = [s["slug"] for s in SUBSTANCES]
    for a in slugs:
        for b in slugs:
            if a != b:
                cross_get(a, b)
    for s in SUBSTANCES:
        n = len(s["refs"])
        blob = repr({k: v for k, v in s.items() if k != "refs"})
        nums = set(int(x) for g in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", blob) for x in g.split(","))
        for m in re.finditer(r"refs'?:?\s*'([\d, ]+)'", blob):
            nums.update(int(x) for x in m.group(1).replace(" ", "").split(",") if x)
        for tup in s["matrix"]:
            nums.update(int(x) for x in tup[3].split(",") if x.strip())
        for tup in s["props"]:
            nums.update(int(x) for x in tup[3].split(",") if x.strip())
        bad = sorted(x for x in nums if x < 1 or x > n)
        if bad:
            raise SystemExit(f"{s['slug']}: citas fuera de rango {bad} (hay {n} referencias)")
        for p in s["pictos"]:
            if p not in PICTO:
                raise SystemExit(f"{s['slug']}: pictograma desconocido {p}")

if __name__ == "__main__":
    check()
    write("index.html", index())
    write("etiquetas.html", etiquetas())
    for s in SUBSTANCES:
        write(f"fichas/{s['slug']}.html", ficha(s))
    write(".nojekyll", "")
    write("assets/img/favicon.svg",
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
          '<stop offset="0" stop-color="#1f5c4d"/><stop offset="1" stop-color="#3fbf9b"/></linearGradient></defs><rect width="32" height="32" rx="8" fill="url(#g)"/>'
          '<g fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6h8M13.5 6v7L8 22.5a2 2 0 0 0 1.7 3h12.6a2 2 0 0 0 1.7-2.8L18.5 13V6"/><path d="M10.5 19h11"/></g></svg>')
    print("Sitio generado en", os.path.abspath(ROOT), "·", len(SUBSTANCES), "sustancias")
