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
            user = user.strip()
            pwd = pwd.strip()
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

    <p style="font-size:18px;">
    This system automatically adjusts product prices based on demand,
    stock levels, customer ratings, and seasonal trends.
    </p>

    <h3>🚀 Features:</h3>
    <ul>
    <li>Real-time pricing updates</li>
    <li>Interactive analytics dashboard</li>
    <li>Profit analysis</li>
    <li>Smart recommendations</li>
    </ul>

    <h3>🎯 Objective:</h3>
    <p>
    To simulate real-world pricing strategies used by companies like Amazon and Uber.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ---------- DASHBOARD ----------
elif menu == "Dashboard":
    set_bg("https://images.unsplash.com/photo-1551288049-bebda4e38f71")

    if not st.session_state.logged_in:
        st.warning("Please login first 🔐")
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
    df['Demand'] = df['Demand'] + [random.randint(-5,5) for _ in range(len(df))]
    df['Stock'] = df['Stock'] + [random.randint(-10,10) for _ in range(len(df))]
    df['Last_Updated'] = datetime.datetime.now()

    # Pricing logic
    def calc(r):
        price = r['Base_Price']
        if r['Demand'] > 80: price *= 1.2
        elif r['Demand'] < 50: price *= 0.9
        if r['Stock'] > 150: price *= 0.85
        elif r['Stock'] < 50: price *= 1.15
        return round(price,2)

    df['Dynamic_Price'] = df.apply(calc, axis=1)
    df['Profit'] = df['Dynamic_Price'] - df['Base_Price']

    df['Recommendation'] = df['Demand'].apply(
        lambda x: "Increase" if x>80 else "Decrease" if x<40 else "Stable"
    )

    # ---------- FILTERS ----------
    st.sidebar.header("Filters")
    search = st.sidebar.text_input("Search Product")
    season = st.sidebar.selectbox("Season", ["All"] + list(df['Season'].unique()))
    top_n = st.sidebar.slider("Top N Products", 5, 50, 10)

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

    # Top N Bar
    with colA:
        top_products = df.sort_values(by="Dynamic_Price", ascending=False).head(top_n)
        fig, ax = plt.subplots()
        ax.bar(top_products['Product_Name'], top_products['Dynamic_Price'])
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Pie
    with colB:
        fig, ax = plt.subplots()
        ax.pie(df['Season'].value_counts(), labels=df['Season'].value_counts().index, autopct='%1.1f%%')
        st.pyplot(fig)

    colC, colD = st.columns(2)

    with colC:
        fig, ax = plt.subplots()
        ax.hist(df['Dynamic_Price'], bins=20)
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

    # ---------- RECOMMENDATIONS ----------
    st.subheader("📌 Recommendations")
    st.dataframe(df[['Product_Name','Dynamic_Price','Recommendation']])

# ---------- ABOUT ----------
elif menu == "About":
    set_bg("https://images.unsplash.com/photo-1498050108023-c5249f4df085")

    st.markdown("""
    <div style="background:rgba(0,0,0,0.6);padding:20px;border-radius:10px;">
    <h1>ℹ️ About This Project</h1>

    <p>
    This Dynamic Pricing System is developed to simulate modern retail pricing strategies.
    </p>

    <h3>🛠️ Technologies Used:</h3>
    <ul>
    <li>Python</li>
    <li>Pandas</li>
    <li>Matplotlib & Seaborn</li>
    <li>Streamlit</li>
    </ul>

    <h3>📊 Key Functionalities:</h3>
    <ul>
    <li>Dynamic price calculation</li>
    <li>Real-time data simulation</li>
    <li>Interactive dashboard</li>
    <li>Recommendation system</li>
    </ul>

    <p>
    This project demonstrates how businesses can use data analytics to optimize pricing decisions.
    </p>
    </div>
    """, unsafe_allow_html=True)
