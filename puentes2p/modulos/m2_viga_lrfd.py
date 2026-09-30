"""Módulo 2 - Viga interior preforzada. AASHTO LRFD. Págs. 14-30 del PDF."""
from ..motor import C, D, Modulo, envolvente_cortante, envolvente_momento, suma
from .m1_viga_std import _seccion_compuesta

SECCIONES = ["0", "0.06", "0.1", "0.2", "0.3", "0.4", "0.5"]


def construir(sobrescribir=None) -> Modulo:
    m = Modulo("LRFD", "Viga interior preforzada - AASHTO LRFD", "2_Viga_LRFD",
               "Puente tipo losa-vigas preforzadas. Viga AASHTO-PCI Bulb-Tee BT-72. "
               "Diseño según especificaciones AASHTO LRFD (carga HL-93: camión HS20-44 + carril).",
               sobrescribir)

    # ------------------------------------------------------------------ 2
    m.sec("2. Materiales")
    m.dato("ts", 19, "cm", "Espesor de la losa interior")
    m.dato("tws", 1.0, "cm", "Sobre-espesor de desgaste")
    m.ec("t", "ts+tws", "cm", "Espesor total", doc=20)
    m.dato("to", 20, "cm", "Espesor de la losa en el voladizo", tex="t_o")
    m.dato("fcd1", 280, "kgf/cm**2", "f'c de diseño de la losa", tex=r"f'_{c,d1}")
    m.dato("fcd2", 450, "kgf/cm**2", "f'c de diseño de la viga", tex=r"f'_{c,d2}")
    m.dato("fci", 405, "kgf/cm**2", "f'c de la viga en la transferencia", tex=r"f'_{ci}")
    m.dato("Wc", 2.4, "tonf/m**3", "Peso unitario del hormigón")
    m.dato("L2", 36.9, "m", "Longitud total de la viga")
    m.dato("L1", 36.6, "m", "Tramo de diseño")
    m.dato("dt", 0.5, "inch", "Diámetro del torón (7 alambres, baja relajación)", tex="d_t")
    m.dato("fpu", 19, "tonf/cm**2", "Resistencia a la tensión del torón")
    m.dato("Ast", 98.7, "mm**2", "Área de un torón")
    m.ec("fpy", "0.9*fpu", "tonf/cm**2", "Resistencia a la fluencia", "LRFD T. 5.4.4.1-1", doc=17.1)
    m.nota("Esfuerzos límites para los torones [LRFD T. 5.9.3-1].")
    m.ec("fpi", "0.75*fpu", "tonf/cm**2", "Antes de la transferencia (fpi ≤ 0.75 fpu)", doc=14.25)
    m.ec("fpe_lim", "0.8*fpy", "tonf/cm**2", "Estado límite de servicio (después de pérdidas)",
         tex=r"f_{pe,lim}", doc=13.68)
    m.dato("Ep", 2003.748, "tonf/cm**2", "Módulo de elasticidad del torón", "LRFD T. 5.4.4.2")
    m.dato("fy", 4.2, "tonf/cm**2", "Fluencia del acero de refuerzo")
    m.dato("Es", 2038.902, "tonf/cm**2", "Módulo de elasticidad del acero de refuerzo", "LRFD T. 5.4.3.2")
    m.dato("fws", 5, "cm", "Espesor de la capa de rodadura")
    m.dato("Wb", 0.4465, "tonf/m", "Peso de la barrera New Jersey (por lado)")

    # ------------------------------------------------------------------ 3
    m.sec("3. Propiedades de la sección transversal de una viga interior")
    m.sec("3.1 Sección no compuesta", 2)
    m.dato("Ag", 0.4948, "m**2", "Área de la viga")
    m.dato("hg", 182.88, "cm", "Altura de la viga")
    m.dato("Ig", 0.22722, "m**4", "Inercia de la viga")
    m.dato("yb", 92.964, "cm", "CG - fibra inferior")
    m.ec("yt", "hg-yb", "cm", "CG - fibra superior", doc=89.92)
    m.ec("Sb", "Ig/yb", "m**3", "Módulo de sección, fibra inferior", doc=0.24)
    m.ec("St", "Ig/yt", "m**3", "Módulo de sección, fibra superior", doc=0.25)
    m.ec("Wg", "Ag*Wc", "tonf/m", "Peso de la viga", doc=1.19)
    ec_e = "33000*(Wc/(kip/ft**3))**1.5*SQRT({f}/ksi)*ksi"
    m.ec("Ec", ec_e.format(f="fcd1"), "tonf/cm**2", "M.E. de la losa", "LRFD Eq. 5.4.2.4-1", doc=268.52)
    m.ec("Eci", ec_e.format(f="fci"), "tonf/cm**2", "M.E. de la viga en la transferencia", doc=322.94)
    m.ec("Ecs", ec_e.format(f="fcd2"), "tonf/cm**2", "M.E. de la viga (cargas de servicio)", doc=340.41)

    m.sec("3.2 Sección compuesta. Ancho efectivo del ala [LRFD 4.6.2.6.1]", 2)
    m.ec("bea1", "0.25*L1", "cm", "1/4 del tramo de diseño", doc=915)
    m.dato("S", 275, "cm", "Separación entre vigas (promedio)")
    m.ec("bea2", "S", "cm", "Separación entre vigas", doc=275)
    m.dato("tw", 15.24, "cm", "Espesor del alma")
    m.dato("bew1", 106.68, "cm", "Ancho del ala superior de la viga")
    m.ec("bew", "MAX(0.5*bew1,tw)", "cm", "Mayor de: tw ó 1/2 ancho del ala superior", doc=53.34)
    m.ec("bea3", "12*ts+bew", "cm", "12 ts + bew", doc=281.34)
    m.ec("wfe", "MIN(bea1,bea2,bea3)", "cm", "Ancho de ala efectivo", doc=275)
    m.ec("ndg", "Ec/Ecs", "", "Razón modular losa/viga", tex="n_{dg}", doc=0.789)
    m.sec("3.2.3 Propiedades de la sección transformada", 2)
    m.ec("wft", "ndg*wfe", "m", "Ancho de ala transformado", doc=2.17)
    m.ec("aft", "wft*ts", "m**2", "Área de ala transformada", doc=0.41)
    m.ec("Ift", "wft*ts**3/12", "m**4", "Inercia propia del ala", doc=0.0012)
    m.dato("th", 1.0, "cm", "Espesor mínimo de cartela (centro del tramo)")
    m.dato("wfg", 106.68, "cm", "Ancho del ala superior (viga)")
    m.ec("wth", "ndg*wfg", "m", "Ancho de cartela transformado", doc=0.84)
    m.ec("ath", "wth*th", "m**2", "Área de cartela transformada", doc=0.0084)
    m.ec("Iat", "wth*th**3/12", "cm**4", "Inercia de cartela", doc=7.01)
    _seccion_compuesta(m)

    # ------------------------------------------------------------------ 4
    m.sec("4. Fuerzas cortantes y momentos flectores")
    m.sec("4.1 Cargas muertas [LRFD Art. 3.3.2]", 2)
    m.ec("Wd", "t*S*Wc", "tonf/m", "Peso de la losa", doc=1.32)
    m.ec("Wha", "th*wfg*Wc", "tonf/m", "Peso de la cartela", doc=0.03)
    m.ec("Ws", "Wd+Wha", "tonf/m", "Peso de losa + cartela", doc=1.35)
    m.nota("LRFD A. 4.6.2.2.1: las CM de barreras y carpeta se distribuyen uniformemente entre todas las "
           "vigas si: ancho de losa constante; Nb ≥ 4; voladizo ≤ 3.0 ft; vigas paralelas de igual "
           "rigidez; curvatura en planta < 4°; sección de la Tabla 4.6.2.2.1-1.")
    m.dato("Nb", 6, "", "Número de vigas")
    m.verif("chk_Nb", "Nb>4", "Número de vigas Nb > 4")
    m.dato("Lo", 91.44, "cm", "Longitud del voladizo", tex="L_o")
    m.dato("Lbar", 45.72, "cm", "Ancho de la barrera en la base")
    m.ec("de_v", "Lo-Lbar", "ft", "Parte de la calzada en el voladizo", tex="d_e", doc=1.5)
    m.verif("chk_de", "de_v<=3*ft", "Calzada en el voladizo ≤ 3.0 ft")
    m.ec("WDCb", "Wb*2/Nb", "tonf/m", "Peso de las 2 barreras por viga", doc=0.149)
    m.dato("w", 14.634, "m", "Ancho de capa de rodadura")
    m.ec("WDW", "Wc*fws*w/Nb", "tonf/m", "Peso de carpeta asfáltica por viga", doc=0.29)
    filas = []
    for i, s in enumerate(SECCIONES):
        fila = [D(f"xL_{i}", float(s)), C(f"x_{i}", f"xL_{i}*L1")]
        for q, nv, nm in (("Wg", "Vg", "Mg"), ("Ws", "Vs", "Ms"), ("WDCb", "Vb", "Mb"), ("WDW", "Vws", "Mws")):
            fila.append(C(f"{nv}_{i}", f"{q}*(L1/2-x_{i})"))
            fila.append(C(f"{nm}_{i}", f"{q}*x_{i}*(L1-x_{i})/2"))
        filas.append(fila)
    m.tabla("Cortantes (tonf) y momentos (tonf·m) no mayorados por CM - viga interior",
            ["x/L", "x", "Vg", "Mg", "Vs", "Ms", "Vb", "Mb", "Vws", "Mws"],
            ["", "m", "tonf", "tonf*m", "tonf", "tonf*m", "tonf", "tonf*m", "tonf", "tonf*m"], filas)

    m.sec("4.2 Carga viva [LRFD A. 3.6.1.2]", 2)
    m.nota("Factores de distribución de carga viva para una viga interior [LRFD A. 4.6.2.2]; "
           "sección transversal tipo (k) [LRFD T. 4.6.2.2.1-1].")
    m.ec("NL", "INT(w/(12*ft))", "", "Número de carriles de diseño", "LRFD A. 3.6.1.1.1", doc=4)
    m.ec("S_ft", "S", "ft", "Separación entre vigas", tex="S", doc=9.02)
    m.verif("chk_S", "AND(S>=3.5*ft,S<=16*ft)", "(a) 3.5 ≤ S ≤ 16.0 ft")
    m.ec("ts_in", "ts", "inch", "Espesor de losa", tex="t_s", doc=7.48)
    m.verif("chk_ts", "AND(ts>=4.5*inch,ts<=12*inch)", "(b) 4.5 ≤ ts ≤ 12.0 in")
    m.ec("L1_ft", "L1", "ft", "Tramo", tex="L_1", doc=120.08)
    m.verif("chk_L", "AND(L1>=20*ft,L1<=240*ft)", "(c) 20 ≤ L ≤ 240 ft")
    m.verif("chk_Nb4", "Nb>=4", "(d) Nb ≥ 4")
    m.ec("nc", "Ecs/Ec", "", "Razón modular viga/losa", tex="n_c", doc=1.27)
    m.ec("eg", "ts/2+th+yt", "inch", "Distancia entre CG de viga y losa", doc=39.53)
    m.ec("Kg", "nc*(Ig+Ag*eg**2)", "inch**4", "Parámetro de rigidez longitudinal", "LRFD Eq. 4.6.2.2.1-1",
         doc=2211647.48)
    m.verif("chk_Kg", "AND(Kg>=10000*inch**4,Kg<=7000000*inch**4)", "(e) 10 000 ≤ Kg ≤ 7 000 000 in⁴")
    kg = "((Kg/inch**4)/(12*(L1/ft)*(ts/inch)**3))**0.1"
    m.ec("DFM1", f"0.06+(S/(14*ft))**0.4*(S/L1)**0.3*{kg}", "",
         "Distribución para momento: 1 carril de diseño", "LRFD T. 4.6.2.2.2b-1", doc=0.499)
    m.ec("DFM2", f"0.075+(S/(9.5*ft))**0.6*(S/L1)**0.2*{kg}", "",
         "Distribución para momento: 2 o más carriles", "LRFD T. 4.6.2.2.2b-1", doc=0.733)
    m.ec("FDMimax", "MAX(DFM1,DFM2)", "", "Factor de distribución para momento (controla)", doc=0.733,
         clave=True)
    m.dato("FPM", 1.2, "", "Factor de presencia múltiple", "LRFD A. 3.6.1.1.2")
    m.ec("DFMf", "DFM1/FPM", "", "Factor de distribución para fatiga", doc=0.416)
    m.ec("DFV1", "0.36+S/(25*ft)", "", "Distribución para cortante: 1 carril", "LRFD T. 4.6.2.2.3a-1",
         doc=0.721)
    m.ec("DFV2", "0.2+S/(12*ft)-(S/(35*ft))**2", "", "Distribución para cortante: 2 o más carriles", doc=0.885)
    m.ec("FDVimax", "MAX(DFV1,DFV2)", "", "Factor de distribución para cortante (controla)", doc=0.885,
         clave=True)
    m.nota("Amplificación dinámica IM: solo se aplica a la carga del camión [LRFD T. 3.6.2.1-1].")
    m.dato("ELf", 15, "pct", "IM para el estado límite de fatiga", tex="IM_f")
    m.dato("IM", 33, "pct", "IM para los demás estados límite")
    m.dato("P", 32, "kip", "Carga por eje del camión HS20-44")
    m.dato("le1", 14, "ft", "Separación ejes delantero-central", tex="l_1")
    m.dato("le2", 14, "ft", "Separación ejes central-trasero (camión de diseño)", tex="l_2")
    m.dato("le2f", 30, "ft", "Separación ejes central-trasero (camión de fatiga)", tex="l_{2,f}")
    m.dato("WLL", 0.64, "kip/ft", "Carga de carril de diseño")
    m.nota("VLT = V camión·DFV·(1+IM); MLT = M camión·DFM·(1+IM); VLL = V carril·DFV; MLL = M carril·DFM; "
           "Mf = M camión de fatiga·DFMf·(1+IMf). Cortante máximo de carril: w(L-x)²/(2L).")
    cargas = ["(P/4)", "P", "P"]
    dd, df = ["0", "le1", "(le1+le2)"], ["0", "le1", "(le1+le2f)"]
    filas = []
    for i, s in enumerate(SECCIONES):
        x = f"x_{i}"
        filas.append([C(None, f"xL_{i}"), C(None, x),
                      C(f"VLT_{i}", f"FDVimax*(1+IM)*{envolvente_cortante(x, 'L1', cargas, dd)}"),
                      C(f"MLT_{i}", f"FDMimax*(1+IM)*{envolvente_momento(x, 'L1', cargas, dd)}"),
                      C(f"VLL_{i}", f"FDVimax*WLL*(L1-{x})**2/(2*L1)"),
                      C(f"MLL_{i}", f"FDMimax*WLL*{x}*(L1-{x})/2"),
                      C(f"Mf_{i}", f"DFMf*(1+ELf)*{envolvente_momento(x, 'L1', cargas, df)}")])
    m.tabla("Cortantes (tonf) y momentos (tonf·m) no mayorados por CV - viga interior",
            ["x/L", "x", "VLT", "MLT", "VLL", "MLL", "Mf (fatiga)"],
            ["", "m", "tonf", "tonf*m", "tonf", "tonf*m", "tonf*m"], filas)

    # ------------------------------------------------------------------ 5
    m.sec("5. Estimación del pretensado")
    m.sec("5.1 Esfuerzos por carga de servicio en el centro del tramo (Servicio III)", 2)
    for n, d in (("Mg", 198.84), ("Ms", 225.31), ("Mb", 24.92), ("Mws", 49.01), ("MLT", 253.55),
                 ("MLL", 116.88)):
        m.ec(n, f"{n}_6", "tonf*m", f"Momento {n} en el centro del tramo", doc=d)
    m.ec("fb", "(Mg+Ms)/Sb+(Mb+Mws+0.8*(MLT+MLL))/Sbc", "tonf/cm**2",
         "Esfuerzo de tensión en la fibra inferior", doc=0.286)
    m.sec("5.2 Esfuerzos límites del hormigón", 2)
    m.ec("fltcs", "-0.19*SQRT(fcd2/ksi)*ksi", "tonf/cm**2", "Tensión límite en servicio", "LRFD A. 5.9.4.2b",
         doc=-0.03)
    m.sec("5.3 Número de torones requeridos", 2)
    m.ec("fpb", "fb+fltcs", "tonf/cm**2", "Precompresión requerida en la fibra inferior", doc=0.25)
    m.ec("ybs_e", "0.05*hg", "cm", "Distancia estimada 0.05h", doc=9.14)
    m.dato("ybs_a", 10, "cm", "Distancia asumida CG torones - fibra inferior")
    m.ec("ec1", "yb-ybs_a", "cm", "Excentricidad en el centro del claro", doc=82.96)
    m.ec("Ppe", "fpb*Ag*Sb/(Sb+Ag*ec1)", "tonf", "Fuerza de pretensado total después de pérdidas",
         doc=466.09)
    m.dato("p_perd", 25, "pct", "Pérdida final asumida (% de fpi)", tex="p")
    m.ec("Fpe_t", "Ast*fpi*(1-p_perd)", "tonf", "Fuerza final por torón", tex="F_{pe}", doc=10.55)
    m.ec("Nti", "Ppe/Fpe_t", "", "Número de torones requeridos", doc=44.19)
    m.dato("Nt", 48, "", "Número de torones adoptado (2a iteración)", clave=True)
    m.verif("chk_Nt", "Nt>=Nti", "Torones adoptados ≥ requeridos")
    m.ec("Aps", "Ast*Nt", "cm**2", "Área total de acero de preesfuerzo", doc=47.38)
    filas, prod, cnt = [], [], []
    for k, (n, d) in enumerate([(12, .05), (12, .10), (8, .15), (4, .20), (2, .25), (2, .30), (2, .35),
                                (2, .40), (2, .45), (2, .50)], 1):
        filas.append([f"y{k}", D(f"nc_{k}", n), D(f"dc_{k}", d), C(f"ADc_{k}", f"nc_{k}*dc_{k}")])
        cnt.append(f"nc_{k}")
        prod.append(f"ADc_{k}")
    m.tabla("Distribución de torones (centro del tramo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "m", "m"], filas)
    m.ec("Nt_tab", suma(cnt), "", "Total de torones en la tabla", ftex=r"\sum A", doc=48)
    m.verif("chk_tab", "AND(Nt_tab>=Nt,Nt_tab<=Nt)", "La tabla de distribución contiene Nt torones")
    m.ec("ybs", f"({suma(prod)})/Nt_tab", "cm", "CG de torones - fibra inferior",
         ftex=r"\dfrac{\sum A\cdot B}{\sum A}", doc=17.292)
    m.ec("ec2", "yb-ybs", "cm", "Excentricidad de los torones", doc=75.67)
    m.ec("epg", "ec2", "cm", "Excentricidad de los torones", doc=75.67)

    # ------------------------------------------------------------------ 6
    m.sec("6. Pérdidas del pretensado")
    m.nota("ΔfpT = ΔfpES + ΔfpSR + ΔfpCR + ΔfpR2  [LRFD Eq. 5.9.5.1-1]")
    m.sec("6.1 Acortamiento elástico [LRFD Eq. 5.9.5.2.3a]", 2)
    m.dato("Pfpi", 9, "pct", "Pérdida inicial de fpi empleada", tex="P_{fpi}")
    m.ec("Fstbt", "Ast*fpi*(1-Pfpi)", "tonf", "Fuerza por torón en la transferencia", doc=12.8)
    m.ec("Ppi", "Nt*Fstbt", "tonf", "Fuerza total de pretensado (antes de transferencia)", doc=614.35)
    m.ec("fcgp", "Ppi/Ag+Ppi*epg**2/Ig-Mg*epg/Ig", "tonf/cm**2", "Esfuerzo en el CG de los torones", doc=0.21)
    m.ec("DfpES", "Ep/Eci*fcgp", "tonf/m**2", "Pérdida por acortamiento elástico", tex=r"\Delta f_{pES}",
         doc=13201.26)
    m.ec("pact", "DfpES/fpi", "", "Pérdida real por acortamiento elástico", doc=0.0926)
    m.verif("chk_pact", "ABS(pact-Pfpi)<=0.01", "Pérdida real ≈ asumida (±1 %): no se requiere iterar")
    m.sec("6.2 Contracción [LRFD Eq. 5.9.5.4.2-1]", 2)
    m.dato("H", 70, "", "Humedad relativa (%)")
    m.ec("DfpSR", "17*ksi-0.15*ksi*H", "tonf/m**2", "Pérdida por contracción", tex=r"\Delta f_{pSR}",
         doc=4569.95)
    m.sec("6.3 Flujo plástico [LRFD Eq. 5.9.5.4.3-1]", 2)
    m.ec("Dfcdp", "Ms*epg/Ig+(Mb+Mws)*(ybc-ybs)/Ic", "tonf/m**2", "Cambio de esfuerzo por cargas permanentes",
         tex=r"\Delta f_{cdp}", doc=947.34)
    m.ec("DfpCR", "12*fcgp-7*Dfcdp", "tonf/m**2", "Pérdida por flujo plástico", tex=r"\Delta f_{pCR}",
         doc=18900.33)
    m.sec("6.4 Relajación de los torones", 2)
    m.dato("DfpR1", 0, "ksi", "Relajación antes de la transferencia (se considera en fábrica)",
           tex=r"\Delta f_{pR1}")
    m.ec("DfpR2", "0.3*(20*ksi-0.4*DfpES-0.2*(DfpSR+DfpCR))", "tonf/m**2", "Relajación después de la transferencia",
         "LRFD Eq. 5.9.5.4.4c-1", tex=r"\Delta f_{pR2}", doc=1226.05)
    m.sec("6.5 Pérdidas totales en la transferencia", 2)
    m.ec("Dfpi", "DfpES", "tonf/cm**2", "Pérdida inicial", tex=r"\Delta f_{pi}", doc=1.32)
    m.ec("fpt", "fpi-Dfpi", "tonf/cm**2", "Esfuerzo en torones después de la transferencia", doc=12.93)
    m.ec("Ft", "fpt*Ast", "tonf", "Fuerza en cada torón", doc=12.76)
    m.ec("pi_ini", "Dfpi/fpi*100", "", "% de pérdida inicial", tex="p_i", doc=9.26)
    m.sec("6.6 Pérdidas totales en cargas de servicio", 2)
    m.ec("DfpT", "DfpES+DfpSR+DfpCR+DfpR2", "tonf/m**2", "Pérdidas totales", tex=r"\Delta f_{pT}", doc=37897.59)
    m.ec("fpe", "fpi-DfpT", "tonf/cm**2", "Esfuerzo después de todas las pérdidas", doc=10.46)
    m.verif("chk_fpe", "fpe<=0.8*fpy", "fpe ≤ 0.8 fpy", "LRFD T. 5.9.3-1", doc="OK")
    m.ec("FtLL", "fpe*Ast", "tonf", "Fuerza por torón", tex="F_{tLL}", doc=10.32)
    m.ec("FTot", "FtLL*Nt", "tonf", "Fuerza total de pretensado después de pérdidas", tex="F_T", doc=495.56, clave=True)
    m.ec("pt", "(fpi-fpe)/fpi*100", "", "% de pérdida final", doc=26.59, clave=True)

    # ------------------------------------------------------------------ 7
    m.sec("7. Esfuerzos en el hormigón en la transferencia")
    m.ec("Ppit", "Ft*Nt", "tonf", "Fuerza total de pretensado después de la transferencia",
         tex=r"P_{pi,transf}", doc=612.57)
    m.sec("7.1 Esfuerzos límites [LRFD T. 5.9.4]", 2)
    m.ec("flc", "0.6*fci", "tonf/cm**2", "Compresión en la transferencia", doc=0.24)
    m.ec("flt1", "-0.0948*SQRT(fci/ksi)*ksi", "ksi", "Tensión sin refuerzo auxiliar adherido", doc=-0.23)
    m.ec("flt", "MAX(flt1,-0.2*ksi)", "ksi", "Tensión límite (gobierna el menor valor absoluto)", doc=-0.2)
    m.ec("flt2", "-0.22*SQRT(fci/ksi)*ksi", "ksi", "Tensión con refuerzo auxiliar adherido", doc=-0.53)
    m.sec("7.2 Esfuerzos en la sección de longitud de transferencia", 2)
    m.ec("Ltransf", "60*dt", "m", "Longitud de transferencia (60 dt)", "LRFD Art. 5.8.2.3", doc=0.76)
    m.ec("xt", "Ltransf", "m", "Sección de análisis")
    m.ec("Mglt", "0.5*Wg*xt*(L2-xt)", "tonf*m", "Momento por peso de la viga", doc=16.35)
    m.ec("ft_lt", "Ppit/Ag-Ppit*epg/St+Mglt/St", "tonf/cm**2", "Esfuerzo en la parte superior", doc=-0.05)
    m.verif("chk_ft_lt", "ft_lt>=flt2", "Fibra superior (torones rectos)", doc="NO OK", clave=False)
    m.ec("fb_lt", "Ppit/Ag+Ppit*epg/Sb-Mglt/Sb", "tonf/cm**2", "Esfuerzo en la parte inferior", doc=0.31)
    m.verif("chk_fb_lt", "fb_lt<=flc", "Fibra inferior (torones rectos)", doc="NO OK", clave=False)
    m.nota("Los esfuerzos superan los límites: se desvían 12 torones en los puntos 0.4L.")
    filas, pb, nb = [], [], []
    for k, (n, d) in enumerate([(12, .05), (12, .10), (8, .15), (4, .20)], 1):
        filas.append([f"y{k}", D(f"ne_{k}", n), D(f"de_{k}", d), C(f"ADe_{k}", f"ne_{k}*de_{k}")])
        nb.append(f"ne_{k}")
        pb.append(f"ADe_{k}")
    m.tabla("Torones rectos en el extremo (desde el fondo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "m", "m"], filas)
    m.ec("Nblt", suma(nb), "", "Torones inferiores rectos", tex="N_{blt}", ftex=r"\sum A", doc=36)
    m.ec("ybe", f"({suma(pb)})/Nblt", "cm", "CG de torones rectos - fibra inferior", doc=10.56)
    filas, pt, nt = [], [], []
    for k, (n, d) in enumerate([(2, .30), (2, .25), (2, .20), (2, .15), (2, .10), (2, .05)], 5):
        filas.append([f"y{k}", D(f"nt_{k}", n), D(f"dt_{k}", d), C(f"ADt_{k}", f"nt_{k}*dt_{k}")])
        nt.append(f"nt_{k}")
        pt.append(f"ADt_{k}")
    m.tabla("Torones desviados en el extremo (desde arriba)",
            ["Fila", "# Torones (A)", "Dist. desde arriba (B)", "(A)·(B)"], ["", "", "m", "m"], filas)
    m.ec("Ntlt", suma(nt), "", "Torones desviados", tex="N_{tlt}", ftex=r"\sum A", doc=12)
    m.ec("yte", f"({suma(pt)})/Ntlt", "cm", "CG de torones desviados - fibra superior (extremo)", doc=17.5)
    m.verif("chk_Ntlt", "AND(Nblt+Ntlt>=Nt,Nblt+Ntlt<=Nt)", "Rectos + desviados = Nt")
    filas, ph = [], []
    for k, (n, d) in enumerate([(2, .25), (2, .30), (2, .35), (2, .40), (2, .45), (2, .50)], 5):
        filas.append([f"y{k}", D(f"nh_{k}", n), D(f"dh_{k}", d), C(f"ADh_{k}", f"nh_{k}*dh_{k}")])
        ph.append(f"ADh_{k}")
    m.tabla("Torones desviados en el punto 'harp' (desde el fondo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "m", "m"], filas)
    m.ec("Nthp", suma([f"nh_{k}" for k in range(5, 11)]), "", "Torones desviados en el punto harp",
         tex="N_{thp}", ftex=r"\sum A", doc=12)
    m.ec("yph", f"({suma(ph)})/Nthp", "cm", "CG de torones desviados - fibra inferior (punto harp)", doc=37.5)
    m.ec("llt", "0.4*L2", "m", "Punto harp (0.4 L2)", doc=14.76)
    m.ec("ylt", "yte+(hg-yph-yte)/llt*Ltransf", "cm", "CG torones desviados - fibra superior (long. transf.)",
         doc=24.1)
    m.dato("dstr", 0.05, "m", "Distancia entre torones")
    m.ec("y_lt", "(Nblt*ybe+Ntlt*(hg-ylt))/Nt", "cm", "CG de todos los torones (long. transf.)", doc=47.61)
    filas, pe = [], []
    for k in range(1, 5):
        filas.append([f"y{k}", C(None, f"ne_{k}"), C(None, f"de_{k}"), C(f"AEx_{k}", f"ne_{k}*de_{k}")])
        pe.append(f"AEx_{k}")
    for k in range(5, 11):
        filas.append([f"y{k}", C(None, f"nt_{k}"), C(f"dEx_{k}", f"hg-dt_{k}"), C(f"AEx_{k}", f"nt_{k}*dEx_{k}")])
        pe.append(f"AEx_{k}")
    m.tabla("Patrón de torones en el extremo (desde el fondo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "m", "m"], filas)
    m.ec("ybs_ext", f"({suma(pe)})/Nt", "cm", "CG de todos los torones - fondo (extremo)", doc=49.26)
    m.ec("exc", "yb-y_lt", "cm", "Excentricidad en la longitud de transferencia", doc=45.35)
    m.ec("ft_ext", "Ppit/Ag-Ppit*exc/St+Mglt/St", "tonf/cm**2", "Esfuerzo en la parte superior", doc=0.02)
    m.verif("chk_ft_ext", "ft_ext<=flc", "Fibra superior (con torones desviados)", doc="OK")
    m.ec("fb_ext", "Ppit/Ag+Ppit*exc/Sb-Mglt/Sb", "tonf/cm**2", "Esfuerzo en la parte inferior", doc=0.23)
    m.verif("chk_fb_ext", "fb_ext<=flc", "Fibra inferior (con torones desviados)", doc="OK")
    m.sec("7.3 Esfuerzos en los puntos 'harp'", 2)
    m.ec("xph", "llt", "m", "Ubicación del punto harp")
    m.ec("Mgph", "0.5*Wg*xph*(L2-xph)", "tonf*m", "Momento por peso de la viga", doc=194.03)
    m.ec("ft_ph", "Ppit/Ag-Ppit*epg/St+Mgph/St", "tonf/cm**2", "Esfuerzo en la parte superior", doc=0.02)
    m.verif("chk_ft_ph", "ft_ph<=flc", "Fibra superior en punto harp", doc="OK")
    m.ec("fb_ph", "Ppit/Ag+Ppit*epg/Sb-Mgph/Sb", "tonf/cm**2", "Esfuerzo en la parte inferior", doc=0.23)
    m.verif("chk_fb_ph", "fb_ph<=flc", "Fibra inferior en punto harp", doc="OK")
    m.sec("7.4 Esfuerzos en el centro del tramo", 2)
    m.ec("xcl", "0.5*L2", "m", "Centro del tramo", doc=18.45)
    m.ec("Mgcl", "0.5*Wg*xcl*(L2-xcl)", "tonf*m", "Momento por peso de la viga", doc=202.12)
    m.ec("ft_cl", "Ppit/Ag-Ppit*epg/St+Mgcl/St", "tonf/cm**2", "Esfuerzo en la parte superior", doc=0.02)
    m.verif("chk_ft_cl", "ft_cl<=flc", "Fibra superior en centro del tramo", doc="OK")
    m.ec("fb_cl", "Ppit/Ag+Ppit*epg/Sb-Mgcl/Sb", "tonf/cm**2", "Esfuerzo en la parte inferior", doc=0.23)
    m.verif("chk_fb_cl", "fb_cl<=flc", "Fibra inferior en centro del tramo", doc="OK")
    m.sec("7.5 Fuerzas de sujeción", 2)
    m.ec("fs_s", "0.8*fpu", "tonf/cm**2", "Esfuerzo en el torón al tensar", tex="f_s", doc=15.2)
    m.ec("Fs_t", "Ast*fs_s", "tonf", "Fuerza por torón", tex="F_s", doc=15)
    m.ec("psi_h", "ATAN((hg-yph-yte)/llt)", "deg", "Ángulo 'harp'", tex=r"\psi", doc=4.95)
    m.dato("ff", 1.05, "", "Factor de fricción", tex="f_f")
    m.ec("Fsuj", "ff*Fs_t*SIN(psi_h)", "tonf", "Fuerza de sujeción por torón", doc=1.36)
    m.ec("Fsujtot", "Ntlt*Fsuj", "tonf", "Fuerza de sujeción total", doc=16.32, clave=True)

    # ------------------------------------------------------------------ 8
    m.sec("8. Esfuerzos en el hormigón debido a las cargas de servicio")
    m.ec("Ppecs", "FTot", "tonf", "Pretensado efectivo (pérdidas refinadas)", tex=r"P_{pe,c.s}", doc=495.56)
    m.sec("8.1 Esfuerzos límites [LRFD Art. 5.9.4.2]", 2)
    m.ec("fpcsl2", "0.45*fcd2", "tonf/cm**2", "Compresión viga - cargas permanentes (Servicio I)", doc=0.2)
    m.ec("fpcsl1", "0.45*fcd1", "tonf/cm**2", "Compresión losa - cargas permanentes", doc=0.13)
    m.ec("fptcsl2", "0.6*fcd2", "tonf/cm**2", "Compresión viga - todas las cargas", doc=0.27)
    m.ec("fptcsl1", "0.6*fcd1", "tonf/cm**2", "Compresión losa - todas las cargas", doc=0.17)
    m.ec("fpttsl2", "-0.19*SQRT(fcd2/ksi)*ksi", "tonf/cm**2", "Tensión en viga (Servicio III)", doc=-0.0338)
    m.sec("8.2 Esfuerzos en el centro del tramo", 2)
    m.ec("ftg1", "Ppecs/Ag-Ppecs*epg/St+(Mg+Ms)/St+(Mws+Mb)/Stg", "tonf/cm**2",
         "Fibra superior viga - cargas permanentes", doc=0.13)
    m.verif("chk_ftg1", "ftg1<=fpcsl2", "Fibra superior viga - permanentes", doc="OK")
    m.ec("ftg2", "ftg1+(MLT+MLL)/Stg", "tonf/cm**2", "Fibra superior viga - permanentes + transitorias", doc=0.16)
    m.verif("chk_ftg2", "ftg2<=fptcsl2", "Fibra superior viga - todas las cargas", doc="OK")
    m.ec("ftg1t", "(Mws+Mb)/Stc", "tonf/cm**2", "Fibra superior losa - permanentes", doc=0.01)
    m.verif("chk_ftg1t", "ftg1t<=fpcsl1", "Losa - permanentes", doc="OK")
    m.ec("ftg2t", "ftg1t+(MLT+MLL)/Stc", "tonf/cm**2", "Fibra superior losa - permanentes + transitorias",
         doc=0.05)
    m.verif("chk_ftg2t", "ftg2t<=fptcsl1", "Losa - todas las cargas", doc="OK")
    m.ec("fb_s", "Ppecs/Ag+Ppecs*epg/Sb-(Mg+Ms)/Sb-(Mws+Mb+0.8*(MLT+MLL))/Sbc", "tonf/cm**2",
         "Fibra inferior viga - Servicio III", tex="f_b", doc=-0.0326)
    m.verif("chk_fb_s", "fb_s>=fpttsl2", "Fibra inferior viga - tensión Servicio III", doc="OK")
    m.sec("8.3 Esfuerzo límite de fatiga [LRFD A. 5.5.3.1]", 2)
    m.ec("ftg2lf", "Ppecs/Ag+Ppecs*epg/Sb-(Mg+Ms)/Sb-(Mws+Mb)/Sbc", "tonf/cm**2",
         "Compresión inferior por permanentes y pretensado", doc=0.06)
    m.ec("Mf", "Mf_6", "tonf*m", "Momento de fatiga (centro del tramo)", doc=107.54)
    m.verif("chk_fat", "2*(0.75*Mf/Sbc)<ftg2lf", "Fatiga: 2(0.75 Mf/Sbc) < f compresión", doc="OK")

    # ------------------------------------------------------------------ 9
    m.sec("9. Estado límite de resistencia")
    m.dato("nD", 1, "", "Factor de ductilidad", tex=r"\eta_D")
    m.dato("nR", 1, "", "Factor de redundancia", tex=r"\eta_R")
    m.dato("nI", 1, "", "Factor de importancia operativa", tex=r"\eta_I")
    m.ec("eta_i", "nD*nR*nI", "", "Modificador de cargas", tex=r"\eta_i", doc=1)
    m.dato("FDCmax", 1.25, "", "Factor de carga DC", tex=r"\gamma_{DC}")
    m.dato("FDWmax", 1.5, "", "Factor de carga DW", tex=r"\gamma_{DW}")
    m.dato("FLL", 1.75, "", "Factor de carga LL", tex=r"\gamma_{LL}")
    m.ec("FIM", "1+IM", "", "Factor de impacto", doc=1.33)
    m.ec("Mu", "eta_i*(FDCmax*(Mg+Mb+Ms)+FDWmax*Mws+FLL*(MLT+MLL))", "tonf*m", "Momento de diseño (Resistencia I)",
         doc=1283.117, clave=True)
    m.nota("fps = fpu(1 - k·c/d_p)  [LRFD Eq. 5.7.3.1.1-1], válido si fpe ≥ 0.5 fpu.")
    m.ec("k", "2*(1.04-fpy/fpu)", "", "Factor k (torones de baja relajación)", "LRFD Eq. 5.7.3.1.1-2", doc=0.28)
    m.ec("d_p", "hsc-ybs", "m", "Fibra comprimida - CG de los torones", doc=1.86)
    m.dato("As", 0, "cm**2", "Refuerzo a tensión no pretensado")
    m.dato("Asp", 0, "cm**2", "Refuerzo a compresión", tex="A'_s")
    m.dato("fy_r", 4200, "kgf/cm**2", "fy del refuerzo a tensión", tex="f_y")
    m.dato("fyp", 4200, "kgf/cm**2", "fy del refuerzo a compresión", tex="f'_y")
    m.ec("b", "wfe", "m", "Ancho efectivo del ala comprimida", doc=2.75)
    m.ec("beta1", "IF(ROUND(fcd1/(kgf/cm**2),6)<=280,0.85,IF(ROUND(fcd1/(kgf/cm**2),6)>550,0.65,"
                  "0.85-0.05*(fcd1-280*kgf/cm**2)/(70*kgf/cm**2)))", "", "Factor β1", "LRFD Art. 5.7.2.2",
         doc=0.85)
    m.ec("c", "(Aps*fpu+As*fy_r-Asp*fyp)/(0.85*fcd1*beta1*b+k*Aps*fpu/d_p)", "cm", "Profundidad del eje neutro",
         "LRFD Eq. 5.7.3.1.1-4", doc=15.79)
    m.verif("chk_c", "c<ts", "Comportamiento de sección rectangular (c < ts)", doc="OK")
    m.verif("chk_fpe05", "fpe>=0.5*fpu", "fpe ≥ 0.5 fpu", doc="OK")
    m.ec("fps", "fpu*(1-k*c/d_p)", "tonf/cm**2", "Esfuerzo promedio en el torón", doc=18.55)
    m.ec("a", "beta1*c", "cm", "Profundidad del bloque de compresión", doc=13.43)
    m.ec("Mn", "Aps*fps*(d_p-0.5*a)", "tonf*m", "Resistencia nominal a flexión", "LRFD Eq. 5.7.3.2.2-1",
         doc=1571.769)
    m.dato("phi", 1, "", "Factor de resistencia (tensión controlada)", "LRFD 5.5.4.2.1", tex=r"\phi")
    m.ec("Mr", "phi*Mn", "tonf*m", "Resistencia a flexión mayorada", doc=1571.769, clave=True)
    m.verif("chk_Mr", "Mr>Mu", "Resistencia a flexión Mr > Mu", doc="OK")

    # ------------------------------------------------------------------ 10
    m.sec("10. Límites del refuerzo [LRFD Art. 5.7.3.3]")
    m.ec("de", "d_p", "cm", "Peralte efectivo (As = 0)", doc=185.59)
    m.verif("chk_cde", "c/de<=0.42", "Máximo refuerzo: c/de ≤ 0.42", doc="OK")
    m.ec("fr", "0.24*SQRT(fcd2/ksi)*ksi", "tonf/cm**2", "Módulo de ruptura", "LRFD Art. 5.4.2.6", doc=0.04)
    m.ec("fpb2", "Ppecs/Ag+Ppecs*epg/Sb", "tonf/cm**2", "Compresión por pretensado efectivo", tex="f_{pb}",
         doc=0.25)
    m.ec("Mdnc", "Mg+Ms", "tonf*m", "Momento por CM (sección no compuesta)", doc=424.159)
    m.ec("Mcr", "Sbc*(fr+fpb2)-Mdnc*(Sbc/Sb-1)", "tonf*m", "Momento de fisuración", doc=827.531)
    m.ec("Mcr12", "1.2*Mcr", "tonf*m", "1.2 Mcr", tex=r"1.2M_{cr}", doc=993.037)
    m.ec("Mu133", "1.33*Mu", "tonf*m", "1.33 Mu", tex=r"1.33M_u", doc=1706.545)
    m.ec("Mmenor", "MIN(Mcr12,Mu133)", "tonf*m", "Menor valor", doc=993.037)
    m.verif("chk_Mmin", "Mr>Mmenor", "Refuerzo mínimo", doc="OK")

    # ------------------------------------------------------------------ 11
    m.sec("11. Diseño por corte")
    m.nota("Se requiere refuerzo transversal cuando Vu > 0.5φ(Vc + Vp)  [LRFD Eq. 5.8.2.4-1].")
    m.dato("phic", 0.9, "", "Factor de resistencia para cortante", "LRFD 5.5.4.2.1", tex=r"\phi_c")
    m.sec("11.1 Sección crítica [LRFD Art. 5.8.3.2]", 2)
    m.ec("hc", "hsc", "cm", "Altura total de la sección compuesta", doc=202.88)
    m.dato("theta", 23, "deg", "Ángulo de inclinación de los esfuerzos diagonales", tex=r"\theta")
    m.ec("ybshp", "ybe", "cm", "CG del grupo de torones rectos", doc=10.56)
    m.ec("de2", "hc-ybshp", "cm", "Peralte efectivo en la sección crítica", tex="d_e", doc=192.32)
    m.ec("dv0", "de2-0.5*a", "cm", "de - a/2", doc=185.61)
    m.verif("chk_dv1", "dv0>=0.9*de2", "dv ≥ 0.9 de", doc="OK")
    m.verif("chk_dv2", "dv0>=0.72*hc", "dv ≥ 0.72 h", doc="OK")
    m.ec("dv", "MAX(dv0,0.9*de2,0.72*hc)", "cm", "Peralte de cortante adoptado", doc=185.61)
    m.ec("sc1", "dv", "cm", "dv", doc=185.61)
    m.ec("sc2", "0.5*dv/TAN(theta)", "cm", "0.5 dv cot θ", doc=218.64)
    m.ec("scmax", "MAX(sc1,sc2)", "cm", "Sección crítica desde el eje del apoyo", doc=218.64)
    m.ec("xsc", "scmax/L1", "", "Ubicación relativa de la sección crítica", doc=0.06)
    m.nota("Las fuerzas en la sección crítica se toman de la fila x/L = 0.06 de las tablas.")
    m.sec("11.2 Contribución del hormigón al corte [LRFD Eq. 5.8.3.3-3]", 2)
    m.ec("Mu1", "eta_i*(FDCmax*(Mg_1+Mb_1+Ms_1)+FDWmax*Mws_1+FLL*(MLT_1+MLL_1))", "tonf*m",
         "Momento mayorado (sección 0.06L)", doc=294.86)
    m.ec("Vu1", "eta_i*(FDCmax*(Vg_1+Vb_1+Vs_1)+FDWmax*Vws_1+FLL*(VLT_1+VLL_1))", "tonf",
         "Cortante mayorado (sección 0.06L)", doc=142.954, clave=True)
    m.dato("Nu1", 0, "kip", "Fuerza axial mayorada")
    m.ec("fpo", "0.75*fpu", "tonf/cm**2", "Parámetro fpo", "LRFD Art. 5.8.3.4.2", doc=14.25)
    m.ec("Vp", "FtLL*Nthp*SIN(psi_h)", "tonf", "Componente vertical del pretensado", doc=10.69)
    m.ec("Apsb", "Nblt*Ast", "cm**2", "Área de torones en el lado de tensión", tex="A_{ps,b}", doc=35.53)
    num = "(ABS(Mu1)/d_p+0.5*Nu1+0.5*ABS(Vu1-Vp)/TAN(theta)-Apsb*fpo)"
    m.ec("eps1", f"{num}/(2*(Es*As+Ep*Apsb))", "", "Deformación en el refuerzo a tensión εx",
         "LRFD Eq. 5.8.3.4.2-2", tex=r"\varepsilon_s", doc=-0.001346)
    m.dato("Act", 405, "inch**2", "Área de hormigón en el lado a tensión", tex="A_{ct}")
    m.ec("eps2", f"IF(eps1<0,{num}/(2*(Ecs*Act+Es*As+Ep*Apsb)),eps1)", "",
         "εx corregida (si es negativa)", "LRFD Eq. 5.8.3.4.2-3", tex=r"\varepsilon_x", doc=-0.0000998)
    m.dato("bv", 15.24, "cm", "Ancho efectivo del alma")
    m.ec("vu", "ABS(Vu1-phic*Vp)/(phic*bv*dv)", "tonf/cm**2", "Esfuerzo por corte", "LRFD Eq. 5.8.3.4.2-1",
         doc=0.05)
    m.ec("Rel1", "vu/fcd2", "", "Relación vu/f'c", doc=0.116)
    m.dato("thetag", 22.8, "deg", "θ de la tabla LRFD 5.8.3.4.2-1", tex=r"\theta_g")
    m.dato("betag", 2.94, "", "β de la tabla LRFD 5.8.3.4.2-1", tex=r"\beta_g")
    m.ec("Vc", "0.0316*betag*SQRT(fcd2/ksi)*ksi*bv*dv", "tonf", "Contribución del hormigón", doc=46.74)
    m.sec("11.3 Contribución del refuerzo al corte", 2)
    m.ec("Vlim", "0.5*phic*(Vc+Vp)", "tonf", "0.5 φ (Vc + Vp)", tex="V", doc=25.85)
    m.sel("req_ref", "Vu1>Vlim", "Req. Ref. transversal", "NO Req. Ref. transversal",
          "Requisito de refuerzo transversal", "LRFD Eq. 5.8.2.4-1", doc="Req. Ref. transversal")
    m.ec("Vs1", "Vu1/phic-Vc-Vp", "tonf", "Resistencia requerida del refuerzo", doc=101.4)
    m.dato("alpha", 90, "deg", "Inclinación del refuerzo transversal (estribos verticales)", tex=r"\alpha")
    m.dato("sp", 0.30, "m", "Separación de estribos")
    m.ec("fyh", "fy", "tonf/m**2", "Fluencia del refuerzo a cortante", doc=42000)
    m.ec("Av", "sp*Vs1/(fyh*dv/TAN(theta))", "cm**2", "Área de refuerzo requerida", doc=1.66)
    m.verif("chk_vu", "vu<0.125*fcd2", "vu < 0.125 f'c", "LRFD Eq. 5.8.2.7-1", doc="OK")
    m.dato("smaxc", 0.61, "m", "Espaciamiento máx. 24 in")
    m.ec("sc", "0.8*dv", "cm", "0.8 dv", doc=148.49)
    m.ec("Smax", "MIN(smaxc,sc)", "m", "Espaciamiento máximo", doc=0.61)
    m.verif("chk_Smax", "Smax>sp", "Separación ≤ máxima", doc="OK")
    m.dato("db", 1.2, "cm", "Diámetro del estribo")
    m.ec("Ab", "0.25*PI()*db**2", "cm**2", "Área de una barra", doc=1.13)
    m.ec("Abt", "2*Ab", "cm**2", "Área del estribo (2 ramas)", doc=2.26)
    m.verif("chk_Abt", "Abt>Av", "Estribo proporcionado ≥ requerido", doc="OK")
    m.ec("Vs2", "Abt*fyh*dv/TAN(theta)/sp", "tonf", "Resistencia del refuerzo proporcionado",
         "LRFD Eq. 5.8.3.3-4", doc=138.47)
    m.ec("Amin", "0.0316*SQRT(fcd2/ksi)*ksi*bv*sp/fyh", "cm**2", "Refuerzo transversal mínimo",
         "LRFD Eq. 5.8.2.5-1", doc=0.61)
    m.verif("chk_Amin", "Abt>Amin", "Refuerzo ≥ mínimo", doc="OK")
    m.sec("11.4 Máxima resistencia nominal al corte", 2)
    m.ec("Vn2", "Vc+Vs2", "tonf", "Vc + Vs", doc=185.22)
    m.ec("Vn3", "0.25*fcd2*bv*dv", "tonf", "0.25 f'c bv dv", "LRFD Eq. 5.8.3.3-2", doc=318.23)
    m.verif("chk_Vn", "Vn2<Vn3", "Vc + Vs ≤ 0.25 f'c bv dv", doc="OK")

    # ------------------------------------------------------------------ 12
    m.sec("12. Transferencia de corte en la interfaz [LRFD A. 5.8.4]")
    m.ec("dv1", "de2-0.5*ts", "m", "Distancia acero a tensión - mitad de la losa", doc=1.83)
    m.ec("Vu1i", "eta_i*(FDCmax*Vb_1+FDWmax*Vws_1+FLL*(VLT_1+VLL_1))", "tonf",
         "Cortante mayorado por cargas sobreimpuestas (0.06L)", tex="V_{u1}", doc=91.963)
    m.ec("Vhi", "Vu1i/dv1", "tonf/m", "Cortante horizontal mayorado", "LRFD Eq. C5.8.4.1-1", doc=50.3)
    m.ec("Vni", "Vhi/phic", "tonf/m", "Resistencia nominal requerida", doc=55.89)
    m.dato("c_coh", 0.075, "ksi", "Factor de cohesión", "LRFD 5.8.4.2", tex="c")
    m.dato("lam", 1, "", "Hormigón de peso normal", tex=r"\lambda")
    m.ec("mu_f", "0.6*lam", "", "Coeficiente de fricción", tex=r"\mu", doc=0.6)
    m.ec("bvi", "wfg", "cm", "Ancho de contacto losa-viga", tex="b_v", doc=106.68)
    m.dato("Lvi", 2.54, "cm", "Longitud unitaria de interfaz")
    m.ec("Acv", "bvi*Lvi", "cm**2", "Área que resiste la transferencia de corte", doc=270.97)
    m.dato("Pc", 0, "tonf", "Fuerza de compresión normal al plano")
    m.ec("Avf", "((Vni*cm-c_coh*Acv)/mu_f-Pc)/fyh", "cm**2", "Refuerzo requerido en la interfaz (como en el PDF)",
         doc=-0.35)
    m.nota("Avf < 0: la cohesión supera la fuerza aplicada; se proporciona el refuerzo mínimo.")
    m.ec("Avfmin", "Abt/sp", "cm**2/m", "Refuerzo proporcionado (estribo Ø12 mm @ 30 cm)", doc=7.54)
    m.ec("Avf2", "0.05*ksi*bvi/fyh", "cm**2/m", "Mínimo refuerzo en la interfaz 0.05 bv/fy", "LRFD Eq. 5.8.4.1-4",
         doc=8.93)
    m.sel("chk_Avf", "Avfmin>Avf2", "OK", "NO OK", "Refuerzo proporcionado ≥ mínimo", doc="NO OK")
    m.ec("Rel2", "Vni/bvi", "ksi", "Vn/Acv", doc=0.075)
    m.verif("chk_Rel2", "Rel2<0.1*ksi", "Vn/Acv < 0.1 ksi: se puede despreciar el mínimo", doc="OK")
    m.ec("Vnip", "c_coh*bvi+mu_f*(Abt/(12*inch)*fyh)", "kip/inch", "Resistencia nominal proporcionada", doc=4.2)
    m.dato("k1", 0.2, "", "Factor K1", tex="K_1")
    m.ec("k1fcbv", "k1*fcd1*bvi", "kip/inch", "0.2 f'c Acv", "LRFD Eq. 5.8.4.1-2", doc=33.45)
    m.dato("k2", 0.8, "kip/inch**2", "Factor K2", tex="K_2")
    m.ec("k2Acv", "k2*bvi", "kip/inch", "0.8 Acv", "LRFD Eq. 5.8.4.1-3", doc=33.6)
    m.verif("chk_Vni1", "Vnip<k1fcbv", "Vni ≤ K1 f'c Acv", doc="OK")
    m.verif("chk_Vni2", "Vnip<k2Acv", "Vni ≤ K2 Acv", doc="OK")

    # ------------------------------------------------------------------ 13
    m.sec("13. Refuerzo longitudinal mínimo [LRFD Art. 5.8.3.5]")
    m.nota("Aps·fps + As·fy ≥ Mu/(dv·φf) + 0.5Nu/φc + (Vu/φv - Vp - 0.5Vs)·cot θ  [LRFD Eq. 5.8.3.5-1]")
    m.sec("13.1 Refuerzo requerido en la cara del apoyo", 2)
    m.ec("dap", "0.5*(L2-L1)", "cm", "Eje del apoyo al extremo de la viga", doc=15)
    m.ec("Vuapoyo", "eta_i*(FDCmax*(Vg_0+Vb_0+Vs_0)+FDWmax*Vws_0+FLL*(VLT_0+VLL_0))", "tonf",
         "Cortante mayorado en el apoyo", doc=158.462)
    m.dato("Mu_ap", 0, "tonf*m", "Momento mayorado en el apoyo", tex="M_u")
    m.dato("Nu_ap", 0, "tonf", "Fuerza axial en el apoyo", tex="N_u")
    m.ec("Vca", "Mu_ap/(dv*phic)+0.5*Nu_ap/phic+(Vuapoyo/phic-0.5*Vs2-Vp)/TAN(theta)", "tonf",
         "Tensión requerida en el refuerzo longitudinal", doc=226.49)
    m.ec("dapd", "dap+ybe/TAN(theta)", "cm", "Cruce de la fisura con el CG de torones rectos", doc=39.87)
    m.ec("Ltransf2", "60*dt", "cm", "Longitud de transferencia", doc=76.2)
    m.ec("fpsb1", "(fpi-DfpT)*(dap+ybe/TAN(theta))/Ltransf2", "tonf/cm**2", "Pretensado disponible", doc=5.47)
    m.ec("Fpa1", "Apsb*fpsb1+As*fy_r", "tonf", "Fuerza de pretensado disponible", doc=194.46)
    m.sel("chk_Fpa1", "Fpa1>Vca", "OK", "NO OK", "Fuerza disponible ≥ requerida", doc="NO OK")
    m.ec("Asca", "(Vca-Fpa1)/fyh", "cm**2", "Acero adicional requerido", doc=7.63)
    m.dato("dca", 1.6, "cm", "Diámetro del refuerzo adicional")
    m.ec("Abca", "0.25*PI()*dca**2", "cm**2", "Área de una barra", doc=2.011)
    m.ec("Nbca", "ROUNDUP(Asca/Abca,0)", "", "Número de barras", doc=4)
    m.dato("wap", 6, "cm", "Ancho de apoyo asumido")
    m.ec("d_ap", "0.5*wap+dapd", "cm", "Cruce de la fisura desde el extremo", doc=42.87)
    m.ec("fpsb2", "(fpi-DfpT)*(dap+0.5*wap+ybe/TAN(theta))/Ltransf2", "ksi", "Pretensado disponible", doc=83.7)
    m.ec("Fpa2", "Apsb*fpsb2+As*fy_r", "kip", "Fuerza disponible", doc=460.96)
    m.verif("chk_Fpa2", "Fpa2>Vlim", "Fuerza disponible > V (criterio del PDF)", si="CUMPLE", no="NO CUMPLE",
            doc="CUMPLE")

    # ------------------------------------------------------------------ 14
    m.sec("14. Zona de anclaje pretensada [Art. 5.10.10]")
    m.ec("Ppi_a", "Nt*Ast*fpi", "tonf", "Fuerza en torones antes de la transferencia", tex="P_{pi}", doc=675.11)
    m.ec("Pr", "0.04*Ppi_a", "tonf", "Resistencia a la fractura (4% Ppi)", doc=27)
    m.dato("fs_anc", 20, "ksi", "Esfuerzo admisible en el acero", tex="f_s")
    m.ec("Asza", "Pr/fs_anc", "cm**2", "Área de acero requerida", doc=19.2)
    m.ec("d025h", "0.25*hg", "cm", "Distancia h/4 desde el extremo", doc=45.72)
    m.dato("Nbza", 5, "", "Número de barras (doble ramal)")
    m.dato("dbza", 1.6, "cm", "Diámetro de barra")
    m.ec("Abza", "PI()/4*dbza**2", "cm**2", "Área de una barra", doc=2.01)
    m.ec("Abtza", "Nbza*2*Abza", "cm**2", "Área total", doc=20.11)
    m.verif("chk_Abtza", "Abtza>Asza", "Refuerzo en zona de anclaje", doc="OK")
    m.dato("sep_za", 10, "cm", "Espaciamiento")
    m.dato("dza", 5, "cm", "Primera barra desde el extremo")
    m.sec("14.2 Refuerzo de confinamiento [LRFD Art. 5.10.10.2]", 2)
    m.ec("dcf", "1.5*hg", "inch", "Longitud confinada desde el extremo", doc=108)
    m.dato("drc", 15, "cm", "Espaciamiento máximo del refuerzo de confinamiento")

    # ------------------------------------------------------------------ 15
    m.sec("15. Deflexión y contraflecha [LRFD Art. 5.7.3.6.2]")
    m.ec("Ppt", "Nt*Ft", "tonf", "Fuerza total de pretensado", doc=612.57)
    m.ec("e_p", "ec2-(yb-ybs_ext)", "m", "Diferencia de excentricidad centro - extremo", tex="e'", doc=0.32)
    m.ec("a_hp", "llt", "m", "Extremo de la viga - punto harp", tex="a", doc=14.76)
    m.ec("Dp", "Ppt/(Eci*Ig)*(ec2*L2**2/8-e_p*a_hp**2/6)", "cm", "Contraflecha por pretensado (↑)",
         tex=r"\Delta_p", doc=9.78)
    m.ec("Dg", "5*Wg*L2**4/(384*Eci*Ig)", "cm", "Peso propio después de la transferencia (↓)",
         tex=r"\Delta_g", doc=3.91)
    m.ec("Dgi", "5*Wg*L1**4/(384*Eci*Ig)", "cm", "Peso propio en el izaje (↓)", tex=r"\Delta_{gi}", doc=3.78)
    m.ec("Ds", "5*Ws*L1**4/(384*Ecs*Ig)", "cm", "Losa y cartela (↓)", tex=r"\Delta_s", doc=4.06)
    m.ec("Dbws", "5*(WDCb+WDW)*L1**4/(384*Ecs*Ic)", "cm", "Barreras y capa de rodadura (↓)",
         tex=r"\Delta_{b+ws}", doc=0.66)
    m.ec("Dpg", "Dp-Dg", "cm", "Después de la transferencia (↑)", tex=r"\Delta_{pg}", doc=5.88)
    m.ec("Dpg2", "1.8*Dp-1.85*Dgi", "cm", "Total en el izaje, factores PCI (↑)", tex=r"\Delta_{pg,izaje}",
         doc=10.61, clave=True)
    m.sec("Deflexión por carga viva e impacto [LRFD Art. 2.5.2.6.2]", 2)
    m.ec("DLDef", "L1/800", "cm", "Límite L/800", tex=r"\Delta_{LL,adm}", doc=4.58)
    m.ec("FDF", "NL/Nb", "", "Factor de distribución para deflexión", doc=0.67)
    m.ec("w_ll", "WLL*FDMimax", "tonf/m", "Carga de carril por viga (con DFM)", tex="w", doc=0.7)
    m.ec("DLL", "5*w_ll*L1**4/(384*Ecs*Ic)", "cm", "Deflexión por carga de carril (↓)", tex=r"\Delta_{LL}",
         doc=1.05)
    m.dato("P1", 32, "kip", "Carga por eje trasero")
    m.dato("L2cd", 168, "inch", "Separación de ejes")
    m.dato("bd", 11.895, "m", "Posición del eje delantero")
    m.ec("xd", "0.5*L1", "m", "Centro del claro", doc=18.3)
    m.ec("aCD1", "0.5*(L1-L2cd)", "ft", "Posición de los ejes traseros", tex="a_{CD1}", doc=53.04)
    m.ec("DP1", "P1*aCD1/(24*Ecs*Ic)*(3*L1**2-4*aCD1**2)", "cm", "Deflexión por ejes traseros",
         tex=r"\Delta_{P1}", doc=1.87)
    m.ec("DP2", "0.25*P1*bd*xd/(6*Ecs*Ic*L1)*(L1**2-bd**2-xd**2)", "cm", "Deflexión por eje delantero",
         tex=r"\Delta_{P2}", doc=0.19964)
    m.ec("DPT", "DP1+DP2", "cm", "Deflexión del camión", tex=r"\Delta_{PT}", doc=2.07)
    m.ec("DLT", "DPT*FIM*FDMimax", "cm", "Camión con impacto (↓)", tex=r"\Delta_{LT}", doc=2.02)
    m.ec("DLTc2", "0.25*DLT+DLL", "cm", "25% camión + carril", tex=r"\Delta_{LT,c2}", doc=1.5528)
    m.ec("Dmayor", "MAX(DLT,DLTc2)", "cm", "Deflexión por carga viva", tex=r"\Delta_{mayor}", doc=2.02, clave=True)
    m.verif("chk_Dll", "Dmayor<DLDef", "Deflexión por carga viva ≤ L/800", doc="OK")
    return m
