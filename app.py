import streamlit as st 
import pandas as pd 
import matplotlib 
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import json
from pathlib import Path

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="University Student Analytics",
    page_icon="🎓",
    layout="wide",
)

# ─────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("university_student_data.csv")

df = load_data()

# ─────────────────────────────────────────────
# Sidebar — filters
# ─────────────────────────────────────────────
st.sidebar.title("Filters")

years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect(
    "Academic Year", years, default=years
)

terms = df["Term"].unique().tolist()
selected_terms = st.sidebar.multiselect(
    "Term", terms, default=terms
)

departments = ["Engineering", "Business", "Arts", "Science"]
selected_depts = st.sidebar.multiselect(
    "Department", departments, default=departments
)

# ─────────────────────────────────────────────
# Filtered dataset
# ─────────────────────────────────────────────
mask = df["Year"].isin(selected_years) & df["Term"].isin(selected_terms)
filtered = df[mask].copy()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("University Student Analytics Dashboard")
st.markdown(
    "Analytical overview of admissions, enrollment, retention, and satisfaction"
)
st.markdown("---")

# ─────────────────────────────────────────────
# KPI cards
# ─────────────────────────────────────────────
if not filtered.empty:
    avg_retention    = filtered["Retention Rate (%)"].mean()
    avg_satisfaction = filtered["Student Satisfaction (%)"].mean()
    total_enrolled   = filtered["Enrolled"].sum()
    total_apps       = filtered["Applications"].sum()
    admission_rate   = (filtered["Admitted"].sum() / total_apps * 100) if total_apps else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Avg Retention Rate",    f"{avg_retention:.1f}%")
    k2.metric("Avg Satisfaction",      f"{avg_satisfaction:.1f}%")
    k3.metric("Total Enrolled",        f"{total_enrolled:,}")
    k4.metric("Avg Admission Rate",    f"{admission_rate:.1f}%")
else:
    st.warning("No data matches the selected filters.")
    st.stop()

st.markdown("---")

# ─────────────────────────────────────────────
# Row 1 — Retention trend (line) + Satisfaction by year (bar)
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Retention Rate Trend Over Time")
    retention_by_year = (
        filtered.groupby("Year")["Retention Rate (%)"].mean().reset_index()
    )
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    ax1.plot(
        retention_by_year["Year"],
        retention_by_year["Retention Rate (%)"],
        marker="o", linewidth=2, color="#1f77b4"
    )
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Retention Rate (%)")
    ax1.set_ylim(80, 95)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    ax1.set_xticks(retention_by_year["Year"])
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

with col2:
    st.subheader("Student Satisfaction Score by Year")
    sat_by_year = (
        filtered.groupby("Year")["Student Satisfaction (%)"].mean().reset_index()
    )
    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    ax2.bar(
        sat_by_year["Year"],
        sat_by_year["Student Satisfaction (%)"],
        color="#2ca02c", alpha=0.85
    )
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Satisfaction (%)")
    ax2.set_ylim(70, 95)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    ax2.set_xticks(sat_by_year["Year"])
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

st.markdown("---")

# ─────────────────────────────────────────────
# Row 2 — Spring vs Fall comparison (grouped bar) + Dept breakdown (pie)
# ─────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Spring vs Fall — Key Metrics Comparison")
    term_comparison = (
        filtered.groupby("Term")[["Enrolled", "Retention Rate (%)", "Student Satisfaction (%)"]].mean()
    )
    spring = term_comparison.loc["Spring"] if "Spring" in term_comparison.index else None
    fall   = term_comparison.loc["Fall"]   if "Fall"   in term_comparison.index else None

    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(6, 3.5))

    # Left subplot — Enrolled (absolute values)
    enrolled_vals = [
        spring["Enrolled"] if spring is not None else 0,
        fall["Enrolled"]   if fall   is not None else 0,
    ]
    ax3a.bar(["Spring", "Fall"], enrolled_vals,
             color=["#1f77b4", "#ff7f0e"], alpha=0.85, width=0.5)
    ax3a.set_title("Avg Enrolled", fontsize=10)
    ax3a.set_ylabel("Students")
    ax3a.set_ylim(0, max(enrolled_vals) * 1.2 if max(enrolled_vals) > 0 else 1)
    for i, v in enumerate(enrolled_vals):
        ax3a.text(i, v + 5, f"{v:.0f}", ha="center", fontsize=9)
    ax3a.grid(axis="y", linestyle="--", alpha=0.5)

    # Right subplot — Retention & Satisfaction (same % scale)
    metrics = ["Retention (%)", "Satisfaction (%)"]
    spring_pct = [
        spring["Retention Rate (%)"]       if spring is not None else 0,
        spring["Student Satisfaction (%)"] if spring is not None else 0,
    ]
    fall_pct = [
        fall["Retention Rate (%)"]         if fall is not None else 0,
        fall["Student Satisfaction (%)"]   if fall is not None else 0,
    ]
    w = 0.3
    xi = range(len(metrics))
    ax3b.bar([i - w/2 for i in xi], spring_pct, w, label="Spring", color="#1f77b4", alpha=0.85)
    ax3b.bar([i + w/2 for i in xi], fall_pct,   w, label="Fall",   color="#ff7f0e", alpha=0.85)
    ax3b.set_xticks(list(xi))
    ax3b.set_xticklabels(metrics, fontsize=9)
    ax3b.set_title("Rates (%)", fontsize=10)
    ax3b.set_ylim(70, 95)
    ax3b.legend(fontsize=8)
    ax3b.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

with col4:
    st.subheader("Enrollment by Department (selected period)")
    dept_cols = {
        "Engineering": "Engineering Enrolled",
        "Business":    "Business Enrolled",
        "Arts":        "Arts Enrolled",
        "Science":     "Science Enrolled",
    }
    dept_totals = {
        dept: filtered[col].sum()
        for dept, col in dept_cols.items()
        if dept in selected_depts
    }
    if dept_totals:
        fig4, ax4 = plt.subplots(figsize=(5, 3.5))
        ax4.pie(
            dept_totals.values(),
            labels=dept_totals.keys(),
            autopct="%1.1f%%",
            startangle=140,
        )
        ax4.axis("equal")
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)
    else:
        st.info("Select at least one department to display this chart.")

st.markdown("---")

# ─────────────────────────────────────────────
# Row 3 — Retention vs Satisfaction scatter + Applications funnel
# ─────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Retention vs Satisfaction (by Year)")
    # Group by year to avoid overlapping Spring/Fall duplicate points
    scatter_data = (
        filtered.groupby("Year")[["Retention Rate (%)", "Student Satisfaction (%)"]].mean().reset_index()
    )
    fig5, ax5 = plt.subplots(figsize=(6, 3.5))
    sc = ax5.scatter(
        scatter_data["Retention Rate (%)"],
        scatter_data["Student Satisfaction (%)"],
        c=scatter_data["Year"],
        cmap="viridis",
        s=100,
        alpha=0.9,
        zorder=3,
    )
    for _, row in scatter_data.iterrows():
        ax5.annotate(
            str(int(row["Year"])),
            (row["Retention Rate (%)"], row["Student Satisfaction (%)"]),
            textcoords="offset points", xytext=(6, 4), fontsize=7.5,
        )
    plt.colorbar(sc, ax=ax5, label="Year")
    ax5.set_xlabel("Retention Rate (%)")
    ax5.set_ylabel("Satisfaction (%)")
    ax5.grid(linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

with col6:
    st.subheader("Applications → Admitted → Enrolled (avg)")
    funnel_data = {
        "Applications": filtered["Applications"].mean(),
        "Admitted":     filtered["Admitted"].mean(),
        "Enrolled":     filtered["Enrolled"].mean(),
    }
    fig6, ax6 = plt.subplots(figsize=(6, 3.5))
    colors = ["#4c72b0", "#55a868", "#c44e52"]
    bars = ax6.barh(
        list(funnel_data.keys()),
        list(funnel_data.values()),
        color=colors,
        alpha=0.85
    )
    for bar, val in zip(bars, funnel_data.values()):
        ax6.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                 f"{val:,.0f}", va="center", fontsize=10)
    ax6.set_xlabel("Average Count")
    ax6.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig6)
    plt.close(fig6)

st.markdown("---")

# ─────────────────────────────────────────────
# Raw data toggle
# ─────────────────────────────────────────────
with st.expander("View filtered raw data"):
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)


# This model uses a separate student-level dataset. The filters above apply only
# to the aggregated university dashboard, not to these held-out model results.
st.markdown("---")
st.header("Predicción de resultados estudiantiles")
st.caption(
    "Estudio independiente con 4.424 registros individuales de una institución "
    "portuguesa (UCI 697). Estos resultados no describen a la Universidad de la Costa "
    "y no cambian con los filtros del panel superior."
)

results_dir = Path(__file__).resolve().parent / "results"
metrics_path = results_dir / "model_metrics.json"
importance_path = results_dir / "permutation_importance.csv"
if metrics_path.exists() and importance_path.exists():
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    test = metrics["test"]
    baseline = metrics["baseline_test"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Recall de Dropout", f"{test['dropout_recall']:.1%}")
    c2.metric("F1 macro", f"{test['f1_macro']:.1%}")
    c3.metric("Estudiantes de prueba", f"{metrics['test_rows']:,}")
    st.caption(
        f"Referencia que siempre elige la clase más frecuente: F1 macro "
        f"{baseline['f1_macro']:.1%}; recall de Dropout {baseline['dropout_recall']:.1%}. "
        "Métricas calculadas sobre un conjunto de prueba separado (20%)."
    )

    labels = test["labels"]
    matrix = pd.DataFrame(test["confusion_matrix"], index=labels, columns=labels)
    left, right = st.columns(2)
    with left:
        st.subheader("Matriz de confusión")
        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(matrix.values, cmap="Blues")
        ax.set_xticks(range(len(labels)), labels=labels)
        ax.set_yticks(range(len(labels)), labels=labels)
        ax.set_xlabel("Predicción")
        ax.set_ylabel("Resultado real")
        for row in range(len(labels)):
            for col in range(len(labels)):
                ax.text(col, row, matrix.iat[row, col], ha="center", va="center")
        fig.colorbar(im, ax=ax, shrink=0.8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with right:
        st.subheader("Recall y F1 por resultado")
        class_scores = pd.DataFrame({
            name: {
                "Recall": test["classification_report"][name]["recall"],
                "F1": test["classification_report"][name]["f1-score"],
                "Soporte": test["classification_report"][name]["support"],
            }
            for name in labels
        }).T
        st.dataframe(class_scores.style.format({"Recall": "{:.1%}", "F1": "{:.1%}", "Soporte": "{:.0f}"}))

    st.subheader("Variables asociadas con el rendimiento del modelo")
    importance = pd.read_csv(importance_path).head(10)
    st.bar_chart(importance.set_index("feature")["importance_mean"], horizontal=True)
    st.caption(
        "Importancia por permutación: caída media del F1 macro al mezclar una variable "
        "en los datos de prueba. Indica asociación predictiva, no causalidad ni efecto "
        "de una intervención. Se excluyeron todas las variables del segundo semestre."
    )
    with st.expander("Método y límites"):
        st.markdown(
            "Bosque aleatorio con codificación de categorías y evaluación estratificada. "
            "La clase `Enrolled` aún no tiene un desenlace final; el conjunto no incluye "
            "cohortes ni identificadores para una validación temporal o institucional. "
            "No usar estas predicciones para decisiones individuales sin validación local, "
            "evaluación de sesgos y supervisión humana."
        )
else:
    st.info("Ejecute `python -m analysis.train_model` para generar los resultados del modelo.")
