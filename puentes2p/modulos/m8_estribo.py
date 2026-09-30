"""Módulo 8 - Estribo sobre cimentación superficial. AASHTO LRFD 2017. Págs. 41-51 del PDF."""
from ..motor import C, D, Modulo

COMBOS = [("RMax", "Resistencia I - Máx."), ("RMin", "Resistencia I - Mín."),
          ("EMax", "Evento Extremo I - Máx."), ("EMin", "Evento Extremo I - Mín."), ("S", "Servicio I")]


def construir(sobrescribir=None) -> Modulo:
    m = Modulo("EST", "Estribo sobre cimentación superficial - AASHTO LRFD", "8_Estribo",
               "Diseño de estribo en voladizo de un puente de tramo simple sobre suelo no rocoso. "
               "AASHTO LRFD 2017.", sobrescribir)
    m.sec("Datos")
    m.dato("fcest", 21, "MPa", "f'c del estribo", tex=r"f'_{c,est}")
    m.dato("fcsup", 28, "MPa", "f'c de la superestructura", tex=r"f'_{c,sup}")
    m.dato("fy", 420, "MPa", "Fluencia del acero de refuerzo")
    m.dato("PEH", 2400, "kgf/m**3", "Peso específico del hormigón", tex=r"\gamma_{H}")
    m.nota("Información del suelo: suelo no rocoso.")
    m.dato("PUS", 2000, "kgf/m**3", "Peso específico del suelo", tex=r"\gamma_s")
    m.dato("qn", 1.2, "MPa", "Capacidad de carga nominal del suelo")
    m.dato("phif", 30, "deg", "Ángulo efectivo de fricción interna del suelo", tex=r"\phi'_f")
    m.dato("PGA", 0.20, "", "Coeficiente de aceleración pico del terreno")
    m.sec("Cargas provenientes de la superestructura (por metro de estribo)")
    m.dato("DC", 11000, "kgf/m", "Carga muerta de componentes")
    m.dato("DW", 1500, "kgf/m", "Carga muerta de superficie de rodadura")
    m.dato("LLIM", 9300, "kgf/m", "Carga viva + impacto", tex=r"LL_{LL+IM}")
    m.dato("BR", 1570, "kgf/m", "Fuerza de frenado")

    m.sec("Cargas y momentos debido al peso de la subestructura")
    m.dato("Lest", 10.5, "m", "Longitud del estribo")
    for n, v in (("l1", 1.1), ("l2", 3.4), ("l3", 1.0), ("l4", 1.5), ("l5", 0.3), ("l6", 0.6), ("l8", 1.2),
                 ("l9", 2.8), ("l10", 1.1)):
        m.dato(n, v, "m", f"Dimensión {n} del estribo", tex=f"l_{{{n[1:]}}}")
    m.ec("l7", "l2+l3", "m", "Altura de la pantalla bajo el espaldar", tex="l_{7}", doc=4.4)
    m.ec("H", "l1+l2+l3+l4", "m", "Altura del relleno", doc=7)
    m.ec("Dcim", "l1", "m", "Altura del cimiento", tex="D", doc=1.1)
    m.ec("B", "l8+l5+l6+l9", "m", "Base del estribo", doc=4.9)
    m.nota("DC por metro: zapata, pantalla y espaldar se calculan por metro de ancho; topes y muros de ala "
           "se reparten en la longitud del estribo Lest. Brazos medidos desde la punta de la zapata.")
    elems = [("zapata", "B", "l1", 1.0, 1, "m", "B/2"),
             ("pantalla", "l5+l6", "l7", 1.0, 1, "m", "l8+(l5+l6)/2"),
             ("espaldar", "l5", "l4", 1.0, 1, "m", "l8+l6+l5/2"),
             ("topes", "l6", "l10", 0.8, 2, "Lest", "l8+l6/2"),
             ("muros ala", "l9", "l2+l3+l4", 0.5, 2, "Lest", "l8+l5+l6+l9/2")]
    filas = []
    for k, (n, bb, hh, an, cu, div, x) in enumerate(elems, 1):
        filas.append([n, C(f"eb_{k}", bb), C(f"eh_{k}", hh), D(f"ea_{k}", an), D(f"eu_{k}", cu),
                      C(f"evol_{k}", f"eb_{k}*eh_{k}*ea_{k}*eu_{k}"),
                      C(f"eDC_{k}", f"evol_{k}*PEH/{div}"),
                      C(f"ex_{k}", x), C(f"eM_{k}", f"eDC_{k}*ex_{k}")])
    m.tabla("Peso propio del estribo", ["Sección", "Base", "Altura", "Ancho", "Cantidad", "Volumen", "DC",
                                        "x", "Mx"],
            ["", "m", "m", "m", "", "m**3", "tonf/m", "m", "tonf*m/m"], filas)
    m.ec("DCest", "+".join(f"eDC_{k}" for k in range(1, 6)), "tonf/m", "Peso propio del estribo",
         tex=r"DC_{est}", ftex=r"\sum DC_i", doc=27.54)
    m.ec("MxDCest", "+".join(f"eM_{k}" for k in range(1, 6)), "tonf*m/m", "Momento del peso propio",
         tex=r"Mx_{DC,est}", ftex=r"\sum DC_i\,x_i", doc=63.06)
    m.ec("xDCest", "MxDCest/DCest", "m", "Brazo del peso propio", tex=r"x_{DC,est}", doc=2.29)
    m.sec("Carga y momento debidos al peso propio del relleno", 2)
    m.ec("BaseEV", "l9", "m", "Base del relleno", tex=r"Base_{EV}", doc=2.8)
    m.ec("AltoEV", "l2+l3+l4", "m", "Altura del relleno", tex=r"Alto_{EV}", doc=5.9)
    m.ec("EV", "BaseEV*AltoEV*PUS", "tonf/m", "Peso del relleno", doc=33.04)
    m.ec("xrell", "B-l9/2", "m", "Brazo del relleno", tex=r"x_{relleno}", doc=3.5)
    m.ec("MxEV", "EV*xrell", "tonf*m/m", "Momento del relleno", tex=r"Mx_{EV}", doc=115.64)

    m.sec("Sobrecarga por carga viva sobre el relleno (LS) [A. 3.11.5.3, A. 3.11.6.4]")
    m.dato("delta", 0, "deg", "Ángulo de fricción relleno-muro", tex=r"\delta")
    m.dato("beta", 0, "deg", "Ángulo del relleno con la horizontal", tex=r"\beta")
    m.dato("theta", 90, "deg", "Ángulo de la cara posterior del muro con la horizontal", tex=r"\theta")
    m.ec("ka_c", "SIN(theta+phif)**2/((1+SQRT(SIN(phif+delta)*SIN(phif-beta)/(SIN(theta-delta)*SIN(theta+beta))))**2"
               "*SIN(theta)**2*SIN(theta-delta))", "", "Coeficiente de empuje activo (Coulomb)", "A. 3.11.5.3-1",
         tex="k_a", doc=0.33)
    m.dato("heq", 600, "mm", "Altura equivalente de suelo por sobrecarga", "T. 3.11.6.4-1")
    m.ec("DpLS", "ka_c*PUS*heq", "tonf/m**2", "Presión por sobrecarga", tex=r"\Delta p_{LS}", doc=0.4)
    m.ec("LSy", "DpLS*l9", "tonf/m", "Componente vertical de la sobrecarga", doc=1.12)
    m.ec("MxLSy", "LSy*xrell", "tonf*m/m", "Momento estabilizante de la sobrecarga", tex=r"Mx_{LSy}", doc=3.92)

    m.sec("Acciones verticales por metro de estribo", 2)
    m.ec("xDC", "l8+l6/2", "m", "Brazo de DC y DW de la superestructura", tex="x_{DC}", doc=1.5)
    m.ec("MxDC", "DC*xDC", "tonf*m/m", "Momento de DC superestructura", tex=r"Mx_{DC}", doc=16.5)
    m.ec("MxDW", "DW*xDC", "tonf*m/m", "Momento de DW", tex=r"Mx_{DW}", doc=2.25)
    m.ec("MxLL", "LLIM*xDC", "tonf*m/m", "Momento de LL+IM", tex=r"Mx_{LL+IM}", doc=13.95)
    m.ec("SV", "DCest+DC+DW+LLIM+EV+LSy", "tonf/m", "Suma de fuerzas verticales", tex=r"\Sigma V", doc=83.5)
    m.ec("SMV", "MxDCest+MxDC+MxDW+MxLL+MxEV+MxLSy", "tonf*m/m", "Suma de momentos estabilizantes",
         tex=r"\Sigma MV", doc=215.32)

    m.sec("Empuje horizontal del suelo (EH) [A. 3.11.5.3]")
    m.ec("KA", "(1-SIN(phif))/(1+SIN(phif))", "", "Coeficiente de presión activa (Rankine)", tex="K_A", doc=0.33)
    m.ec("DpEH", "KA*PUS*H", "tonf/m**2", "Presión activa en la base", tex=r"\Delta p_{EH}", doc=4.67)
    m.ec("EH", "DpEH*H/2", "tonf/m", "Empuje activo estático", doc=16.33)
    m.ec("yEH", "H/3", "m", "Brazo", tex="y_{EH}", doc=2.33)
    m.ec("MyEH", "EH*yEH", "tonf*m/m", "Momento de volteo", tex=r"My_{EH}", doc=38.11)
    m.ec("LSx", "DpLS*H", "tonf/m", "Empuje por sobrecarga viva", doc=2.8)
    m.ec("yLSx", "H/2", "m", "Brazo", tex="y_{LSx}", doc=3.5)
    m.ec("MyLSx", "LSx*yLSx", "tonf*m/m", "Momento de volteo", tex=r"My_{LSx}", doc=9.8)

    m.sec("Fuerzas sísmicas [A. 11.6.5]")
    m.nota("Efecto combinado de PAE (empuje dinámico del relleno, Ec. 11.6.5.3-2) y PIR (fuerza inercial del "
           "muro, Ec. 11.6.5.1-1). kh = 0.5 kh0 [A. 11.6.5.2.2].")
    m.dato("Fpga", 1.2, "", "Coeficiente de sitio para período corto", tex=r"F_{pga}")
    m.ec("As_s", "Fpga*PGA", "", "Coeficiente de aceleración pico As", tex="A_s", doc=0.24)
    m.ec("kh0", "As_s", "", "kh0", tex="k_{h0}", doc=0.24)
    m.ec("kh", "0.5*kh0", "", "Coeficiente sísmico horizontal", tex="k_h", doc=0.12)
    m.dato("kv", 0, "", "Coeficiente sísmico vertical", "A. 11.6.5.2.1", tex="k_v")
    m.dato("deltas", 0, "deg", "Fricción suelo-muro (sismo)", tex=r"\delta")
    m.dato("betas", 0, "deg", "Inclinación del muro respecto a la vertical", tex=r"\beta")
    m.dato("i_r", 0, "deg", "Inclinación del relleno", tex="i")
    m.ec("thetaMO", "ATAN(kh/(1-kv))", "deg", "Ángulo θMO", tex=r"\theta_{MO}", doc=6.84)
    m.verif("chk_MO", "phif>=i_r+thetaMO", "φ ≥ i + θMO (Ec. 11.6.5.3-1)", si="CUMPLE", no="NO CUMPLE",
            doc="CUMPLE")
    m.ec("KAE", "COS(phif-thetaMO-betas)**2/(COS(thetaMO)*COS(betas)**2*COS(deltas+thetaMO+betas))"
                "*(1+SQRT(SIN(phif+deltas)*SIN(phif-thetaMO-i_r)/(COS(deltas+thetaMO+betas)*COS(i_r-betas))))**(-2)",
         "", "Coeficiente de empuje sísmico (Mononobe-Okabe)", tex="K_{AE}", doc=0.411)
    m.ec("PAE", "0.5*KAE*H**2*PUS", "tonf/m", "Fuerza sísmica PAE", doc=20.12)
    m.ec("DPAE", "PAE-EH", "tonf/m", "Incremento dinámico ΔPAE", tex=r"\Delta P_{AE}", doc=3.79)
    m.ec("YDPAE", "0.5*H", "m", "Brazo de ΔPAE", tex=r"Y_{\Delta PAE}", doc=3.5)
    m.ec("MDPAE", "DPAE*YDPAE", "tonf*m/m", "Momento de ΔPAE", tex=r"M_{\Delta PAE}", doc=13.26)
    m.ec("Ws_s", "EV", "tonf/m", "Peso del suelo detrás del muro", tex="W_s", doc=33.04)
    m.ec("Ww", "DCest", "tonf/m", "Peso del estribo", tex="W_w", doc=27.54)
    m.ec("PIR", "kh*(Ww+Ws_s)", "tonf/m", "Fuerza inercial PIR", tex="P_{IR}", doc=7.27)
    m.ec("Empuje", "MAX(DPAE,EH)", "tonf/m", "Empuje activo sísmico", tex=r"Empuje_{act.sis}", doc=16.33)
    m.ec("Pseis1", "DPAE+0.5*PIR", "tonf/m", "Combinación 1", tex=r"P_{seis1}", doc=7.42)
    m.ec("Pseis2", "0.5*Empuje+PIR", "tonf/m", "Combinación 2", tex=r"P_{seis2}", doc=15.44)
    m.ec("Pseis", "MAX(Pseis1,Pseis2)", "tonf/m", "Fuerza sísmica de diseño", tex=r"P_{seis}", doc=15.44,
         clave=True)
    m.ec("YPseis", "0.4*H", "m", "Punto de aplicación", tex=r"Y_{Pseis}", doc=2.8)
    m.ec("MPseis", "Pseis*YPseis", "tonf*m/m", "Momento respecto al punto de volteo", tex=r"MP_{seis}",
         doc=43.22)
    m.sec("Fuerza sísmica proveniente de la superestructura, Hu [A. 14.6.3, C. 11.6.5.1]", 2)
    m.dato("mu_s", 0.2, "", "Coeficiente de fricción", tex=r"\mu")
    m.dato("FDCmax", 1.25, "", "Factor DC (Resistencia I)", tex=r"\gamma_{DC}")
    m.dato("FDWmax", 1.5, "", "Factor DW (Resistencia I)", tex=r"\gamma_{DW}")
    m.dato("FLLIMEV", 0.5, "", "Factor LL (Evento Extremo I)", tex=r"\gamma_{EQ}")
    m.ec("Hu", "mu_s*(FDCmax*DC+FDWmax*DW+FLLIMEV*LLIM)", "tonf/m", "Fuerza de fricción por desplazamiento",
         doc=4.13)
    m.ec("YHu", "l1+l7", "m", "Brazo de Hu", tex="Y_{Hu}", doc=5.5)
    m.ec("MHu", "Hu*YHu", "tonf*m/m", "Momento de Hu", tex="MH_u", doc=22.72)
    m.ec("SHsis", "Pseis+Hu", "tonf/m", "Suma de acciones sísmicas", tex=r"\Sigma H_{sis}", doc=19.57)
    m.ec("SMHsis", "MPseis+MHu", "tonf*m/m", "Suma de momentos sísmicos", tex=r"\Sigma MH_{sis}", doc=65.94)

    m.sec("Verificación de la estabilidad y esfuerzos sobre el suelo [T. 3.4.1-1, T. 3.4.1-2]")
    m.ec("YBR", "H+1.8*m", "m", "Brazo del frenado", tex="Y_{BR}", doc=8.8)
    m.ec("MBR", "BR*YBR", "tonf*m/m", "Momento del frenado", tex="M_{BR}", doc=13.82)
    m.ec("SH", "EH+Pseis+Hu+BR+LSx", "tonf/m", "Suma de fuerzas horizontales", tex=r"\Sigma H", doc=40.27)
    m.ec("SMH", "MyEH+MPseis+MHu+MBR+MyLSx", "tonf*m/m", "Suma de momentos de volteo", tex=r"\Sigma MH",
         doc=127.66)

    cv = [("DC", "MxDC"), ("DCest", "MxDCest"), ("DW", "MxDW"), ("EV", "MxEV"), ("LLIM", "MxLL"), ("LSy", "MxLSy")]
    gv = {"RMax": (1.25, 1.25, 1.50, 1.35, 1.75, 1.75), "RMin": (0.90, 0.90, 0.65, 1.00, 0, 0),
          "EMax": (1.25, 1.25, 1.50, 1.35, 0.50, 0.50), "EMin": (0.90, 0.90, 0.65, 1.00, 0, 0),
          "S": (1, 1, 1, 1, 1, 1)}
    ch = [("EH", "MyEH"), ("LSx", "MyLSx"), ("BR", "MBR"), ("Pseis", "MPseis"), ("Hu", "MHu")]
    gh = {"RMax": (1.50, 1.75, 1.75, 0, 0), "RMin": (0.90, 0, 0, 0, 0),
          "EMax": (1.50, 0.50, 0.50, 1.00, 1.00), "EMin": (0.90, 0, 0, 1.00, 1.00),
          "S": (1, 1, 1, 0, 0)}
    m.tabla("Factores de carga - fuerzas verticales y momentos estabilizantes",
            ["Estado límite", "DC super.", "DC est.", "DW", "EV", "LL+IM", "LSy"], [""] * 7,
            [[t] + [D(f"gv_{c}_{j}", gv[c][j]) for j in range(6)] for c, t in COMBOS])
    m.tabla("Factores de carga - fuerzas horizontales y momentos de volteo",
            ["Estado límite", "EH", "LSx", "BR", "Pseis", "Hbu"], [""] * 6,
            [[t] + [D(f"gh_{c}_{j}", gh[c][j]) for j in range(5)] for c, t in COMBOS])
    filas = []
    for c, t in COMBOS:
        filas.append([t,
                      C(f"V_{c}", "+".join(f"gv_{c}_{j}*{n}" for j, (n, _) in enumerate(cv))),
                      C(f"MV_{c}", "+".join(f"gv_{c}_{j}*{mm}" for j, (_, mm) in enumerate(cv))),
                      C(f"H_{c}", "+".join(f"gh_{c}_{j}*{n}" for j, (n, _) in enumerate(ch))),
                      C(f"MH_{c}", "+".join(f"gh_{c}_{j}*{mm}" for j, (_, mm) in enumerate(ch)))])
    m.tabla("Combinaciones de carga (por metro de estribo)", ["Estado límite", "ΣV", "ΣMV", "ΣH", "ΣMH"],
            ["", "tonf/m", "tonf*m/m", "tonf/m", "tonf*m/m"], filas)

    m.sec("Verificación al volcamiento [A. 11.6.3, A. 11.6.5, A. 10.5.2]", 2)
    m.nota("Xo = (MV - MH)/V ;  e = B/2 - Xo ;  se exige e < emax.")
    m.ec("emax_R", "B/3", "m", "Excentricidad máxima - Resistencia I (A. 11.6.3.3)", tex=r"e_{max,R}", doc=1.63)
    m.dato("gEQ", 0.5, "", "Factor de carga viva simultánea con sismo", tex=r"\gamma_{EQ}")
    m.ec("emax_E", "11*B/30", "m", "Excentricidad máxima - Evento Extremo I (A. 11.6.5)", tex=r"e_{max,EV}",
         doc=1.8)
    filas = []
    for c, t in COMBOS[:4]:
        em = "emax_R" if c[0] == "R" else "emax_E"
        filas.append([t, C(None, f"V_{c}"), C(None, f"MV_{c}"), C(None, f"MH_{c}"),
                      C(f"Xo_{c}", f"(MV_{c}-MH_{c})/V_{c}"), C(f"e_{c}", f"B/2-Xo_{c}"), C(None, em),
                      C(f"vol_{c}", f'IF(e_{c}<{em},"OK","NO OK")', verif=True, desc=f"Volcamiento - {t}")])
    m.tabla("Verificación al volcamiento", ["Estado", "ΣV", "MV", "MH", "Xo", "e", "emax", "Cumple"],
            ["", "tonf/m", "tonf*m/m", "tonf*m/m", "m", "m", "m", ""], filas)

    m.sec("Esfuerzos sobre el suelo [A. 10.6.3, A. 10.5.5.2.2]", 2)
    m.dato("phibr", 0.45, "", "Factor de resistencia - Resistencia I", tex=r"\varphi_{b,r}")
    m.ec("qR", "phibr*qn", "tonf/m**2", "Capacidad mayorada - Resistencia I", doc=55.06)
    m.dato("phibev", 0.8, "", "Factor de resistencia - Evento Extremo I", tex=r"\varphi_{b,EV}")
    m.ec("qREV", "phibev*qn", "tonf/m**2", "Capacidad mayorada - Evento Extremo I", tex=r"q_{R,EV}", doc=97.89)
    m.dato("phibs", 0.65, "", "Factor de resistencia - Servicio I", tex=r"\varphi_{b,S}")
    m.ec("qRS", "phibs*qn", "tonf/m**2", "Capacidad mayorada - Servicio I", tex=r"q_{R,S}", doc=79.54)
    m.ec("Xo_S", "(MV_S-MH_S)/V_S", "m", "Xo - Servicio I", doc=1.84)
    m.ec("e_S", "B/2-Xo_S", "m", "Excentricidad - Servicio I", doc=0.61)
    filas = []
    for c, t in COMBOS:
        q = {"R": "qR", "E": "qREV", "S": "qRS"}[c[0]]
        filas.append([t, C(None, f"V_{c}"), C(None, f"e_{c}"), C(f"sig_{c}", f"V_{c}/(B-2*e_{c})"), C(None, q),
                      C(f"cap_{c}", f'IF(sig_{c}<={q},"OK","NO OK")', verif=True,
                        desc=f"Esfuerzo sobre el suelo - {t}")])
    m.tabla("Esfuerzo último actuante sobre suelo no rocoso (σv = V/(B - 2e))",
            ["Estado", "ΣV", "e", "σv", "qR", "Cumple"], ["", "tonf/m", "m", "tonf/m**2", "tonf/m**2", ""], filas)

    m.sec("Verificación al desplazamiento [A. 10.6.3.4, T. 10.5.5.2.2-1]", 2)
    m.nota("RR = φτ·V·tan δ + φep·Rep ; para hormigón vaciado contra el suelo tan δ = tan φf.")
    m.ec("tanphi", "TAN(phif)", "", "tan φf", tex=r"\tan\phi'_f", doc=0.577)
    m.dato("phitau", 0.8, "", "Factor de resistencia al corte suelo-cimentación", tex=r"\phi_\tau")
    m.dato("phiep", 0.5, "", "Factor de resistencia pasiva", tex=r"\phi_{ep}")
    m.ec("Kp", "(1+SIN(phif))/(1-SIN(phif))", "", "Coeficiente de presión pasiva", tex="K_P", doc=3)
    m.dato("Hpas", 0.9, "m", "Altura de suelo pasivo", tex="H")
    m.ec("Rep", "0.5*Kp*PUS*Hpas**2", "tonf/m", "Resistencia pasiva nominal", doc=2.43)
    filas = []
    for c, t in COMBOS[:4]:
        filas.append([t, C(None, f"V_{c}"), C(None, f"H_{c}"), C(f"RR_{c}", f"phitau*V_{c}*tanphi+phiep*Rep"),
                      C(f"desl_{c}", f'IF(RR_{c}>H_{c},"OK","NO OK")', verif=True, desc=f"Deslizamiento - {t}")])
    m.tabla("Verificación del deslizamiento del estribo",
            ["Estado", "V", "H actuante", "RR resistente", "Cumple"], ["", "tonf/m", "tonf/m", "tonf/m", ""], filas)

    # -------------------------------------------------------------- pantalla
    m.sec("Diseño de la pantalla - armadura interior")
    m.ec("Hpant", "l2+l3+l4", "m", "Altura de la pantalla", tex=r"H_{pantalla}", doc=5.9)
    m.ec("ka_p", "ROUND(KA,2)", "", "Coeficiente de empuje (redondeado, como en el PDF)", tex="k_a", doc=0.33)
    m.ec("Dp_p", "ka_p*Hpant*PUS", "tonf/m**2", "Presión en la base de la pantalla", tex=r"\Delta p", doc=3.89)
    m.tabla("Cargas horizontales sobre la pantalla (Resistencia I y Evento Extremo I)",
            ["Carga", "Fuerza", "Brazo Y", "Mx"], ["", "tonf/m", "m", "tonf*m/m"],
            [["EH = Δp·H/2", C("pnEH", "Dp_p*Hpant/2"), C("pnyEH", "Hpant/3"), C("pnMEH", "pnEH*pnyEH")],
             ["Pseis", C("pnPs", "Pseis"), C("pnyPs", "0.4*Hpant"), C("pnMPs", "pnPs*pnyPs")],
             ["Hbu", C("pnHu", "Hu"), C("pnyHu", "l7"), C("pnMHu", "pnHu*pnyHu")],
             ["BR", C("pnBR", "BR"), C("pnyBR", "Hpant+1.8*m"), C("pnMBR", "pnBR*pnyBR")],
             ["LSx = H·Δp", C("pnLS", "Hpant*ka_p*heq*PUS"), C("pnyLS", "Hpant/2"), C("pnMLS", "pnLS*pnyLS")]])
    m.sec("Momento de diseño", 2)
    m.dato("FEH", 1.5, "", "Factor de carga EH", tex=r"\gamma_{EH}")
    m.dato("FEQ", 1, "", "Factor de carga EQ", tex=r"\gamma_{EQ}")
    m.dato("FLS", 1.75, "", "Factor de carga LS y BR", tex=r"\gamma_{LS}")
    m.dato("nD", 1, "", "Factor de ductilidad", tex=r"\eta_D")
    m.dato("nR", 1, "", "Factor de redundancia", tex=r"\eta_R")
    m.dato("nI", 1, "", "Factor de importancia", tex=r"\eta_I")
    m.ec("n_mod", "nD*nR*nI", "", "Modificador de carga", tex=r"\eta", doc=1)
    m.ec("MuEV", "n_mod*(FEH*pnMEH+FEQ*(pnMPs+pnMHu))", "tonf*m/m", "Evento Extremo I", tex=r"M_{u,EV}", doc=88.5)
    m.ec("MuR", "n_mod*(FEH*pnMEH+FLS*(pnMLS+pnMBR))", "tonf*m/m", "Resistencia I", tex=r"M_{u,R}", doc=67.1)
    m.ec("MU", "MAX(MuR,MuEV)", "tonf*m/m", "Momento último de la pantalla", tex="M_U", doc=88.5, clave=True)
    m.sec("Estimación del refuerzo", 2)
    m.dato("b_t", 1, "m", "Ancho tributario", tex="b")
    m.dato("dh", 25, "mm", "Diámetro del acero de refuerzo", tex=r"d_{hierro}")
    m.ec("Ah", "0.25*PI()*dh**2", "cm**2", "Área de una barra", tex=r"A_{hierro}", doc=4.91)
    m.dato("rech", 7.5, "cm", "Recubrimiento", tex=r"rec")
    m.ec("Aest", "l5+l6", "m", "Espesor de la pantalla", tex=r"A_{est}", doc=0.9)
    m.ec("d", "Aest-(rech+0.5*dh)", "m", "Peralte efectivo", doc=0.81)
    m.ec("beta1", "IF(ROUND(fcest/MPa,6)<=28,0.85,IF(ROUND(fcest/MPa,6)>56,0.65,0.85-0.05*(fcest-28*MPa)/(7*MPa)))",
         "", "Factor β1", doc=0.85)
    m.dato("phi", 0.9, "", "Factor de reducción de resistencia", tex=r"\phi")
    m.dato("j", 0.9, "", "Brazo relativo (expresión aproximada)")
    m.ec("Asp", "MU/(phi*fy*j*d)", "cm**2/m", "Acero requerido", doc=31.4)
    m.ec("ap", "Asp*b_t*fy/(0.85*fcest*b_t)", "cm", "Profundidad del bloque de compresión", doc=7.39)
    m.ec("cp", "ap/beta1", "cm", "Eje neutro", doc=8.69)
    m.ec("etp", "0.003*(d-cp)/cp", "", "Deformación del acero en tensión", tex=r"\varepsilon_t", doc=0.025)
    m.verif("chk_etp", "etp>=0.005", "εt ≥ 0.005 (tensión controlada) - pantalla", doc="OK")
    m.dato("Nb_p", 7, "", "Número de barras por metro", tex="N")
    m.ec("AsT", "Nb_p*Ah/b_t", "cm**2/m", "Acero total", doc=34.36)
    m.verif("chk_AsT", "AsT>=Asp", "Acero proporcionado ≥ requerido - pantalla", doc="OK")
    m.ec("MUv", "phi*AsT*fy*(d-0.5*ap)", "tonf*m/m", "Capacidad de momento", tex="M_{U,V}", doc=102.72)
    m.verif("chk_MUv", "MUv>MU", "Capacidad ≥ momento último - pantalla", si="CUMPLE", no="NO CUMPLE", doc="CUMPLE")
    m.ec("S_h", "Ah/AsT", "m", "Separación", tex="S", doc=0.143)
    m.dato("Sasum", 14, "cm", "Separación adoptada (emplear Ø25 mm @ 14 cm)", tex="S_{asumido}", clave=True)
    m.sec("Comprobación del As mínimo [Ec. 5.7.3.3.2-1]", 2)
    m.ec("Ss", "b_t*Aest**2/6", "m**3", "Módulo de la sección", doc=0.135)
    m.ec("fr", "0.63*SQRT(fcest/MPa)*MPa", "kgf/cm**2", "Módulo de ruptura", doc=29.44)
    m.ec("FMcr", "1.2*fr*Ss/b_t", "tonf*m/m", "1.2 Mcr", doc=47.69)
    m.ec("FMu", "1.33*MU", "tonf*m/m", "1.33 Mu", doc=117.7)
    m.ec("MUmin", "MIN(FMcr,FMu)", "tonf*m/m", "Menor valor", doc=47.69)
    m.verif("chk_MUmin", "MUv>MUmin", "As mínimo - pantalla", si="CUMPLE", no="NO CUMPLE", doc="CUMPLE")
    m.sec("Refuerzo por contracción y temperatura en la pantalla [A. 5.10.8]", 2)
    m.ec("Astemp", "0.75*Aest*l7*MPa/(2*(Aest+l7)*fy)", "mm**2/mm", "Acero de temperatura", tex=r"A_{s,temp}",
         doc=0.67)
    m.verif("chk_Astemp", "AND(Astemp>=0.233*mm**2/mm,Astemp<=1.27*mm**2/mm)", "0.233 ≤ As ≤ 1.27 mm²/mm - pantalla")
    m.dato("dht", 16, "mm", "Diámetro del refuerzo", tex=r"d_{hierro,t}")
    m.ec("Aht", "PI()*dht**2/4", "cm**2", "Área del refuerzo", tex=r"A_{hierro,t}", doc=2.01)
    m.ec("Sapt", "Aht/Astemp", "m", "Separación requerida", tex=r"S_{a,p,t}", doc=0.301)
    m.ec("Smax1", "3*Aest", "cm", "Separación máxima 3·espesor", doc=270)
    m.dato("Smax2", 45, "cm", "Separación máxima 45 cm")
    m.nota("Emplear Ø16 mm @ 25 cm.")

    # -------------------------------------------------------------- zapata
    m.sec("Diseño de la armadura de la zapata - punta (Resistencia I)")
    m.ec("sigRmax", "sig_RMax", "tonf/m**2", "Esfuerzo máximo en el suelo", tex=r"\sigma_{R,max}", doc=33.46)
    m.ec("Mpz", "sigRmax*l8**2/2", "tonf*m/m", "Momento en la punta", tex="M_{p,z}", doc=24.09)
    m.ec("Ss_z", "0.1667*b_t*l1**2", "m**3", "Módulo de la sección", tex="S_s", doc=0.202)
    m.ec("FMcrpz", "1.2*fr*Ss_z/b_t", "tonf*m/m", "1.2 Mcr", tex=r"FMcr_{p,z}", doc=71.26)
    m.ec("FMupz", "1.33*Mpz", "tonf*m/m", "1.33 Mu", tex=r"FMu_{p,z}", doc=32.04)
    m.ec("MUminpz", "MIN(FMcrpz,FMupz)", "tonf*m/m", "Menor valor", tex=r"MU_{min,p,z}", doc=32.04)
    m.sel("chk_Mpz", "Mpz>MUminpz", "CUMPLE", "NO CUMPLE", "Mu > MUmin (si no, se diseña con MUmin)",
          doc="NO CUMPLE")
    m.ec("Mupz_d", "MAX(Mpz,MUminpz)", "tonf*m/m", "Momento de diseño de la punta", tex=r"M_{u,p,z}", doc=32.04)
    m.dato("dhpz", 20, "mm", "Diámetro del refuerzo", tex=r"d_{hierro,p,z}")
    m.ec("Ahpz", "0.25*PI()*dhpz**2", "cm**2", "Área de una barra", tex=r"A_{hierro,p,z}", doc=3.14)
    m.ec("dpe", "l1-(rech+0.5*dhpz)", "cm", "Peralte efectivo", tex="d_{p,e}", doc=101.5)
    m.ec("Aspz", "Mupz_d/(phi*fy*j*dpe)", "cm**2/m", "Acero requerido", tex="A_{s,p,z}", doc=9.1)
    m.ec("apz", "Aspz*b_t*fy/(0.85*fcest*b_t)", "cm", "Bloque de compresión", tex="a_{p,z}", doc=2.14)
    m.ec("cpz", "apz/beta1", "cm", "Eje neutro", tex="c_{p,z}", doc=2.52)
    m.ec("etpz", "0.003*(dpe-cpz)/cpz", "", "Deformación del acero", tex=r"\varepsilon_{t,p,z}", doc=0.118)
    m.verif("chk_etpz", "etpz>=0.005", "εt ≥ 0.005 - punta", doc="OK")
    m.dato("Npz", 3, "", "Número de barras por metro", tex="N_{p,z}")
    m.ec("AsTpz", "Npz*Ahpz/b_t", "cm**2/m", "Acero total", tex="AsT_{p,z}", doc=9.42)
    m.verif("chk_AsTpz", "AsTpz>=Aspz", "Acero proporcionado ≥ requerido - punta", si="CUMPLE", no="NO CUMPLE",
            doc="CUMPLE")
    m.ec("MUVpz", "phi*AsTpz*fy*(dpe-0.5*apz)", "tonf*m/m", "Capacidad de momento", tex="MU_{V,p,z}", doc=36.48)
    m.verif("chk_MUVpz", "MUVpz>MUminpz", "Capacidad de momento - punta", si="CUMPLE", no="NO CUMPLE", doc="CUMPLE")
    m.ec("Spz", "Ahpz/Aspz", "m", "Separación requerida", tex="S_{p,z}", doc=0.345)
    m.dato("Sasumpz", 35, "cm", "Separación adoptada (emplear Ø20 mm @ 35 cm)", tex=r"S_{asumido,p,z}", clave=True)
    m.sec("Verificación del esfuerzo cortante [A. 5.7.3.3, A. 5.7.3.4.1]", 2)
    m.ec("Vu", "sigRmax*l8*b_t", "tonf", "Cortante en la unión zapata-pantalla", doc=40.15)
    m.ec("dv", "dpe", "m", "Peralte de cortante", doc=1.02)
    m.verif("chk_dv", "3*dv>l8", "3 dv > l8", doc="OK")
    m.dato("betav", 2, "", "Factor β", tex=r"\beta_v")
    m.dato("thetav", 45, "deg", "Ángulo θ", tex=r"\theta_v")
    m.ec("Vc", "0.083*betav*SQRT(fcest/MPa)*MPa*b_t*dv", "tonf", "Resistencia nominal del hormigón", doc=78.73)
    m.ec("Vuc", "phi*Vc", "tonf", "Resistencia última del hormigón", tex="V_{u,c}", doc=70.86)
    m.verif("chk_Vuc", "Vuc>Vu", "Cortante en la punta", doc="OK")

    m.sec("Diseño del talón de la zapata")
    m.ec("DCz", "eDC_1", "tonf/m", "Peso de la zapata", tex=r"DC_{zapata}", doc=12.94)
    m.ec("sigRmin", "sig_RMin", "tonf/m**2", "Esfuerzo mínimo en el suelo", tex=r"\sigma_{R,min}", doc=15.28)
    m.ec("bEV", "0.5*l9", "m", "Brazo del relleno", tex=r"b_{EV}", doc=1.4)
    m.ec("bDCz", "0.5*l9", "m", "Brazo del peso de la zapata", tex=r"b_{DC,z}", doc=1.4)
    m.ec("esigmin", "e_RMin", "m", "Excentricidad", tex=r"e_{\sigma,min}", doc=0.2)
    m.ec("B2e", "B-2*esigmin", "m", "B - 2e", doc=4.5)
    m.ec("bsig", "B2e-(l8+l6+l5)", "m", "Longitud cargada bajo el talón", tex=r"b_{\sigma}", doc=2.4)
    m.dato("FEV", 1.35, "", "Factor de carga EV", tex=r"\gamma_{EV}")
    m.dato("FDC", 1.25, "", "Factor de carga DC", tex=r"\gamma_{DC,z}")
    m.ec("Mutz", "n_mod*(FEV*EV*bEV+FDC*DCz*bDCz-sigRmin*bsig**2/2)", "tonf*m/m", "Momento último en el talón",
         tex="M_{u,t,z}", doc=41.25)
    m.ec("FMcrtz", "1.2*fr*Ss_z/b_t", "tonf*m/m", "1.2 Mcr", tex=r"FMcr_{t,z}", doc=71.26)
    m.ec("FMutz", "1.33*Mutz", "tonf*m/m", "1.33 Mu", tex=r"FMu_{t,z}", doc=54.86)
    m.ec("MUmintz", "MIN(FMcrtz,FMutz)", "tonf*m/m", "Menor valor", tex=r"MU_{min,t,z}", doc=54.86)
    m.sel("chk_Mutz", "Mutz>MUmintz", "CUMPLE", "NO CUMPLE", "Mu > MUmin (si no, se diseña con MUmin)",
          doc="NO CUMPLE")
    m.ec("Mutz_d", "MAX(Mutz,MUmintz)", "tonf*m/m", "Momento de diseño del talón", tex=r"M_{u,t,z,d}", doc=54.86)
    m.dato("dhtz", 20, "mm", "Diámetro del refuerzo", tex=r"d_{hierro,t,z}")
    m.ec("Ahtz", "0.25*PI()*dhtz**2", "cm**2", "Área de una barra", tex=r"A_{hierro,t,z}", doc=3.14)
    m.ec("dtz", "l1-(rech+0.5*dhtz)", "m", "Peralte efectivo", tex="d_{t,z}", doc=1.02)
    m.ec("Astz", "Mutz_d/(phi*fy*j*dtz)", "cm**2/m", "Acero requerido", tex="A_{s,t,z}", doc=15.58)
    m.ec("atz", "Astz*b_t*fy/(0.85*fcest*b_t)", "cm", "Bloque de compresión", tex="a_{t,z}", doc=3.67)
    m.ec("ctz", "atz/beta1", "cm", "Eje neutro", tex="c_{t,z}", doc=4.31)
    m.ec("etptz", "0.003*(dtz-ctz)/ctz", "", "Deformación del acero", tex=r"\varepsilon_{t,t,z}", doc=0.068)
    m.verif("chk_etptz", "etptz>=0.005", "εt ≥ 0.005 - talón", doc="OK")
    m.dato("Ntz", 5, "", "Número de barras por metro", tex="N_{t,z}")
    m.ec("AsTtz", "Ntz*Ahtz/b_t", "cm**2/m", "Acero total", tex="AsT_{t,z}", doc=15.71)
    m.verif("chk_AsTtz", "AsTtz>=Astz", "Acero proporcionado ≥ requerido - talón", si="CUMPLE", no="NO CUMPLE",
            doc="CUMPLE")
    m.ec("MUVtz", "phi*AsTtz*fy*(dtz-0.5*atz)", "tonf*m/m", "Capacidad de momento", tex="MU_{V,t,z}", doc=60.35)
    m.verif("chk_MUVtz", "MUVtz>MUmintz", "Capacidad de momento - talón", si="CUMPLE", no="NO CUMPLE", doc="CUMPLE")
    m.ec("Stz", "Ahtz/AsTtz", "m", "Separación", tex="S_{t,z}", doc=0.2)
    m.dato("Sasumtz", 20, "cm", "Separación adoptada (emplear Ø20 mm @ 20 cm)", tex=r"S_{asumido,t,z}", clave=True)
    m.sec("Refuerzo por contracción y temperatura en la zapata [A. 5.10.8]", 2)
    m.ec("Astz_t", "0.75*B*l1*MPa/(2*(B+l1)*fy)", "mm**2/mm", "Acero de temperatura", tex=r"A_{s,t,z}", doc=0.8)
    m.verif("chk_Astz_t", "AND(Astz_t>=0.233*mm**2/mm,Astz_t<=1.27*mm**2/mm)", "0.233 ≤ As ≤ 1.27 mm²/mm - zapata")
    m.dato("dhtt", 16, "mm", "Diámetro del refuerzo", tex=r"d_{h,t,z}")
    m.ec("Ahtt", "0.25*PI()*dhtt**2", "cm**2", "Área del refuerzo", tex=r"A_{h,t,z}", doc=2.01)
    m.ec("Saptz", "Ahtt/Astz_t", "cm", "Separación requerida", tex=r"S_{a,p,t,z}", doc=25.07)
    m.ec("Smax1tz", "3*l1", "cm", "Separación máxima 3·espesor", tex=r"Smax_{1,t,z}", doc=330)
    m.dato("Smax2tz", 45, "cm", "Separación máxima 45 cm", tex=r"Smax_{2,t,z}")
    m.nota("Emplear Ø16 mm @ 25 cm.")
    return m
