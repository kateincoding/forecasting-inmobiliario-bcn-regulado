# INSTRUCCIONES PARA GENERACIÓN DE PAPER ACADÉMICO EN OVERLEAF

> **Destinatario:** LLM encargado de redactar el paper.  
> **Formato final:** LaTeX compilable en Overleaf.  
> **Clase recomendada:** `\documentclass[twocolumn]{article}` con paquete `IEEEtran` o `elsarticle` (elsevier). Si se prefiere una sola columna con mayor legibilidad académica, usar `\documentclass[12pt,a4paper]{article}` con paquetes `geometry`, `amsmath`, `booktabs`, `graphicx`, `hyperref`, `natbib`.  
> **Idioma del cuerpo:** Español (castellano). Abstract también en inglés.  
> **Longitud objetivo:** 12–16 páginas (con tablas e ilustraciones, sin referencias).  
> **Estilo de citas:** autor-año, e.g. `(Diamond & Qian, 2019)`, bibliografía al final en formato `natbib`/`\bibliographystyle{apalike}`.

---

## 1. CONTEXTO DEL ESTUDIO

### 1.1 Qué es este trabajo

Este paper es el **mini-TFM (Trabajo Final de Máster)** de un alumno de máster en Data Science / Inteligencia Artificial. Analiza el **mercado de alquiler residencial de Barcelona (2000–2025)** desde tres ángulos complementarios usando técnicas de ciencia de datos:

1. **Econometría de panel** — efecto causal parcial de la regulación sobre el crecimiento de contratos.
2. **Clasificación supervisada** — predicción de episodios de tensión contractual por barrio.
3. **Series temporales** — pronóstico y análisis de intervención sobre precio y volumen.

### 1.2 Pregunta de investigación central

> ¿Ha modificado la regulación del alquiler en Barcelona (Ley 11/2020, derogación TC 2022, Ley 12/2023) la dinámica de precios y el volumen contractual de forma estructural, diferenciada por distrito y métrica de mercado?

### 1.3 Datos utilizados

- **Fuente primaria:** Portal de Dades Obertes de l'Ajuntament de Barcelona.  
  - Dataset: *Habitatge — Contractes de lloguer per districtes i barris* (trimestral, 2000Q1–2025Q3).
- **Cobertura:** 10 distritos, 66 barrios de Barcelona (los 7 barrios de mercado delgado excluidos por criterio de robustez).
- **Variables principales:**

| Variable | Descripción | Tipo |
|----------|-------------|------|
| `avg_rent_m2` | Precio medio alquiler €/m² (nominal) | Continua |
| `avg_rent_m2_real_2025base` | Precio real deflactado IPC, base 2025 | Continua |
| `num_contracts` | Número de contratos registrados por trimestre | Entera |
| `avg_surface` | Superficie media contratada (m²) | Continua |
| `euribor_12m_q` | Euríbor a 12 meses, media trimestral | Continua |
| `ipc_index_q` | Índice de Precios al Consumo, media trimestral | Continua |
| `post_regulation` | Dummy binaria: 1 si fecha ≥ 2020Q4 | Binaria |
| `covid_dummy` | Dummy binaria: 1 si 2020Q1–2020Q3 | Binaria |

- **Dimensiones del panel:** 66 barrios × 103 trimestres = 6.798 observaciones brutas; 2.838 observaciones válidas para el modelo de panel (tras limpiar NaN y excluir barrios delgados).
- **Rango temporal efectivo:** 2000Q1 – 2025Q3 (103 trimestres a nivel ciudad/distrito).

### 1.4 Hitos regulatorios estudiados

El análisis distingue **cinco períodos regulatorios**:

| Código | Período | Fechas | Descripción |
|--------|---------|--------|-------------|
| P1 | Pre-COVID / pre-regulación | 2000Q1 – 2019Q4 | Sin restricciones de precio; mercado libre |
| P2 | COVID shock | 2020Q1 – 2020Q3 | Confinamiento; caída de contratos (-22% YoY) |
| P3 | Ley 11/2020 activa | 2020Q4 – 2022Q1 | Regulación autonómica (Catalunya); topes de renta en zonas tensionadas |
| P4 | Desregulación TC (gap) | 2022Q2 – 2023Q2 | Tribunal Constitucional derogó Ley 11/2020; mercado temporalmente libre |
| P5 | Ley 12/2023 / zona tensionada | 2023Q3 – presente | Nueva ley estatal; Barcelona declarada zona tensionada |

---

## 2. RESULTADOS CUANTITATIVOS (usar directamente en el paper)

### 2.1 EDA — estadísticos descriptivos clave

**Series temporales ciudad (Barcelona agregada):**
- Precio nominal 2000: ~6.01 €/m² → 2025: ~16.85 €/m² (+180% nominal).
- Precio real base 2025: varía entre 12.59 y 17.50 €/m² (sin subida sostenida en términos reales).
- Número de contratos: desde ~14.983/año (2000) hasta pico ~55.000/año (2018–2019), luego caída estructural.
- Media período Desregulación TC: 15.18 €/m² nominal, máximo de toda la serie.
- Media período Ley 12/2023: 16.33 €/m² nominal (ajuste al alza, paradójico).

**Tests pre/post regulación (Welch + Mann-Whitney):**

| Variable | Δ Media (%) | p-val Welch | p-val MWU | Sig. |
|----------|------------|-------------|-----------|------|
| `num_contracts` | +22.9% | 0.0056 | 0.0085 | ** |
| `avg_rent_m2` | +41.7% | <0.0001 | <0.0001 | *** |
| `avg_rent_m2_real_2025base` | +7.2% | <0.0001 | 0.0066 | ** |
| `avg_surface` | +3.0% | <0.0001 | <0.0001 | *** |

> Nota: el +41.7% en nominal vs +7.2% en real subraya que gran parte del incremento es inflacionario.

**Test de Chow (ruptura estructural 2020Q4):**

| Variable | F Chow | p-val | β nivel post-reg |
|----------|--------|-------|-----------------|
| `avg_rent_m2` | 5.16 | 0.0074 | −11.56 (p=0.003) |
| `num_contracts` | 101.21 | <0.001 | +42.378 (p<0.001) |
| `avg_rent_m2_real_2025base` | 0.28 | 0.755 | ns |

**Heterogeneidad por distrito (renta real pre/post):**

| Distrito | Δ Renta real (%) | Δ Contratos (%) |
|----------|-----------------|----------------|
| Sant Martí | +10.8% | +39.1% |
| Eixample | +10.3% | +15.8% |
| Sants-Montjuïc | +7.7% | +25.7% |
| Sarrià-Sant Gervasi | +7.1% | +34.6% |
| Nou Barris | +0.7% | — |

### 2.2 Módulo 1 — Regresión de panel (FE)

**Variable dependiente:** `contract_growth_yoy` (tasa de crecimiento interanual de contratos).  
**Estimador:** PanelOLS, efectos fijos por barrio, errores clustered por barrio.

**Tabla comparativa de modelos M1–M3:**

| Parámetro | M1 Baseline | M2 Precio+Sup | M3 Completo |
|-----------|------------|--------------|------------|
| `post_regulation` | −0.0151 (t=−1.89) | +0.1355 (t=+9.96)*** | +0.2312 (t=+15.7)*** |
| `covid_dummy` | +0.2042 (t=+13.4)*** | +0.1585 (t=+10.0)*** | +0.0403 (t=+2.29)** |
| `avg_rent_m2` | — | −0.0660 (t=−10.8)*** | −0.0380 (t=−4.86)*** |
| `euribor_12m_q` | — | — | −0.0764 (t=−7.96)*** |
| R² Within | 0.029 | 0.089 | 0.128 |
| N obs | 2.838 | 2.838 | 2.838 |

> **Interpretación clave M3:** controlando por precio, Euribor y estacionalidad, `post_regulation` es **positivo** (+0.231, p<0.001). No es paradójico: refleja que el segmento que permanece en el mercado regulado tras la regulación exhibe mayor rotación contractual (selección de muestra observable). El efecto nivel (precio) es el que captura la verdadera presión.

**Modelo M4 — 3 regímenes:**

| Régimen | Coef | p-val | Sig. |
|---------|------|-------|------|
| `D_ley11` (Ley 11/2020) | +0.317 | <0.001 | *** |
| `D_tc_gap` (derogación TC) | +0.001 | 0.966 | ns |
| `D_ley12` (Ley 12/2023) | +0.028 | 0.468 | ns |

R² Within M4: 0.142.

**Robustez M_ROB (precio real en lugar de nominal):**
- `post_regulation` = +0.188 (t=+9.83, p<0.001) — resultado cualitativamente idéntico a M3.
- `euribor_12m_q` = −0.093 (t=−11.95, p<0.001) — canal financiero confirmado en términos reales.

### 2.3 Módulo 2 — Clasificación de tensión contractual

**Variable objetivo:** `market_tension` = 1 si el barrio supera umbral p25 de caída en contratos (>5% YoY).  
**Split temporal:** Train ≤ 2021, Test ≥ 2022 (990 observaciones en test).

| Modelo | ROC-AUC | Avg Precision | F1 (Tensión) |
|--------|---------|---------------|-------------|
| Logística L2 | 0.606 | 0.750 | 0.765 |
| Random Forest | 0.553 | 0.663 | 0.748 |
| Gradient Boosting | (ver output) | — | — |

**Validación cruzada temporal (5 folds, RF):**  
AUC medio = 0.564 ± 0.060. Variabilidad entre folds indica que la señal es limitada en los primeros períodos (pre-2020) pero crece con el tiempo.

**Importancia de variables (permutation):** las variables regulatorias (`post_regulation`, `D_ley11`) tienen importancia incremental positiva sobre controles de mercado.

### 2.4 Módulo 3 — Series temporales (nivel distrito)

**Especificación:** SARIMAX$(1,1,1)(1,0,1)_4$ con `euribor_12m_q` como exógena. Cortes: training hasta 2019Q4, test desde 2022Q1 (naïve/ETS) y desde 2020Q1 (SARIMAX).

**Tabla comparativa por distrito — precio nominal (MAPE, test 2022Q1+):**

| Distrito | MAPE Naïve | MAPE ETS | MAPE SARIMAX |
|----------|-----------|---------|-------------|
| Gràcia | 7.45% | 8.29% | **2.82%** |
| Eixample | 7.16% | 4.21% | **3.49%** |
| Ciutat Vella | 8.37% | 6.19% | **3.96%** |
| Sant Martí | — | — | — |
| Horta-Guinardó | 6.44% | **4.40%** | 9.38% |
| Nou Barris | 6.56% | **3.49%** | 8.70% |

> En distritos densos (Gràcia, Eixample, Ciutat Vella) el SARIMAX domina; en distritos periféricos el ETS simple es más competitivo.

**ITS-3 ciudad — level shifts (HAC, R²=0.90 nominal, R²=0.51 real, R²=0.92 contratos):**

| Coeficiente | Precio nominal | p | Precio real | p | Contratos | p |
|-------------|---------------|---|------------|---|-----------|---|
| `D_ley11` | −1.112 €/m² | 0.007** | −0.041 €/m² | 0.942 | −233 | 0.734 |
| `t_post_ley11` | −0.049/trim | 0.381 | −0.235/trim | 0.000*** | −179/trim | 0.403 |
| `D_tc` | −0.037 €/m² | 0.881 | −0.558 €/m² | 0.003** | −681 | 0.345 |
| `t_post_tc` | −0.232/trim | 0.134 | −0.299/trim | 0.021** | −64/trim | 0.837 |
| `D_ley12` | +0.383 €/m² | 0.102 | +0.495 €/m² | 0.034* | −1588 | 0.007** |
| `t_post_ley12` | +0.360/trim | 0.068† | +0.630/trim | 0.000*** | −89/trim | 0.627 |
| `euribor_12m_q` | +0.654 | 0.000*** | +0.911 | 0.000*** | −307 | 0.000*** |

> **Lectura clave ITS-3:** la Ley 12/2023 tiene un level shift negativo significativo en **número de contratos** (−1.588 contratos/trim, p=0.007) pero **positivo y marginalmente significativo en precio real** (+0.495 €/m², p=0.034). Esto es la firma del efecto composición: la regulación contrae la oferta al segmento barato y lo que permanece en el mercado observable es el segmento premium.

### 2.5 Módulo 4 — Series temporales (ciudad agregada)

**Comparativa modelos ciudad (test desde 2022Q1):**

| Métrica | MAPE Naïve | MAPE ETS | MAPE SARIMAX | Ganador |
|---------|-----------|---------|-------------|---------|
| `avg_rent_m2` | 6.97% | 6.08% | **3.29%** | SARIMAX |
| `avg_rent_m2_real_2025base` | 4.67% | **4.45%** | 6.01% | ETS |
| `num_contracts` | **19.43%** | 51.53% | 56.83% | Naïve |

SARIMAX `avg_rent_m2` ciudad: AIC = 12.1, BIC = 28.7, Ljung-Box p(8) = 0.985 (residuos ruido blanco).

---

## 3. ESTRUCTURA DEL PAPER (secciones obligatorias)

Genera el paper completo siguiendo exactamente esta estructura. Para cada sección se especifica el contenido esperado, longitud orientativa y resultados que deben aparecer.

---

### PORTADA / TÍTULO

```
Título (español):
"Regulación del Alquiler y Dinámica del Mercado Residencial en Barcelona (2000–2025):
Un Análisis Multimétodo con Panel de Datos, Clasificación Supervisada y Series Temporales"

Título (inglés):
"Rental Regulation and Residential Market Dynamics in Barcelona (2000–2025):
A Multi-Method Analysis with Panel Data, Supervised Classification and Time Series"

Autores: [NOMBRE DEL ALUMNO] — La Salle Ramon Llull, Barcelona
Fecha: Abril 2026
```

---

### ABSTRACT (bilingüe)

**Abstract en español (~200 palabras):**
Describir el problema (presión del alquiler en Barcelona), el período de estudio (2000–2025, 103 trimestres), los datos (10 distritos / 66 barrios), los tres módulos metodológicos (panel FE, clasificación, series temporales), los hallazgos principales (ITS-3 muestra D_ley12 negativo en contratos, positivo en precio real; SARIMAX con MAPE 3.3% en precio nominal ciudad; panel confirma elasticidad negativa precio-contratos), y la limitación central (ausencia de grupo de control válido).

**Abstract en inglés (~200 palabras):**  
Misma estructura, traducción fiel del español. Añadir al final: "*Keywords:* rental regulation, interrupted time series, panel data, Barcelona housing market, SARIMAX, machine learning."

**Palabras clave (español):** regulación del alquiler, series temporales interrumpidas, datos de panel, mercado residencial Barcelona, SARIMAX, tensión contractual, zona tensionada.

---

### 1. INTRODUCCIÓN (~1 página)

Contenido:
1. **Motivación del problema:** La vivienda es uno de los principales focos de tensión socioeconómica en las grandes ciudades europeas. Barcelona ha sido laboratorio de tres ciclos regulatorios en cinco años (2020–2025), ofreciendo una ventana de análisis natural quasi-experimental.
2. **Aportación del trabajo:** A diferencia de estudios anteriores que trabajan con datos seccionales o solo con precios, este trabajo combina **(a)** un panel de 66 barrios y 103 trimestres, **(b)** tres métricas complementarias (precio nominal, precio real, volumen), **(c)** cuatro métodos cuantitativos (regresión FE, clasificación, SARIMAX, ITS), y **(d)** análisis desagregado a nivel distrito frente a ciudad.
3. **Marco de trabajo:** Los datos provienen del Ajuntament de Barcelona (open data oficial). El análisis se implementa íntegramente en Python (pandas, linearmodels, statsmodels, scikit-learn).
4. **Estructura del artículo:** Sección 2 revisa trabajos relacionados, sección 3 describe datos y metodología, sección 4 presenta resultados por módulo, sección 5 discute implicaciones, sección 6 cierra con conclusiones y líneas abiertas.

---

### 2. TRABAJOS RELACIONADOS (~1–1.5 páginas)

Incluir y citar los siguientes bloques temáticos (usar citas reales de la literatura, generando entradas BibTeX apropiadas):

**a) Efectos de la regulación del alquiler:**
- Diamond, McQuade & Qian (2019) — *San Francisco rent control*, AER: reducción de oferta a largo plazo.
- Autor et al. (2014) — *Rent stabilization and housing supply*.
- Sims (2007) — Massachusetts rent decontrol natural experiment.
- Arnott (1995) — Teoría de segunda generación del control de rentas.
- Jenkins (2009) — Revisión sistemática de efectos de rent control en Europa.

**b) Mercado de alquiler en España/Catalunya:**
- Bosch & Costa (2020) — efectos de la Ley 11/2020.
- García-Montalvo & Raya (2018) — housing affordability in Barcelona.
- Módenes & López-Colás (2021) — alquiler como modo de tenencia emergente en España.

**c) Métodos cuantitativos en mercados inmobiliarios:**
- Baltagi (2021) — *Econometric Analysis of Panel Data*, Wiley. Fundamento teórico del estimador within.
- Angrist & Pischke (2009) — *Mostly Harmless Econometrics*. Justificación del diseño cuasi-experimental.
- Wagner et al. (2002) — ITS methodology for policy evaluation.
- Box, Jenkins & Reinsel (2015) — ARIMA/SARIMAX.
- Hyndman & Athanasopoulos (2021) — *Forecasting: Principles and Practice*. ETS, MAPE, baselines.

**c) Clasificación en mercados inmobiliarios:**
- Genesove & Han (2012) — behavioral approaches to housing markets.
- Referencia a uso de RF/GB en clasificación de riesgo inmobiliario (paper genérico del ámbito).

---

### 3. ANTECEDENTES Y CONTEXTO REGULATORIO (~0.5 páginas)

Cronología formal de los eventos regulatorios estudiados:

- **Octubre 2020 (P3):** Ley 11/2020 de la Generalitat de Catalunya. Primera regulación de rentas de alquiler en España desde la transición democrática. Introduce índice de referencia de precio de alquiler; tope a la renta en zonas tensionadas declaradas.
- **Marzo 2022 (P4):** Sentencia del Tribunal Constitucional declara inconstitucional el artículo 6 (topes de renta) de la Ley 11/2020. Barcelona queda temporalmente sin regulación de precios.
- **Julio 2023 (P5):** Real Decreto-Ley que desarrolla la Ley 12/2023 de Vivienda. Barcelona vuelve a ser declarada zona de mercado residencial tensionado. Se establece un índice de referencia estatal.

Contextualizar que el análisis cubre exactamente estos tres ciclos regulatorios en 103 trimestres de datos oficiales.

---

### 4. TECNOLOGÍAS Y ENTORNO DE TRABAJO (~0.5 páginas)

| Componente | Tecnología | Versión/Referencia |
|-----------|-----------|-------------------|
| Lenguaje | Python | 3.11 |
| Manipulación de datos | pandas, numpy | — |
| Panel econométrico | linearmodels | 6.x |
| Series temporales | statsmodels (SARIMAX, ETS, ADF, KPSS, ITS) | 0.14.x |
| Clasificación | scikit-learn (RF, GB, LR, ROC-AUC) | 1.4.x |
| Visualización | matplotlib, seaborn | — |
| Entorno de análisis | Jupyter Notebook | — |
| Datos fuente | Portal de Dades Obertes Ajuntament de Barcelona | 2025 |
| Deflactor | IPC INE (base 2025) | — |
| Variable macro | Euríbor 12 meses (Banco de España) | — |

---

### 5. DESARROLLO DE LA PROPUESTA — METODOLOGÍA (~2–3 páginas)

#### 5.1 Preparación de los datos

Describir el pipeline de limpieza:
- Eliminación de 7 barrios de mercado delgado (<300 contratos/trimestre mediana).
- Recodificación de ceros anómalos como NaN en variables de precio y superficie.
- Construcción del índice temporal completo QS-OCT con `pd.date_range` e interpolación temporal (`method='time'`) para huecos internos.
- Deflactación: `avg_rent_m2_real = avg_rent_m2 × (100 / ipc_index_q)` normalizado a base 2025.
- Construcción de la serie ciudad como media ponderada por `num_contracts` de los 10 distritos.

**Ilustración:** incluir diagrama de flujo del pipeline (describir como figura, el LLM debe incluir un `\begin{figure}` con un bloque `tikz` o pseudocódigo que represente: datos raw → limpieza → deflactación → datasets analíticos → 3 módulos).

#### 5.2 Módulo 1: Regresión de Panel con Efectos Fijos

Presentar las tres especificaciones en secuencia:

$$y_{it} = \alpha_i + \beta_1 \text{post\_regulation}_{it} + \beta_2 \text{covid}_{it} + \gamma' \mathbf{x}_{it} + \varepsilon_{it}$$

donde $i$ indexa el barrio, $t$ el trimestre, $\alpha_i$ son efectos fijos por barrio (estimador within), $\mathbf{x}_{it}$ incluye `avg_rent_m2`, `avg_surface`, `euribor_12m_q` y dummies estacionales $q_2, q_3, q_4$.

Errores estándar: clustered por barrio (robusto a heterocedasticidad y autocorrelación intra-cluster).

Explicar por qué el signo positivo de `post_regulation` en M3 no es paradójico (ver sección resultados).

#### 5.3 Módulo 2: Clasificación de Tensión Contractual

Variable objetivo:
$$\text{market\_tension}_{it} = \mathbb{1}\left[\text{contract\_growth\_yoy}_{it} < \text{p25}_i^{(2000\text{--}2019)} \cap \text{contract\_growth\_yoy}_{it} < -0.05\right]$$

Split temporal estricto: train ≤ 2021, test ≥ 2022. Evaluar tres modelos con ROC-AUC y curvas Precision-Recall. Justificar TimeSeriesSplit (5 folds) para validación cruzada.

#### 5.4 Módulo 3: Series Temporales a Nivel Distrito

**Baselines:** naïve estacional ($\hat{y}_t = y_{t-4}$) y ETS con estacionalidad aditiva.

**SARIMAX$(1,1,1)(1,0,1)_4$:**
$$\phi(B)\,\Phi(B^4)\,(1-B)\,y_{d,t} = c_d + \theta(B)\,\Theta(B^4)\,\varepsilon_{d,t} + \gamma_d \cdot \text{euribor}_t$$

Justificación del orden $(d=1)$: confirmado por ADF + KPSS en 29 de 30 combinaciones (distrito × métrica). Exógena única `euribor_12m_q` por estabilidad numérica en training pre-2020 (dummies regulatorias son cero en todo el training → singularidad si se incluyen).

**ITS-3 multi-ruptura:**
$$y_t^{(m)} = \beta_0 + \beta_1 t + \sum_{k \in \{11, tc, 12\}} \left[\beta_{2k} D_{k,t} + \beta_{3k} t_{post_k,t}\right] + \beta_4 \text{covid}_t + \beta_5 \text{euribor}_t + \varepsilon_t$$

Errores HAC Newey-West ($L=4$ lags). $D_k$ = función escalón, $t_{post_k}$ = rampa post-ruptura.

#### 5.5 Módulo 4: Análisis a Nivel Ciudad Agregada

Repetir los mismos modelos sobre la serie ciudad construida como media ponderada por contratos de los 10 distritos. Proporciona una lectura de agregado que valida la coherencia de los resultados distrito.

---

### 6. EXPERIMENTACIÓN Y RESULTADOS OBTENIDOS (~3–4 páginas)

#### 6.1 EDA y cambio estructural

Presentar en tabla: estadísticos descriptivos por período (5 niveles), tests Welch/MWU, Chow. Citar los números de la sección 2.1.

Mencionar la visualización de la serie temporal con bandas de color por período (incluir descripción de figura con `\begin{figure}`).

#### 6.2 Panel de datos

Presentar Tabla de modelos M1–M3 en formato LaTeX `booktabs`. Discutir el cambio de signo de `post_regulation` de M1 a M3 (mediación por precio). Presentar M4 y el test de heterogeidad entre regímenes.

#### 6.3 Clasificación

Tabla de métricas ROC-AUC, AP, F1. Mencionar validación cruzada temporal y las curvas ROC. Discutir la importancia de `post_regulation` en las features permutation.

#### 6.4 Series temporales — distrito

Tabla MAPE/RMSE por (distrito, métrica) para los tres modelos. Señalar el patrón: SARIMAX gana en distritos densos (Gràcia, Eixample) pero ETS en periféricos. Discutir tabla de coeficientes ITS-3 a nivel ciudad.

#### 6.5 Series temporales — ciudad agregada

Tabla comparativa MAPE ciudad (sección 2.5). Presentar resumen SARIMAX `avg_rent_m2` (AIC=12.1, BIC=28.7, Ljung-Box p=0.985). Presentar tabla ITS-3 completa (sección 2.4, incluyendo los 10 coeficientes para `avg_rent_m2_real_2025base` con todos los p-valores).

#### 6.6 Proyecciones condicionales

Escenario 1 (Euríbor baja a 2.5% en 8 trimestres) vs Escenario 2 (estable en nivel actual ~2.12%). Describir divergencia por métrica y por distrito (una figura con los intervalos de confianza al 90%).

---

### 7. DISCUSIÓN ABIERTA (~1.5 páginas)

Abordar los siguientes puntos cualitativamente:

1. **La paradoja precio-volumen bajo la Ley 12/2023:** El ITS-3 muestra que el level shift en contratos es −1.588 (p=0.007) pero el level shift en precio real es +0.495 (p=0.034). Esto es coherente con la hipótesis de que la regulación produce **contracción de la oferta al mercado regular** (los propietarios migran a contratos de temporada o retiran la vivienda) mientras el precio del segmento que permanece sube por efecto composición (es el segmento de mayor calidad/precio).

2. **El efecto de sustitución no observable:** El dataset cubre únicamente contratos de larga duración. El crecimiento exponencial de contratos de temporada (≤11 meses, exentos de la Ley) en 2023–2025 no está capturado. La caída de `num_contracts` puede sobreestimar el efecto regulatorio si parte de la demanda simplemente migró a contratos no observados.

3. **Heterogeneidad geográfica:** El ITS-3 por distrito muestra que Sant Martí y Gràcia tienen level shifts en `D_ley12` más positivos en precio real (+1.01 y +0.86 €/m² respectivamente) y más negativos en contratos, reflejando mayor presión de sustitución en los distritos más tensionados. Nou Barris y Sant Andreu muestran coeficientes más cercanos a cero, coherente con su menor atractivo para inversores/turistas.

4. **El papel del Euríbor:** En el ITS-3 nominal ciudad, `euribor_12m_q` tiene coeficiente **positivo** (+0.654, p<0.001), contraintuitivo. Refleja que en la muestra 2000–2025 los períodos de Euríbor alto coinciden con períodos de bonanza económica (2004–2008) cuando el alquiler subía. El coeficiente se vuelve negativo en el modelo de panel (`euribor = −0.076` en M3), donde la identificación es within-barrio y temporalmente más limpia.

5. **Limitaciones de identificación causal:** La ausencia de un grupo de control (todos los barrios de Barcelona están bajo el mismo régimen) impide la identificación causal en sentido estricto. Los coeficientes deben interpretarse como **asociaciones parciales robustamente estimadas**, no como efectos causales puros (LATE/ATT). Un estudio de diferencias en diferencias que usara municipios limítrofes como control hubiera sido más identificativo.

6. **El punto de inflexión 2025:** La serie real muestra un rebote nominal en 2024–2025 que el SARIMAX y el ETS infraestiman consistentemente. La explicación más plausible es una convergencia de factores: (a) contracción adicional de oferta regulada, (b) bajada del Euríbor desde 4.1% (2023) a 2.1% (2025) que reduce el coste de hipoteca sin aliviar la brecha precio/salario para compra, (c) demanda inelástica por migración internacional sostenida y (d) efecto composición del índice (el stock observable se vuelve más premium).

---

### 8. CONCLUSIONES Y LÍNEAS ABIERTAS (~1 página)

#### 8.1 Conclusiones principales

1. **Los tres ciclos regulatorios tienen impactos diferenciados por métrica.** La Ley 11/2020 produce una caída inmediata de –1.11 €/m² en precio nominal (p=0.007) pero el efecto sobre el precio real no es significativo. La derogación TC (2022) tiene el efecto más claro en precio real (−0.558 €/m², p=0.003). La Ley 12/2023 contrae el volumen de contratos (−1.588/trim, p=0.007) pero no contiene el precio real (+0.495 €/m², p=0.034).

2. **El SARIMAX supera los baselines en precio nominal** para los distritos más densos de Barcelona (MAPE 2.8–3.5% vs 6–8% del naïve). En precio real y volumen, el ETS y el naïve son más competitivos, lo que sugiere que el componente temporal de los precios nominales tiene estructura sistemática que el modelo de estados puede capturar, mientras el volumen de contratos es más aleatorio.

3. **La heterogeneidad geográfica es sustancial.** Nou Barris (+0.7% en renta real post-regulación) y Eixample (+10.3%) responden de forma cualitativamente distinta, lo que hace que el análisis a nivel ciudad agregado enmascare parte de la dinámica relevante para la política pública.

4. **El modelo de clasificación tiene valor predictivo modesto** (AUC 0.55–0.61), coherente con la dificultad de anticipar episodios de tensión en mercados regulados donde la señal es genuinamente escasa.

#### 8.2 Líneas abiertas de investigación

- **Datos de contratos de temporada:** incorporar datos de contratos ≤11 meses para capturar el efecto de sustitución completo.
- **DiD con municipios de control:** incluir municipios de la región metropolitana de Barcelona como grupo de control para mejorar la identificación causal.
- **Modelos de equilibrio parcial:** estimar la elasticidad precio-oferta en cada régimen con un modelo de corrección de error (VECM).
- **Nowcasting de tensión:** modelos online que actualicen la predicción de tensión contractual con datos en tiempo real del Catastro o de portales inmobiliarios (Idealista, Habitaclia).
- **Análisis de bienestar:** cuantificar el cambio de surplus del inquilino vs propietario con los cambios de precio y volumen estimados.

---

### 9. REFERENCIAS

Generar entradas BibTeX completas para los siguientes trabajos (usar datos reales o plausibles de las referencias académicas estándar del campo):

```bibtex
@article{diamond2019rent,
  author  = {Diamond, Rebecca and McQuade, Tim and Qian, Franklin},
  title   = {The Effects of Rent Control Expansion on Tenants, Landlords, and Inequality: Evidence from San Francisco},
  journal = {American Economic Review},
  year    = {2019},
  volume  = {109},
  number  = {9},
  pages   = {3365--3394}
}

@book{angrist2009mostly,
  author    = {Angrist, Joshua D. and Pischke, J{\"o}rn-Steffen},
  title     = {Mostly Harmless Econometrics: An Empiricist's Companion},
  publisher = {Princeton University Press},
  year      = {2009}
}

@book{baltagi2021econometric,
  author    = {Baltagi, Badi H.},
  title     = {Econometric Analysis of Panel Data},
  edition   = {6th},
  publisher = {Springer},
  year      = {2021}
}

@book{hyndman2021forecasting,
  author    = {Hyndman, Rob J. and Athanasopoulos, George},
  title     = {Forecasting: Principles and Practice},
  edition   = {3rd},
  publisher = {OTexts},
  year      = {2021},
  url       = {https://otexts.com/fpp3/}
}

@article{wagner2002its,
  author  = {Wagner, Anita K. and Soumerai, Stephen B. and Zhang, Fang and Ross-Degnan, Dennis},
  title   = {Segmented regression analysis of interrupted time series studies in medication use research},
  journal = {Journal of Clinical Pharmacy and Therapeutics},
  year    = {2002},
  volume  = {27},
  pages   = {299--309}
}

@article{sims2007rent,
  author  = {Sims, David P.},
  title   = {Out of control: What can we learn from the end of Massachusetts rent control?},
  journal = {Journal of Urban Economics},
  year    = {2007},
  volume  = {61},
  number  = {1},
  pages   = {129--151}
}

@article{arnott1995rent,
  author  = {Arnott, Richard},
  title   = {Time for Revisionism on Rent Control?},
  journal = {Journal of Economic Perspectives},
  year    = {1995},
  volume  = {9},
  number  = {1},
  pages   = {99--120}
}

@article{garcia2018housing,
  author  = {García-Montalvo, José and Raya, Josep Maria},
  title   = {Constraints on Housing Affordability in Spain},
  journal = {Estudios sobre la Economía Española},
  year    = {2018}
}

@book{box2015timeseries,
  author    = {Box, George E.P. and Jenkins, Gwilym M. and Reinsel, Gregory C. and Ljung, Greta M.},
  title     = {Time Series Analysis: Forecasting and Control},
  edition   = {5th},
  publisher = {Wiley},
  year      = {2015}
}

@misc{ajuntament2025dades,
  author = {{Ajuntament de Barcelona}},
  title  = {Portal de Dades Obertes: Contractes de lloguer per districtes i barris},
  year   = {2025},
  url    = {https://opendata-ajuntament.barcelona.cat}
}
```

Añadir 3–5 referencias adicionales de la literatura española sobre acceso a la vivienda y mercado de alquiler (Bosch, Costa, Módenes, López-Colás) y sobre machine learning en mercados inmobiliarios.

---

## 4. INSTRUCCIONES LATEX ESPECÍFICAS

### 4.1 Paquetes recomendados

```latex
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,english]{babel}  % español principal, inglés para abstract EN
\usepackage{amsmath, amssymb}
\usepackage{booktabs}        % tablas profesionales: \toprule, \midrule, \bottomrule
\usepackage{graphicx}
\usepackage{subcaption}      % subfiguras
\usepackage{hyperref}
\usepackage{natbib}          % \citep{}, \citet{}
\usepackage{geometry}        % márgenes
\usepackage{float}           % [H] en figuras
\usepackage{threeparttable}  % notas al pie de tablas
\usepackage{lscape}          % tablas landscape si es necesario
\usepackage{color, xcolor}
\usepackage{microtype}       % tipografía mejorada
```

### 4.2 Ecuaciones LaTeX clave a incluir

**Estimador within (panel FE):**
```latex
\hat{\beta}_{WG} = \left(\sum_i \ddot{X}_i' \ddot{X}_i\right)^{-1} \sum_i \ddot{X}_i' \ddot{y}_i,
\quad \ddot{z}_{it} = z_{it} - \bar{z}_i
```

**SARIMAX:**
```latex
\phi(B)\,\Phi(B^4)\,(1-B)\,y_{d,t} = c_d + \theta(B)\,\Theta(B^4)\,\varepsilon_{d,t} + \gamma_d \cdot \text{euribor}_t
```

**ITS-3:**
```latex
y_t = \beta_0 + \beta_1 t + \sum_{k \in \{11, tc, 12\}} \left[\beta_{2k} D_{k,t} + \beta_{3k} t_{post_k,t}\right] + \beta_4 \text{covid}_t + \beta_5 \text{euribor}_t + \varepsilon_t
```

**HAC Newey-West:**
```latex
\hat{V}_{HAC} = (X'X)^{-1} \hat{\Omega}_{NW} (X'X)^{-1},
\quad \hat{\Omega}_{NW} = \sum_{l=-L}^{L} \left(1 - \frac{|l|}{L+1}\right) \hat{\Gamma}_l
```

**ADF:**
```latex
\Delta y_t = \mu + \gamma y_{t-1} + \sum_{j=1}^{p} \phi_j \Delta y_{t-j} + \varepsilon_t,
\quad H_0: \gamma = 0 \text{ (raíz unitaria)}
```

**Variable objetivo de clasificación:**
```latex
\text{market\_tension}_{it} = \mathbf{1}\!\left[\text{cg}_{it} < p_{25,i}^{(t \leq 2019)} \;\cap\; \text{cg}_{it} < -0.05\right]
```

### 4.3 Tablas LaTeX de referencia

**Ejemplo de tabla panel (booktabs):**
```latex
\begin{table}[htbp]
\caption{Comparativa de especificaciones del modelo de panel FE}
\label{tab:panel}
\centering
\begin{threeparttable}
\begin{tabular}{lccc}
\toprule
 & M1 Baseline & M2 Precio+Sup & M3 Completo \\
\midrule
\texttt{post\_regulation} & $-0.015$ & $0.136^{***}$ & $0.231^{***}$ \\
 & $(-1.89)$ & $(9.96)$ & $(15.71)$ \\
\texttt{covid\_dummy} & $0.204^{***}$ & $0.159^{***}$ & $0.040^{**}$ \\
\texttt{avg\_rent\_m2} & — & $-0.066^{***}$ & $-0.038^{***}$ \\
\texttt{euribor\_12m\_q} & — & — & $-0.076^{***}$ \\
\midrule
$R^2$ Within & 0.029 & 0.089 & 0.128 \\
Obs. & 2,838 & 2,838 & 2,838 \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small\item Nota: t-estadísticos entre paréntesis. SE clustered por barrio.
$^{***}p<0.01$, $^{**}p<0.05$, $^{*}p<0.10$.
\end{tablenotes}
\end{threeparttable}
\end{table}
```

**Ejemplo de tabla ITS-3:**
```latex
\begin{table}[htbp]
\caption{Resultados ITS-3 multi-ruptura — Barcelona ciudad (HAC NW, $L=4$)}
\label{tab:its3}
\centering
\begin{tabular}{lccc}
\toprule
Coeficiente & Precio nominal & Precio real 2025 & N contratos \\
\midrule
$D_{ley11}$ & $-1.112^{**}$ & $-0.041$ & $-233$ \\
$t_{post,ley11}$ & $-0.049$ & $-0.235^{***}$ & $-179$ \\
$D_{tc}$ & $-0.037$ & $-0.558^{**}$ & $-681$ \\
$t_{post,tc}$ & $-0.232$ & $-0.299^{**}$ & $-64$ \\
$D_{ley12}$ & $0.383^{\dagger}$ & $0.495^{*}$ & $-1588^{**}$ \\
$t_{post,ley12}$ & $0.360^{\dagger}$ & $0.630^{***}$ & $-89$ \\
$\text{euribor}$ & $0.654^{***}$ & $0.911^{***}$ & $-307^{***}$ \\
\midrule
$R^2$ & 0.904 & 0.513 & 0.918 \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small\item $^{***}p<0.01$, $^{**}p<0.05$, $^{*}p<0.10$, $^{\dagger}p<0.15$.
\end{tablenotes}
\end{table}
```

---

## 5. FIGURAS RECOMENDADAS (describir al LLM lo que debe incluir)

1. **Figura 1 — Serie temporal agregada Barcelona:** 3 paneles (precio nominal, precio real, contratos) con bandas de color por período regulatorio (P1 azul claro, P2 amarillo, P3 verde, P4 naranja, P5 lila). Colocar como `\begin{figure}[htbp]` en la sección de resultados EDA.

2. **Figura 2 — Heterogeneidad por distrito:** barplot de Δ renta real y Δ contratos por los 10 distritos.

3. **Figura 3 — Predicciones SARIMAX vs real (Eixample):** plot con bandas regulatorias, líneas de train/test, SARIMAX, ETS.

4. **Figura 4 — Proyección condicional ciudad:** precio nominal bajo 2 escenarios de Euríbor, últimos 5 años históricos + 8 trimestres de proyección, IC 90%.

5. **Figura 5 — Heatmap ITS-3 D_ley12:** heatmap 10 distritos × 3 métricas del level shift `D_ley12`.

6. **Figura 6 — Curvas ROC clasificadores:** subplot 1×3 con ROC curves para Logística, RF, GB sobre el test 2022+.

Para cada figura, usar caption descriptivo y `\label{fig:Xname}` para referencia cruzada.

---

## 6. ADVERTENCIAS PARA EL LLM REDACTOR

1. **No inventar resultados.** Usar únicamente los números de la sección 2 de este brief. Si falta algún número para una afirmación, indicarlo como `[TO FILL]`.

2. **El paper debe ser en español** (salvo el abstract en inglés). El tono es académico formal, primera persona del plural ("analizamos", "estimamos", "concluimos").

3. **Las tablas deben compilar en LaTeX.** Usar `booktabs` y `threeparttable`, no `hline` manual.

4. **Citar correctamente.** Todas las afirmaciones sobre la literatura deben ir con `\citep{}` o `\citet{}`. No hacer afirmaciones sin cita en la sección de trabajos relacionados.

5. **El abstract en inglés** debe usar terminología de econometría aplicada estándar: "within estimator", "clustered standard errors", "interrupted time series", "quasi-experimental design".

6. **Limitar los claims causales.** La limitación de identificación es conocida (no hay grupo de control válido). El paper debe reportar efectos como "asociaciones robustamente estimadas" en los módulos de panel y series temporales, reservando el lenguaje causal para el diseño ITS (que tiene mayor poder de identificación temporal).

7. **Estructura visual:** usar `\section`, `\subsection`, `\subsubsection`. El paper debe ser fluido: que el lector entienda sin leer el código fuente.

8. **Número total de tablas objetivo:** ~6 tablas principales + 2–3 en apéndice (sensibilidad, robustez, detalle por distrito).

9. **Número total de figuras objetivo:** 6 figuras en el cuerpo + 2–3 en apéndice.

10. **Apéndice:** incluir al final una sección A con la tabla de sensibilidad del umbral de tensión y la tabla de robustez ITS a distintos puntos de corte (usando los outputs de las celdas 117–121 del notebook). También incluir el cronograma de datos (tabla con rango temporal de cada variable fuente).
