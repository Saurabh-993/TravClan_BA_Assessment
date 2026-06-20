# 🌍 TravClan BA Assessment Solution

A professional, data-driven analytics project focused on hotel booking insights, cancellation analysis, and SQL-based reporting. This repository turns raw booking data into clear business recommendations through structured analysis, visualizations, and a normalized database design.

---

## 🎯 Project Purpose

TravClan’s dataset was analyzed to answer key business questions around:

- data quality and validation
- cancellation behavior and business risk
- realized revenue and booking performance
- scalable SQL schema design for analytics

The project is structured as a complete assessment solution with analysis, code, and supporting documentation.

---

## 🧩 What This Project Does

### 1. 📊 Data Quality Analysis

This section checks the integrity of the booking data and ensures the analysis follows the assessment footnotes correctly. It focuses on:

- invalid stays where checkout occurs on or before check-in
- review rating inconsistencies across customer segments
- realized revenue for luxury properties based on completed bookings only

### 2. 📈 Cancellation Crisis Investigation

This section explores why cancellations are high and which factors contribute most to the problem. It includes:

- cancellation rate analysis across cities and months
- comparisons between cancellation rate and total cancellation volume
- root-cause checks around lead time, booking channel, and city-season effects
- a business recommendation with expected impact and risk

### 3. 🗄️ SQL Challenge Solution

The project also includes a normalized database design for the booking dataset. It covers:

- customer, property, booking, and review table design
- constraints and validation rules
- analytical SQL queries using window functions such as RANK and LAG

---

## ⚙️ How It Works

1. Load the hotel booking dataset from the provided CSV file.
2. Apply cleaning and validation rules to handle data quality issues.
3. Analyze booking behavior through Python and pandas.
4. Create visualizations for cancellation patterns and business insights.
5. Design a relational schema and write SQL queries for reporting and analytics.

This workflow combines business analysis, data engineering, and decision support into one cohesive solution.

---

## 🛠️ Tech Stack

- Python 3.11+
- pandas for data manipulation
- matplotlib and seaborn for visualizations
- Jupyter Notebook for analysis workflow
- PostgreSQL for relational database design
- psycopg2 for database connectivity
- requests for API-related tasks

---

## 📁 Project Structure

```text
TravClan/
├── hotel_bookings.csv
├── roadmap.md
├── README.md
├── code/
│   ├── analysis.ipynb
│   ├── data_cleaning.py
│   └── schema.sql
├── project/
│   ├── weather_analyzer.py
│   ├── insight.md
│   └── ai_usage_note.md
└── answers/
    └── answers.pdf
```

---

## ✅ Key Deliverables

- a complete business analytics notebook
- actionable insight into booking cancellations
- SQL schema and query solutions
- a polished project structure suitable for assessment submission

---

## ▶️ How to Use

- Open the notebook in the code folder to explore the full analysis.
- Review the SQL implementation in the schema file.
- Check the project folder for supporting notes and additional outputs.

---

## 💡 Summary

This project demonstrates how raw booking data can be transformed into meaningful business decisions. It combines careful data validation, insightful visualization, and robust database design to provide a complete analytics story.
