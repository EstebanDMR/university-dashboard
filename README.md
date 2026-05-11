# University Student Analytics Dashboard

**Course:** Data Mining — Universidad de la Costa  
**Professor:** José Escorcia-Gutierrez, Ph.D.  
**Activity:** Activity I — Data Visualization and Dashboard Deployment

## Team members

- Esteban Mercado Rachath
- Iván Cortés Cure

## Purpose

Interactive analytical dashboard that visualizes student admission, enrollment,
retention, and satisfaction trends across academic years and departments, enabling
data-driven decision-making for university management.

## Dataset

`university_student_data.csv` — contains the following columns:

| Column | Description |
|---|---|
| Year | Academic year (2015–2024) |
| Term | Semester — Spring or Fall |
| Applications | Total applications received |
| Admitted | Students admitted |
| Enrolled | Students who enrolled |
| Retention Rate (%) | Percentage of students retained year-over-year |
| Student Satisfaction (%) | Average satisfaction score |
| Engineering Enrolled | Enrollment in Engineering department |
| Business Enrolled | Enrollment in Business department |
| Arts Enrolled | Enrollment in Arts department |
| Science Enrolled | Enrollment in Science department |

## Dashboard features

- **KPI cards** — avg retention, avg satisfaction, total enrolled, admission rate
- **Line chart** — retention rate trend over time
- **Bar chart** — student satisfaction by year
- **Grouped bar chart** — Spring vs Fall comparison
- **Pie/donut chart** — enrollment breakdown by department
- **Scatter plot** — retention vs satisfaction colored by year
- **Horizontal bar chart** — applications → admitted → enrolled funnel
- **Interactive filters** — year, term, department (sidebar)
- **Raw data viewer** — expandable table of the filtered dataset

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed on **Streamlit Cloud** directly from this repository.

Live URL: https://university-dashboard-nud6vkg7cqcjcu9izmhczt.streamlit.app/

## Repository structure

```text
├── app.py                         # Streamlit dashboard
├── requirements.txt              # Python dependencies
├── university_student_data.csv   # Dataset
├── activity1_data_visualization.ipynb
└── README.md                     # Project documentation
```

## Technologies Used

- Python
- Pandas
- Matplotlib
- Streamlit
- GitHub
- Streamlit Cloud
