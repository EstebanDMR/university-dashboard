"""Explore individual student outcomes and review a reproducible classifier."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


ROOT = Path(__file__).resolve().parent
CLASSES = ["Dropout", "Enrolled", "Graduate"]
OUTCOMES = {"Dropout": "Deserción", "Enrolled": "En curso", "Graduate": "Graduación"}
APPROVED = "Curricular units 1st sem (approved)"

st.set_page_config(page_title="Student Outcome Analytics", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "student_dropout_uci.csv")


df = load_data()
st.title("Student Outcome Analytics")
st.markdown("Exploración de resultados estudiantiles y evaluación de un modelo de deserción.")
st.caption("Fuente: UCI 697. Registros individuales de una institución portuguesa.")

st.sidebar.header("Explorar estudiantes")
selected_outcomes = st.sidebar.multiselect(
    "Resultado observado", CLASSES, default=CLASSES, format_func=OUTCOMES.get,
)
age_range = st.sidebar.slider(
    "Edad al ingresar", int(df["Age at enrollment"].min()),
    int(df["Age at enrollment"].max()),
    (int(df["Age at enrollment"].min()), int(df["Age at enrollment"].max())),
)
scholarship = st.sidebar.selectbox("Beca", ["Todos", "Con beca", "Sin beca"])
mask = df["Target"].isin(selected_outcomes) & df["Age at enrollment"].between(*age_range)
if scholarship != "Todos":
    mask &= df["Scholarship holder"].eq(int(scholarship == "Con beca"))
filtered = df.loc[mask].copy()
st.sidebar.caption("Los filtros se aplican a Exploración y Datos. La evaluación del modelo usa su conjunto de prueba completo.")

exploration_tab, model_tab, data_tab = st.tabs(["Exploración", "Evaluación del modelo", "Datos y fuente"])

with exploration_tab:
    st.subheader("Resultados observados")
    if filtered.empty:
        st.info("No hay estudiantes con esta selección. Amplíe los filtros para explorar los datos.")
    else:
        first, second, third = st.columns(3)
        first.metric("Registros seleccionados", f"{len(filtered):,}")
        second.metric("Deserción observada", f"{filtered['Target'].eq('Dropout').mean():.1%}")
        third.metric("Edad mediana al ingresar", f"{filtered['Age at enrollment'].median():.0f} años")
        st.caption("La proporción de deserción describe la selección actual. Filtrar por resultado cambia esa proporción.")
        counts = filtered["Target"].value_counts().reindex(CLASSES, fill_value=0)
        st.bar_chart(counts.rename(index=OUTCOMES).rename("Estudiantes"))

        st.subheader("Desempeño en el primer semestre")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.boxplot(
            data=filtered.assign(Resultado=filtered["Target"].map(OUTCOMES)),
            x="Resultado", y=APPROVED, order=list(OUTCOMES.values()),
            color="#8eb9ad", ax=ax,
        )
        ax.set_xlabel("Resultado observado")
        ax.set_ylabel("Unidades curriculares aprobadas")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption("La distribución muestra asociaciones entre desempeño y resultado. No identifica causas de deserción.")

with model_tab:
    st.subheader("Clasificación de resultados estudiantiles")
    metrics_path = ROOT / "results" / "model_metrics.json"
    importance_path = ROOT / "results" / "permutation_importance.csv"
    if not (metrics_path.exists() and importance_path.exists()):
        st.info("Los resultados aún no están disponibles. Consulte la sección de reproducción del README.")
    else:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        test = metrics["test"]
        baseline = metrics["baseline_test"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Recall de deserción", f"{test['dropout_recall']:.1%}")
        c2.metric("F1 macro", f"{test['f1_macro']:.1%}")
        c3.metric("Estudiantes de prueba", f"{metrics['test_rows']:,}")
        st.caption(
            f"Referencia que siempre elige la clase más frecuente: F1 macro "
            f"{baseline['f1_macro']:.1%}; recall de deserción {baseline['dropout_recall']:.1%}. "
            "Evaluación sobre un conjunto de prueba separado (20%)."
        )
        labels = test["labels"]
        matrix = pd.DataFrame(test["confusion_matrix"], index=labels, columns=labels)
        left, right = st.columns(2)
        with left:
            st.subheader("Matriz de confusión")
            fig, ax = plt.subplots(figsize=(5, 4))
            im = ax.imshow(matrix.values, cmap="Blues")
            translated = [OUTCOMES[label] for label in labels]
            ax.set_xticks(range(len(labels)), labels=translated)
            ax.set_yticks(range(len(labels)), labels=translated)
            ax.set_xlabel("Predicción")
            ax.set_ylabel("Resultado real")
            for row in range(len(labels)):
                for col in range(len(labels)):
                    ax.text(
                        col, row, matrix.iat[row, col], ha="center", va="center",
                        color="white" if matrix.iat[row, col] > matrix.values.max() / 2 else "black",
                    )
            fig.colorbar(im, ax=ax, shrink=0.8)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        with right:
            st.subheader("Métricas por resultado")
            class_scores = pd.DataFrame({
                OUTCOMES[name]: {
                    "Recall": test["classification_report"][name]["recall"],
                    "F1": test["classification_report"][name]["f1-score"],
                    "Soporte": test["classification_report"][name]["support"],
                }
                for name in labels
            }).T
            st.dataframe(class_scores.style.format({"Recall": "{:.1%}", "F1": "{:.1%}", "Soporte": "{:.0f}"}))

        st.subheader("Variables asociadas al rendimiento del modelo")
        importance = pd.read_csv(importance_path).head(10)
        st.bar_chart(importance.set_index("feature")["importance_mean"], horizontal=True)
        st.caption(
            "Importancia por permutación: caída media del F1 macro al mezclar una variable "
            "en los datos de prueba. Indica asociación predictiva, no causalidad. "
            "Se excluyeron las variables del segundo semestre y las macroeconómicas."
        )
        with st.expander("Método y límites"):
            st.markdown(
                "Bosque aleatorio con categorías codificadas y validación cruzada "
                "en entrenamiento. Las variables del primer semestre pueden reflejar "
                "una deserción ya iniciada. `Enrolled` aún no tiene un desenlace final. "
                "El conjunto no permite validación temporal ni garantiza rendimiento "
                "en otra institución. Las decisiones individuales requieren validación "
                "local, evaluación de sesgos y supervisión humana."
            )

with data_tab:
    st.subheader("Datos individuales")
    st.markdown(
        "[Predict Students' Dropout and Academic Success — UCI 697]"
        "(https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success). "
        f"El archivo completo contiene {len(df):,} registros y {df.shape[1] - 1} variables, "
        "más el resultado `Target`. Los códigos y nombres de columnas se conservan como en la fuente."
    )
    st.markdown(
        "Realinho, V., Vieira Martins, M., Machado, J., & Baptista, L. (2021). "
        "[DOI: 10.24432/C5MC89](https://doi.org/10.24432/C5MC89). "
        "Licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)."
    )
    st.caption(f"Vista filtrada: {len(filtered):,} registros. En curso corresponde a la clase Enrolled.")
    st.dataframe(filtered.reset_index(drop=True))
    st.download_button(
        "Descargar selección en CSV", filtered.to_csv(index=False).encode("utf-8"),
        file_name="student_outcomes_filtered.csv", mime="text/csv",
    )
