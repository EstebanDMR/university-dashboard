import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

# Team credits in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**Team members**")
st.sidebar.markdown(
    "- Esteban Mercado Rachath  \n"
    "- Iván Cortés Cure"
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
    "Analytical overview of admissions, enrollment, retention, and satisfaction — "
    "Universidad de la Costa · Data Mining · Prof. José Escorcia-Gutierrez"
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
    st.subheader("Spring vs Fall — Enrollment Comparison")
    term_comparison = (
        filtered.groupby("Term")[["Enrolled", "Retention Rate (%)", "Student Satisfaction (%)"]].mean()
    )
    fig3, ax3 = plt.subplots(figsize=(6, 3.5))
    x = range(len(term_comparison.columns))
    width = 0.3
    spring_vals = term_comparison.loc["Spring"].values if "Spring" in term_comparison.index else [0,0,0]
    fall_vals   = term_comparison.loc["Fall"].values   if "Fall"   in term_comparison.index else [0,0,0]
    ax3.bar([i - width/2 for i in x], spring_vals, width, label="Spring", color="#1f77b4", alpha=0.85)
    ax3.bar([i + width/2 for i in x], fall_vals,   width, label="Fall",   color="#ff7f0e", alpha=0.85)
    ax3.set_xticks(list(x))
    ax3.set_xticklabels(["Enrolled", "Retention (%)", "Satisfaction (%)"])
    ax3.legend()
    ax3.grid(axis="y", linestyle="--", alpha=0.5)
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
    fig5, ax5 = plt.subplots(figsize=(6, 3.5))
    scatter = ax5.scatter(
        filtered["Retention Rate (%)"],
        filtered["Student Satisfaction (%)"],
        c=filtered["Year"],
        cmap="viridis",
        s=80,
        alpha=0.85
    )
    plt.colorbar(scatter, ax=ax5, label="Year")
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
