"""Registro de los módulos de cálculo, en el orden del PDF original."""
from . import m1_viga_std, m2_viga_lrfd, m3_m4_pilas, m5_m6_m7, m8_estribo

MODULOS = [
    ("STD", m1_viga_std.construir),
    ("LRFD", m2_viga_lrfd.construir),
    ("PAC", m3_m4_pilas.construir_acero),
    ("PPR", m3_m4_pilas.construir_preforzada),
    ("VC", m5_m6_m7.construir_cabezal),
    ("FR", m5_m6_m7.construir_frenado),
    ("RE", m5_m6_m7.construir_reaccion),
    ("EST", m8_estribo.construir),
]


def construir_todos(sobrescribir: dict | None = None, solo: list[str] | None = None):
    sobrescribir = sobrescribir or {}
    return [f(sobrescribir.get(cod, {})) for cod, f in MODULOS if not solo or cod in solo]
