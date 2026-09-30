"""Generador del reporte LaTeX (memoria de cálculo) a partir del mismo modelo."""
from __future__ import annotations

import ast
import datetime as _dt
import math
import os
import shutil
import subprocess

from .motor import Modulo, Nota, Seccion, Tabla, Var, a_tex, escapar_tex, unidad_tex

PREAMBULO = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-nodecimaldot,es-noquoting,es-noshorthands]{babel}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage[margin=2cm,headheight=14pt]{geometry}
\usepackage{booktabs,longtable,array}
\usepackage{adjustbox}
\usepackage[table]{xcolor}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\definecolor{azul}{HTML}{1F3864}
\definecolor{verde}{HTML}{006100}
\definecolor{rojo}{HTML}{9C0006}
\definecolor{fondodato}{HTML}{FFFFCC}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textsc{Diseño de Puentes - 2P}}
\fancyhead[R]{\small\nouppercase{\leftmark}}
\fancyfoot[C]{\small\thepage}
\setlength{\parindent}{0pt}
\setcounter{secnumdepth}{1}
\allowdisplaybreaks
\newcommand{\ok}[1]{\textcolor{verde}{\textbf{#1}}}
\newcommand{\nook}[1]{\textcolor{rojo}{\textbf{#1}}}
\newcommand{\info}[1]{\textcolor{azul}{\textbf{#1}}}
\newcommand{\eqitem}[3]{\par\noindent\begin{minipage}{\linewidth}{\small #1}\hfill{\scriptsize\textcolor{gray}{#2}}\\[2pt]
  \hspace*{1.5em}\adjustbox{max width=\dimexpr\linewidth-1.5em\relax}{$\displaystyle #3$}\end{minipage}\par\smallskip}
\newcommand{\nota}[1]{\par\noindent{\small\itshape\textcolor{black!70}{#1}}\par\smallskip}
"""


def fmt(v) -> str:
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return str(v)
    if v == 0:
        return "0"
    a = abs(v)
    if abs(v - round(v)) <= 1e-9 * max(1.0, a) and a < 1e7:
        s = f"{int(round(v)):,}"
    elif a >= 1000:
        s = f"{v:,.2f}"
    elif a >= 100:
        s = f"{v:.2f}"
    elif a >= 1:
        s = f"{v:.3f}"
    elif a >= 0.01:
        s = f"{v:.4f}"
    else:
        e = int(math.floor(math.log10(a)))
        mant = v / 10 ** e
        return f"{mant:.3f}\\times10^{{{e}}}"
    return s.replace(",", "\\,")


def _valor_tex(v: Var) -> str:
    val = v.valor_mostrado
    if isinstance(val, str):
        return _res_tex(v, val)
    u = unidad_tex(v.unidad)
    return r"\mathbf{" + fmt(val) + "}" + u


def _res_tex(v: Var, val: str) -> str:
    txt = escapar_tex(val)
    if v.tipo == "sel":
        return r"\text{\info{" + txt + "}}"
    if "NO" in val.upper():
        return r"\text{\nook{" + txt + "}}"
    return r"\text{\ok{" + txt + "}}"


def _ecuacion(mod: Modulo, v: Var) -> str:
    sim = mod.simbolo(v.nombre)
    if v.tipo in ("verif", "sel"):
        cond = a_tex(ast.parse(v.cond, mode="eval"), mod.simbolo)
        return cond + r"\;\;\Rightarrow\;\;" + _res_tex(v, v.valor)
    partes = [sim]
    if v.ftex:
        partes.append(v.ftex)
    elif v.mostrar_expr:
        arbol = ast.parse(v.expr, mode="eval")
        cuerpo = a_tex(arbol, mod.simbolo)
        if len(v.expr) > 600:
            cuerpo = r"\text{(envolvente)}"
        if not (isinstance(arbol.body, ast.Constant)):
            partes.append(cuerpo)
    partes.append(_valor_tex(v))
    return " = ".join(partes)


def _tabla_datos(mod: Modulo, datos: list[Var]) -> str:
    filas = []
    for v in datos:
        filas.append(f"${mod.simbolo(v.nombre)}$ & {escapar_tex(v.desc)} & "
                     f"\\cellcolor{{fondodato}}{fmt(v.valor_mostrado)} & ${unidad_tex(v.unidad).replace(chr(92) + ',', '')}$"
                     f" & {{\\scriptsize {escapar_tex(v.ref)}}} \\\\")
    return ("\\begin{longtable}{@{}l p{0.52\\linewidth} r l l@{}}\n\\toprule\n"
            "\\textbf{Dato} & \\textbf{Descripción} & \\textbf{Valor} & \\textbf{Unidad} & \\textbf{Ref.}\\\\\n"
            "\\midrule\n" + "\n".join(filas) + "\n\\bottomrule\n\\end{longtable}\n")


def _celda_tex(c) -> str:
    if c is None:
        return ""
    if isinstance(c, Var):
        val = c.valor_mostrado
        if isinstance(val, str):
            if "NO" in val.upper():
                return r"\nook{" + escapar_tex(val) + "}"
            return r"\ok{" + escapar_tex(val) + "}"
        s = "$" + fmt(val) + "$"
        if c.tipo == "dato":
            return r"\cellcolor{fondodato}" + s
        return s
    return escapar_tex(str(c))


def _tabla(tb: Tabla) -> str:
    n = len(tb.encabezados)
    enc = []
    for h, u in zip(tb.encabezados, tb.unidades + [""] * n):
        t = r"\textbf{" + escapar_tex(h) + "}"
        if u:
            t += r"\\ {\scriptsize $" + unidad_tex(u).replace("\\,", "") + "$}"
        enc.append(r"\begin{tabular}[b]{@{}c@{}}" + t + r"\end{tabular}")
    cuerpo = [" & ".join(_celda_tex(c) for c in fila) + r" \\" for fila in tb.filas]
    return ("\\begin{center}\n{\\small\\textbf{" + escapar_tex(tb.titulo) + "}}\\\\[3pt]\n"
            "\\adjustbox{max width=\\linewidth}{\\begin{tabular}{" + "c" * n + "}\n\\toprule\n"
            + " & ".join(enc) + r" \\" + "\n\\midrule\n" + "\n".join(cuerpo) + "\n\\bottomrule\n\\end{tabular}}\n"
            "\\end{center}\n")


def _modulo(mod: Modulo) -> str:
    out = [f"\\section{{{escapar_tex(mod.titulo)}}}\n", f"\\nota{{{escapar_tex(mod.descripcion)}}}\n"]
    datos: list[Var] = []

    def vaciar():
        if datos:
            out.append(_tabla_datos(mod, datos))
            datos.clear()

    for it in mod.items:
        if isinstance(it, Var) and it.tipo == "dato":
            datos.append(it)
            continue
        vaciar()
        if isinstance(it, Seccion):
            out.append(("\\subsection" if it.nivel == 1 else "\\subsubsection") + "{" + escapar_tex(it.titulo) + "}\n")
        elif isinstance(it, Nota):
            out.append("\\nota{" + escapar_tex(it.texto) + "}\n")
        elif isinstance(it, Tabla):
            out.append(_tabla(it))
        elif isinstance(it, Var):
            out.append("\\eqitem{" + escapar_tex(it.desc) + "}{" + escapar_tex(it.ref) + "}{"
                       + _ecuacion(mod, it) + "}\n")
    vaciar()
    return "\n".join(out)


def _resumen(modulos: list[Modulo]) -> str:
    filas_r, filas_v = [], []
    for mod in modulos:
        for v in mod.vars.values():
            if v.clave and v.tipo in ("ec", "dato"):
                filas_r.append(f"{mod.codigo} & {escapar_tex(v.desc)} & ${mod.simbolo(v.nombre)}$ & "
                               f"${fmt(v.valor_mostrado)}${'$' + unidad_tex(v.unidad) + '$' if v.unidad else ''} \\\\")
            if v.tipo == "verif" and v.clave:
                filas_v.append(f"{mod.codigo} & {escapar_tex(v.desc)} & {_celda_tex(v)} \\\\")
    nno = sum(1 for m in modulos for v in m.vars.values()
              if v.tipo == "verif" and v.clave and "NO" in str(v.valor).upper())
    return ("\\section*{Resumen de resultados}\n\\addcontentsline{toc}{section}{Resumen de resultados}\n\\markboth{Resumen de resultados}{Resumen de resultados}\n"
            "\\begin{longtable}{@{}l p{0.55\\linewidth} l r@{}}\n\\toprule\n"
            "\\textbf{Mód.} & \\textbf{Resultado} & \\textbf{Símbolo} & \\textbf{Valor}\\\\\n\\midrule\n\\endhead\n"
            + "\n".join(filas_r) + "\n\\bottomrule\n\\end{longtable}\n"
            "\\subsection*{Verificaciones}\n"
            f"\\nota{{Total de verificaciones: {len(filas_v)}; no cumplen: {nno}.}}\n"
            "\\begin{longtable}{@{}l p{0.7\\linewidth} c@{}}\n\\toprule\n"
            "\\textbf{Mód.} & \\textbf{Verificación} & \\textbf{Resultado}\\\\\n\\midrule\n\\endhead\n"
            + "\n".join(filas_v) + "\n\\bottomrule\n\\end{longtable}\n\\clearpage\n")


def escribir_latex(modulos: list[Modulo], ruta: str, titulo="Diseño de Puentes - 2P",
                   autor="Memoria de cálculo automatizada") -> str:
    fecha = _dt.date.today().strftime("%d/%m/%Y")
    intro = (
        "\\section*{Introducción}\n\\addcontentsline{toc}{section}{Introducción}\n\\markboth{Introducción}{Introducción}\n"
        "Esta memoria reproduce, de forma automatizada, los cálculos del documento "
        "\\emph{Puentes\\_2P\\_calculos.pdf} (puente tipo losa-vigas preforzadas). "
        "Cada ecuación se define una sola vez en Python; a partir de esa definición se generan "
        "(1) los valores de este reporte, (2) las fórmulas vivas del libro Excel "
        "\\texttt{Puentes\\_2P.xlsx} y (3) las ecuaciones que se muestran aquí.\n\n"
        "Los cálculos internos se realizan en tonf y m; las unidades (cm, kip, ksi, psi, MPa, ...) "
        "actúan como factores de conversión, igual que en Mathcad. Los datos de entrada se muestran "
        "con fondo amarillo. Las verificaciones se indican en \\ok{verde} (cumple) o \\nook{rojo} "
        "(no cumple); las selecciones informativas en \\info{azul}.\n\n"
        "Las cargas vivas móviles (camión HS20, camión de fatiga) se calculan con líneas de influencia "
        "de la viga simplemente apoyada, colocando cada eje sobre la sección de análisis en ambos "
        "sentidos de circulación (envolvente exacta).\n\\clearpage\n")
    doc = [PREAMBULO,
           "\\title{\\color{azul}\\textbf{" + escapar_tex(titulo) + "}\\\\[4pt]\\large Puente tipo losa-vigas "
           "preforzadas: superestructura, pila, viga cabezal y estribo}",
           "\\author{" + escapar_tex(autor) + "}", "\\date{" + fecha + "}",
           "\\begin{document}", "\\maketitle", "\\tableofcontents", "\\clearpage", intro, _resumen(modulos)]
    for mod in modulos:
        doc.append(_modulo(mod))
        doc.append("\\clearpage")
    doc.append("\\end{document}\n")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(doc))
    return ruta


def compilar_pdf(ruta_tex: str) -> str | None:
    """Compila con pdflatex (dos pasadas para el índice). Devuelve la ruta del PDF o None."""
    exe = shutil.which("pdflatex")
    if not exe:
        return None
    d = os.path.dirname(os.path.abspath(ruta_tex))
    nombre = os.path.basename(ruta_tex)
    for _ in range(2):
        r = subprocess.run([exe, "-interaction=nonstopmode", "-halt-on-error", nombre], cwd=d,
                           capture_output=True, text=True)
        if r.returncode != 0:
            log = r.stdout[-3000:]
            raise RuntimeError("Error de pdflatex:\n" + log)
    base = os.path.splitext(ruta_tex)[0]
    for ext in (".aux", ".log", ".toc", ".out"):
        try:
            os.remove(base + ext)
        except OSError:
            pass
    return base + ".pdf"
