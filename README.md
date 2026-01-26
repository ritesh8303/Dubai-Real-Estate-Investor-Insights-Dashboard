# Dubai Apartment Investment Explorer

This repository contains an end‑to‑end data analysis and visualization project exploring the Dubai rental apartment market from an **investor’s perspective**.  
Using the public *“Dubai Real Estate Goldmine, UAE Rental Market Data”* dataset, the project identifies communities where apartments provide **relatively low entry cost** and **strong rental income per square meter**.

---

## Project Objectives

- Clean and prepare a real‑world real estate dataset for analysis.
- Explore Dubai apartment rentals using **Pandas** and **exploratory data analysis (EDA)**.
- Engineer investor‑focused metrics such as:
  - Annual rent  
  - Size in square meters  
  - Rent per square meter per year
- Compare **communities and bedroom types** (Studio, 1BR, 2BR, 3+) to find:
  - Areas with **lower rent per sqm** (more space for less money)
  - Areas with **higher rent per sqm** (premium locations)
- Build visualizations with **Matplotlib/Seaborn** and **Plotly**.
- Prepare data for an interactive **Streamlit dashboard** for property‑investment exploration.

---

## Repository Structure

```text
.
├── data/
│   ├── dubai_raw.csv                 # Original dataset (not committed if large)
│   ├── dubai_clean_listings.csv      # Cleaned listing‑level data
│   └── dubai_agg_communities.csv     # Aggregated metrics by community & bedroom type
├── notebooks/
│   └── dubai_investor_eda.ipynb      # Main analysis notebook (Pandas + EDA + plots)
├── app/
│   └── app.py                        # Streamlit dashboard (optional / WIP)
├── images/
│   └── *.png                         # Exported charts / screenshots for README
├── README.md
└── requirements.txt
