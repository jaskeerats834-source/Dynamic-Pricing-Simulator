import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import datetime
from streamlit_autorefresh import st_autorefresh

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dynamic Pricing Dashboard", layout="wide")

# ------------------ AUTO REFRESH ------------------
st_autorefresh(interval=5000, limit=None, key="refresh")

# ------------------ CUSTOM STYLE ------------------
st.markdown("""
<style>
.block-container {padding-top: 2rem;}
[data-testid="stMetric"] {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.title("🚀 Dynamic Pricing Dashboard")
st.caption("Real-Time Retail Decision Support System")

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Controls")

# ------------------ FILE INPUT ------------------
file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_default():
    return pd.read_csv("default_dataset.csv")

if file is not None:
    df = pd.read_csv(file)
    st.success("Custom dataset loaded ✅")
else:
    df = load_default()
    st.info("Using default dataset")

# ------------------ LOADING SPINNER ------------------
with st.spinner("Processing data..."):
    
    # REAL-TIME SIMULATION
    df['Demand'] = df['Demand'].apply(lambda x: max(0, x + random.randint(-5, 5)))
    df['Stock'] = df['Stock'].apply(lambda x: max(0, x + random.randint(-10, 10)))
    df['Last_Updated'] = datetime.datetime.now()

    # DYNAMIC PRICE
    def calc(row):
        price = row['Base_Price']
        if row['Demand'] > 80: price *= 1.2
        elif row['Demand'] < 50: price *= 0.9
        if row['Stock'] > 150: price *= 0.85
        elif row['Stock'] < 50: price *= 1.15
        price *= (1 + (row['Rating'] - 4) * 0.05)
        if row['Season'] == "Winter": price *= 1.1
        elif row['Season'] == "Summer": price *= 1.05
        return round(price, 2)

    df['Dynamic_Price'] = df.apply(calc, axis=1)

    # PROFIT
    df['Profit'] = df['Dynamic_Price'] - df['Base_Price']

    # RECOMMENDATION
    def recommend(row):
        if row['Demand'] > 80 and row['Stock'] < 50:
            return "Increase Price"
        elif row['Demand'] < 40:
            return "Decrease Price"
        else:
            return "Keep Same"

    df['Recommendation'] = df.apply(recommend, axis=1)

# ------------------ FILTERS ------------------
search = st.sidebar.text_input("Search Product")
top_n = st.sidebar.slider("Top N", 5, 50, 10)
season = st.sidebar.selectbox("Season", ["All"] + list(df['Season'].unique()))

price_range = st.sidebar.slider(
    "Price Range",
    int(df['Dynamic_Price'].min()),
    int(df['Dynamic_Price'].max()),
    (int(df['Dynamic_Price'].min()), int(df['Dynamic_Price'].max()))
)

filtered = df.copy()

if search:
    filtered = filtered[filtered['Product_Name'].str.contains(search, case=False)]

if season != "All":
    filtered = filtered[filtered['Season'] == season]

filtered = filtered[
    (filtered['Dynamic_Price'] >= price_range[0]) &
    (filtered['Dynamic_Price'] <= price_range[1])
]

# ------------------ KPI ------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Products", len(filtered))
col2.metric("Avg Base", f"₹{filtered['Base_Price'].mean():.0f}")
col3.metric("Avg Dynamic", f"₹{filtered['Dynamic_Price'].mean():.0f}")
col4.metric("Increase %",
            f"{((filtered['Dynamic_Price'].mean()-filtered['Base_Price'].mean())/filtered['Base_Price'].mean()*100):.1f}%")
col5.metric("Avg Profit", f"₹{filtered['Profit'].mean():.0f}")

st.caption(f"🕒 Last Updated: {df['Last_Updated'].iloc[0]}")

st.markdown("---")

# ------------------ BEST PRODUCT ------------------
best_product = filtered.loc[filtered['Dynamic_Price'].idxmax()]
st.success(f"🔥 Best Product: {best_product['Product_Name']} (₹{best_product['Dynamic_Price']})")

# ------------------ CHARTS ------------------
st.subheader("📈 Analytics")

colA, colB = st.columns(2)

with colA:
    top = filtered.sort_values(by="Dynamic_Price", ascending=False).head(top_n)
    fig, ax = plt.subplots()
    ax.bar(top['Product_Name'], top['Dynamic_Price'])
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

with colB:
    season_counts = filtered['Season'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(season_counts, labels=season_counts.index, autopct='%1.1f%%')
    st.pyplot(fig)

st.markdown("---")

colC, colD = st.columns(2)

with colC:
    fig, ax = plt.subplots()
    ax.hist(filtered['Dynamic_Price'], bins=20)
    st.pyplot(fig)

with colD:
    fig, ax = plt.subplots()
    ax.scatter(filtered['Demand'], filtered['Dynamic_Price'])
    st.pyplot(fig)

st.markdown("---")

colE, colF = st.columns(2)

with colE:
    trend = filtered['Dynamic_Price'].rolling(20).mean()
    fig, ax = plt.subplots()
    ax.plot(trend)
    st.pyplot(fig)

with colF:
    fig, ax = plt.subplots()
    sns.heatmap(filtered[['Base_Price','Demand','Stock','Rating','Dynamic_Price']].corr(),
                annot=True, ax=ax)
    st.pyplot(fig)

st.markdown("---")

# ------------------ RECOMMENDATIONS ------------------
st.subheader("📌 Recommendations")
st.dataframe(filtered[['Product_Name','Dynamic_Price','Recommendation']])

# ------------------ DOWNLOAD ------------------
csv = filtered.to_csv(index=False).encode('utf-8')

st.download_button("📥 Download Results", csv, "results.csv")

# ------------------ TABLE ------------------
st.subheader("📂 Dataset")
st.dataframe(filtered, use_container_width=True)