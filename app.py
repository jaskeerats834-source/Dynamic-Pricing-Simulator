import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import datetime
from streamlit_autorefresh import st_autorefresh

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dynamic Pricing System", layout="wide")

# ------------------ SESSION STATE ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ SIDEBAR NAVIGATION ------------------
menu = st.sidebar.radio("Navigation", ["Login", "Home", "Dashboard", "About"])

# ------------------ LOGIN PAGE ------------------
if menu == "Login":
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
        else:
            st.error("Invalid Credentials ❌")

# ------------------ HOME PAGE ------------------
elif menu == "Home":
    st.title("🏠 Dynamic Pricing System")

    st.write("""
    This system automatically adjusts product prices based on:
    - Demand 📈  
    - Stock 📦  
    - Ratings ⭐  
    - Season 🌦️  

    🔥 Features:
    - Real-time simulation
    - Data analytics dashboard
    - Profit calculation
    - Smart recommendations
    """)

# ------------------ DASHBOARD ------------------
elif menu == "Dashboard":

    if not st.session_state.logged_in:
        st.warning("Please login first 🔐")
        st.stop()

    st.title("📊 Dynamic Pricing Dashboard")

    # AUTO REFRESH
    st_autorefresh(interval=5000, limit=None, key="refresh")

    # FILE UPLOAD
    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    @st.cache_data
    def load_default():
        return pd.read_csv("default_dataset.csv")

    if file:
        df = pd.read_csv(file)
    else:
        df = load_default()

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

    # EXTRA FEATURES
    df['Profit'] = df['Dynamic_Price'] - df['Base_Price']

    def recommend(row):
        if row['Demand'] > 80 and row['Stock'] < 50:
            return "Increase Price"
        elif row['Demand'] < 40:
            return "Decrease Price"
        else:
            return "Keep Same"

    df['Recommendation'] = df.apply(recommend, axis=1)

    # FILTERS
    st.sidebar.header("Filters")

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

    # KPI
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Products", len(filtered))
    col2.metric("Avg Base", f"₹{filtered['Base_Price'].mean():.0f}")
    col3.metric("Avg Dynamic", f"₹{filtered['Dynamic_Price'].mean():.0f}")
    col4.metric("Increase %",
                f"{((filtered['Dynamic_Price'].mean()-filtered['Base_Price'].mean())/filtered['Base_Price'].mean()*100):.1f}%")
    col5.metric("Avg Profit", f"₹{filtered['Profit'].mean():.0f}")

    st.caption(f"Last Updated: {df['Last_Updated'].iloc[0]}")

    st.markdown("---")

    # BEST PRODUCT
    best = filtered.loc[filtered['Dynamic_Price'].idxmax()]
    st.success(f"Best Product: {best['Product_Name']} (₹{best['Dynamic_Price']})")

    # CHARTS
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

    # RECOMMENDATIONS
    st.subheader("Recommendations")
    st.dataframe(filtered[['Product_Name','Dynamic_Price','Recommendation']])

    # DOWNLOAD
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results", csv, "results.csv")

    # TABLE
    st.subheader("Dataset")
    st.dataframe(filtered)

# ------------------ ABOUT PAGE ------------------
elif menu == "About":
    st.title("ℹ️ About Project")

    st.write("""
    This is a Dynamic Pricing System developed using Python and Streamlit.

    It simulates real-world pricing strategies used in e-commerce platforms.

    Technologies Used:
    - Python
    - Pandas
    - Matplotlib & Seaborn
    - Streamlit

    Developed for academic project purposes.
    """)
