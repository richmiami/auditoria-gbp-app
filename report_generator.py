"""
Generador del reporte de Auditoria GBP / SEO Local / Reputacion Digital, en .docx,
con la misma identidad visual (azul marino + dorado, badges de severidad por color)
usada en la plantilla de Word original. Puro python-docx: no depende de Node.

Uso:
    from report_generator import build_report
    build_report(data, "salida.docx")

`data` es un dict con la misma forma que produce app.py / integrations.py.
Ver mock_data() al final de este archivo para un ejemplo completo de las llaves esperadas.
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.section import WD_SECTION

# ---------------------------------------------------------------------------
# Paleta (debe coincidir con la plantilla original)
# ---------------------------------------------------------------------------
NAVY = "1B2A4A"
NAVY_DARK = "12203A"
TEAL = "2C6E63"
GOLD = "C9962B"
GOLD_LIGHT = "F4E5C2"
LIGHT_GRAY = "F2F2F0"
MID_GRAY = "6B7280"
WHITE = "FFFFFF"
TEXT_DARK = "222222"
GREEN_SOFT = "E7F3EE"
GREEN_BORDER = "2E9E5B"

SEVERITY_COLORS = {
    "Crítico": ("C0392B", WHITE),
    "Alto": ("E07B24", WHITE),
    "Medio": ("D4AC0D", "3A3000"),
    "Bajo": ("2E9E5B", WHITE),
}
STATUS_COLORS = {
    "Crítico": ("C0392B", WHITE),
    "Deficiente": ("C0392B", WHITE),
    "Débil": ("E07B24", WHITE),
    "Necesita Trabajo": ("D4AC0D", "3A3000"),
    "Aceptable": ("2E86AB", WHITE),
    "Bueno": ("2E9E5B", WHITE),
}
USAGE_COLORS = {
    "No se usa": ("C0392B", WHITE),
    "Parcial": ("D4AC0D", "3A3000"),
    "Optimizado": ("2E9E5B", WHITE),
}

PAGE_CONTENT_TWIPS = 9360  # US Letter, márgenes de 1in


# ---------------------------------------------------------------------------
# Helpers de bajo nivel (shading / bordes: python-docx no los expone directo)
# ---------------------------------------------------------------------------

def _set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _set_cell_borders(cell, color="D9D9D9", size=4):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)


def _set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for edge, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tcPr.append(mar)


def _set_col_widths(table, widths_twips):
    table.autofit = False
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = Twips(widths_twips[idx])
    grid = table._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for gridcol, w in zip(grid.findall(qn("w:gridCol")), widths_twips):
            gridcol.set(qn("w:w"), str(w))


def _cell_text(cell, text, *, bold=False, color=TEXT_DARK, size=9, align="left",
               italic=False, valign="center"):
    cell.vertical_alignment = {
        "center": WD_ALIGN_VERTICAL.CENTER,
        "top": WD_ALIGN_VERTICAL.TOP,
    }.get(valign, WD_ALIGN_VERTICAL.CENTER)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }.get(align, WD_ALIGN_PARAGRAPH.LEFT)
    run = p.add_run(str(text))
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = "Calibri"
    return p


def _head_cell(cell, text, *, align="left", fill=NAVY):
    _set_cell_bg(cell, fill)
    _set_cell_borders(cell, color=fill)
    _set_cell_margins(cell)
    _cell_text(cell, text, bold=True, color=WHITE, size=9.5, align=align)


def _body_cell(cell, text, *, align="left", fill=None, bold=False, color=TEXT_DARK, size=9):
    if fill:
        _set_cell_bg(cell, fill)
    _set_cell_borders(cell)
    _set_cell_margins(cell)
    _cell_text(cell, text, bold=bold, color=color, size=size, align=align)


def _badge_cell(cell, value, color_map=SEVERITY_COLORS):
    fill, color = color_map.get(value, ("AAAAAA", WHITE))
    _set_cell_bg(cell, fill)
    _set_cell_borders(cell)
    _set_cell_margins(cell)
    _cell_text(cell, value, bold=True, color=color, size=9, align="center")


def _add_field_run(paragraph, field_code, *, size=7.5, color=MID_GRAY, bold=False):
    run = paragraph.add_run()
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = "Calibri"
    run.bold = bold
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = field_code
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)
    return run


def _no_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    cant = OxmlElement("w:cantSplit")
    trPr.append(cant)


def _repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    trPr.append(th)


# ---------------------------------------------------------------------------
# Bloques de alto nivel
# ---------------------------------------------------------------------------

def _section_title(doc, number, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(8)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), NAVY)
    pPr.append(shd)
    border = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "24")
    left.set(qn("w:space"), "4")
    left.set(qn("w:color"), GOLD)
    border.append(left)
    pPr.append(border)
    run = p.add_run(f"  {number}. {title}" if number else f"  {title}")
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(WHITE)
    run.font.size = Pt(12)
    run.font.name = "Calibri"
    return p


def _sub_note(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(MID_GRAY)
    run.font.name = "Calibri"
    return p


def _body_text(doc, text, *, bold=False, size=10, color=TEXT_DARK, space_after=8, space_before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = "Calibri"
    return p


def _bullets(doc, items, *, size=10):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(it)
        run.font.size = Pt(size)
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor.from_string(TEXT_DARK)


def _table(doc, columns, rows, *, badge_col=None, color_map=SEVERITY_COLORS, zebra=True):
    """columns: [(header, width_twips, align)]; rows: list of value-lists."""
    n = len(columns)
    table = doc.add_table(rows=1 + len(rows), cols=n)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    widths = [c[1] for c in columns]
    _set_col_widths(table, widths)

    hdr = table.rows[0]
    _no_row_split(hdr)
    _repeat_header(hdr)
    for ci, (label, _w, align) in enumerate(columns):
        _head_cell(hdr.cells[ci], label, align=align)

    for ri, rowvals in enumerate(rows):
        row = table.rows[ri + 1]
        _no_row_split(row)
        fill = LIGHT_GRAY if (zebra and ri % 2 == 1) else None
        for ci, val in enumerate(rowvals):
            align = columns[ci][2]
            if badge_col == ci:
                _badge_cell(row.cells[ci], val, color_map)
            else:
                _body_cell(row.cells[ci], val, align=align, fill=fill)
    return table


def _stat_boxes(doc, stats):
    n = len(stats)
    width = PAGE_CONTENT_TWIPS // n
    table = doc.add_table(rows=1, cols=n)
    _set_col_widths(table, [width] * n)
    row = table.rows[0]
    _no_row_split(row)
    for i, s in enumerate(stats):
        cell = row.cells[i]
        _set_cell_bg(cell, "EEF2F6")
        _set_cell_borders(cell, color="D9D9D9")
        _set_cell_margins(cell, top=160, bottom=160, left=140, right=140)
        cell.text = ""
        p1 = cell.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(s["number"])
        r1.bold = True
        r1.font.size = Pt(20)
        r1.font.color.rgb = RGBColor.from_string(NAVY)
        r1.font.name = "Calibri"

        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(s["label"])
        r2.bold = True
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor.from_string(TEXT_DARK)
        r2.font.name = "Calibri"

        p3 = cell.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = p3.add_run(s["source"])
        r3.italic = True
        r3.font.size = Pt(7)
        r3.font.color.rgb = RGBColor.from_string(MID_GRAY)
        r3.font.name = "Calibri"
    return table


def _callout(doc, title, lines, *, fill=GOLD_LIGHT, border=GOLD):
    table = doc.add_table(rows=1, cols=1)
    _set_col_widths(table, [PAGE_CONTENT_TWIPS])
    row = table.rows[0]
    _no_row_split(row)
    cell = row.cells[0]
    _set_cell_bg(cell, fill)
    _set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge, sz in (("top", 4), ("bottom", 4), ("right", 4), ("left", 24)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:color"), border)
        borders.append(el)
    tcPr.append(borders)
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor.from_string(NAVY_DARK)
    r.font.name = "Calibri"
    for line in lines:
        bp = cell.add_paragraph(style="List Bullet")
        bp.paragraph_format.space_after = Pt(3)
        br = bp.add_run(line)
        br.font.size = Pt(9.5)
        br.font.color.rgb = RGBColor.from_string(TEXT_DARK)
        br.font.name = "Calibri"
    return table


def _cover_header(doc, kicker, title_lines, subtitle, date_line):
    table = doc.add_table(rows=1, cols=1)
    _set_col_widths(table, [PAGE_CONTENT_TWIPS])
    row = table.rows[0]
    _no_row_split(row)
    cell = row.cells[0]
    _set_cell_bg(cell, NAVY_DARK)
    _set_cell_margins(cell, top=340, bottom=340, left=320, right=320)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge, sz, col in (("top", 2, NAVY_DARK), ("bottom", 32, GOLD), ("left", 2, NAVY_DARK), ("right", 2, NAVY_DARK)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:color"), col)
        borders.append(el)
    tcPr.append(borders)
    cell.text = ""
    p0 = cell.paragraphs[0]
    r0 = p0.add_run(kicker.upper())
    r0.bold = True
    r0.font.size = Pt(10)
    r0.font.color.rgb = RGBColor.from_string(GOLD)
    r0.font.name = "Calibri"

    p1 = cell.add_paragraph()
    r1 = p1.add_run(title_lines)
    r1.bold = True
    r1.font.size = Pt(26)
    r1.font.color.rgb = RGBColor.from_string(WHITE)
    r1.font.name = "Calibri"

    p2 = cell.add_paragraph()
    r2 = p2.add_run(subtitle)
    r2.font.size = Pt(12)
    r2.font.color.rgb = RGBColor.from_string("D7DEE8")
    r2.font.name = "Calibri"

    p3 = cell.add_paragraph()
    r3 = p3.add_run(date_line)
    r3.font.size = Pt(9.5)
    r3.font.color.rgb = RGBColor.from_string("AAB6C6")
    r3.font.name = "Calibri"
    return table


def _prepared_by(doc, name, title, contact):
    table = doc.add_table(rows=1, cols=1)
    _set_col_widths(table, [PAGE_CONTENT_TWIPS])
    row = table.rows[0]
    _no_row_split(row)
    cell = row.cells[0]
    _set_cell_bg(cell, "F5F6F8")
    _set_cell_margins(cell, top=200, bottom=200, left=260, right=260)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge, sz, col in (("top", 0, WHITE), ("bottom", 0, WHITE), ("right", 0, WHITE), ("left", 28, GOLD)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single" if sz else "none")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:color"), col)
        borders.append(el)
    tcPr.append(borders)
    cell.text = ""
    p0 = cell.paragraphs[0]
    r0 = p0.add_run("PREPARADO POR")
    r0.bold = True
    r0.font.size = Pt(8.5)
    r0.font.color.rgb = RGBColor.from_string(GOLD)
    r0.font.name = "Calibri"

    p1 = cell.add_paragraph()
    r1 = p1.add_run(name)
    r1.bold = True
    r1.font.size = Pt(14)
    r1.font.color.rgb = RGBColor.from_string(NAVY_DARK)
    r1.font.name = "Calibri"

    p2 = cell.add_paragraph()
    r2 = p2.add_run(title)
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor.from_string(TEXT_DARK)
    r2.font.name = "Calibri"

    p3 = cell.add_paragraph()
    r3 = p3.add_run(contact)
    r3.font.size = Pt(9)
    r3.font.color.rgb = RGBColor.from_string(MID_GRAY)
    r3.font.name = "Calibri"
    return table


def _business_table(doc, rows):
    columns = [("Campo", 3000, "left"), ("Detalle", 6360, "left")]
    table = doc.add_table(rows=1 + len(rows), cols=2)
    _set_col_widths(table, [3000, 6360])
    hdr = table.rows[0]
    _no_row_split(hdr)
    _repeat_header(hdr)
    _head_cell(hdr.cells[0], "Campo", fill=TEAL)
    _head_cell(hdr.cells[1], "Detalle", fill=TEAL)
    for i, (label, value) in enumerate(rows):
        r = table.rows[i + 1]
        _no_row_split(r)
        fill = LIGHT_GRAY if i % 2 == 1 else None
        _body_cell(r.cells[0], label, bold=True, fill=fill)
        _body_cell(r.cells[1], value, fill=fill)
    return table


def _score_table(doc, scores, overall):
    c1, c2, c3 = 4210, 2210, 2960
    table = doc.add_table(rows=2 + len(scores), cols=3)
    _set_col_widths(table, [c1, c2, c3])
    hdr = table.rows[0]
    _no_row_split(hdr)
    _repeat_header(hdr)
    _head_cell(hdr.cells[0], "Área Auditada")
    _head_cell(hdr.cells[1], "Puntuación", align="center")
    _head_cell(hdr.cells[2], "Estado", align="center")
    for i, s in enumerate(scores):
        r = table.rows[i + 1]
        _no_row_split(r)
        fill = LIGHT_GRAY if i % 2 == 1 else None
        _body_cell(r.cells[0], s["area"], fill=fill)
        _body_cell(r.cells[1], s["score"], align="center", fill=fill)
        _badge_cell(r.cells[2], s["status"], STATUS_COLORS)
    last = table.rows[-1]
    _no_row_split(last)
    _body_cell(last.cells[0], "Salud General de SEO Local", bold=True, fill="E7ECF2")
    _body_cell(last.cells[1], overall["score"], align="center", bold=True, fill="E7ECF2")
    _badge_cell(last.cells[2], overall["status"], STATUS_COLORS)
    return table


def _pricing_table(doc, packages):
    c1, c2, c3 = 2100, 5360, 1900
    table = doc.add_table(rows=1 + len(packages), cols=3)
    _set_col_widths(table, [c1, c2, c3])
    hdr = table.rows[0]
    _no_row_split(hdr)
    _repeat_header(hdr)
    _head_cell(hdr.cells[0], "Paquete")
    _head_cell(hdr.cells[1], "Incluye")
    _head_cell(hdr.cells[2], "Inversión", align="center")
    for i, p in enumerate(packages):
        row = table.rows[i + 1]
        _no_row_split(row)
        fill = "FBF0D9" if p.get("highlight") else (LIGHT_GRAY if i % 2 == 1 else None)
        _body_cell(row.cells[0], p["name"], bold=True, fill=fill)
        cell = row.cells[1]
        if fill:
            _set_cell_bg(cell, fill)
        _set_cell_borders(cell)
        _set_cell_margins(cell)
        cell.text = ""
        for j, inc in enumerate(p["includes"]):
            para = cell.paragraphs[0] if j == 0 else cell.add_paragraph()
            para.style = doc.styles["List Bullet"]
            r = para.add_run(inc)
            r.font.size = Pt(9)
            r.font.name = "Calibri"
            r.font.color.rgb = RGBColor.from_string(TEXT_DARK)
        _body_cell(row.cells[2], p["price"], align="center", bold=True, fill=fill, color=NAVY_DARK)
    return table


def _header_footer(section, business_label, prepared_by_name):
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.text = ""
    r1 = hp.add_run("AUDITORÍA GBP · SEO LOCAL · REPUTACIÓN DIGITAL")
    r1.font.size = Pt(7)
    r1.font.color.rgb = RGBColor.from_string(MID_GRAY)
    r1.font.name = "Calibri"
    tabs = hp.paragraph_format.tab_stops
    tabs.add_tab_stop(Twips(PAGE_CONTENT_TWIPS), alignment=WD_TAB_ALIGNMENT.RIGHT)
    hp.add_run("\t" + business_label).font.size = Pt(7)

    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.text = ""
    r = fp.add_run(f"Preparado por {prepared_by_name}")
    r.font.size = Pt(7.5)
    r.font.color.rgb = RGBColor.from_string(MID_GRAY)
    r.font.name = "Calibri"
    ftabs = fp.paragraph_format.tab_stops
    ftabs.add_tab_stop(Twips(PAGE_CONTENT_TWIPS), alignment=WD_TAB_ALIGNMENT.RIGHT)
    tail = fp.add_run("\tPágina ")
    tail.font.size = Pt(7.5)
    tail.font.color.rgb = RGBColor.from_string(MID_GRAY)
    tail.font.name = "Calibri"
    _add_field_run(fp, "PAGE")
    mid = fp.add_run(" de ")
    mid.font.size = Pt(7.5)
    mid.font.color.rgb = RGBColor.from_string(MID_GRAY)
    mid.font.name = "Calibri"
    _add_field_run(fp, "NUMPAGES")


# ---------------------------------------------------------------------------
# Constructor principal
# ---------------------------------------------------------------------------

def build_report(data, out_path):
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.59)
    section.page_height = Cm(27.94)
    section.top_margin = Cm(1.75)
    section.bottom_margin = Cm(1.75)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)

    _header_footer(section, data["business"]["shortName"], data["preparedBy"]["name"])

    # ---- Portada ----
    _cover_header(
        doc,
        "Perfil de Negocio en Google (GBP)",
        "Auditoría de SEO Local y Reputación Digital",
        data["business"]["name"],
        f"Fecha de auditoría: {data['auditDate']}",
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    _body_text(doc, "Datos del Negocio", bold=True, size=13, color=NAVY_DARK, space_after=6)
    _business_table(doc, [
        ("Nombre del negocio", data["business"]["name"]),
        ("Sitio web", data["business"]["website"]),
        ("Teléfono", data["business"]["phone"]),
        ("Dirección", data["business"]["address"]),
        ("Categoría principal", data["business"]["category"]),
        ("Categorías adicionales", data["business"]["categoriesAdd"]),
        ("Reseñas / Calificación", data["business"]["reviews"]),
        ("Horario de atención", data["business"]["hours"]),
        ("Estado del perfil", data["business"]["status"]),
    ])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    _body_text(doc, "Resumen de Puntuación — Salud de SEO Local", bold=True, size=13, color=NAVY_DARK, space_after=6)
    _score_table(doc, data["scores"], data["overall"])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    _prepared_by(doc, **data["preparedBy"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 1. Hallazgos GBP ----
    _section_title(doc, 1, "Hallazgos de la Auditoría de Perfil de Google (GBP)")
    _sub_note(doc, "Basado en datos obtenidos en vivo de Google Places API y revisión del perfil.")
    _table(
        doc,
        [("#", 450, "center"), ("Área", 1650, "left"), ("Hallazgo", 4200, "left"),
         ("Impacto", 1750, "left"), ("Severidad", 1300, "center")],
        [[it["num"], it["area"], it["issue"], it["impact"], it["severity"]] for it in data["issues"]],
        badge_col=4,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 2. Keywords ----
    _section_title(doc, 2, "Brecha de Palabras Clave para SEO Local")
    _sub_note(doc, "Volumen de búsqueda mensual obtenido en vivo (Keywords Everywhere / DataForSEO).")
    _table(
        doc,
        [("Palabra Clave", 2650, "left"), ("Vol. Mensual", 1400, "center"),
         ("Competencia", 1250, "center"), ("Dificultad", 1650, "center"), ("Uso Actual", 2400, "center")],
        [[k["keyword"], k.get("volume", "—"), k.get("competition", "—"), k["difficulty"], k["currentUse"]] for k in data["keywords"]],
        badge_col=4, color_map=USAGE_COLORS,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 3. Reviews ----
    _section_title(doc, 3, "Por Qué las Reseñas Son Críticas Para Su Negocio")
    _body_text(doc, data["reviewsIntro"], space_after=10)
    _stat_boxes(doc, data["reviewStats"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    _callout(doc, "Lo que esto significa para " + data["business"]["shortName"], data["reviewRisk"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 4. GoHighLevel ----
    _section_title(doc, 4, "La Solución: Reseñas Automáticas con GoHighLevel")
    _body_text(doc, data["ghl"]["intro"], space_after=8)
    _body_text(doc, "Cómo funciona el sistema:", bold=True, size=10.5, space_after=4)
    _bullets(doc, data["ghl"]["steps"])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    _stat_boxes(doc, data["ghl"]["stats"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    _callout(doc, "Caso de referencia del sector", data["ghl"]["caseStudy"], fill=GREEN_SOFT, border=GREEN_BORDER)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 5. GBP optimization ----
    _section_title(doc, 5, "Optimización de Perfil de Google (GBP) y Google Maps")
    _body_text(doc, data["gbpOpt"]["intro"], space_after=8)
    _stat_boxes(doc, data["gbpOpt"]["stats"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    _body_text(doc, "Qué haremos en su perfil:", bold=True, size=10.5, space_after=4)
    _bullets(doc, data["gbpOpt"]["actions"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 6. Website ----
    _section_title(doc, 6, "Auditoría del Sitio Web (SEO Local) — en vivo")
    _sub_note(doc, data["websiteNote"])
    _table(
        doc,
        [("#", 450, "center"), ("Hallazgo", 2700, "left"), ("Detalle", 4700, "left"), ("Severidad", 1500, "center")],
        [[w["num"], w["issue"], w["details"], w["severity"]] for w in data["websiteIssues"]],
        badge_col=3,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 7. Competitors ----
    _section_title(doc, 7, "Análisis de la Competencia — en vivo (Google Maps)")
    _sub_note(doc, "Negocios que Google Maps posiciona hoy para el término de búsqueda del nicho.")
    _table(
        doc,
        [("Competidor", 2000, "left"), ("Reseñas", 1100, "center"), ("Calificación", 1200, "center"), ("Sitio Web", 4950, "left")],
        [[c["name"], c.get("reviewCount", "—"), c.get("rating", "—"), c.get("website", "—")] for c in data["competitors"]],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    _body_text(doc, "Metas de Crecimiento (90 Días)", bold=True, size=13, color=NAVY_DARK, space_after=6)
    _table(
        doc,
        [("Indicador (KPI)", 4200, "left"), ("Actual", 2500, "center"), ("Meta a 90 días", 2660, "center")],
        [[g["kpi"], g["current"], g["target"]] for g in data["growthTargets"]],
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 8. Citations ----
    _section_title(doc, 8, "Auditoría de Citas Locales (Directorios y Mapas)")
    _sub_note(doc, "El NAP (Nombre, Dirección, Teléfono) debe coincidir exactamente en cada plataforma. Checklist manual.")
    _table(
        doc,
        [("Plataforma", 2100, "left"), ("Tipo", 1500, "left"), ("Estado", 1500, "center"),
         ("Acción Requerida", 3000, "left"), ("Prioridad", 1250, "center")],
        [[c["platform"], c["type"], c["status"], c["action"], c["priority"]] for c in data["citations"]],
        badge_col=4,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 9. Action plan ----
    _section_title(doc, 9, "Plan de Acción de 90 Días")
    _table(
        doc,
        [("Fase", 1500, "left"), ("Tarea", 5150, "left"), ("Responsable", 1450, "left"), ("Prioridad", 1250, "center")],
        [[a["phase"], a["task"], a["owner"], a["priority"]] for a in data["actionPlan"]],
        badge_col=3,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 10. Pricing ----
    _section_title(doc, 10, "Paquetes de Inversión")
    _body_text(doc, data["pricingIntro"], space_after=10)
    _pricing_table(doc, data["packages"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    _callout(doc, "Por qué esta inversión se paga sola", data["roiPoints"], fill=GREEN_SOFT, border=GREEN_BORDER)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---- 11. Next steps ----
    _section_title(doc, 11, "Próximos Pasos")
    _body_text(doc, data["nextStepsIntro"], space_after=8)
    _bullets(doc, data["nextSteps"])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    _prepared_by(doc, **data["preparedBy"])

    doc.save(out_path)
    return out_path
