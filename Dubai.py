import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dubai Real Estate – Investor Dashboard",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# ---------- DATA LOADING & PREP ----------

@st.cache_data
def load_data():
    df_raw = pd.read_csv("bayut_selling_properties.csv")

    df = df_raw.copy()
    df.columns = [
        "price_aed",          # price
        "price_segment",      # pricecategory
        "property_type",      # type
        "bedrooms",           # beds
        "bathrooms",          # baths
        "full_location",      # address
        "furnishing",         # furnishing
        "construction_status",# completionstatus
        "listing_date",       # postdate
        "average_rent",       # averagerent
        "project_name",       # buildingname
        "year_of_completion", # yearofcompletion
        "total_parking_spaces",# totalparkingspaces
        "total_floors",       # totalfloors
        "size_sqft",          # totalbuildingareasqft
        "elevators",          # elevators
        "community",          # areaname
        "city",               # city
        "country",            # country
        "latitude",           # Latitude
        "longitude",          # Longitude
        "listing_purpose",    # purpose
    ]

    # Only Dubai
    df = df[df["city"] == "Dubai"].copy()

    # Parse date
    df["listing_date"] = pd.to_datetime(df["listing_date"], format="%d-%m-%Y", errors="coerce")

    # Numeric columns
    num_cols = [
        "price_aed", "bedrooms", "bathrooms", "average_rent",
        "year_of_completion", "total_parking_spaces", "total_floors",
        "size_sqft", "elevators", "latitude", "longitude"
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filter bad rows
    df = df[(df["price_aed"] > 0) & (df["size_sqft"] > 0)]

    # Investor features
    df["price_per_sqft"] = df["price_aed"] / df["size_sqft"]
    df["year"] = df["listing_date"].dt.year
    df["month"] = df["listing_date"].dt.to_period("M")

    bins = [0, 1_000_000, 2_000_000, 3_000_000, 5_000_000, 10_000_000, np.inf]
    labels = ["<1M", "1–2M", "2–3M", "3–5M", "5–10M", "10M+"]
    df["price_band"] = pd.cut(df["price_aed"], bins=bins, labels=labels, include_lowest=True)

    return df

df = load_data()

# ---------- HEADER ----------

st.title("Dubai Real Estate – Investor Dashboard")
st.caption("Exploring Dubai sale listings by price, community, and investor segments.")

# ---------- SIDEBAR FILTERS ----------

with st.sidebar:
    st.header("Filters")

    years = sorted(df["year"].dropna().unique())
    selected_years = st.multiselect(
        "Year",
        options=years,
        default=years,
    )

    top_communities = df["community"].value_counts().head(20).index.tolist()
    selected_communities = st.multiselect(
        "Community (top 20 by count)",
        options=top_communities,
        default=top_communities,
    )

    property_types = sorted(df["property_type"].dropna().unique())
    selected_types = st.multiselect(
        "Property type",
        options=property_types,
        default=property_types,
    )

    status_options = sorted(df["construction_status"].dropna().unique())
    selected_status = st.multiselect(
        "Construction status",
        options=status_options,
        default=status_options,
    )

    plot_choice = st.selectbox(
        "Select plot",
        [
            "Price distribution",
            "Top communities by price per sqft",
            "Off-plan vs ready (price per sqft)",
            "Furnished vs unfurnished",
            "Monthly trend in price per sqft",
            "Size vs price per sqft",
            "Price bands by community (top 8)",
            "Bedrooms vs price per sqft",
            "Correlation heatmap",
        ]
    )

# ---------- APPLY FILTERS ----------

filtered = df.copy()
if selected_years:
    filtered = filtered[filtered["year"].isin(selected_years)]

if selected_communities:
    filtered = filtered[filtered["community"].isin(selected_communities)]

if selected_types:
    filtered = filtered[filtered["property_type"].isin(selected_types)]

if selected_status:
    filtered = filtered[filtered["construction_status"].isin(selected_status)]

st.markdown(f"**Filtered rows:** {len(filtered):,} (out of {len(df):,})")

# ---------- PLOTS ----------

if len(filtered) == 0:
    st.warning("No data for the current filter combination.")
    st.stop()

if plot_choice == "Price distribution":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribution of listing prices (AED)")
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(filtered["price_aed"], bins=40, ax=ax)
        ax.set_xlabel("Price (AED)")
        ax.set_xlim(0, filtered["price_aed"].quantile(0.99))
        st.pyplot(fig)

    with col2:
        st.subheader("Price by property type (Dubai)")
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.boxplot(
            data=filtered,
            x="property_type",
            y="price_aed",
            showfliers=False,
            ax=ax,
        )
        ax.set_xlabel("Property type")
        ax.set_ylabel("Price (AED)")
        ax.set_ylim(0, filtered["price_aed"].quantile(0.99))
        plt.xticks(rotation=30)
        st.pyplot(fig)

elif plot_choice == "Top communities by price per sqft":
    st.subheader("Top communities by median price per sqft")
    community_stats = (
        filtered.groupby("community")
        .agg(
            median_price_per_sqft=("price_per_sqft", "median"),
            count=("price_aed", "size"),
        )
        .reset_index()
    )
    top = (
        community_stats[community_stats["count"] >= 30]
        .sort_values("median_price_per_sqft", ascending=False)
        .head(20)
    )

    if top.empty:
        st.info("Not enough data per community after filtering.")
    else:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(
            data=top,
            y="community",
            x="median_price_per_sqft",
            ax=ax,
        )
        ax.set_xlabel("Median price per sqft (AED)")
        ax.set_ylabel("Community")
        st.pyplot(fig)

elif plot_choice == "Off-plan vs ready (price per sqft)":
    st.subheader("Price per sqft: Off-plan vs Ready")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=filtered,
        x="construction_status",
        y="price_per_sqft",
        showfliers=False,
        ax=ax,
    )
    ax.set_xlabel("Construction status")
    ax.set_ylabel("Price per sqft (AED)")
    ax.set_ylim(0, filtered["price_per_sqft"].quantile(0.99))
    st.pyplot(fig)

elif plot_choice == "Furnished vs unfurnished":
    st.subheader("Price per sqft: Furnished vs Unfurnished")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=filtered,
        x="furnishing",
        y="price_per_sqft",
        showfliers=False,
        ax=ax,
    )
    ax.set_xlabel("Furnishing")
    ax.set_ylabel("Price per sqft (AED)")
    ax.set_ylim(0, filtered["price_per_sqft"].quantile(0.99))
    st.pyplot(fig)

elif plot_choice == "Monthly trend in price per sqft":
    st.subheader("Average price per sqft over time")
    monthly = (
        filtered.groupby("month")
        .agg(avg_price_per_sqft=("price_per_sqft", "mean"))
        .reset_index()
    )
    monthly["month_str"] = monthly["month"].astype(str)

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(
        data=monthly,
        x="month_str",
        y="avg_price_per_sqft",
        marker="o",
        ax=ax,
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg price per sqft (AED)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

elif plot_choice == "Size vs price per sqft":
    st.subheader("Size vs price per sqft (sample up to 5,000)")
    sample = filtered.sample(min(5000, len(filtered)), random_state=42)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=sample,
        x="size_sqft",
        y="price_per_sqft",
        hue="property_type",
        alpha=0.4,
        ax=ax,
    )
    ax.set_xlim(0, filtered["size_sqft"].quantile(0.99))
    ax.set_ylim(0, filtered["price_per_sqft"].quantile(0.99))
    ax.set_xlabel("Size (sqft)")
    ax.set_ylabel("Price per sqft (AED)")
    plt.legend(title="Property type", bbox_to_anchor=(1.05, 1), loc="upper left")
    st.pyplot(fig)

elif plot_choice == "Price bands by community (top 8)":
    st.subheader("Price band distribution in top 8 communities")
    top8 = filtered["community"].value_counts().head(8).index
    band_stats = (
        filtered[filtered["community"].isin(top8)]
        .groupby(["community", "price_band"])
        .size()
        .reset_index(name="count")
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=band_stats,
        x="price_band",
        y="count",
        hue="community",
        ax=ax,
    )
    ax.set_xlabel("Price band (AED)")
    ax.set_ylabel("Number of listings")
    plt.legend(title="Community", bbox_to_anchor=(1.05, 1), loc="upper left")
    st.pyplot(fig)

elif plot_choice == "Bedrooms vs price per sqft":
    st.subheader("Price per sqft by bedroom count")
    beds_focus = filtered[filtered["bedrooms"].between(0, 5)]

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=beds_focus,
        x="bedrooms",
        y="price_per_sqft",
        showfliers=False,
        ax=ax,
    )
    ax.set_xlabel("Bedrooms")
    ax.set_ylabel("Price per sqft (AED)")
    ax.set_ylim(0, beds_focus["price_per_sqft"].quantile(0.99))
    st.pyplot(fig)

elif plot_choice == "Correlation heatmap":
    st.subheader("Correlation of investor variables")
    corr_cols = [
        "price_aed",
        "price_per_sqft",
        "bedrooms",
        "bathrooms",
        "size_sqft",
        "average_rent",
        "total_parking_spaces",
        "total_floors",
    ]
    corr_cols = [c for c in corr_cols if c in filtered.columns]
    corr = filtered[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=ax,
    )
    st.pyplot(fig)
