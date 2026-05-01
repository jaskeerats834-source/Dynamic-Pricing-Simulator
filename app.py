import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import datetime
from streamlit_autorefresh import st_autorefresh

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dynamic Pricing System", layout="wide")

# ------------------ GLOBAL STYLE ------------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1551288049-bebda4e38f71");
    background-size: cover;
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background-color: rgba(0,0,0,0.85);
}
[data-testid="stMetric"] {
    background-color: rgba(30,41,59,0.8);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------ USER DATABASE ------------------
users = {
    "admin": {"password": "admin123"},
    "user1": {"password": "user123"},
    "guest": {"password": "guest123"}
}

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ------------------ SIDEBAR ------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.markdown("## 🚀 DPS System")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation", ["Login", "Home", "Dashboard", "About"])

# ------------------ LOGIN PAGE ------------------
if menu == "Login":
    st.markdown("<h1 style='text-align:center; color:white;'>🔐 Welcome Back</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Login to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username} ✅")
            else:
                st.error("Invalid credentials ❌")

# ------------------ HOME PAGE ------------------
elif menu == "Home":
    st.markdown("""
    <h1 style='color:white;'>📊 Dynamic Pricing System</h1>
    <p style='color:white; font-size:18px;'>
    A real-time retail pricing system that adjusts product prices based on demand,
    stock levels, ratings, and seasonal trends.
    </p>
    """, unsafe_allow_html=True)

    st.image("https://images.unsplash.com/photo-1556740749-887f6717d7e4", use_container_width=True)

    st.markdown("""
    ### 🚀 Key Features:
    - Real-time pricing updates  
    - Interactive analytics dashboard  
    - Profit insights  
    - Smart recommendations  

    ### 🎯 Objective:
    To simulate real-world dynamic pricing strategies used in e-commerce platforms.
    """)

# ------------------ DASHBOARD ------------------
elif menu == "Dashboard":

    if not st.session_state.logged_in:
        st.warning("Please login first 🔐")
        st.stop()

    st.title("📊 Dynamic Pricing Dashboard")

    col1, col2 = st.columns([8,1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.caption(f"Logged in as: {st.session_state.username}")

    st_autorefresh(interval=5000, limit=None, key="refresh")

    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    @st.cache_data
    def load_default():
        return pd.read_csv("default_dataset.csv")

    df = pd.read_csv(file) if file else load_default()

    # Real-time simulation
    df['Demand'] = df['Demand'].apply(lambda x: max(0, x + random.randint(-5, 5)))
    df['Stock'] = df['Stock'].apply(lambda x: max(0, x + random.randint(-10, 10)))
    df['Last_Updated'] = datetime.datetime.now()

    # Pricing logic
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
    df['Profit'] = df['Dynamic_Price'] - df['Base_Price']

    def recommend(row):
        if row['Demand'] > 80 and row['Stock'] < 50:
            return "Increase Price"
        elif row['Demand'] < 40:
            return "Decrease Price"
        else:
            return "Keep Same"

    df['Recommendation'] = df.apply(recommend, axis=1)

    # Filters
    search = st.sidebar.text_input("Search Product")
    top_n = st.sidebar.slider("Top N", 5, 50, 10)
    season = st.sidebar.selectbox("Season", ["All"] + list(df['Season'].unique()))

    filtered = df.copy()

    if search:
        filtered = filtered[filtered['Product_Name'].str.contains(search, case=False)]

    if season != "All":
        filtered = filtered[filtered['Season'] == season]

    # KPIs
    st.subheader("📊 Key Metrics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", len(filtered))
    c2.metric("Avg Base", f"₹{filtered['Base_Price'].mean():.0f}")
    c3.metric("Avg Dynamic", f"₹{filtered['Dynamic_Price'].mean():.0f}")
    c4.metric("Avg Profit", f"₹{filtered['Profit'].mean():.0f}")

    st.caption(f"Last Updated: {df['Last_Updated'].iloc[0]}")

    st.markdown("---")

    # Charts
    colA, colB = st.columns(2)

    with colA:
        top = filtered.sort_values(by="Dynamic_Price", ascending=False).head(top_n)
        fig, ax = plt.subplots()
        ax.bar(top['Product_Name'], top['Dynamic_Price'])
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

    with colB:
        fig, ax = plt.subplots()
        ax.hist(filtered['Dynamic_Price'], bins=20)
        st.pyplot(fig)

    st.markdown("---")

    st.subheader("📌 Recommendations")
    st.dataframe(filtered[['Product_Name','Dynamic_Price','Recommendation']])

# ------------------ ABOUT ------------------
elif menu == "About":
    st.title("ℹ️ About Project")

    st.write("""
    Dynamic Pricing System built using Python & Streamlit.

    Features:
    - Multi-user login system
    - Real-time pricing simulation
    - Interactive analytics dashboard
    - Recommendation system
    """)
