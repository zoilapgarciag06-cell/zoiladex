# Diseño de Puentes 2P: memoria de cálculo automatizada

Automatización completa del documento **Puentes_2P_calculos.pdf**: puente tipo losa-vigas preforzadas.
Cada ecuación se escribe **una sola vez** en Python. A partir de ella se generan:

| Salida | Archivo | Contenido |
|---|---|---|
| Excel automatizado | `salida/Puentes_2P.xlsx` | 8 hojas de cálculo con **fórmulas vivas**. Si cambia una celda amarilla, todo se recalcula |
| Reporte LaTeX | `salida/Reporte_Puentes_2P.tex` | Memoria de cálculo con ecuaciones, tablas y verificaciones |
| Reporte PDF | `salida/Reporte_Puentes_2P.pdf` | El `.tex` compilado (77 páginas) |

## Módulos (en el orden del PDF)

| Código / hoja | Contenido | Págs. PDF |
|---|---|---|
| `STD` / `1_Viga_STD` | Viga interior preforzada BT-72, AASHTO Estándar (HS20): propiedades, cargas, pretensado, pérdidas, esfuerzos, flexión, corte, anclaje, deflexiones | 1-13 |
| `LRFD` / `2_Viga_LRFD` | La misma viga según AASHTO LRFD (HL-93, fatiga, pérdidas refinadas, corte por MCFT simplificado, interfaz) | 14-30 |
| `PAC` / `3_Pila_Acero` | Descarga de CM sobre una pila (vigas de acero) | 31-32 |
| `PPR` / `4_Pila_Preforzada` | Descarga de CM sobre una pila (vigas AASHTO IV) | 33-34 |
| `VC` / `5_Viga_Cabezal` | Viga cabezal por el método ASD: corte, flexión, temperatura, refuerzo superficial | 35-38 |
| `FR` / `6_Frenado` | Fuerza de frenado BR | 39 |
| `RE` / `7_Reaccion_Estribo` | Reacción de la carga viva sobre el estribo | 40 |
| `EST` / `8_Estribo` | Estribo LRFD: cargas, sismo (Mononobe-Okabe), volcamiento, capacidad portante, deslizamiento, pantalla, punta y talón | 41-51 |

## Uso

```bash
pip install -r requirements.txt          # openpyxl
python puentes_2p.py                     # genera Excel + .tex + .pdf en ./salida
python puentes_2p.py --set STD.Nt=46 --set EST.l9=3.2 --salida caso2   # cambiar datos
python puentes_2p.py --modulos STD,LRFD  # solo algunos módulos
python puentes_2p.py --verificar         # recalcula el Excel con LibreOffice y lo compara con Python
```

- `--set MOD.nombre=valor`: modifica un dato de entrada. El valor va en las unidades que muestra el Excel, por ejemplo `STD.fcg=500` en kgf/cm².
- Para compilar el PDF se necesita `pdflatex` (TeX Live con `babel-spanish`, `adjustbox` y `booktabs`). Sin él, se genera solo el `.tex`.

### El libro Excel

- **Celdas amarillas con texto azul**: datos editables. Todo lo demás son fórmulas.
- Columna **E**: cada valor en unidades base (tonf, m), con un nombre definido `<HOJA>_<símbolo>`
  (por ejemplo `STD_Psec` o `LRFD_Mu`). Así las fórmulas se leen como en Mathcad:
  `=33000*(STD_Wc/(u_kip/u_ft^3))^1.5*SQRT(STD_fcs/u_ksi)*u_ksi`.
- La hoja **Unidades** define las constantes de conversión (`u_cm`, `u_kip`, `u_ksi`, `u_MPa`, ...).
- La hoja **Resumen** reúne los resultados principales y las 116 verificaciones, con semáforo verde o rojo.
- Las columnas **Valor PDF** y **Dif. vs PDF** comparan cada resultado con la memoria original.

## Validación

- Se compararon 817 valores del PDF original y todos coinciden dentro del 1.2 % (redondeo del PDF).
- Las 1 895 celdas con nombre del Excel, recalculadas con LibreOffice, coinciden con Python (tolerancia 1e-6).
- Cargas móviles: el camión HS20 y el camión de fatiga se resuelven con líneas de influencia exactas. Cada eje se
  coloca sobre la sección y se prueban ambos sentidos de circulación.

## Estructura del código

```
puentes_2p.py              CLI: ejecuta todo y escribe las salidas
puentes2p/motor.py         motor: variables, unidades, evaluación, traducción a Excel y a LaTeX
puentes2p/excel.py         escritor del libro Excel (openpyxl)
puentes2p/latex.py         escritor del reporte LaTeX y compilación con pdflatex
puentes2p/verificar.py     verificación cruzada Excel <-> Python (LibreOffice)
puentes2p/modulos/         los 8 módulos de cálculo
```

Para añadir un cálculo, basta una línea en el módulo correspondiente:

```python
m.ec("Mn", "Aps*fsu*d*(1-0.6*rho*fsu/fcs)", "tonf*m", "Resistencia nominal a flexión", "STD Eq. 9-13")
```

Esa línea crea a la vez el valor en Python, la fórmula viva en Excel y la ecuación en LaTeX.

## Observaciones sobre el PDF original

Se reproduce el PDF tal cual, pero estos puntos conviene revisarlos:

1. **STD, tabla de CV, M(L+I) en 0.3L**: el PDF da 223.36 tonf·m. La envolvente exacta del camión HS20 da
   220.36 tonf·m, probablemente por un error de transcripción en el PDF. En LRFD, Mf en 0.3L da 95.89 frente a 94.08.
2. **LRFD 12.3**: `Avf` usa `Vni·cm` como en el PDF. Lo coherente sería `Vni·Lvi` con Lvi = 2.54 cm. En ambos
   casos Avf < 0, así que la conclusión no cambia.
3. **LRFD 13.1**: el PDF compara `Fpa2` contra `V = 0.5φ(Vc+Vp)`. Contra `Vca` (226.5 tonf) no cumpliría.
   Se deja el criterio del PDF, marcado como tal.
4. **STD 8.2**: además de la comparación del PDF, se añadió la verificación de tensión en la fibra inferior
   (fb ≥ -6√f'c).
