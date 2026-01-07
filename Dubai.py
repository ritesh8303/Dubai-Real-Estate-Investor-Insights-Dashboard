import streamlit as st
import pandas as pd
from pathlib import Path
import base64

# ------------------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Dubai Investments", layout="wide")

# ------------------------------------------------------------------------------
# Background image (set your file name here)
# ------------------------------------------------------------------------------
BG_IMAGE = "dubai_bg.jpg"  # <- change to your own image file name

def set_background(image_path: str):
    img_file = Path(image_path)
    if not img_file.exists():
        return  # fail silently if image missing
    b64 = base64.b64encode(img_file.read_bytes()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{b64}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    /* add subtle dark overlay for readability */
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.60);
        pointer-events: none;
        z-index: -1;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background(BG_IMAGE)

# ------------------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("bayut_selling_properties.csv")
    df["listingdate"] = pd.to_datetime(df["listingdate"], errors="coerce")
    return df

df = load_data()

# ------------------------------------------------------------------------------
# Title and short subtitle
# ------------------------------------------------------------------------------
st.markdown(
    "<h1 style='color:white;'>Dubai Property Investment Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#cccccc;'>Filter Dubai listings and see key investor metrics at a glance.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# Sidebar – keep it simple
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

with st.sidebar.expander("Advanced filters", expanded=False):
    property_types = ["All"] + sorted(df["propertytype"].dropna().unique().tolist())
    ptype_choice = st.selectbox("Property type", property_types)

    furnishing_options = ["All"] + sorted(df["furnishing"].dropna().unique().tolist())
    furnishing_choice = st.selectbox("Furnishing", furnishing_options)

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
# Top KPIs (clean, centered)
# ------------------------------------------------------------------------------
st.markdown("### Summary")

kpi_cols = st.columns(3)

listings_count = int(len(fdf))
median_price = int(fdf["priceaed"].median()) if listings_count else 0
median_pps = float(round(fdf["pricepersqft"].median(), 1)) if listings_count else 0.0

with kpi_cols[0]:
    st.metric("Listings", f"{listings_count:,}")
with kpi_cols[1]:
    st.metric("Median price (AED)", f"{median_price:,}")
with kpi_cols[2]:
    st.metric("Median price / sqft (AED)", f"{median_pps:,.1f}")

# ------------------------------------------------------------------------------
# Main layout: chart + small table
# ------------------------------------------------------------------------------
left, right = st.columns([1.1, 1])

# Chart: simple histogram of price per sqft
with left:
    st.markdown("### Price per sqft (trimmed at 99th percentile)")
    if listings_count:
        trimmed = fdf["pricepersqft"].clip(
            upper=fdf["pricepersqft"].quantile(0.99)
        )
        st.bar_chart(trimmed.reset_index(drop=True))
    else:
        st.info("No data for current filter selection.")

# Table: small, renamed columns
with right:
    st.markdown("### Sample listings (first 50 rows)")
    sample_cols = [
        "priceaed", "pricepersqft", "sizesqft",
        "bedrooms", "bathrooms", "community",
        "propertytype", "furnishing", "listingdate",
    ]

    if listings_count:
        display = (
            fdf.sort_values("priceaed")
               .head(50)[sample_cols]
               .rename(columns={
                   "priceaed": "Price (AED)",
                   "pricepersqft": "Price / sqft (AED)",
                   "sizesqft": "Size (sqft)",
                   "bedrooms": "Beds",
                   "bathrooms": "Baths",
                   "community": "Community",
                   "propertytype": "Type",
                   "furnishing": "Furnishing",
                   "listingdate": "Listing date",
               })
        )
        st.dataframe(display, use_container_width=True, height=450)
    else:
        st.info("No listings to show.")
