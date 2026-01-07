import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Dubai Investments", layout="wide")

# ------------------------------------------------------------------------------
# Load data (light, preprocessed CSV)
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    # IMPORTANT: this CSV must be the 6909 x 13 light file
    df = pd.read_csv("bayut_selling_properties.csv")
    df["listingdate"] = pd.to_datetime(df["listingdate"], errors="coerce")
    return df

df = load_data()

# ------------------------------------------------------------------------------
# App title
# ------------------------------------------------------------------------------
st.title("Dubai Property Investment Dashboard")

# ------------------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------------------
st.sidebar.header("Filters")

min_price = int(df["priceaed"].min())
max_price = int(df["priceaed"].max())

price_range = st.sidebar.slider(
    "Price range (AED)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=50_000,
)

communities = ["All"] + sorted(df["community"].dropna().unique().tolist())
community_choice = st.sidebar.selectbox("Community", communities)

property_types = ["All"] + sorted(df["propertytype"].dropna().unique().tolist())
ptype_choice = st.sidebar.selectbox("Property type", property_types)

furnishing_options = ["All"] + sorted(df["furnishing"].dropna().unique().tolist())
furnishing_choice = st.sidebar.selectbox("Furnishing", furnishing_options)

# ------------------------------------------------------------------------------
# Apply filters
# ------------------------------------------------------------------------------
mask = df["priceaed"].between(price_range[0], price_range[1])

if community_choice != "All":
    mask &= df["community"] == community_choice

if ptype_choice != "All":
    mask &= df["propertytype"] == ptype_choice

if furnishing_choice != "All":
    mask &= df["furnishing"] == furnishing_choice

fdf = df[mask]

# ------------------------------------------------------------------------------
# Summary metrics
# ------------------------------------------------------------------------------
st.subheader("Summary")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Listings", int(len(fdf)))
with col2:
    st.metric(
        "Median price (AED)",
        int(fdf["priceaed"].median()) if len(fdf) else 0,
    )
with col3:
    st.metric(
        "Median price / sqft (AED)",
        float(round(fdf["pricepersqft"].median(), 1)) if len(fdf) else 0.0,
    )

# ------------------------------------------------------------------------------
# Sample table (limit rows for speed)
# ------------------------------------------------------------------------------
st.subheader("Sample listings (first 200 rows)")

sample_cols = [
    "priceaed", "pricepersqft", "sizesqft", "bedrooms",
    "bathrooms", "community", "propertytype",
    "furnishing", "listingdate",
]

if len(fdf):
    st.dataframe(
        fdf.sort_values("priceaed").head(200)[sample_cols],
        use_container_width=True,
    )
else:
    st.info("No listings for current filter selection.")

# ------------------------------------------------------------------------------
# Simple chart
# ------------------------------------------------------------------------------
st.subheader("Price per sqft (trimmed at 99th percentile)")

if len(fdf):
    trimmed = fdf["pricepersqft"].clip(
        upper=fdf["pricepersqft"].quantile(0.99)
    )
    st.line_chart(trimmed.reset_index(drop=True))
else:
    st.info("No data to plot for current filters.")
