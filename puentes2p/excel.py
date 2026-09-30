"""Generador del libro Excel automatizado (fórmulas vivas con nombres definidos)."""
from __future__ import annotations

import ast

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

from .motor import UNIDADES, Modulo, Nota, Seccion, Tabla, Var, a_excel, a_texto, unidad_texto

FUENTE = "Arial"
F_NORMAL = Font(name=FUENTE, size=10)
F_NEGRITA = Font(name=FUENTE, size=10, bold=True)
F_TITULO = Font(name=FUENTE, size=14, bold=True, color="1F3864")
F_SUB = Font(name=FUENTE, size=10, italic=True, color="595959")
F_DATO = Font(name=FUENTE, size=10, color="0000FF", bold=True)
F_GRIS = Font(name=FUENTE, size=9, color="7F7F7F")
F_NOTA = Font(name=FUENTE, size=9, italic=True, color="404040")
R_DATO = PatternFill("solid", fgColor="FFFF99")
R_SEC1 = PatternFill("solid", fgColor="BDD7EE")
R_SEC2 = PatternFill("solid", fgColor="E7EEF7")
R_ENC = PatternFill("solid", fgColor="1F3864")
R_TAB = PatternFill("solid", fgColor="D9E1F2")
F_ENC = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
R_OK = PatternFill("solid", fgColor="C6EFCE")
R_NO = PatternFill("solid", fgColor="FFC7CE")
BORDE = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
CENTRO = Alignment(horizontal="center", vertical="center")

ENCABEZADOS = ["Símbolo", "Descripción", "Valor", "Unidad", "Valor base (tonf, m)", "Fórmula / expresión",
               "Referencia", "Valor PDF", "Dif. vs PDF"]
ANCHOS = [16, 58, 16, 12, 18, 70, 22, 12, 11]


def _unidad_xl(u: str) -> str | None:
    if not u:
        return None
    from .motor import factor_unidad
    if abs(factor_unidad(u) - 1.0) < 1e-15:
        return None
    return a_excel(ast.parse(u, mode="eval"), lambda n: "u_" + n)


def _formato(v) -> str:
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return "General"
    a = abs(v)
    if a == 0 or (abs(v - round(v)) <= 1e-9 * max(1.0, a) and a < 1e6):
        return "#,##0"
    if a >= 1000:
        return "#,##0.00"
    if a >= 1:
        return "0.000"
    if a >= 0.01:
        return "0.0000"
    return "0.000E+00"


def _nombre_xl(mod: Modulo, v: Var) -> str:
    return f"{mod.codigo}_{v.nombre}"


def _preparar_referencias(mod: Modulo):
    for v in mod.vars.values():
        v.xl_nombre = _nombre_xl(mod, v)
        ux = _unidad_xl(v.unidad)
        if v.en_tabla and ux:
            v.xl_ref = f"({v.xl_nombre}*{ux})"
        else:
            v.xl_ref = v.xl_nombre


def _formula(mod: Modulo, expr: str) -> str:
    def resolver(n):
        if n in UNIDADES:
            return "u_" + n
        return mod.vars[n].xl_ref
    return a_excel(ast.parse(expr, mode="eval"), resolver)


def _definir(wb, nombre, hoja, celda):
    col, fila = celda.column_letter, celda.row
    dn = DefinedName(nombre, attr_text=f"'{hoja}'!${col}${fila}")
    wb.defined_names[nombre] = dn


def _semaforo(ws, celda_ref: str):
    ws.conditional_formatting.add(celda_ref, FormulaRule(
        formula=[f'ISNUMBER(SEARCH("NO",{celda_ref}))'], fill=R_NO, font=Font(name=FUENTE, bold=True, color="9C0006")))
    ws.conditional_formatting.add(celda_ref, FormulaRule(
        formula=[f'NOT(ISNUMBER(SEARCH("NO",{celda_ref})))'], fill=R_OK,
        font=Font(name=FUENTE, bold=True, color="006100")))


# ---------------------------------------------------------------------------
def _hoja_unidades(wb):
    ws = wb.create_sheet("Unidades")
    ws["A1"] = "Unidades y constantes de conversión"
    ws["A1"].font = F_TITULO
    ws["A2"] = ("Todas las fórmulas trabajan internamente en tonf y m (ángulos en radianes). Cada unidad es un "
                "nombre definido (u_cm, u_ksi, ...) que convierte a esas unidades base.")
    ws["A2"].font = F_SUB
    for j, t in enumerate(["Nombre Excel", "Unidad", "Valor en base (tonf, m, rad)", "Descripción"], 1):
        c = ws.cell(4, j, t)
        c.font, c.fill, c.alignment = F_ENC, R_ENC, CENTRO
    fila = 5
    for n, (val, desc) in UNIDADES.items():
        ws.cell(fila, 1, "u_" + n).font = F_NEGRITA
        ws.cell(fila, 2, unidad_texto(n)).font = F_NORMAL
        c = ws.cell(fila, 3, val)
        c.font, c.number_format = F_NORMAL, "0.000000000"
        ws.cell(fila, 4, desc).font = F_NORMAL
        _definir(wb, "u_" + n, "Unidades", c)
        fila += 1
    for j, w in enumerate([16, 12, 26, 40], 1):
        ws.column_dimensions[get_column_letter(j)].width = w


def _escribir_var(wb, ws, mod: Modulo, v: Var, fila: int):
    ux = _unidad_xl(v.unidad)
    ws.cell(fila, 1, v.nombre).font = F_NEGRITA
    ws.cell(fila, 2, v.desc).font = F_NORMAL
    ws.cell(fila, 4, unidad_texto(v.unidad)).font = F_NORMAL
    ws.cell(fila, 7, v.ref).font = F_GRIS
    cv, cb = ws.cell(fila, 3), ws.cell(fila, 5)
    if v.tipo == "dato":
        cv.value = v.valor_mostrado
        cv.font, cv.fill = F_DATO, R_DATO
        cv.comment = Comment("Dato editable: cambie este valor y el libro se recalcula.", "puentes2p")
        cb.value = f"=C{fila}*{ux}" if ux else f"=C{fila}"
        ws.cell(fila, 6, "dato").font = F_GRIS
    else:
        cb.value = "=" + _formula(mod, v.expr)
        cv.value = f"=E{fila}/{ux}" if ux else f"=E{fila}"
        cv.font = F_NEGRITA if v.clave else F_NORMAL
        texto = a_texto(v.cond) if v.tipo in ("verif", "sel") else a_texto(v.expr)
        ws.cell(fila, 6, texto if len(texto) < 400 else "(envolvente de carga móvil)").font = F_GRIS
    cv.number_format = _formato(v.valor_mostrado)
    cb.number_format = "General"
    cb.font = F_GRIS
    if v.tipo in ("verif", "sel"):
        cv.alignment = CENTRO
        if v.tipo == "verif":
            _semaforo(ws, f"C{fila}")
    if v.doc is not None:
        ch = ws.cell(fila, 8, v.doc)
        ch.font, ch.number_format = F_GRIS, _formato(v.doc)
        if not isinstance(v.doc, str) and v.doc != 0:
            cd = ws.cell(fila, 9, f"=C{fila}/H{fila}-1")
            cd.number_format, cd.font = "0.0%", F_GRIS
    for j in range(1, 10):
        ws.cell(fila, j).border = BORDE
    _definir(wb, v.xl_nombre, ws.title, cb)


def _escribir_tabla(wb, ws, mod: Modulo, tb: Tabla, fila: int) -> int:
    fila += 1
    c = ws.cell(fila, 1, tb.titulo)
    c.font = Font(name=FUENTE, size=10, bold=True, color="1F3864")
    fila += 1
    for j, (h, u) in enumerate(zip(tb.encabezados, tb.unidades + [""] * len(tb.encabezados)), 1):
        t = h + (f" ({unidad_texto(u)})" if u else "")
        c = ws.cell(fila, j, t)
        c.font, c.fill, c.alignment, c.border = F_NEGRITA, R_TAB, Alignment(horizontal="center", wrap_text=True), BORDE
    fila += 1
    for fr in tb.filas:
        for j, celda in enumerate(fr, 1):
            c = ws.cell(fila, j)
            c.border = BORDE
            c.font = F_NORMAL
            if celda is None:
                continue
            if isinstance(celda, Var):
                ux = _unidad_xl(celda.unidad)
                if celda.tipo == "dato":
                    c.value = celda.valor_mostrado
                    c.font, c.fill = F_DATO, R_DATO
                else:
                    f = _formula(mod, celda.expr)
                    c.value = f"=({f})/{ux}" if ux else "=" + f
                c.number_format = _formato(celda.valor_mostrado)
                c.alignment = Alignment(horizontal="center")
                if celda.tipo == "verif":
                    _semaforo(ws, c.coordinate)
                _definir(wb, celda.xl_nombre, ws.title, c)
            else:
                c.value = celda
                c.font = F_NEGRITA
        fila += 1
    return fila


def _hoja_modulo(wb, mod: Modulo):
    ws = wb.create_sheet(mod.hoja)
    ws["A1"] = mod.titulo
    ws["A1"].font = F_TITULO
    ws["A2"] = mod.descripcion
    ws["A2"].font = F_SUB
    ws["A3"] = ("Celdas amarillas con texto azul = datos editables. Todo lo demás son fórmulas. "
                "La columna E guarda cada valor en unidades base (tonf, m) con nombre definido "
                f"'{mod.codigo}_<símbolo>'.")
    ws["A3"].font = F_NOTA
    for j, (t, w) in enumerate(zip(ENCABEZADOS, ANCHOS), 1):
        c = ws.cell(5, j, t)
        c.font, c.fill, c.alignment = F_ENC, R_ENC, CENTRO
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "C6"
    fila = 6
    for it in mod.items:
        if isinstance(it, Seccion):
            if it.nivel == 1:
                fila += 1
            for j in range(1, 10):
                ws.cell(fila, j).fill = R_SEC1 if it.nivel == 1 else R_SEC2
            ws.cell(fila, 1, it.titulo).font = Font(name=FUENTE, size=11 if it.nivel == 1 else 10, bold=True,
                                                    color="1F3864")
            fila += 1
        elif isinstance(it, Nota):
            ws.cell(fila, 2, it.texto).font = F_NOTA
            fila += 1
        elif isinstance(it, Var):
            _escribir_var(wb, ws, mod, it, fila)
            fila += 1
        elif isinstance(it, Tabla):
            fila = _escribir_tabla(wb, ws, mod, it, fila) + 1
    ws.sheet_view.zoomScale = 90


def _hoja_resumen(wb, modulos):
    ws = wb.create_sheet("Resumen", 1)
    ws["A1"] = "Resumen de resultados y verificaciones"
    ws["A1"].font = F_TITULO
    ws["A2"] = "Todas las celdas de esta hoja son vínculos vivos a las hojas de cálculo."
    ws["A2"].font = F_SUB
    fila = 4
    for j, t in enumerate(["Módulo", "Resultado principal", "Símbolo", "Valor", "Unidad"], 1):
        c = ws.cell(fila, j, t)
        c.font, c.fill, c.alignment = F_ENC, R_ENC, CENTRO
    fila += 1
    for mod in modulos:
        for v in mod.vars.values():
            if v.clave and v.tipo in ("ec", "dato"):
                ux = _unidad_xl(v.unidad)
                ws.cell(fila, 1, mod.codigo).font = F_NORMAL
                ws.cell(fila, 2, v.desc).font = F_NORMAL
                ws.cell(fila, 3, v.nombre).font = F_NEGRITA
                ref = v.xl_nombre if not v.en_tabla else v.xl_nombre
                c = ws.cell(fila, 4, f"={ref}/{ux}" if ux and not v.en_tabla else f"={ref}")
                c.number_format, c.font = _formato(v.valor_mostrado), F_NEGRITA
                ws.cell(fila, 5, unidad_texto(v.unidad)).font = F_NORMAL
                for j in range(1, 6):
                    ws.cell(fila, j).border = BORDE
                fila += 1
    fila += 2
    for j, t in enumerate(["Módulo", "Verificación", "Símbolo", "Resultado", "Hoja"], 1):
        c = ws.cell(fila, j, t)
        c.font, c.fill, c.alignment = F_ENC, R_ENC, CENTRO
    fila += 1
    ini = fila
    for mod in modulos:
        for v in mod.vars.values():
            if v.tipo == "verif" and v.clave:
                ws.cell(fila, 1, mod.codigo).font = F_NORMAL
                ws.cell(fila, 2, v.desc).font = F_NORMAL
                ws.cell(fila, 3, v.nombre).font = F_NEGRITA
                c = ws.cell(fila, 4, f"={v.xl_nombre}")
                c.alignment = CENTRO
                _semaforo(ws, f"D{fila}")
                ws.cell(fila, 5, mod.hoja).font = F_GRIS
                for j in range(1, 6):
                    ws.cell(fila, j).border = BORDE
                fila += 1
    ws.cell(fila + 1, 2, "Verificaciones que no cumplen:").font = F_NEGRITA
    c = ws.cell(fila + 1, 4, f'=COUNTIF(D{ini}:D{fila - 1},"NO*")')
    c.font, c.alignment = F_NEGRITA, CENTRO
    for j, w in enumerate([10, 62, 16, 18, 22], 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A5"


def _hoja_inicio(wb, modulos, titulo):
    ws = wb.active
    ws.title = "Inicio"
    ws["A1"] = titulo
    ws["A1"].font = Font(name=FUENTE, size=16, bold=True, color="1F3864")
    ws["A2"] = "Puente tipo losa-vigas preforzadas - memoria de cálculo automatizada"
    ws["A2"].font = F_SUB
    lineas = [
        ("Cómo usar este libro", None),
        ("1. Modifique únicamente las celdas amarillas con texto azul (datos). Todo lo demás son fórmulas.", None),
        ("2. Excel recalcula todas las hojas automáticamente; la hoja 'Resumen' muestra resultados y "
         "verificaciones (verde = cumple, rojo = no cumple).", None),
        ("3. Cada valor se guarda también en unidades base (tonf, m) en la columna E con un nombre definido "
         "'<HOJA>_<símbolo>' (Fórmulas > Administrador de nombres).", None),
        ("4. Las columnas 'Valor PDF' y 'Dif. vs PDF' comparan con la memoria original (Puentes_2P_calculos.pdf).",
         None),
        ("5. El mismo modelo se ejecuta en Python (puentes_2p.py) y genera el reporte LaTeX/PDF.", None),
        ("", None),
        ("Hojas", None),
    ]
    fila = 4
    for t, _ in lineas:
        c = ws.cell(fila, 1, t)
        c.font = F_NEGRITA if t in ("Cómo usar este libro", "Hojas") else F_NORMAL
        fila += 1
    for mod in modulos:
        c = ws.cell(fila, 1, mod.hoja)
        c.hyperlink = f"#'{mod.hoja}'!A1"
        c.font = Font(name=FUENTE, size=10, color="0563C1", underline="single")
        ws.cell(fila, 2, mod.titulo).font = F_NORMAL
        fila += 1
    for nombre, desc in (("Resumen", "Resultados principales y verificaciones"),
                         ("Unidades", "Constantes de conversión de unidades")):
        c = ws.cell(fila, 1, nombre)
        c.hyperlink = f"#'{nombre}'!A1"
        c.font = Font(name=FUENTE, size=10, color="0563C1", underline="single")
        ws.cell(fila, 2, desc).font = F_NORMAL
        fila += 1
    fila += 1
    ws.cell(fila, 1, "Leyenda").font = F_NEGRITA
    c = ws.cell(fila + 1, 1, 12.5)
    c.font, c.fill = F_DATO, R_DATO
    ws.cell(fila + 1, 2, "Dato editable").font = F_NORMAL
    ws.cell(fila + 2, 1, "=A" + str(fila + 1) + "*2").font = F_NORMAL
    ws.cell(fila + 2, 2, "Resultado de fórmula").font = F_NORMAL
    c = ws.cell(fila + 3, 1, "OK")
    c.fill, c.font = R_OK, Font(name=FUENTE, bold=True, color="006100")
    ws.cell(fila + 3, 2, "Verificación que cumple").font = F_NORMAL
    c = ws.cell(fila + 4, 1, "NO OK")
    c.fill, c.font = R_NO, Font(name=FUENTE, bold=True, color="9C0006")
    ws.cell(fila + 4, 2, "Verificación que no cumple").font = F_NORMAL
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 90


def escribir_excel(modulos: list[Modulo], ruta: str, titulo="Diseño de Puentes - 2P"):
    wb = Workbook()
    for mod in modulos:
        _preparar_referencias(mod)
    _hoja_inicio(wb, modulos, titulo)
    for mod in modulos:
        _hoja_modulo(wb, mod)
    _hoja_resumen(wb, modulos)
    _hoja_unidades(wb)
    wb.calculation.fullCalcOnLoad = True
    wb.save(ruta)
    return ruta
