"""Módulos 3 y 4 - Descarga por carga muerta de la superestructura sobre una pila.
Págs. 31-32 (vigas de acero) y 33-34 (vigas preforzadas) del PDF."""
from ..motor import C, D, Modulo


def _datos_comunes(m: Modulo):
    m.sec("Datos")
    m.dato("Lp", 120, "m", "Longitud del puente")
    m.dato("Lt", 30, "m", "Longitud del tramo")
    m.dato("Atp", 10, "m", "Ancho del tablero")
    m.sec("Altura y separación de vigas")
    m.tabla("Distribución transversal",
            ["Descripción", "Unidad", "Cantidad", "Total"], ["", "m", "", "m"],
            [["Separación vigas", D("sv_u", 2.5), D("sv_n", 3), C("sv_t", "sv_u*sv_n")],
             ["Longitud voladizo", D("vo_u", 1.25), D("vo_n", 2), C("vo_t", "vo_u*vo_n")],
             ["Ancho total puente", None, None, C("an_t", "sv_t+vo_t")]])
    m.verif("chk_ancho", "AND(an_t>=Atp-0.001,an_t<=Atp+0.001)", "Distribución transversal = ancho del tablero")
    m.sec("Peso de la losa")
    m.dato("el", 7, "inch", "Espesor mínimo de losa", tex="e_l")
    m.dato("ea", 0.2, "m", "Espesor de losa asumido", tex="e_a")
    m.verif("chk_el", "ea>=el", "Espesor asumido ≥ mínimo")
    m.dato("PUha", 2.4, "tonf/m**3", "Peso unitario del hormigón armado", tex=r"\gamma_{ha}")
    m.ec("Wl", "ea*Atp*Lt*PUha", "tonf", "Peso total de la losa", doc=144)


def _barrera_y_otros(m: Modulo):
    m.sec("Peso de barrera")
    m.nota("Sección de barrera descompuesta en rectángulos y triángulos; brazo medido desde el borde exterior.")
    geo = [("A1", 0.15, 0.525, 1, "b_1/2"), ("A2", 0.05, 0.525, 0.5, "b_1+b_2/3"),
           ("A3", 0.2, 0.25, 1, "b_3/2"), ("A4", 0.175, 0.25, 0.5, "b_3+b_4/3"), ("A5", 0.375, 0.075, 1, "b_5/2")]
    filas = []
    for k, (n, b, h, f, x) in enumerate(geo, 1):
        filas.append([n, D(f"b_{k}", b), D(f"h_{k}", h), D(f"f_{k}", f), C(f"Ar_{k}", f"f_{k}*b_{k}*h_{k}"),
                      C(f"wb_{k}", f"Ar_{k}*PUha"), C(f"xb_{k}", x), C(f"mb_{k}", f"wb_{k}*xb_{k}")])
    m.tabla("Sección de la barrera", ["Elemento", "Base", "Altura", "Factor forma", "Área", "Peso",
                                      "C.G.", "Momento"],
            ["", "m", "m", "", "m**2", "tonf/m", "m", "tonf*m/m"], filas)
    m.ec("Abar", "+".join(f"Ar_{k}" for k in range(1, 6)), "m**2", "Área de la barrera", ftex=r"\sum A_i",
         doc=0.19188)
    m.ec("wbar", "+".join(f"wb_{k}" for k in range(1, 6)), "tonf/m", "Peso de la barrera", tex="w_b", ftex=r"\sum w_i",
         doc=0.4605)
    m.ec("Mbar", "+".join(f"mb_{k}" for k in range(1, 6)), "tonf*m/m", "Momento respecto al borde",
         ftex=r"\sum w_i x_i", doc=0.058)
    m.ec("xcg_b", "Mbar/wbar", "m", "C.G. de la barrera", doc=0.125)
    m.ec("Wb", "wbar*(2*Lt)", "tonf", "Peso total de las barreras", doc=27.63)
    m.sec("Peso de carpeta asfáltica")
    m.ec("Ab", "b_5", "m", "Ancho de la barrera", doc=0.375)
    m.ec("Aca", "Atp-2*Ab", "m", "Ancho de carpeta asfáltica", doc=9.25)
    m.dato("eca", 0.05, "m", "Espesor de carpeta asfáltica")
    m.dato("PUasf", 2.3, "tonf/m**3", "Peso unitario del hormigón asfáltico", tex=r"\gamma_{asf}")
    m.ec("Wca", "eca*Aca*PUasf*Lt", "tonf", "Peso de carpeta asfáltica", doc=31.91)
    m.sec("Peso de instalaciones")
    m.dato("q_inst", 0.03, "tonf/m**2", "Postes de alumbrado y demás", tex="w_{inst}")
    m.ec("Winst", "q_inst*Lt*Atp", "tonf", "Peso total de instalaciones", tex="W_{inst,total}", doc=9)


def construir_acero(sobrescribir=None) -> Modulo:
    m = Modulo("PAC", "Descarga CM sobre una pila - vigas de acero", "3_Pila_Acero",
               "Descarga por carga muerta de la superestructura (vigas de acero) sobre una pila.", sobrescribir)
    _datos_comunes(m)
    m.sec("Peso de las vigas de acero")
    m.ec("hvm", "0.04*Lt", "m", "Altura de la viga (0.04 L, AASHTO T. 2.5.2.6.3-1)", doc=1.2)
    m.dato("hvma", 1.20, "m", "Altura de viga adoptada")
    m.dato("PUa", 7.85, "tonf/m**3", "Peso unitario del acero", tex=r"\gamma_a")
    m.tabla("Sección de la viga", ["Sección", "D1", "D2", "Área"], ["", "m", "m", "m**2"],
            [["Patín sup.", D("D1_1", 0.35), D("D2_1", 0.0254), C("Sa_1", "D1_1*D2_1")],
             ["Alma", D("D1_2", 1.35), D("D2_2", 0.0125), C("Sa_2", "D1_2*D2_2")],
             ["Patín inf.", D("D1_3", 0.35), D("D2_3", 0.0254), C("Sa_3", "D1_3*D2_3")]])
    m.ec("Svm", "ROUND(Sa_1+Sa_2+Sa_3,4)", "m**2", "Sección de la viga (redondeada)", doc=0.0347)
    m.ec("wvm", "PUa*Svm*Lt", "tonf", "Peso de una viga", doc=8.17)
    m.dato("Nvm", 4, "", "Número de vigas")
    m.ec("Wtvm", "wvm*Nvm", "tonf", "Peso total de las vigas", doc=32.69)
    m.ec("Wd", "0.05*Wtvm", "tonf", "Peso del diafragma metálico (5 % de las vigas)", doc=1.63)
    _barrera_y_otros(m)
    m.sec("Peso total de los componentes")
    m.ec("Wtotal", "Wtvm+Wd+Wb+Wca+Wl+Winst", "tonf", "Peso total", doc=246.86, clave=True)
    m.ec("W", "Wtotal/(Lt*Atp)", "tonf/m**2", "Peso aferente a la pila", doc=0.82, clave=True)
    return m


def construir_preforzada(sobrescribir=None) -> Modulo:
    m = Modulo("PPR", "Descarga CM sobre una pila - vigas preforzadas", "4_Pila_Preforzada",
               "Descarga por carga muerta de la superestructura (vigas AASHTO IV) sobre una pila.", sobrescribir)
    _datos_comunes(m)
    m.sec("Peso de las vigas preforzadas (AASHTO tipo IV)")
    m.dato("wvp", 0.822, "kip/ft", "Peso por metro de la viga", doc=0.822)
    m.ec("w1vp", "wvp*Lt", "tonf", "Peso de una viga", doc=36.7)
    m.dato("Nvm", 4, "", "Número de vigas")
    m.ec("Wtvm", "w1vp*Nvm", "tonf", "Peso total de las vigas", doc=146.79)
    m.sec("Peso de diafragmas")
    m.dato("Sv", 2.5, "m", "Separación de vigas")
    m.dato("hd", 54, "inch", "Altura del diafragma")
    m.dato("Ad", 0.25, "m", "Ancho del diafragma")
    m.dato("Ld", 2.3, "m", "Longitud del diafragma")
    m.ec("wd", "hd*Ad*Ld*PUha", "tonf", "Peso de un diafragma", doc=1.89)
    m.dato("Nd", 12, "", "Número de diafragmas")
    m.ec("Wdha", "Nd*wd", "tonf", "Peso total de diafragmas", doc=22.71)
    _barrera_y_otros(m)
    m.sec("Peso total de los componentes")
    m.ec("Wtotal", "Wtvm+Wdha+Wb+Wca+Wl+Winst", "tonf", "Peso total", doc=382.05, clave=True)
    m.ec("W", "Wtotal/(Lt*Atp)", "tonf/m**2", "Peso aferente a la pila", doc=1.27, clave=True)
    return m
