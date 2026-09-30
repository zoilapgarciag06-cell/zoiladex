#!/usr/bin/env python3
"""
Diseño de Puentes - 2P: memoria de cálculo automatizada.

Ejecuta los 8 módulos de cálculo del documento "Puentes_2P_calculos.pdf" y genera:
  * salida/Puentes_2P.xlsx          libro Excel con fórmulas vivas (datos editables en amarillo)
  * salida/Reporte_Puentes_2P.tex   reporte LaTeX
  * salida/Reporte_Puentes_2P.pdf   reporte compilado (si pdflatex está disponible)

Ejemplos:
  python puentes_2p.py
  python puentes_2p.py --set STD.Nt=46 --set LRFD.L1=38 --salida caso2
  python puentes_2p.py --modulos STD,LRFD --sin-pdf
  python puentes_2p.py --verificar        # recalcula el Excel con LibreOffice y lo compara con Python

Los valores de --set se dan en las unidades de despliegue del dato (las que muestra el Excel).
"""
from __future__ import annotations

import argparse
import os
import sys

from puentes2p import MODULOS, construir_todos
from puentes2p.excel import escribir_excel
from puentes2p.latex import compilar_pdf, escribir_latex
from puentes2p.motor import ErrorModelo


def _parse_set(items):
    out: dict[str, dict[str, float]] = {}
    for it in items or []:
        try:
            clave, val = it.split("=", 1)
            mod, nombre = clave.split(".", 1)
            out.setdefault(mod.upper(), {})[nombre] = float(val)
        except ValueError:
            sys.exit(f"--set inválido: '{it}'. Use MODULO.nombre=valor, p. ej. STD.Nt=46")
    return out


def _comparar_pdf(modulos):
    filas = []
    for m in modulos:
        for v in m.vars.values():
            if v.doc is None:
                continue
            val = v.valor_mostrado
            if isinstance(v.doc, str):
                if val != v.doc:
                    filas.append((m.codigo, v.nombre, val, v.doc))
            elif abs(val - v.doc) > max(0.012 * abs(v.doc), 0.006 if abs(v.doc) < 1 else 0.0):
                filas.append((m.codigo, v.nombre, val, v.doc))
    return filas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", default="salida", help="carpeta de salida (por defecto: salida)")
    ap.add_argument("--set", action="append", metavar="MOD.nombre=valor", help="modifica un dato de entrada")
    ap.add_argument("--modulos", help="lista de módulos a ejecutar: " + ",".join(c for c, _ in MODULOS))
    ap.add_argument("--sin-excel", action="store_true")
    ap.add_argument("--sin-latex", action="store_true")
    ap.add_argument("--sin-pdf", action="store_true")
    ap.add_argument("--verificar", action="store_true", help="recalcula el Excel con LibreOffice y lo compara")
    a = ap.parse_args(argv)

    sob = _parse_set(a.set)
    solo = [s.strip().upper() for s in a.modulos.split(",")] if a.modulos else None
    try:
        modulos = construir_todos(sob, solo)
    except ErrorModelo as e:
        sys.exit(f"Error en el modelo: {e}")
    for cod, cambios in sob.items():
        for nombre in cambios:
            mods = [m for m in modulos if m.codigo == cod]
            if not mods or nombre not in mods[0].vars or mods[0].vars[nombre].tipo != "dato":
                sys.exit(f"--set: '{cod}.{nombre}' no es un dato de entrada")

    os.makedirs(a.salida, exist_ok=True)
    print("=" * 78)
    print(" DISEÑO DE PUENTES - 2P   |   memoria de cálculo automatizada")
    print("=" * 78)
    total_no = 0
    for m in modulos:
        vf = [v for v in m.vars.values() if v.tipo == "verif" and v.clave]
        no = [v for v in vf if "NO" in str(v.valor).upper()]
        total_no += len(no)
        print(f" [{m.codigo:4s}] {m.titulo:<58s} {len(m.vars):4d} var | {len(vf):3d} verif | {len(no)} no cumplen")
        for v in no:
            print(f"          - {v.desc}: {v.valor}")
    print("-" * 78)
    print(" Resultados principales:")
    for m in modulos:
        for v in m.vars.values():
            if v.clave and v.tipo in ("ec", "dato"):
                val = v.valor_mostrado
                from puentes2p.motor import unidad_texto
                print(f"   {m.codigo:4s} {v.desc[:52]:<52s} {v.nombre:>10s} = {val:12.4f} {unidad_texto(v.unidad)}")
    difs = _comparar_pdf(modulos)
    if not sob:
        print("-" * 78)
        print(f" Comparación con el PDF original: {len(difs)} diferencias > 1.2 %")
        for d in difs:
            print(f"   {d[0]}.{d[1]}: Python = {d[2]}  PDF = {d[3]}")

    if not a.sin_excel:
        rx = escribir_excel(modulos, os.path.join(a.salida, "Puentes_2P.xlsx"))
        print(f"\n Excel  -> {rx}")
        if a.verificar:
            from puentes2p.verificar import comparar, recalcular_libreoffice
            rec = recalcular_libreoffice(rx)
            if rec is None:
                print("   (LibreOffice no disponible: no se pudo verificar)")
            else:
                n, err = comparar(modulos, rec)
                print(f"   Verificación Excel vs Python: {n} celdas, {len(err)} diferencias")
                for e in err[:20]:
                    print("    ", e)
    if not a.sin_latex:
        rt = escribir_latex(modulos, os.path.join(a.salida, "Reporte_Puentes_2P.tex"))
        print(f" LaTeX  -> {rt}")
        if not a.sin_pdf:
            try:
                pdf = compilar_pdf(rt)
                print(f" PDF    -> {pdf}" if pdf else " PDF    -> (pdflatex no disponible)")
            except RuntimeError as e:
                print(str(e))
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
