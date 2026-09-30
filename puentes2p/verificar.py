"""Verificación cruzada Python <-> Excel.

Recalcula el libro con LibreOffice (si está instalado) y compara cada celda con nombre
definido contra el valor calculado en Python.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from openpyxl import load_workbook


def recalcular_libreoffice(ruta: str, timeout: int = 300) -> str | None:
    """Recalcula una copia del libro con LibreOffice headless.
    Devuelve la ruta de la copia recalculada (en un directorio temporal) o None."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    tmp = tempfile.mkdtemp(prefix="puentes2p_")
    cmd = [soffice, "--headless", "--norestore", f"-env:UserInstallation=file://{tmp}/perfil",
           "--convert-to", "xlsx", "--outdir", os.path.join(tmp, "out"), os.path.abspath(ruta)]
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return None
    generado = os.path.join(tmp, "out", os.path.basename(ruta))
    return generado if os.path.exists(generado) else None


def comparar(modulos, ruta_recalculada: str, tol: float = 1e-6):
    wb = load_workbook(ruta_recalculada, data_only=True)
    errores, n = [], 0
    for mod in modulos:
        for v in mod.vars.values():
            dn = wb.defined_names.get(v.xl_nombre)
            if dn is None:
                errores.append((mod.codigo, v.nombre, "sin nombre definido", None))
                continue
            hoja, coord = next(iter(dn.destinations))
            val = wb[hoja][coord.replace("$", "")].value
            esperado = v.valor_mostrado if v.en_tabla else v.valor
            n += 1
            if isinstance(esperado, str) or isinstance(val, str):
                if val != esperado:
                    errores.append((mod.codigo, v.nombre, esperado, val))
            elif isinstance(esperado, bool):
                continue
            else:
                if val is None or abs(val - esperado) > tol * max(1.0, abs(esperado)):
                    errores.append((mod.codigo, v.nombre, esperado, val))
    return n, errores
