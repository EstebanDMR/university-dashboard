# Student Outcome Analytics

Proyecto de análisis de datos y aprendizaje automático para explorar los
resultados de estudiantes y evaluar un clasificador de deserción, continuidad
y graduación. Incluye análisis reproducible en Python y un dashboard en Streamlit.

## Datos

Se utiliza un único conjunto: [Predict Students' Dropout and Academic Success,
UCI 697](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success).
Cada fila representa un estudiante de una institución portuguesa.

| Característica | Valor |
|---|---|
| Registros | 4.424 |
| Variables de entrada disponibles | 36 |
| Variable objetivo | `Target` |
| `Dropout` (deserción) | 1.421 |
| `Enrolled` (en curso) | 794 |
| `Graduate` (graduación) | 2.209 |
| Valores faltantes | 0 |
| Filas exactamente duplicadas | 0 |

El archivo `data/student_dropout_uci.csv` conserva los nombres y códigos
originales. Consulte el diccionario de variables en UCI para interpretarlos.
Su SHA-256 es
`a1b1a6531bbb93a5c7fdf0093b47172776652a4ffb12342fb79655c85b74801b`.

**Atribución:** Realinho, V., Vieira Martins, M., Machado, J., & Baptista, L.
(2021). *Predict Students' Dropout and Academic Success*. UCI Machine Learning
Repository. [DOI: 10.24432/C5MC89](https://doi.org/10.24432/C5MC89).
Licencia de los datos: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Proceso

1. El notebook `student_dropout_analysis.ipynb` inspecciona tipos, valores
   faltantes y duplicados con Pandas y explora distribuciones con Seaborn.
2. El modelo usa 27 variables de ingreso y del primer semestre. Se excluyen
   las seis variables del segundo semestre y las tres macroeconómicas.
3. Una separación estratificada reserva 20% para prueba (semilla 42).
   La imputación y codificación de categorías se ajustan dentro del pipeline.
4. Un bosque aleatorio se evalúa con cinco pliegues de validación cruzada
   sobre entrenamiento y después sobre el conjunto de prueba separado.
   Se compara con una referencia que siempre predice la clase mayoritaria.
5. La importancia por permutación mide la caída de F1 macro al mezclar cada
   variable original en prueba. Las métricas y sus versiones de dependencias
   se guardan en `results/`.

## Resultados

| Métrica en prueba | Bosque aleatorio | Referencia |
|---|---:|---:|
| F1 macro | 0,663 | 0,222 |
| Recall de deserción | 0,701 | 0,000 |

El conjunto de prueba tiene 885 estudiantes. El modelo identifica 199 de
284 casos de deserción y omite 85. La clase `Enrolled` tiene F1 de 0,448.
La validación cruzada en entrenamiento obtiene F1 macro de 0,679 ± 0,027
(media ± desviación estándar). El informe por clase y la matriz de confusión
están en `results/model_metrics.json`.

## Dashboard

- **Exploración:** distribución de resultados y unidades aprobadas durante
  el primer semestre. Filtros por resultado observado, edad y beca.
- **Evaluación del modelo:** recall, F1, matriz de confusión e importancia
  de variables sobre el conjunto de prueba completo.
- **Datos y fuente:** tabla filtrada, descarga CSV, atribución y licencia.

Los filtros afectan a la exploración y la tabla. Las métricas del modelo
se leen de los resultados guardados y no se recalculan al filtrar.

## Ejecución local

Requiere Python 3.11 o superior.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para regenerar las métricas:

```bash
python -m analysis.train_model
```

Para ejecutar el notebook, instale `requirements-notebook.txt` y ábralo con
Jupyter desde la raíz del repositorio:

```bash
pip install -r requirements-notebook.txt
jupyter lab student_dropout_analysis.ipynb
```

La app está configurada para Streamlit Cloud con `app.py` como entrada.
[Abrir dashboard](https://university-dashboard-nud6vkg7cqcjcu9izmhczt.streamlit.app/).

## Limitaciones

- `Enrolled` es un estado sin desenlace final. Su interpretación difiere
  de las clases de graduación y deserción.
- Las medidas del primer semestre no están disponibles al ingresar y
  pueden reflejar una deserción ya iniciada. La evaluación es retrospectiva.
- No hay cohortes ni años por estudiante que permitan validación temporal.
  Una separación aleatoria puede sobreestimar el rendimiento futuro.
- Los datos proceden de una sola institución portuguesa. Las métricas
  no garantizan resultados en otra institución.
- La importancia predictiva no demuestra causalidad. El modelo incluye
  variables demográficas y no cuenta con una evaluación de equidad.
  Su uso en decisiones individuales requiere validación local y supervisión humana.

## Estructura

```text
├── app.py
├── student_dropout_analysis.ipynb
├── analysis/
│   ├── __init__.py
│   └── train_model.py
├── data/
│   └── student_dropout_uci.csv
├── results/
│   ├── model_metrics.json
│   └── permutation_importance.csv
├── requirements.txt
├── requirements-notebook.txt
└── .devcontainer/devcontainer.json
```
