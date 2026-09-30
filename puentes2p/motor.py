"""
Motor de cálculo de la memoria "Diseño de Puentes - 2P".

Cada variable se define UNA sola vez mediante una expresión escrita con la
sintaxis de funciones de Excel (IF, MAX, MIN, SQRT, ATAN, ...) y los operadores
de Python (+ - * / **). A partir de esa única definición el motor:

  * evalúa el valor en Python (unidades base: tonf y m),
  * genera la fórmula viva de Excel (con nombres definidos),
  * genera la ecuación en LaTeX para el reporte.

Las unidades (cm, kip, ksi, MPa, ...) son constantes numéricas, igual que en
Mathcad: un dato "f'c = 280 kgf/cm²" se guarda internamente como 2800 tonf/m².
"""
from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Unidades (base: tonf, m, rad)
# ---------------------------------------------------------------------------
_KIP = 0.45359237           # tonf
_IN = 0.0254                # m
_N = 1.0 / 9806.65          # tonf

UNIDADES: dict[str, tuple[float, str]] = {
    "m": (1.0, "metro"),
    "cm": (0.01, "centímetro"),
    "mm": (0.001, "milímetro"),
    "inch": (_IN, "pulgada"),
    "ft": (0.3048, "pie"),
    "tonf": (1.0, "tonelada fuerza"),
    "kgf": (0.001, "kilogramo fuerza"),
    "kip": (_KIP, "kilolibra fuerza"),
    "N": (_N, "newton"),
    "ksi": (_KIP / _IN ** 2, "kip/in²"),
    "psi": (_KIP / _IN ** 2 / 1000.0, "lbf/in²"),
    "MPa": (1.0e6 * _N, "megapascal (N/mm²)"),
    "deg": (math.pi / 180.0, "grado sexagesimal"),
    "pct": (0.01, "porcentaje"),
}


def _roundup(x, n=0):
    f = 10 ** int(n)
    v = round(abs(x) * f, 9)
    return math.copysign(math.ceil(v) / f, x)


def _round(x, n=0):
    f = 10 ** int(n)
    return math.copysign(math.floor(abs(x) * f + 0.5 + 1e-9) / f, x)


FUNCIONES = {
    "IF": lambda c, a, b: a if c else b,
    "AND": lambda *a: all(a),
    "OR": lambda *a: any(a),
    "MAX": lambda *a: max(a),
    "MIN": lambda *a: min(a),
    "SQRT": math.sqrt,
    "ABS": abs,
    "SIN": math.sin,
    "COS": math.cos,
    "TAN": math.tan,
    "ATAN": math.atan,
    "ASIN": math.asin,
    "ACOS": math.acos,
    "PI": lambda: math.pi,
    "INT": lambda x: math.floor(round(x, 9)),
    "ROUNDUP": _roundup,
    "ROUND": _round,
    "RADIANS": math.radians,
    "DEGREES": math.degrees,
    "LN": math.log,
    "EXP": math.exp,
}


class ErrorModelo(Exception):
    pass


# ---------------------------------------------------------------------------
# Estructuras
# ---------------------------------------------------------------------------
@dataclass
class Var:
    nombre: str
    tipo: str                      # 'dato' | 'ec' | 'verif' | 'sel'
    expr: str | None
    unidad: str = ""
    desc: str = ""
    ref: str = ""
    tex: str | None = None         # símbolo LaTeX
    ftex: str | None = None        # expresión LaTeX (sustituye la automática)
    mostrar_expr: bool = True
    doc: Any = None                # valor del PDF original (unidades de despliegue)
    clave: bool = False            # aparece en la hoja Resumen
    valor: Any = None              # valor en unidades base
    en_tabla: bool = False
    modulo: "Modulo | None" = None
    # Asignados por el escritor de Excel
    xl_nombre: str | None = None
    xl_ref: str | None = None

    @property
    def factor(self) -> float:
        return factor_unidad(self.unidad)

    @property
    def valor_mostrado(self):
        if isinstance(self.valor, (int, float)) and not isinstance(self.valor, bool):
            return self.valor / self.factor
        return self.valor


@dataclass
class Seccion:
    titulo: str
    nivel: int = 1


@dataclass
class Nota:
    texto: str


@dataclass
class C:
    """Celda calculada dentro de una tabla (verif=True: verificación de cumplimiento)."""
    nombre: str | None
    expr: str
    doc: Any = None
    verif: bool = False
    desc: str = ""


@dataclass
class D:
    """Celda de dato (editable) dentro de una tabla."""
    nombre: str
    valor: float


@dataclass
class Tabla:
    titulo: str
    encabezados: list[str]
    unidades: list[str]
    filas: list[list[Any]] = field(default_factory=list)   # str | Var | None


# ---------------------------------------------------------------------------
# Unidades: factor, texto, LaTeX, Excel
# ---------------------------------------------------------------------------
_ns_unidades = {k: v[0] for k, v in UNIDADES.items()}


def factor_unidad(u: str) -> float:
    if not u:
        return 1.0
    return float(eval(u, {"__builtins__": {}}, _ns_unidades))


def unidad_texto(u: str) -> str:
    if not u:
        return ""
    s = u.replace("**2", "²").replace("**3", "³").replace("**4", "⁴").replace("**0.5", "^0.5")
    s = s.replace("*", "·").replace("inch", "in").replace("pct", "%").replace("deg", "°")
    return s


def unidad_tex(u: str) -> str:
    if not u:
        return ""
    if u == "deg":
        return r"^{\circ}"
    if u == "pct":
        return r"\,\%"
    s = re.sub(r"\*\*(\d+(?:\.\d+)?)", r"^{\1}", u)
    s = s.replace("*", r"\cdot ").replace("inch", "in")
    return r"\,\mathrm{" + s + "}"


# ---------------------------------------------------------------------------
# Símbolos LaTeX automáticos
# ---------------------------------------------------------------------------
_GRIEGAS = ["varepsilon", "epsilon", "lambda", "Lambda", "alpha", "beta", "gamma", "Gamma",
            "delta", "Delta", "theta", "Theta", "sigma", "Sigma", "omega", "Omega", "phi",
            "Phi", "psi", "rho", "tau", "eta", "mu", "nu"]


def tex_auto(nombre: str) -> str:
    partes = nombre.split("_")
    base, subs = partes[0], [p for p in partes[1:] if p]
    cabeza = None
    for g in sorted(_GRIEGAS, key=len, reverse=True):
        if base.startswith(g):
            cabeza = "\\" + g
            resto = base[len(g):]
            break
    if cabeza is None:
        m = re.match(r"^([A-Z]{2,})(.*)$", base)
        if m:
            cabeza = r"\mathit{" + m.group(1) + "}"
            resto = m.group(2)
        else:
            cabeza, resto = base[0], base[1:]
    if resto:
        subs = [resto] + subs
    if subs:
        return cabeza + r"_{\mathrm{" + ",".join(subs) + "}}"
    return cabeza


# ---------------------------------------------------------------------------
# Traductores de expresiones (Python AST -> Excel / LaTeX / texto)
# ---------------------------------------------------------------------------
_PREC = {ast.Add: 1, ast.Sub: 1, ast.Mult: 2, ast.Div: 2, ast.Pow: 4}
_CMP_XL = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "=", ast.NotEq: "<>"}
_CMP_TEX = {ast.Lt: "<", ast.LtE: r"\le", ast.Gt: ">", ast.GtE: r"\ge", ast.Eq: "=", ast.NotEq: r"\ne"}


def _num_xl(v) -> str:
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, int):
        return str(v)
    r = repr(float(v))
    return r[:-2] if r.endswith(".0") else r


def _prec(n) -> int:
    if isinstance(n, ast.BinOp):
        return _PREC[type(n.op)]
    if isinstance(n, ast.Compare):
        return 0
    if isinstance(n, ast.UnaryOp):
        return 3
    return 9


def a_excel(nodo, resolver) -> str:
    """Convierte un nodo AST a texto de fórmula Excel. resolver(nombre)->str."""
    n = nodo
    if isinstance(n, ast.Expression):
        return a_excel(n.body, resolver)
    if isinstance(n, ast.Constant):
        if isinstance(n.value, str):
            return '"' + n.value.replace('"', '""') + '"'
        return _num_xl(n.value)
    if isinstance(n, ast.Name):
        return resolver(n.id)
    if isinstance(n, ast.UnaryOp):
        inner = a_excel(n.operand, resolver)
        if isinstance(n.op, ast.USub):
            if _prec(n.operand) < 9:
                inner = "(" + inner + ")"
            return "(-" + inner + ")"
        if isinstance(n.op, ast.UAdd):
            return inner
        raise ErrorModelo("Operador unario no soportado")
    if isinstance(n, ast.BinOp):
        p = _PREC[type(n.op)]
        l = a_excel(n.left, resolver)
        r = a_excel(n.right, resolver)
        pl, pr = _prec(n.left), _prec(n.right)
        if isinstance(n.op, ast.Pow):
            if pl < 9:
                l = "(" + l + ")"
            if pr < 9:
                r = "(" + r + ")"
            return l + "^" + r
        if pl < p:
            l = "(" + l + ")"
        if pr < p or (pr == p and isinstance(n.op, (ast.Sub, ast.Div))):
            r = "(" + r + ")"
        op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}[type(n.op)]
        return l + op + r
    if isinstance(n, ast.Compare):
        if len(n.ops) != 1:
            raise ErrorModelo("Use AND() para comparaciones encadenadas")
        return a_excel(n.left, resolver) + _CMP_XL[type(n.ops[0])] + a_excel(n.comparators[0], resolver)
    if isinstance(n, ast.Call):
        f = n.func.id
        args = ",".join(a_excel(a, resolver) for a in n.args)
        return f + "(" + args + ")"
    raise ErrorModelo(f"Nodo no soportado: {ast.dump(n)}")


def _num_tex(v) -> str:
    if isinstance(v, bool):
        return r"\text{" + str(v) + "}"
    if isinstance(v, int):
        return str(v)
    if float(v).is_integer():
        return str(int(v))
    return ("%.6g" % v)


def a_tex(nodo, simbolo) -> str:
    """Convierte un nodo AST a LaTeX. simbolo(nombre)->str."""

    def par(s):
        return r"\left(" + s + r"\right)"

    def t(n):
        if isinstance(n, ast.Expression):
            return t(n.body)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, str):
                return r"\text{``" + escapar_tex(n.value) + "''}"
            return _num_tex(n.value)
        if isinstance(n, ast.Name):
            return simbolo(n.id)
        if isinstance(n, ast.UnaryOp):
            s = t(n.operand)
            if isinstance(n.operand, ast.BinOp) and _PREC[type(n.operand.op)] <= 2 and not isinstance(n.operand.op, ast.Div):
                s = par(s)
            return "-" + s
        if isinstance(n, ast.BinOp):
            op = type(n.op)
            if op is ast.Div:
                return r"\dfrac{" + t(n.left) + "}{" + t(n.right) + "}"
            if op is ast.Pow:
                b = t(n.left)
                if _prec(n.left) < 9 or isinstance(n.left, ast.Call) and n.left.func.id not in ("SQRT", "ABS"):
                    b = par(b)
                e = n.right
                if isinstance(e, ast.Constant) and e.value == 0.5:
                    return r"\sqrt{" + t(n.left) + "}"
                return "{" + b + "}^{" + t(e) + "}"
            l, r = t(n.left), t(n.right)
            p = _PREC[op]
            if _prec(n.left) < p and not (isinstance(n.left, ast.BinOp) and isinstance(n.left.op, ast.Div)):
                l = par(l)
            if (_prec(n.right) < p or (_prec(n.right) == p and op is ast.Sub)) and not (
                    isinstance(n.right, ast.BinOp) and isinstance(n.right.op, ast.Div)):
                r = par(r)
            if isinstance(n.right, ast.UnaryOp):
                r = par(r)
            if op is ast.Add:
                return l + " + " + r
            if op is ast.Sub:
                return l + " - " + r
            # multiplicación: número·unidad sin punto
            if isinstance(n.right, ast.Name) and n.right.id in UNIDADES and isinstance(n.left, ast.Constant):
                return l + r"\," + r
            return l + r" \cdot " + r
        if isinstance(n, ast.Compare):
            return t(n.left) + " " + _CMP_TEX[type(n.ops[0])] + " " + t(n.comparators[0])
        if isinstance(n, ast.Call):
            f = n.func.id
            a = [t(x) for x in n.args]
            if f == "SQRT":
                return r"\sqrt{" + a[0] + "}"
            if f in ("MAX", "MIN"):
                return "\\" + f.lower() + par(r",\ ".join(a))
            if f == "ABS":
                return r"\left|" + a[0] + r"\right|"
            if f in ("SIN", "COS", "TAN"):
                return "\\" + f.lower() + par(a[0])
            if f == "ATAN":
                return r"\arctan" + par(a[0])
            if f == "ASIN":
                return r"\arcsin" + par(a[0])
            if f == "ACOS":
                return r"\arccos" + par(a[0])
            if f == "PI":
                return r"\pi"
            if f == "INT":
                return r"\left\lfloor " + a[0] + r"\right\rfloor"
            if f == "ROUNDUP":
                return r"\left\lceil " + a[0] + r"\right\rceil"
            if f == "ROUND":
                return r"\operatorname{red}" + par(a[0])
            if f in ("RADIANS", "DEGREES"):
                return a[0]
            if f == "AND":
                return r" \;\wedge\; ".join(a)
            if f == "OR":
                return r" \;\vee\; ".join(a)
            if f == "IF":
                return (r"\begin{cases}" + a[1] + r" & \text{si } " + a[0] + r"\\ " + a[2]
                        + r" & \text{en otro caso}\end{cases}")
            return r"\operatorname{" + f + "}" + par(", ".join(a))
        raise ErrorModelo(f"Nodo no soportado: {ast.dump(n)}")

    return t(nodo)


def a_texto(expr: str) -> str:
    return expr.replace("**", "^").replace(" ", "")


_TEX_ESC = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "≤": r"$\le$", "≥": r"$\ge$", "Ø": r"$\varnothing$", "Δ": r"$\Delta$", "φ": r"$\phi$",
    "θ": r"$\theta$", "ψ": r"$\psi$", "β": r"$\beta$", "γ": r"$\gamma$", "μ": r"$\mu$",
    "ε": r"$\varepsilon$", "σ": r"$\sigma$", "²": r"$^{2}$", "³": r"$^{3}$", "⁴": r"$^{4}$",
    "°": r"$^{\circ}$", "·": r"$\cdot$", "α": r"$\alpha$", "δ": r"$\delta$", "λ": r"$\lambda$",
    "√": r"$\surd$", "Σ": r"$\Sigma$", "π": r"$\pi$", "η": r"$\eta$", "×": r"$\times$",
    "→": r"$\rightarrow$", "'": r"'", "≈": r"$\approx$", "±": r"$\pm$", "↑": r"$\uparrow$",
    "↓": r"$\downarrow$", "≠": r"$\ne$", "“": "``", "”": "''", "–": "--", "—": "---",
}


def _char_tex(ch: str) -> str:
    if ch in _TEX_ESC:
        return _TEX_ESC[ch]
    if ord(ch) < 256:
        return ch
    import unicodedata
    nombre = unicodedata.name(ch, "")
    if nombre.startswith("GREEK SMALL LETTER "):
        return "$\\" + nombre.split()[-1].lower() + "$"
    if nombre.startswith("GREEK CAPITAL LETTER "):
        return "$\\" + nombre.split()[-1].capitalize() + "$"
    return "?"


def escapar_tex(s: str) -> str:
    return "".join(_char_tex(ch) for ch in s)


# ---------------------------------------------------------------------------
# Módulo de cálculo
# ---------------------------------------------------------------------------
class Modulo:
    """Un capítulo de la memoria (una hoja de Excel, una sección del reporte)."""

    def __init__(self, codigo: str, titulo: str, hoja: str, descripcion: str = "",
                 sobrescribir: dict | None = None):
        self.codigo = codigo
        self.titulo = titulo
        self.hoja = hoja
        self.descripcion = descripcion
        self.items: list = []
        self.vars: dict[str, Var] = {}
        self._lower: dict[str, str] = {}
        self.ns: dict[str, Any] = dict(FUNCIONES)
        self.ns.update(_ns_unidades)
        self.sobrescribir = sobrescribir or {}
        self._anon = 0

    # ---- utilidades internas ------------------------------------------
    def _registrar(self, v: Var):
        n = v.nombre
        if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", n):
            raise ErrorModelo(f"[{self.codigo}] Nombre inválido: {n}")
        if n in UNIDADES or n in FUNCIONES:
            raise ErrorModelo(f"[{self.codigo}] '{n}' choca con una unidad o función")
        low = n.lower()
        if low in self._lower:
            raise ErrorModelo(f"[{self.codigo}] Nombre repetido (Excel no distingue mayúsculas): "
                              f"{n} / {self._lower[low]}")
        self._lower[low] = n
        v.modulo = self
        self.vars[n] = v
        self.ns[n] = v.valor

    def _evaluar(self, nombre: str, expr: str):
        try:
            arbol = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise ErrorModelo(f"[{self.codigo}] Sintaxis en {nombre}: {expr}") from e
        for nd in ast.walk(arbol):
            if isinstance(nd, ast.Name) and nd.id not in self.ns:
                raise ErrorModelo(f"[{self.codigo}] {nombre}: '{nd.id}' no está definido")
        try:
            return eval(compile(arbol, "<expr>", "eval"), {"__builtins__": {}}, self.ns)
        except Exception as e:  # noqa: BLE001
            raise ErrorModelo(f"[{self.codigo}] Error evaluando {nombre} = {expr}: {e}") from e

    # ---- API de modelado ----------------------------------------------
    def sec(self, titulo: str, nivel: int = 1):
        self.items.append(Seccion(titulo, nivel))

    def nota(self, texto: str):
        self.items.append(Nota(texto))

    def dato(self, nombre, valor, unidad="", desc="", ref="", tex=None, doc=None, clave=False):
        valor = self.sobrescribir.get(nombre, valor)
        v = Var(nombre, "dato", None, unidad, desc, ref, tex, doc=doc, clave=clave)
        v.valor = valor * v.factor
        self._registrar(v)
        self.items.append(v)
        return v

    def ec(self, nombre, expr, unidad="", desc="", ref="", tex=None, ftex=None, doc=None,
           mostrar_expr=True, clave=False):
        v = Var(nombre, "ec", expr, unidad, desc, ref, tex, ftex, mostrar_expr, doc, clave)
        v.valor = self._evaluar(nombre, expr)
        self._registrar(v)
        self.items.append(v)
        return v

    def verif(self, nombre, cond, desc="", ref="", si="OK", no="NO OK", doc=None, clave=True):
        expr = f'IF({cond},"{si}","{no}")'
        v = Var(nombre, "verif", expr, "", desc, ref, doc=doc, clave=clave)
        v.cond = cond
        v.si, v.no = si, no
        v.valor = self._evaluar(nombre, expr)
        self._registrar(v)
        self.items.append(v)
        return v

    def sel(self, nombre, cond, si, no, desc="", ref="", doc=None):
        """Selección informativa (texto) sin semáforo de cumplimiento."""
        v = self.verif(nombre, cond, desc, ref, si, no, doc, clave=False)
        v.tipo = "sel"
        return v

    def tabla(self, titulo, encabezados, unidades, filas):
        tb = Tabla(titulo, list(encabezados), list(unidades))
        for fila in filas:
            fr = []
            for j, celda in enumerate(fila):
                u = tb.unidades[j] if j < len(tb.unidades) else ""
                if isinstance(celda, C):
                    nombre = celda.nombre
                    if nombre is None:
                        self._anon += 1
                        nombre = f"t{self._anon}_"
                    v = Var(nombre, "verif" if celda.verif else "ec", celda.expr, u, celda.desc,
                            doc=celda.doc, en_tabla=True, clave=celda.verif)
                    v.valor = self._evaluar(nombre, celda.expr)
                    self._registrar(v)
                    fr.append(v)
                elif isinstance(celda, D):
                    val = self.sobrescribir.get(celda.nombre, celda.valor)
                    v = Var(celda.nombre, "dato", None, u, en_tabla=True)
                    v.valor = val * v.factor
                    self._registrar(v)
                    fr.append(v)
                else:
                    fr.append(celda)
            tb.filas.append(fr)
        self.items.append(tb)
        return tb

    # ---- ayudas ----------------------------------------------------------
    def __getitem__(self, nombre):
        return self.vars[nombre].valor

    def simbolo(self, nombre: str) -> str:
        if nombre in UNIDADES:
            return unidad_tex(nombre).replace(r"\,", "") if nombre not in ("deg", "pct") else (
                r"^{\circ}" if nombre == "deg" else r"\%")
        v = self.vars.get(nombre)
        if v is not None and v.tex:
            return v.tex
        return tex_auto(nombre)

    def verificaciones(self):
        return [v for v in self.vars.values() if v.tipo == "verif"]


# ---------------------------------------------------------------------------
# Envolventes de carga móvil (líneas de influencia, viga simplemente apoyada)
# ---------------------------------------------------------------------------
def _posiciones(x, desplaz, k, sentido):
    """Posición de cada eje cuando el eje k está sobre la sección x."""
    pos = []
    for j, dj in enumerate(desplaz):
        if j == k:
            pos.append(None)
        else:
            signo = "+" if sentido > 0 else "-"
            pos.append(f"({x}{signo}(({dj})-({desplaz[k]})))")
    return pos


def envolvente_momento(x: str, L: str, cargas: list[str], desplaz: list[str]) -> str:
    """Máximo momento en la sección x producido por un tren de cargas móviles.
    Se evalúa cada eje sobre la sección y ambos sentidos de circulación."""
    configs = []
    for k in range(len(cargas)):
        for s in (1, -1):
            pos = _posiciones(x, desplaz, k, s)
            terms = []
            for j, P in enumerate(cargas):
                if pos[j] is None:
                    terms.append(f"{P}*{x}*({L}-{x})/{L}")
                else:
                    a = pos[j]
                    terms.append(f"{P}*IF(AND({a}>=0,{a}<={L}),IF({a}<={x},{a}*({L}-{x})/{L},{x}*({L}-{a})/{L}),0)")
            configs.append("+".join(terms))
    return "MAX(" + ",".join(configs) + ")"


def envolvente_cortante(x: str, L: str, cargas: list[str], desplaz: list[str]) -> str:
    """Máximo cortante positivo justo a la derecha de la sección x."""
    configs = []
    for k in range(len(cargas)):
        for s in (1, -1):
            pos = _posiciones(x, desplaz, k, s)
            terms = []
            for j, P in enumerate(cargas):
                if pos[j] is None:
                    terms.append(f"{P}*({L}-{x})/{L}")
                else:
                    a = pos[j]
                    terms.append(f"{P}*IF(AND({a}>={x},{a}<={L}),({L}-{a})/{L},IF(AND({a}>=0,{a}<{x}),-{a}/{L},0))")
            configs.append("+".join(terms))
    return "MAX(" + ",".join(configs) + ")"


def suma(nombres: list[str]) -> str:
    return "+".join(nombres)
