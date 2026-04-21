# Regulación del Alquiler en Barcelona: Análisis Econométrico y Forecasting

**Autores:** Katherine Soto · Juan R. Ortiz · Emilio Delgado  
La Salle — Ramon Llull University

![Barcelona](images/barcelona-sagrada-familia.jpg)

Análisis cuantitativo multimétodo del mercado de alquiler residencial de Barcelona bajo los tres ciclos regulatorios (Ley 11/2020, vacío TC, Ley 12/2023). El proyecto construye un panel trimestral de barrios y distritos (2000–2025) y combina regresión de panel con efectos fijos, clasificación supervisada, series temporales (SARIMAX) e Interrupted Time Series (ITS-3) para cuantificar el efecto causal de la regulación sobre precios nominales, precios reales y volumen contractual.

> **Pregunta de investigación:** ¿Tienen los tres ciclos regulatorios efectos estructurales, estadísticamente distinguibles y geográficamente heterogéneos sobre el precio nominal, el precio real y el volumen contractual del mercado de alquiler de Barcelona?

---

## Hipótesis

**H1 — Regresión de panel:** La regulación redujo significativamente el crecimiento del precio real del alquiler (€/m²) respecto a la tendencia pre-regulatoria, con efectos heterogéneos entre barrios de renta alta y baja.

**H2 — Clasificación:** Es posible predecir si un barrio está bajo tensión de mercado (ratio contratos/oferta > percentil 75) a partir de variables de precio, macroeconómicas y regulatorias, con AUC > 0.65.

**H3 — ITS-3 / SARIMAX:** Cada uno de los tres regímenes regulatorios introduce una ruptura estructural estadísticamente distinguible en la serie de precios y contratos a nivel de distrito, identificable mediante un modelo ITS con tres intervenciones y errores HAC.

---

## Configuración del entorno

### 1. Crear entorno virtual con Python 3.12

```bash
python3.12 -m venv venv312
```

### 2. Activar el entorno

```bash
# macOS / Linux
source venv312/bin/activate

# Windows
venv312\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Arquitectura del proyecto

```
forecasting-inmobiliario-bcn-regulado/
│
├── data/
│   ├── data_raw/          ← Excels originales de Incasol + macrovariables
│   ├── data_interim/      ← Parquets intermedios (post-extract, pre-transform)
│   └── data_cleaned/      ← Parquets finales listos para EDA y modelado
│
├── src/                   ← Data engineering (ETL modular orientado a clases)
│   ├── config.py          ← PipelineConfig: paths, fechas regulatorias, barrios excluidos
│   ├── pipeline.py        ← ETLPipeline: orquestador Extract → Transform → Load
│   ├── extract/
│   │   └── incasol.py     ← IncasolExtractor: parseo de los 4 Excels de Incasol
│   ├── transform/
│   │   ├── macrovars.py   ← MacroVarLoader: IPC, Euribor, IST index
│   │   ├── features.py    ← FeatureEngineer: interfaz fluent para feature engineering
│   │   └── clean.py       ← DataCleaner: filtros finales y tipado
│   └── utils/
│       └── nulls.py       ← NullValidator: reporte y validación de nulos
│
├── notebooks/
│   ├── 0-null-analysis.ipynb  ← Calidad de datos: exploración interactiva de nulos
│   ├── 01-eda.ipynb           ← Análisis exploratorio: series, distribuciones, EDA
│   └── 02-models.ipynb        ← Modelado: panel FE, clasificación, SARIMAX, ITS-3
│
├── paper/
│   └── paper.pdf          ← Paper de investigación completo
│
├── images/
│   └── barcelona-sagrada-familia.jpg
│
└── requirements.txt
```

### Clases del ETL

| Clase | Módulo | Responsabilidad |
|---|---|---|
| `PipelineConfig` | `src/config.py` | Fuente única de verdad: paths y fechas regulatorias |
| `IncasolExtractor` | `src/extract/incasol.py` | Parseo de 4 Excels Incasol (barrios y distritos) |
| `MacroVarLoader` | `src/transform/macrovars.py` | Carga y merge de IPC, Euribor e IST |
| `FeatureEngineer` | `src/transform/features.py` | Feature engineering encadenable (fluent interface) |
| `DataCleaner` | `src/transform/clean.py` | Filtros finales y tipado de columnas |
| `NullValidator` | `src/utils/nulls.py` | Validación de nulos contra umbrales esperados |
| `ETLPipeline` | `src/pipeline.py` | Orquesta las tres fases del ETL |

---

## Flujo de ejecución

### Paso 1 — ETL (Data Engineering)

Desde la raíz del proyecto, con el entorno activado:

```bash
python -m src.pipeline
```

El pipeline ejecuta tres fases:

1. **Extract** — lee los 4 Excels de Incasol y valida duplicados
2. **Transform** — añade macrovariables (IPC, Euribor, IST) y genera features (crecimientos, rezagos, dummies regulatorias, precios reales)
3. **Load** — aplica filtros finales, valida nulos y guarda parquets

Outputs generados en `data/data_cleaned/`:
- `df_distritos_eda.parquet` — panel de distritos (1030 × 27)
- `df_barrios_eda.parquet` — panel de barrios (3102 × 28)

---

### Paso 2 — Análisis de nulos

```bash
jupyter notebook notebooks/0-null-analysis.ipynb
```

Exploración interactiva de la distribución de nulos por columna, validación contra umbrales esperados y verificación de claves únicas del panel.

---

### Paso 3 — EDA

```bash
jupyter notebook notebooks/01-eda.ipynb
```

Análisis exploratorio del panel: series temporales por distrito y barrio, distribuciones de precio nominal y real, test de Chow de ruptura estructural, comparativa de periodos regulatorios y análisis de heterogeneidad geográfica.

---

### Paso 4 — Modelado

```bash
jupyter notebook notebooks/02-models.ipynb
```

Implementación de los modelos que contrastan las tres hipótesis:

- **H1 · Regresión de panel con efectos fijos** — within estimator, dummies regulatorias (D_ley11, D_tc_gap, D_ley12)
- **H2 · Clasificación supervisada** — Random Forest, Logistic Regression, Panel Logit con FE de barrio; evaluación AUC-ROC y SHAP
- **H3 · SARIMAX + ITS-3** — forecasting de precios y contratos por distrito; Interrupted Time Series con tres regímenes y errores HAC

---

## Conclusiones

**H1 — Se acepta parcialmente** La regulación produjo efectos estadísticamente distinguibles sobre precio y volumen, aunque con signo asimétrico según el régimen. La Ley 11/2020 genera un level shift inmediato de −1.11 €/m² en precio nominal (p = 0.007) sin efecto en precio real. La derogación del TC tiene el mayor impacto en precio real (−0.558 €/m², p = 0.003). La Ley 12/2023 contrae el volumen contractual (−1 588 contratos/trimestre, p = 0.007) pero eleva el precio real (+0.495 €/m², p = 0.034), coherente con un efecto composición. Sin embargo, no se detecta diferencial significativo entre barrios de renta alta y baja (β = −0.019, p = 0.301), por lo que la hipótesis de heterogeneidad geográfica en elasticidad se rechaza.

**H2 — Se acepta parcialmente** El Random Forest alcanza AUC = 0.684 (validación cruzada temporal: 0.684 ± 0.083), superando el umbral de 0.65 establecido en la hipótesis. La ingeniería de lag features es el factor determinante: el lag-4 del crecimiento de contratos es la señal dominante según SHAP (|φ̄| = 0.093), por encima de todas las variables de política regulatoria.

**H3 — Se acepta** El modelo ITS-3 identifica rupturas estructurales estadísticamente significativas en las series de precio nominal, precio real y volumen contractual para cada uno de los tres regímenes regulatorios, en todos los distritos analizados. Los intervalos de confianza SARIMAX son estadísticamente válidos (test ARCH p > 0.05) salvo en la serie de contratos de Eixample.

> **Mecanismo central:** La paradoja precio↑ / volumen↓ bajo la Ley 12/2023 es geográficamente consistente y cuantitativamente robusta al sesgo de sustitución hacia contratos de temporada hasta el 20.3% de migración estimada. El efecto composición — salida del mercado de las unidades de menor precio — es la explicación más plausible.
