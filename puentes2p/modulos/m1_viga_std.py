"""Módulo 1 - Viga interior preforzada. AASHTO Estándar (STD). Págs. 1-13 del PDF."""
from ..motor import C, D, Modulo, envolvente_cortante, envolvente_momento, suma

SECCIONES = ["0", "0.0278", "0.1", "0.2", "0.3", "0.4", "0.5"]


def construir(sobrescribir=None) -> Modulo:
    m = Modulo("STD", "Viga interior preforzada - AASHTO Estándar", "1_Viga_STD",
               "Puente tipo losa-vigas preforzadas. Viga AASHTO-PCI Bulb-Tee BT-72. "
               "Diseño según especificaciones AASHTO Estándar (carga HS20).", sobrescribir)

    # ------------------------------------------------------------------ 2
    m.sec("2. Materiales")
    m.dato("ts", 19, "cm", "Espesor estructural de la losa")
    m.dato("tws", 1, "cm", "Sobre-espesor de desgaste")
    m.ec("t", "ts+tws", "cm", "Espesor total de la losa", doc=20)
    m.dato("fcs", 280, "kgf/cm**2", "f'c de diseño de la losa", tex=r"f'_{c,s}")
    m.dato("fcg", 450, "kgf/cm**2", "f'c de diseño de la viga (BT-72)", tex=r"f'_{c,g}")
    m.dato("fci", 380, "kgf/cm**2", "f'c de la viga en la transferencia", tex=r"f'_{ci}")
    m.dato("Wc", 2.4, "tonf/m**3", "Peso unitario del hormigón", "STD A. 3.3.6")
    m.dato("L2", 36.9, "m", "Longitud total de la viga")
    m.dato("L1", 36.6, "m", "Tramo de diseño (entre apoyos)")
    m.dato("dt", 12.7, "mm", "Diámetro del torón (7 alambres, baja relajación)", tex="d_t")
    m.dato("Ast", 98.7, "mm**2", "Área de un torón")
    m.dato("fs", 19, "tonf/cm**2", "Esfuerzo último del torón f's", tex=r"f'_s")
    m.ec("fpy", "0.9*fs", "tonf/cm**2", "Resistencia a la fluencia", "STD A. 9.1.2", doc=17.1)
    m.ec("fsi", "0.75*fs", "tonf/cm**2", "Pretensado inicial", "STD A. 9.15.1", doc=14.25)
    m.dato("Ep", 2003.748, "tonf/cm**2", "Módulo de elasticidad del torón", "STD 9.16.2.1.2")
    m.dato("fy", 4.2, "tonf/cm**2", "Fluencia de barras de refuerzo")
    m.dato("fws", 5, "cm", "Espesor de la capa de rodadura")
    m.dato("Wcha", 2.4, "tonf/m**3", "Peso unitario del hormigón asfáltico", tex=r"W_{c,ha}")
    m.dato("Wb", 0.4465, "tonf/m", "Peso de la barrera New Jersey (por lado)")

    # ------------------------------------------------------------------ 3
    m.sec("3. Propiedades de la sección transversal de una viga interior")
    m.sec("3.1 Sección no compuesta", 2)
    m.dato("Ag", 0.4948, "m**2", "Área de la viga")
    m.dato("hg", 182.88, "cm", "Altura de la viga")
    m.dato("Ig", 0.2272, "m**4", "Inercia de la viga")
    m.dato("yb", 92.964, "cm", "Distancia del CG a la fibra inferior")
    m.ec("yt", "hg-yb", "cm", "Distancia del CG a la fibra superior", doc=89.92)
    m.ec("Sb", "Ig/yb", "m**3", "Módulo de sección, fibra inferior", doc=0.24)
    m.ec("St", "Ig/yt", "m**3", "Módulo de sección, fibra superior", doc=0.25)
    m.ec("Wg", "Ag*Wc", "tonf/m", "Peso propio de la viga", doc=1.19)
    m.nota("Módulo de elasticidad: Ec = 33000·Wc^1.5·√f'c  (Wc en kip/ft³, f'c en ksi) [STD A. 8.7.1]")
    ec_e = "33000*(Wc/(kip/ft**3))**1.5*SQRT({f}/ksi)*ksi"
    m.ec("Ec", ec_e.format(f="fcs"), "tonf/cm**2", "M.E. de la losa", "STD A. 8.7.1", doc=268.52)
    m.ec("Eci", ec_e.format(f="fci"), "tonf/cm**2", "M.E. de la viga en la transferencia", doc=312.82)
    m.ec("Ecs", ec_e.format(f="fcg"), "tonf/cm**2", "M.E. de la viga (cargas de servicio)", doc=340.41)

    m.sec("3.2 Sección compuesta", 2)
    m.nota("Ancho de alma efectivo de la viga: el menor de be1 (ancho del ala superior) y "
           "be2 = 6(2)(h1+h2)+tw+2(h3). [STD A. 9.8.3.1]")
    m.dato("htf1", 8.89, "cm", "Dimensión del ala h1")
    m.dato("htf2", 5.08, "cm", "Dimensión del ala h2")
    m.dato("htf3", 5.08, "cm", "Dimensión del ala h3")
    m.dato("tw", 15.24, "cm", "Espesor del alma de la viga")
    m.dato("bew1", 106.68, "cm", "Ancho del ala superior de la viga")
    m.ec("bew2", "6*2*(htf1+htf2)+tw+2*htf3", "cm", "Ancho be2", doc=193.04)
    m.ec("bew", "MIN(bew1,bew2)", "cm", "Ancho de alma efectivo", doc=106.68)
    m.nota("Ancho de ala efectivo de la sección compuesta: el menor de L/4, S y 6(2)ts+bew. [STD A. 9.8.3.2]")
    m.dato("S", 275, "cm", "Separación entre vigas")
    m.ec("bea1", "0.25*L1", "cm", "1/4 del tramo de diseño", doc=915)
    m.ec("bea2", "S", "cm", "Separación entre vigas", doc=275)
    m.ec("bea3", "6*2*ts+bew", "cm", "6(2)ts + bew", doc=334.68)
    m.ec("wfe", "MIN(bea1,bea2,bea3)", "cm", "Ancho de ala efectivo", doc=275)
    m.ec("ndg", "Ec/Ecs", "", "Razón modular losa/viga", tex="n_{dg}", doc=0.7888)

    m.sec("3.2.3 Propiedades de la sección transformada", 2)
    m.ec("wft", "ndg*wfe", "m", "Ancho de ala transformado", doc=2.17)
    m.ec("aft", "wft*ts", "m**2", "Área del ala transformada", doc=0.41)
    m.ec("Ift", "wft*ts**3/12", "m**4", "Inercia propia del ala", doc=0.0012)
    m.dato("th", 1.0, "cm", "Espesor mínimo de cartela (centro del tramo)")
    m.ec("wth", "ndg*bew1", "m", "Ancho de cartela transformado", doc=0.84)
    m.ec("ath", "wth*th", "m**2", "Área de cartela transformada", doc=0.0084)
    m.ec("Iat", "wth*th**3/12", "cm**4", "Inercia propia de la cartela", doc=7.013)
    _seccion_compuesta(m)

    # ------------------------------------------------------------------ 4
    m.sec("4. Fuerzas cortantes y momentos flectores")
    m.sec("4.1 Cargas muertas (CM) [STD A. 3.3]", 2)
    m.nota("Cargas sobre la sección no compuesta: viga, losa y cartela.")
    m.ec("Wd", "t*S*Wc", "tonf/m", "Peso de la losa", doc=1.32)
    m.ec("Wha", "th*bew1*Wc", "tonf/m", "Peso de la cartela", doc=0.026)
    m.ec("Ws", "Wd+Wha", "tonf/m", "Peso de losa + cartela", doc=1.35)
    m.nota("Cargas sobre la sección compuesta (barreras y capa de rodadura), distribuidas "
           "equitativamente entre todas las vigas [STD A. 3.23.2.3.1.1].")
    m.dato("Nb", 6, "", "Número de vigas")
    m.ec("WDCb", "Wb*2/Nb", "tonf/m", "Peso de las 2 barreras por viga", doc=0.15)
    m.dato("w", 14.634, "m", "Ancho de la capa de rodadura")
    m.ec("WDW", "Wcha*fws*w/Nb", "tonf/m", "Peso de la capa de rodadura por viga", doc=0.29)
    m.nota("Viga simplemente apoyada con carga uniforme q: V(x) = q(L/2 - x); M(x) = q·x(L - x)/2.")
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

    m.sec("4.2 Carga viva (CV): camión HS20 [STD A. 3.7.1.1]", 2)
    m.ec("DF1", "S/(5.5*ft)", "", "Factor de distribución (ruedas/viga)", "STD T. 3.23.1", doc=1.64)
    m.ec("DF", "DF1/2", "", "Factor de distribución (carriles/viga)", doc=0.82)
    m.ec("FDV", "DF", "", "Factor de distribución para cortante", doc=0.82)
    m.ec("FDM", "DF", "", "Factor de distribución para momento", doc=0.82)
    m.ec("Iimp", "50*ft/(L1+125*ft)", "", "Impacto I = 50/(L+125) (L en ft)", "STD Eq. 3-1", tex="I_c", doc=0.204)
    m.verif("chk_imp", "Iimp<=0.3", "Impacto no mayor a 0.3", "STD A. 3.8.2.1")
    m.ec("I", "MIN(Iimp,0.3)", "", "Impacto adoptado", doc=0.204)
    m.dato("P", 32, "kip", "Carga por eje trasero del camión HS20")
    m.dato("le1", 14, "ft", "Distancia entre ejes (delantero-central)", tex="l_1")
    m.dato("le2", 14, "ft", "Distancia entre ejes (central-trasero)", tex="l_2")
    m.dato("WLL", 0.64, "kip/ft", "Carga de carril (referencia)")
    m.nota("Envolvente del camión móvil (ejes P/4, P, P) calculada con líneas de influencia de la "
           "viga simple: cada eje se coloca sobre la sección y se prueban ambos sentidos de circulación.")
    cargas, despl = ["(P/4)", "P", "P"], ["0", "le1", "(le1+le2)"]
    filas = []
    for i, s in enumerate(SECCIONES):
        filas.append([C(None, f"xL_{i}"), C(None, f"x_{i}"),
                      C(f"VLT_{i}", f"FDV*(1+I)*{envolvente_cortante(f'x_{i}', 'L1', cargas, despl)}"),
                      C(f"MLT_{i}", f"FDM*(1+I)*{envolvente_momento(f'x_{i}', 'L1', cargas, despl)}")])
    m.tabla("Cortantes y momentos no mayorados por camión HS20 con impacto",
            ["x/L", "x", "V L+I", "M L+I"], ["", "m", "tonf", "tonf*m"], filas)

    # ------------------------------------------------------------------ 5
    m.sec("5. Estimación del pretensado")
    m.sec("5.1 Esfuerzos por carga de servicio en el centro del tramo", 2)
    m.ec("Mg", "Mg_6", "tonf*m", "Momento por peso de la viga", doc=198.84)
    m.ec("Ms", "Ms_6", "tonf*m", "Momento por losa y cartela", doc=225.31)
    m.ec("Mb", "Mb_6", "tonf*m", "Momento por barreras", doc=24.92)
    m.ec("Mws", "Mws_6", "tonf*m", "Momento por capa de rodadura", doc=49.01)
    m.ec("MLT", "MLT_6", "tonf*m", "Momento por camión + impacto", doc=256.87)
    m.ec("ftb", "(Mg+Ms)/Sb+(Mb+Mws+MLT)/Sbc", "tonf/cm**2", "Esfuerzo de tensión en la fibra inferior",
         doc=0.27)
    m.sec("5.2 Esfuerzos límites permisibles", 2)
    m.ec("Fb", "-6*SQRT(fcg/psi)*psi", "tonf/cm**2", "Tensión permisible en zona precomprimida",
         "STD A. 9.15.2.2", doc=-0.034)
    m.sec("5.3 Número de torones", 2)
    m.ec("fb_req", "ftb+Fb", "tonf/cm**2", "Precompresión requerida en la fibra inferior", tex="f_b", doc=0.24)
    m.ec("ybs_e", "0.05*hg", "cm", "Distancia estimada CG torones - fibra inferior (0.05h)", doc=9.14)
    m.dato("ybs_a", 10, "cm", "Distancia asumida CG torones - fibra inferior")
    m.ec("ec1", "yb-ybs_a", "cm", "Excentricidad del torón en el centro del tramo", doc=82.96)
    m.ec("Pse", "fb_req*Ag*Sb/(Sb+Ag*ec1)", "tonf", "Fuerza de pretensado total después de pérdidas",
         doc=444.01)
    m.dato("p_perd", 25, "pct", "Pérdida final asumida (% de fsi)", tex="p")
    m.ec("pf", "p_perd*fsi", "tonf/cm**2", "Pérdida final", doc=3.56)
    m.ec("Fse_t", "Ast*(fsi-pf)", "tonf", "Fuerza por torón después de pérdidas", tex="F_{se}", doc=10.55)
    m.ec("Nti", "Pse/Fse_t", "", "Número de torones requerido", doc=42.09)
    m.ec("Nt_min", "ROUNDUP(Nti,0)", "", "Número mínimo entero de torones")
    m.dato("Nt", 44, "", "Número de torones seleccionado", clave=True)
    m.verif("chk_Nt", "Nt>=Nti", "Torones seleccionados ≥ requeridos")

    m.sec("5.4 Distribución de torones (centro del tramo)", 2)
    filas, prod, cnt = [], [], []
    for k, (n, d) in enumerate([(12, 5), (12, 10), (8, 15), (4, 20), (2, 25), (2, 30), (2, 35), (2, 40)], 1):
        filas.append([f"y{k}", D(f"nc_{k}", n), D(f"dc_{k}", d), C(f"ADc_{k}", f"nc_{k}*dc_{k}/cm")])
        cnt.append(f"nc_{k}")
        prod.append(f"ADc_{k}")
    m.tabla("Distribución de torones en el centro del tramo",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "cm", ""], filas)
    m.ec("Nt_tab", suma(cnt), "", "Total de torones en la tabla", ftex=r"\sum A", doc=44)
    m.verif("chk_tab", "AND(Nt_tab>=Nt,Nt_tab<=Nt)", "La tabla de distribución contiene Nt torones")
    m.ec("ybs", f"({suma(prod)})*cm/Nt_tab", "cm", "Distancia CG torones - fibra inferior",
         ftex=r"\dfrac{\sum A\cdot B}{\sum A}", doc=14.55)
    m.ec("e_c", "yb-ybs", "cm", "Excentricidad de los torones", doc=78.42)

    # ------------------------------------------------------------------ 6
    m.sec("6. Pérdidas del pretensado [STD A. 9.16.2]")
    m.nota("fpT = SH + ES + CRc + CRs  [STD Eq. 9.3]")
    m.sec("6.1 Contracción del hormigón [STD A. 9.16.2.1.1]", 2)
    m.dato("RH", 70, "", "Humedad relativa (%)")
    m.ec("SH", "17000*psi-150*psi*RH", "tonf/m**2", "Pérdida por contracción", "STD Eq. 9.4", doc=4569.95)
    m.sec("6.2 Acortamiento elástico [STD A. 9.16.2.1.2]", 2)
    m.ec("Psi", "Nt*Ast*0.69*fs", "tonf", "Fuerza de pretensado después de pérdidas iniciales",
         tex="P_{si}", doc=569.341)
    m.ec("fcir", "Psi/Ag+Psi*e_c**2/Ig-Mg*e_c/Ig", "tonf/m**2", "Esfuerzo en el CG de los torones",
         doc=2005.33)
    m.ec("ES", "Ep/Eci*fcir", "tonf/m**2", "Pérdida por acortamiento elástico", "STD Eq. 9.6", doc=12845.13)
    m.sec("6.3 Flujo plástico del hormigón [STD A. 9.16.2.1.3]", 2)
    m.ec("fcds", "Ms*e_c/Ig+(Mb+Mws)*(ybc-ybs)/Ic", "tonf/m**2", "Esfuerzo en el CG de torones por CM",
         doc=979.09)
    m.ec("CRc", "12*fcir-7*fcds", "tonf/m**2", "Pérdida por flujo plástico", "STD Eq. 9.9", doc=17210.33)
    m.sec("6.4 Relajación de los torones [STD A. 9.16.2.1.4]", 2)
    m.ec("CRs", "5*ksi-0.1*ES-0.05*(SH+CRc)", "tonf/m**2", "Pérdida por relajación (baja relajación)",
         "STD Eq. 9.10A", doc=1141.82)
    m.sec("6.5 Pérdidas totales en la transferencia", 2)
    m.ec("fsi_i", "fsi-ES", "tonf/m**2", "Esfuerzo efectivo inicial de pretensado", doc=129654.87)
    m.ec("Psi_i", "Nt*Ast*fsi_i", "tonf", "Fuerza efectiva después de pérdidas iniciales",
         tex="P_{si,i}", doc=563.07)
    m.sec("6.6 Pérdidas totales en cargas de servicio", 2)
    m.ec("fpT", "SH+ES+CRc+CRs", "tonf/m**2", "Pérdidas totales", "STD Eq. 9.3", doc=35767.23)
    m.ec("pT", "fpT/(0.75*fs)", "", "Porcentaje de pérdidas totales", doc=0.251, clave=True)
    m.ec("fse", "0.75*fs-fpT", "tonf/m**2", "Esfuerzo de pretensado final efectivo", doc=106732.77)
    m.ec("Psec", "Nt*Ast*fse", "tonf", "Fuerza de pretensado efectiva", tex="P_{se,c}", doc=463.52,
         clave=True)

    # ------------------------------------------------------------------ 7
    m.sec("7. Esfuerzos en el hormigón durante la transferencia")
    m.sec("7.1 Esfuerzos límites [STD A. 9.15.2.1]", 2)
    m.ec("flc", "0.6*fci", "tonf/m**2", "Compresión permisible", doc=2280)
    m.ec("flt1", "-7.5*SQRT(fci/psi)*psi", "tonf/m**2", "Tensión máxima", doc=-387.661)
    m.ec("flt2", "-0.2*ksi", "tonf/m**2", "Tensión sin refuerzo adherido (0.2 ksi)", doc=-140.61)
    m.ec("flt3", "-3*SQRT(fci/psi)*psi", "tonf/m**2", "Tensión sin refuerzo adherido (3√f'ci)",
         doc=-155.06)
    m.sec("7.2 Esfuerzos en la longitud de transferencia", 2)
    m.ec("Ltransf", "50*dt", "m", "Longitud de transferencia (50 d)", "STD A. 9.20.2.4", doc=0.64)
    m.ec("xt", "Ltransf", "m", "Sección de análisis")
    m.ec("Mglt", "0.5*Wg*xt*(L2-xt)", "tonf*m", "Momento por peso propio (viga de longitud L2)",
         doc=13.67)
    m.ec("ft_lt", "Psi_i/Ag-Psi_i*e_c/St+Mglt/St", "tonf/m**2", "Esfuerzo en fibra superior", doc=-555.377)
    m.verif("chk_ft_lt", "ft_lt>=flt1", "Fibra superior (torones rectos)", doc="NO OK", clave=False)
    m.ec("fb_lt", "Psi_i/Ag+Psi_i*e_c/Sb-Mglt/Sb", "tonf/m**2", "Esfuerzo en fibra inferior", doc=2888.71)
    m.verif("chk_fb_lt", "fb_lt<=flc", "Fibra inferior (torones rectos)", doc="NO OK", clave=False)
    m.nota("Los esfuerzos superan los límites: se desvían torones en los puntos 0.4L (patrón 'harped').")
    m.dato("Nct", 10, "", "Torones desviados", tex="N_{c,t}")

    m.sec("Patrón de torones desviados", 2)
    filas, pb, nb = [], [], []
    for k, (n, d) in enumerate([(12, 5), (12, 10), (8, 15), (2, 20)], 1):
        filas.append([f"y{k}", D(f"ne_{k}", n), D(f"de_{k}", d), C(f"ADe_{k}", f"ne_{k}*de_{k}/cm")])
        nb.append(f"ne_{k}")
        pb.append(f"ADe_{k}")
    m.tabla("Torones rectos en el extremo (medidos desde el fondo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "cm", ""], filas)
    m.ec("Neb", suma(nb), "", "Torones inferiores rectos", tex="N_{e,b}", ftex=r"\sum A", doc=34)
    m.ec("ybe", f"({suma(pb)})*cm/Neb", "cm", "CG de torones rectos - fibra inferior", doc=10)
    filas, pt, nt = [], [], []
    for k, (n, d) in enumerate([(2, 25), (2, 20), (2, 15), (2, 10), (2, 5)], 5):
        filas.append([f"y{k}", D(f"nt_{k}", n), D(f"dt_{k}", d), C(f"ADt_{k}", f"nt_{k}*dt_{k}/cm")])
        nt.append(f"nt_{k}")
        pt.append(f"ADt_{k}")
    m.tabla("Torones desviados en el extremo (medidos desde arriba)",
            ["Fila", "# Torones (A)", "Dist. desde arriba (B)", "(A)·(B)"], ["", "", "cm", ""], filas)
    m.ec("Net", suma(nt), "", "Torones desviados", tex="N_{e,t}", ftex=r"\sum A", doc=10)
    m.ec("yte", f"({suma(pt)})*cm/Net", "cm", "CG de torones desviados - fibra superior (extremo)", doc=15)
    filas, ph, nh = [], [], []
    for k, (n, d) in enumerate([(2, 20), (2, 25), (2, 30), (2, 35), (2, 40)], 4):
        filas.append([f"y{k}", D(f"nh_{k}", n), D(f"dh_{k}", d), C(f"ADh_{k}", f"nh_{k}*dh_{k}/cm")])
        nh.append(f"nh_{k}")
        ph.append(f"ADh_{k}")
    m.tabla("Torones desviados en el punto 'harp' (medidos desde el fondo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (B)", "(A)·(B)"], ["", "", "cm", ""], filas)
    m.ec("Nmb", suma(nh), "", "Torones desviados en el punto harp", tex="N_{m,b}", ftex=r"\sum A", doc=10)
    m.ec("yph", f"({suma(ph)})*cm/Nmb", "cm", "CG de torones desviados - fibra inferior (punto harp)",
         doc=30)
    m.ec("llt", "0.4*L2", "m", "Ubicación del punto harp (0.4 L2)", doc=14.76)
    m.ec("ylt", "yte+(hg-yph-yte)/llt*Ltransf", "cm", "CG de torones desviados - fibra superior (long. transf.)",
         doc=20.93)
    m.dato("dstr", 5, "cm", "Distancia entre torones")
    m.ec("Nblt", "Neb", "", "Torones rectos", tex="N_{blt}", doc=34)
    m.ec("Ntlt", "Nt-Nblt", "", "Torones desviados", tex="N_{tlt}", doc=10)
    m.verif("chk_Ntlt", "AND(Ntlt>=Net,Ntlt<=Net)", "Torones desviados coinciden con la tabla del extremo")
    m.ec("y_lt", "(Nblt*ybe+Ntlt*(hg-ylt))/Nt", "cm", "CG de todos los torones (long. transf.)", doc=44.53)
    filas, pe = [], []
    for k in range(1, 5):
        filas.append([f"y{k}", C(None, f"ne_{k}"), C(None, f"de_{k}/cm"), C(f"AEx_{k}", f"ne_{k}*de_{k}/cm")])
        pe.append(f"AEx_{k}")
    for k in range(5, 10):
        filas.append([f"y{k + 1}", C(None, f"nt_{k}"), C(f"dEx_{k}", f"(hg-dt_{k})/cm"),
                      C(f"AEx_{k}", f"nt_{k}*dEx_{k}")])
        pe.append(f"AEx_{k}")
    m.tabla("Patrón de torones en el extremo (desde el fondo)",
            ["Fila", "# Torones (A)", "Dist. al fondo (cm) (B)", "(A)·(B)"], ["", "", "", ""], filas)
    m.ec("ybs_ext", f"({suma(pe)})*cm/Nt", "cm", "CG de todos los torones - fondo (extremo)", doc=45.88)
    m.ec("elt", "yb-y_lt", "cm", "Excentricidad en la longitud de transferencia", tex="e_{lt}", doc=48.43)
    m.nota("Recálculo de esfuerzos en la sección de longitud de transferencia con torones desviados.")
    m.ec("ft_ext", "Psi_i/Ag-Psi_i*elt/St+Mglt/St", "tonf/m**2", "Esfuerzo en fibra superior", doc=112.871)
    m.verif("chk_ft_ext", "ft_ext<=flc", "Fibra superior (con torones desviados)", doc="OK")
    m.ec("fb_ext", "Psi_i/Ag+Psi_i*elt/Sb-Mglt/Sb", "tonf/m**2", "Esfuerzo en fibra inferior", doc=2197.81)
    m.verif("chk_fb_ext", "fb_ext<=flc", "Fibra inferior (con torones desviados)", doc="OK")

    m.sec("7.3 Esfuerzos en los puntos 'harp'", 2)
    m.ec("xph", "llt", "m", "Ubicación del punto harp")
    m.ec("Mgph", "0.5*Wg*xph*(L2-xph)", "tonf*m", "Momento por peso de la viga", doc=194.033)
    m.ec("ft_ph", "Psi_i/Ag-Psi_i*e_c/St+Mgph/St", "tonf/m**2", "Esfuerzo en fibra superior", doc=158.41)
    m.verif("chk_ft_ph", "ft_ph<=flc", "Fibra superior en punto harp", doc="OK")
    m.ec("fb_ph", "Psi_i/Ag+Psi_i*e_c/Sb-Mgph/Sb", "tonf/m**2", "Esfuerzo en fibra inferior", doc=2150.73)
    m.verif("chk_fb_ph", "fb_ph<=flc", "Fibra inferior en punto harp", doc="OK")
    m.sec("7.4 Esfuerzos en el centro del tramo", 2)
    m.ec("xcl", "0.5*L2", "m", "Centro del tramo", doc=18.45)
    m.ec("Mgcl", "0.5*Wg*xcl*(L2-xcl)", "tonf*m", "Momento por peso de la viga", doc=202.117)
    m.ec("ft_cl", "Psi_i/Ag-Psi_i*e_c/St+Mgcl/St", "tonf/m**2", "Esfuerzo en fibra superior", doc=190.404)
    m.verif("chk_ft_cl", "ft_cl<=flc", "Fibra superior en centro del tramo", doc="OK")
    m.ec("fb_cl", "Psi_i/Ag+Psi_i*e_c/Sb-Mgcl/Sb", "tonf/m**2", "Esfuerzo en fibra inferior", doc=2117.65)
    m.verif("chk_fb_cl", "fb_cl<=flc", "Fibra inferior en centro del tramo", doc="OK")
    m.sec("7.5 Fuerza de sujeción", 2)
    m.ec("fs_s", "0.8*fs", "tonf/m**2", "Esfuerzo inicial máximo antes de pérdidas", tex="f_s", doc=152000)
    m.ec("Fs_t", "Ast*fs_s", "tonf", "Fuerza inicial por torón", tex="F_s", doc=15)
    m.ec("psi_h", "ATAN((hg-yph-yte)/llt)", "deg", "Ángulo 'harp'", tex=r"\psi", doc=5.34)
    m.dato("ff", 1.05, "", "Factor de fricción", tex="f_f")
    m.ec("Fsuj", "ff*Fs_t*SIN(psi_h)", "tonf", "Fuerza de sujeción por torón", doc=1.47)
    m.ec("Fsujtot", "Ntlt*Fsuj", "tonf", "Fuerza de sujeción total", doc=14.65, clave=True)

    # ------------------------------------------------------------------ 8
    m.sec("8. Esfuerzos en el hormigón debido a las cargas de servicio")
    m.sec("8.1 Esfuerzos límites [STD A. 9.15.2.2]", 2)
    m.ec("fpcsl2", "0.6*fcg", "tonf/m**2", "Caso I - compresión en viga", doc=2700)
    m.ec("fpcsl1", "0.6*fcs", "tonf/m**2", "Caso I - compresión en losa", doc=1680)
    m.ec("fpttsl2", "-6*SQRT(fcg/psi)*psi", "tonf/m**2", "Tensión en viga", doc=-337.487)
    m.ec("fptcsl2", "0.4*fcg", "tonf/m**2", "Caso II - compresión en viga", doc=1800)
    m.ec("fptcsl1", "0.4*fcs", "tonf/m**2", "Caso II - compresión en losa", doc=1120)
    m.ec("fciii2", "0.4*fcg", "tonf/m**2", "Caso III - compresión en viga", doc=1800)
    m.ec("fciii1", "0.4*fcs", "tonf/m**2", "Caso III - compresión en losa", doc=1120)
    m.sec("8.2 Esfuerzos en el centro del tramo", 2)
    m.ec("ftg1", "Psec/Ag-Psec*e_c/St+(Mg+Ms)/St+(Mws+Mb)/Stg+MLT/Stg", "tonf/m**2",
         "Fibra superior de la viga - Caso I", doc=1494.58)
    m.verif("chk_ftg1", "ftg1<=fpcsl2", "Fibra superior viga - Caso I", doc="OK")
    m.ec("ftg2", "Psec/Ag-Psec*e_c/St+(Mg+Ms)/St+(Mws+Mb)/Stg", "tonf/m**2",
         "Fibra superior de la viga - Caso II", doc=1247.898)
    m.verif("chk_ftg2", "ftg2<=fptcsl2", "Fibra superior viga - Caso II", doc="OK")
    m.ec("ftg3", "ftg2/2+MLT/Stg", "tonf/m**2", "Fibra superior de la viga - Caso III", doc=870.63)
    m.verif("chk_ftg3", "ftg3<=fciii2", "Fibra superior viga - Caso III", doc="OK")
    m.ec("fb_s", "Psec/Ag+Psec*e_c/Sb-(Mg+Ms)/Sb-(Mws+Mb)/Sbc-MLT/Sbc", "tonf/m**2",
         "Fibra inferior de la viga", tex="f_b", doc=-318.047)
    m.verif("chk_fb_s", "fb_s<=fpcsl2", "Fibra inferior viga - compresión", doc="OK")
    m.verif("chk_fb_t", "fb_s>=fpttsl2", "Fibra inferior viga - tensión (≥ -6√f'c)")
    m.ec("ftg1t", "(Mws+Mb)/Stc+MLT/Stc", "tonf/m**2", "Fibra superior de la losa - Caso I", doc=364.822)
    m.verif("chk_ftg1t", "ftg1t<=fpcsl1", "Losa - Caso I", doc="OK")
    m.ec("ftg2t", "(Mws+Mb)/Stc", "tonf/m**2", "Fibra superior de la losa - Caso II", doc=81.532)
    m.verif("chk_ftg2t", "ftg2t<=fptcsl1", "Losa - Caso II", doc="OK")
    m.ec("ftg3t", "0.5*(Mws+Mb)/Stc+MLT/Stc", "tonf/m**2", "Fibra superior de la losa - Caso III",
         doc=324.056)
    m.verif("chk_ftg3t", "ftg3t<=fciii1", "Losa - Caso III", doc="OK")

    # ------------------------------------------------------------------ 9
    m.sec("9. Resistencia a la flexión [STD A. 9.17]")
    m.nota("Momento de diseño: Grupo I - combinación LFD [STD T. 3.22.1A].")
    m.dato("gamma", 1.3, "", "Factor γ", tex=r"\gamma")
    m.dato("betaD", 1, "", "Factor βD", tex=r"\beta_D")
    m.dato("betaL", 1.67, "", "Factor βL", tex=r"\beta_L")
    m.ec("Mu", "gamma*(betaD*(Mg+Mb+Ms+Mws)+betaL*MLT)", "tonf*m", "Momento último", doc=1205.184, clave=True)
    m.dato("gammap", 0.28, "", "γ' para torón de baja relajación", "STD A. 9.1.2", tex=r"\gamma'")
    m.ec("beta1", "IF(ROUND(fcs/(kgf/cm**2),6)<=280,0.85,IF(ROUND(fcs/(kgf/cm**2),6)>550,0.65,"
                  "0.85-0.05*(fcs-280*kgf/cm**2)/(70*kgf/cm**2)))", "",
         "Factor del bloque de compresión β1", "STD A. 8.16.2.7", doc=0.85)
    m.ec("Aps", "Nt*Ast", "mm**2", "Área de los torones A's", tex="A'_s", doc=4342.8)
    m.ec("b", "wfe", "cm", "Ancho efectivo del ala", doc=275)
    m.ec("d", "hg+th+ts-ybs", "cm", "Peralte al centroide de los torones", doc=188.33)
    m.ec("rho", "Aps/(b*d)", "", "Cuantía ρ'", tex=r"\rho'", doc=0.00084)
    m.ec("fsu", "fs*(1-gammap/beta1*rho*fs/fcs)", "tonf/m**2", "Esfuerzo promedio en el torón (carga última)",
         "STD Eq. 9-17", tex="f^*_{su}", doc=186438.81)
    m.ec("a", "Aps*fsu/(0.85*fcs*b)", "cm", "Profundidad del bloque de compresión", "STD Eq. 9-17.2", doc=12.37)
    m.verif("chk_a", "a<ts", "Bloque dentro del ala (sección rectangular)", doc="OK")
    m.dato("phi", 1, "", "Factor de reducción de resistencia (flexión)", "STD A. 9.14", tex=r"\phi")
    m.ec("Mn", "Aps*fsu*d*(1-0.6*rho*fsu/fcs)", "tonf*m", "Resistencia nominal a flexión", "STD Eq. 9-13",
         doc=1473.8)
    m.ec("Mr", "phi*Mn", "tonf*m", "Resistencia a flexión mayorada", doc=1473.799, clave=True)
    m.verif("chk_Mr", "Mr>Mu", "Resistencia a flexión Mr > Mu", doc="OK")

    # ------------------------------------------------------------------ 10
    m.sec("10. Límites del refuerzo")
    m.sec("10.1 Máximo refuerzo [STD A. 9.18.1]", 2)
    m.ec("Ir", "rho*fsu/fcs", "", "Índice de refuerzo ρ'·f*su/f'c", "STD Eq. 9-20", doc=0.0558)
    m.verif("chk_Ir", "Ir<0.36*beta1", "Refuerzo máximo", doc="OK")
    m.sec("10.2 Mínimo refuerzo [STD A. 9.18.2]", 2)
    m.ec("fr", "7.5*SQRT(fcg/psi)*psi", "tonf/m**2", "Módulo de ruptura", "STD A. 9.15.2.3", doc=421.8584)
    m.ec("fpe", "Psec/Ag+Psec*e_c/Sb", "tonf/m**2", "Compresión por pretensado efectivo en fibra inferior",
         doc=2424.06)
    m.ec("Mdnc", "Mg+Ms", "tonf*m", "Momento por CM en la sección no compuesta", doc=424.16)
    m.ec("Mcr", "Sbc*(fr+fpe)-Mdnc*(Sbc/Sb-1)", "tonf*m", "Momento de fisuración", doc=789.077)
    m.ec("Mcr12", "1.2*Mcr", "tonf*m", "1.2 Mcr", tex=r"1.2M_{cr}", doc=946.89)
    m.verif("chk_Mcr", "Mcr12<Mr", "Refuerzo mínimo: φMn ≥ 1.2 Mcr", doc="OK")

    # ------------------------------------------------------------------ 11
    m.sec("11. Diseño por corte [STD A. 9.20]")
    m.nota("Vu ≤ φ(Vc + Vs)  [STD Eq. 9-26]. La sección crítica se considera a hc/2 desde el eje del apoyo.")
    m.dato("phic", 0.9, "", "Factor de reducción para cortante", "STD A. 9.14", tex=r"\phi_c")
    m.ec("hc", "0.5*(hg+t)", "cm", "Ubicación de la sección crítica (h/2)", doc=101.44)
    m.nota("Las fuerzas en la sección crítica se toman de la fila x/L = 0.0278 de las tablas.")
    m.ec("bp", "tw", "cm", "Ancho del alma b'", tex="b'", doc=15.24)
    m.ec("Vd", "Vg_1+Vs_1+Vb_1+Vws_1", "tonf", "Cortante por CM", doc=51.41)
    m.ec("VLT1", "VLT_1", "tonf", "Cortante por CV + impacto", doc=28.85)
    m.ec("Md", "Mg_1+Ms_1+Mb_1+Mws_1", "tonf*m", "Momento por CM", doc=53.8)
    m.ec("MLT1", "MLT_1", "tonf*m", "Momento por CV + impacto", doc=29.32)
    m.ec("Vu", "gamma*(betaD*Vd+betaL*VLT1)", "tonf", "Cortante mayorado", doc=129.467, clave=True)
    m.ec("Mu1", "gamma*(betaD*Md+betaL*MLT1)", "tonf*m", "Momento mayorado", doc=133.603)
    m.ec("Vmu", "Vu", "tonf", "Cortante mayorado simultáneo con Mu", doc=129.467)
    m.ec("Mmax", "Mu1-Md", "tonf*m", "Momento mayorado por cargas externas", doc=79.8)
    m.ec("Vi", "Vu-Vd", "tonf", "Cortante mayorado por cargas externas", doc=78.05)
    m.ec("dext", "0.5*(L2-L1)", "cm", "Distancia eje del apoyo - extremo de la viga", doc=15)
    m.ec("cg10t", "yte+(hg-yph-yte)/(0.4*L2)*(hc+dext)", "cm", "CG de torones desviados desde arriba (h/2)",
         doc=25.88)
    m.ec("cgtt", "(Nmb*(hg-cg10t)+Neb*ybe)/Nt", "cm", "CG de todos los torones desde el fondo (h/2)",
         doc=43.41)
    m.ec("et", "yb-cgtt", "cm", "Excentricidad de los torones en h/2", tex="e_t", doc=49.55)
    m.ec("fpeb", "Psec/Ag+Psec*et/Sb", "tonf/m**2", "Compresión por pretensado (fibra inferior)", doc=1876.623)
    m.ec("fd", "(Mg_1+Ms_1)/Sb+(Mb_1+Mws_1)/Sbc", "tonf/m**2", "Esfuerzo por CM no mayorada", doc=211.776)
    m.ec("Mcre", "(6*SQRT(fcg/psi)*psi+fpeb-fd)*Sbc", "tonf*m", "Momento de fisuración por cargas externas",
         "STD Eq. 9.28", tex="M_{cr,e}", doc=658.05)
    m.ec("d1", "0.8*hsc", "cm", "0.8 hc", doc=162.3)
    m.ec("d2", "hsc-cgtt", "cm", "Distancia fibra comprimida - CG del refuerzo", doc=159.47)
    m.sel("chk_d2", "d2>0.8*hsc", "OK", "NO OK", "d ≥ 0.8 hc", "STD A. 9.20.2.2", doc="NO OK")
    m.ec("dv1", "MAX(d2,d1)", "cm", "Peralte d adoptado", doc=162.3)
    m.ec("Vci", "0.6*SQRT(fcg/psi)*psi*bp*dv1+Vd+Vi*Mcre/Mmax", "tonf", "Resistencia Vci", "STD Eq. 9-27",
         doc=703.43)
    m.ec("Vcimin", "1.7*SQRT(fcg/psi)*psi*bp*dv1", "tonf", "Vci mínimo", "STD A. 9.20.2.2", doc=23.65)
    m.verif("chk_Vci", "Vcimin<Vci", "Vci ≥ Vci mín", doc="OK")
    m.ec("fpc", "Psec/Ag-Psec*et*(ybc-yb)/Ig+(Mg_1+Ms_1)*(ybc-yb)/Ig", "tonf/m**2",
         "Compresión en el centroide de la sección compuesta", doc=564.138)
    m.ec("Pseph", "Net*Ast*fse", "tonf", "Pretensado efectivo de torones desviados", doc=105.35)
    m.ec("Vp", "Pseph*SIN(psi_h)", "tonf", "Componente vertical del pretensado", doc=9.8)
    m.ec("Vcw", "(3.5*SQRT(fcg/psi)*psi+0.3*fpc)*bp*dv1+Vp", "tonf", "Resistencia Vcw", "STD Eq. 9-29",
         doc=100.36)
    m.ec("Vc", "MIN(Vci,Vcw)", "tonf", "Resistencia nominal del hormigón", doc=100.36)
    m.ec("Vs", "Vu/phic-Vc", "tonf", "Resistencia requerida del refuerzo", doc=43.5)
    m.ec("Vsmax", "8*SQRT(fcg/psi)*psi*bp*dv1", "tonf", "Vs máximo", "STD A. 9.20.3.1", doc=111.3)
    m.verif("chk_Vsmax", "Vsmax>Vs", "Vs ≤ Vs máx", doc="OK")
    m.dato("sp", 30, "cm", "Separación de estribos escogida")
    m.ec("Avp", "sp*Vs/(fy*dv1)", "cm**2", "Área de refuerzo requerida", "STD Eq. 9.30", doc=1.914)
    m.ec("Avmin", "50*bp*sp/(fy/psi)", "cm**2", "Área mínima de refuerzo transversal", "STD Eq. 9.31",
         doc=0.383)
    m.ec("Avmax", "MAX(Avmin,Avp)", "cm**2", "Área requerida", doc=1.914)
    m.ec("Vsc", "4*SQRT(fcg/psi)*psi*bp*dv1", "tonf", "Límite 4√f'c b'd", "STD A. 9.20.3.2", doc=55.65)
    m.sel("chk_Vsc", "Vs>Vsc", "OK", "NO OK", "Vs > 4√f'c b'd (espaciamiento reducido)", doc="NO OK")
    m.ec("sc", "0.75*hsc", "cm", "Espaciamiento máx. (I) 0.75 hc", doc=152.16)
    m.dato("smaxc", 24, "inch", "Espaciamiento máx. (II)")
    m.ec("Smax", "MIN(smaxc,sc)", "cm", "Espaciamiento máximo", doc=60.96)
    m.verif("chk_Smax", "Smax>sp", "Separación ≤ máxima", doc="OK")
    m.dato("db", 1.2, "cm", "Diámetro del estribo")
    m.ec("Ab", "0.25*PI()*db**2", "cm**2", "Área de una barra", doc=1.13)
    m.ec("Abt", "2*Ab", "cm**2", "Área de estribo (2 ramas)", doc=2.262)
    m.verif("chk_Abt", "Abt>Avmax", "Estribo proporcionado ≥ requerido", doc="OK")

    # ------------------------------------------------------------------ 12
    m.sec("12. Diseño del cortante horizontal [STD A. 9.20.4]")
    m.ec("Vnh", "Vu/phic", "tonf", "Resistencia requerida al corte horizontal", "STD Eq. 9.31a", doc=143.85)
    m.ec("Vnhab", "80*psi*bew1*d2", "tonf", "Caso (a&b): 80 bv d", "STD Art. 9.20.4.3", doc=95.69)
    m.sel("chk_Vnhab", "Vnhab>Vnh", "OK", "NO OK", "Caso (a&b): superficie rugosa", doc="NO OK")
    m.ec("Vnhc", "350*psi*bew1*d2", "tonf", "Caso (c): 350 bv d", "STD Art. 9.20.4.3", doc=418.63)
    m.verif("chk_Vnhc", "Vnhc>Vnh", "Cortante horizontal - Caso (c)", doc="OK")
    m.ec("Avh", "50*bew1*sp/(fy/psi)", "cm**2", "Mínimo Avh", "STD A. 9.20.4.5", doc=2.68)
    m.verif("chk_Avh", "Abt>=Avh", "Refuerzo proporcionado ≥ Avh mínimo", doc="NO OK")
    m.ec("smaxvh1", "4*tw", "cm", "Espaciamiento máx. 4b", doc=60.96)
    m.dato("smaxc2", 24, "inch", "Espaciamiento máx. 24 in")
    m.ec("Smaxvh", "MIN(smaxvh1,smaxc2)", "cm", "Espaciamiento máximo", doc=60.96)
    m.verif("chk_Smaxvh", "Smaxvh>sp", "Separación ≤ máxima (corte horizontal)", doc="OK")

    # ------------------------------------------------------------------ 13
    m.sec("13. Zona de anclaje pretensada [STD A. 9.22]")
    m.sec("13.1 Mínimo refuerzo vertical [STD A. 9.22.1]", 2)
    m.dato("fs_anc", 20, "ksi", "Esfuerzo unitario de los estribos verticales", tex="f_s")
    m.ec("Psiza", "Nt*Ast*fsi", "tonf", "Fuerza en torones antes de pérdidas", tex="P_{si}", doc=618.85)
    m.ec("Pr", "0.04*Psiza", "tonf", "4% de la fuerza de pretensado", doc=24.75)
    m.ec("d025", "0.25*d2", "cm", "Distancia d/4 desde el extremo", doc=39.87)
    m.ec("Asza", "Pr/fs_anc", "cm**2", "Área requerida de acero", doc=17.6)
    m.dato("Nbza", 5, "", "Pares de barras")
    m.dato("dbza", 1.6, "cm", "Diámetro de barra")
    m.ec("Abza", "PI()/4*dbza**2", "cm**2", "Área de una barra", doc=2.01)
    m.ec("Abtza", "Nbza*2*Abza", "cm**2", "Área total proporcionada", doc=20.11)
    m.verif("chk_Abtza", "Abtza>Asza", "Refuerzo en zona de anclaje", doc="OK")
    m.dato("sep_za", 3, "inch", "Espaciamiento")
    m.dato("dza", 2, "inch", "Primera barra desde el extremo")
    m.sec("13.2 Refuerzo de confinamiento [STD A. 9.22.2]", 2)
    m.nota("Para una distancia d desde el extremo de la viga se coloca refuerzo para confinar los torones "
           "en el ala inferior.")

    # ------------------------------------------------------------------ 14
    m.sec("14. Deflexión y contraflecha")
    m.sec("14.1 Contraflecha por pretensado en la transferencia", 2)
    m.ec("e_p", "e_c-(yb-ybs_ext)", "cm", "Diferencia de excentricidad centro - extremo", tex="e'", doc=31.34)
    m.ec("a_hp", "llt", "m", "Distancia del extremo al punto harp", tex="a", doc=14.76)
    m.ec("Dp", "Psi_i/(Eci*Ig)*(e_c*L2**2/8-e_p*a_hp**2/6)", "cm", "Contraflecha por pretensado (↑)",
         tex=r"\Delta_p", doc=9.67)
    m.sec("14.2 Deflexión por peso de la viga", 2)
    m.ec("Dg", "5*Wg*L2**4/(384*Eci*Ig)", "cm", "En la transferencia (↓)", tex=r"\Delta_g", doc=4.03)
    m.ec("Dgi", "5*Wg*L1**4/(384*Eci*Ig)", "cm", "En el izaje (↓)", tex=r"\Delta_{gi}", doc=3.9)
    m.sec("14.3 Resumen", 2)
    m.ec("Dpg", "Dp-Dg", "cm", "En la transferencia (↑)", tex=r"\Delta_{pg}", doc=5.64)
    m.ec("Dpg2", "1.8*Dp-1.85*Dgi", "cm", "Total en el izaje, factores PCI (↑)", tex=r"\Delta_{pg,izaje}",
         doc=10.19, clave=True)
    m.sec("14.4 Deflexión por peso de losa y cartela", 2)
    m.ec("Ds", "5*Ws*L1**4/(384*Ecs*Ig)", "cm", "Deflexión (↓)", tex=r"\Delta_s", doc=4.07)
    m.sec("14.5 Deflexión por barreras y capa de rodadura", 2)
    m.ec("Dbws", "5*(WDCb+WDW)*L1**4/(384*Ecs*Ic)", "cm", "Deflexión (↓)", tex=r"\Delta_{b+ws}", doc=0.66)
    m.sec("14.6 Deflexión por carga viva e impacto", 2)
    m.ec("DLDef", "L1/800", "cm", "Deflexión permitida L/800", tex=r"\Delta_{LL,adm}", doc=4.58)
    m.ec("NL", "INT(w/(3.65*m))", "", "Número de carriles", doc=4)
    m.ec("FDF", "NL/Nb", "", "Factor de distribución para deflexión", doc=0.667)
    m.nota("Es más conservador usar el factor de distribución para momento, FDM.")
    m.dato("L2cd", 4.268, "m", "Separación entre ejes del camión")
    m.ec("DP2", "0.25*P*L1**3/(48*Ecs*Ic)", "cm", "Deflexión por eje delantero (P/4) al centro",
         tex=r"\Delta_{P2}", doc=0.24)
    m.ec("aCD1", "(L1-L2cd)/2", "m", "Posición de los ejes traseros", tex="a_{CD1}", doc=16.17)
    m.ec("DP1", "P*aCD1/(24*Ecs*Ic)*(3*L1**2-4*aCD1**2)", "cm", "Deflexión por ejes traseros",
         tex=r"\Delta_{P1}", doc=1.87)
    m.ec("DPT", "DP1+DP2", "cm", "Deflexión total del camión", tex=r"\Delta_{PT}", doc=2.11)
    m.ec("FIM", "1+I", "", "Factor de impacto", doc=1.2)
    m.ec("DLT", "DPT*FIM*FDM", "cm", "Deflexión por CV + impacto", tex=r"\Delta_{LT}", doc=2.08, clave=True)
    m.verif("chk_DLT", "DLT<DLDef", "Deflexión por carga viva ≤ L/800", doc="OK")
    return m


def _seccion_compuesta(m: Modulo):
    """Tabla de propiedades de la sección compuesta (común a STD y LRFD)."""
    m.tabla("Propiedades de la sección compuesta (parte 1)",
            ["Elemento", "Área", "yb", "A·yb", "I propia"],
            ["", "m**2", "m", "m**3", "m**4"],
            [["Viga", C("A_v", "Ag"), C("y_v", "yb"), C("Ay_v", "A_v*y_v"), C("I_v", "Ig")],
             ["Cartela", C("A_h", "ath"), C("y_h", "hg+th/2"), C("Ay_h", "A_h*y_h"), C("I_h", "Iat")],
             ["Losa", C("A_l", "aft"), C("y_l", "hg+th+ts/2"), C("Ay_l", "A_l*y_l"), C("I_l", "Ift")]])
    m.ec("Ac", "A_v+A_h+A_l", "m**2", "Área total de la sección compuesta", doc=0.915)
    m.ec("ybc", "(Ay_v+Ay_h+Ay_l)/Ac", "m", "CG de la sección compuesta - fibra inferior de la viga", doc=1.39)
    m.tabla("Propiedades de la sección compuesta (parte 2: Steiner)",
            ["Elemento", "A(ybc - yb)²", "I + A(ybc - yb)²"],
            ["", "m**4", "m**4"],
            [["Viga", C("Ad_v", "A_v*(ybc-y_v)**2"), C("It_v", "I_v+Ad_v")],
             ["Cartela", C("Ad_h", "A_h*(ybc-y_h)**2"), C("It_h", "I_h+Ad_h")],
             ["Losa", C("Ad_l", "A_l*(ybc-y_l)**2"), C("It_l", "I_l+Ad_l")]])
    m.ec("Ic", "It_v+It_h+It_l", "m**4", "Inercia de la sección compuesta", doc=0.457)
    m.ec("hsc", "hg+th+ts", "m", "Altura total de la sección compuesta", doc=2.03)
    m.ec("ytg", "hg-ybc", "cm", "CG - fibra superior de la viga", doc=43.87)
    m.ec("ytc", "hsc-ybc", "cm", "CG - fibra superior de la losa", doc=63.87)
    m.ec("Sbc", "Ic/ybc", "m**3", "Módulo de sección compuesta, fibra inferior viga", doc=0.33)
    m.ec("Stg", "Ic/ytg", "m**3", "Módulo de sección compuesta, fibra superior viga", doc=1.04)
    m.ec("Stc", "1/ndg*(Ic/ytc)", "m**3", "Módulo de sección compuesta, fibra superior losa", doc=0.91)
