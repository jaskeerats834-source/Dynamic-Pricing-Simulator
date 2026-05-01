import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Dynamic Pricing System", layout="wide")

# ---------- BACKGROUND ----------
def set_bg(url):
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)),
                    url("{url}");
        background-size: cover;
        background-attachment: fixed;
    }}
    h1,h2,h3,h4,p,label,div {{
        color:white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------- USERS ----------
users = {
    "admin": "admin123",
    "user1": "user123",
    "guest": "guest123"
}

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------- SIDEBAR ----------
st.sidebar.title("🚀 DPS System")
menu = st.sidebar.radio("Navigation", ["Login", "Home", "Dashboard", "About"])

# ---------- LOGIN ----------
if menu == "Login":
    set_bg("https://images.unsplash.com/photo-1521791136064-7986c2920216")

    st.markdown("<h1 style='text-align:center;'>🔐 Login</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background:rgba(0,0,0,0.6);padding:20px;border-radius:10px;'>", unsafe_allow_html=True)

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user in users and users[user] == pwd:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.success("Login successful")
            else:
                st.error("Invalid credentials")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- HOME ----------
elif menu == "Home":
    set_bg("https://images.unsplash.com/photo-1556740749-887f6717d7e4")

    st.markdown("""
    <div style="background:rgba(0,0,0,0.6);padding:25px;border-radius:10px;">
    <h1>📊 Dynamic Pricing System</h1>
    <p>A real-time pricing system that adjusts prices based on demand, stock, ratings, and season.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- DASHBOARD ----------
elif menu == "Dashboard":
    set_bg("https://images.unsplash.com/photo-1551288049-bebda4e38f71")

    if not st.session_state.logged_in:
        st.warning("Login first")
        st.stop()

    st.title("📊 Dashboard")

    # Logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.caption(f"User: {st.session_state.username}")

    st_autorefresh(interval=5000, key="refresh")

    file = st.sidebar.file_uploader("Upload CSV")

    @st.cache_data
    def load():
        return pd.read_csv("default_dataset.csv")

    df = pd.read_csv(file) if file else load()

    # Real-time simulation
    df['Demand'] += [random.randint(-5,5) for _ in range(len(df))]
    df['Stock'] += [random.randint(-10,10) for _ in range(len(df))]

    # Pricing
    def calc(r):
        price = r['Base_Price']
        if r['Demand'] > 80: price *= 1.2
        if r['Stock'] < 50: price *= 1.1
        return round(price,2)

    df['Dynamic_Price'] = df.apply(calc, axis=1)
    df['Profit'] = df['Dynamic_Price'] - df['Base_Price']

    df['Recommendation'] = df['Demand'].apply(
        lambda x: "Increase" if x>80 else "Decrease" if x<40 else "Stable"
    )

    # ---------- FILTERS ----------
    search = st.sidebar.text_input("Search")
    season = st.sidebar.selectbox("Season", ["All"] + list(df['Season'].unique()))

    if search:
        df = df[df['Product_Name'].str.contains(search, case=False)]

    if season != "All":
        df = df[df['Season']==season]

    # ---------- KPI ----------
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Products", len(df))
    c2.metric("Avg Base", int(df['Base_Price'].mean()))
    c3.metric("Avg Dynamic", int(df['Dynamic_Price'].mean()))
    c4.metric("Profit", int(df['Profit'].mean()))

    st.markdown("---")

    # ---------- CHARTS ----------
    colA, colB = st.columns(2)

    with colA:
        fig, ax = plt.subplots()
        ax.bar(df['Product_Name'], df['Dynamic_Price'])
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with colB:
        fig, ax = plt.subplots()
        ax.pie(df['Season'].value_counts(), labels=df['Season'].unique(), autopct='%1.1f%%')
        st.pyplot(fig)

    colC, colD = st.columns(2)

    with colC:
        fig, ax = plt.subplots()
        ax.hist(df['Dynamic_Price'])
        st.pyplot(fig)

    with colD:
        fig, ax = plt.subplots()
        ax.scatter(df['Demand'], df['Dynamic_Price'])
        st.pyplot(fig)

    colE, colF = st.columns(2)

    with colE:
        fig, ax = plt.subplots()
        ax.plot(df['Dynamic_Price'].rolling(10).mean())
        st.pyplot(fig)

    with colF:
        fig, ax = plt.subplots()
        sns.heatmap(df[['Base_Price','Demand','Stock','Dynamic_Price']].corr(), annot=True)
        st.pyplot(fig)

    # ---------- RECOMMENDATION ----------
    st.subheader("📌 Recommendations")
    st.dataframe(df[['Product_Name','Dynamic_Price','Recommendation']])

# ---------- ABOUT ----------
elif menu == "About":
    set_bg("https://images.unsplash.com/photo-1498050108023-c5249f4df085")

    st.markdown("""
    <div style="background:rgba(0,0,0,0.6);padding:20px;border-radius:10px;">
    <h1>About</h1>
    <p>Dynamic pricing system with real-time analytics.</p>
    </div>
    """, unsafe_allow_html=True)
