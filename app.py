import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Dynamic Pricing System", layout="wide")

# ---------- BACKGROUND + UI ----------
def set_bg(url):
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)),
                    url("{url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .block-container {{
        animation: fadeIn 0.8s ease-in-out;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(0,0,0,0.9);
    }}

    .stButton>button {{
        border-radius: 10px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        color: white;
        border: none;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        transform: scale(1.08);
        box-shadow: 0px 0px 15px rgba(59,130,246,0.8);
    }}

    .card {{
        background: rgba(0,0,0,0.6);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        transition: 0.3s;
    }}

    .card:hover {{
        transform: translateY(-8px);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
    }}

    h1,h2,h3,p,label,div {{
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
st.sidebar.markdown("## 🚀 Dynamic Pricing System")
menu = st.sidebar.radio("Navigation", ["Login", "Home", "Dashboard", "About"])

# ---------- LOGIN ----------
if menu == "Login":
    set_bg("https://images.unsplash.com/photo-1521791136064-7986c2920216")

    st.markdown("<h1 style='text-align:center;'>🔐 Login</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user.strip() in users and users[user.strip()] == pwd.strip():
                st.session_state.logged_in = True
                st.session_state.username = user
                st.success("Login successful")
            else:
                st.error("Invalid credentials")

        st.markdown('</div>', unsafe_allow_html=True)

# ---------- HOME ----------
elif menu == "Home":
    set_bg("https://images.unsplash.com/photo-1556740749-887f6717d7e4")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("""
    <h1>📊 Dynamic Pricing System</h1>

    <p style="font-size:18px;">
    This application simulates real-time dynamic pricing used in modern retail platforms.
    Prices are adjusted based on demand, stock, ratings, and seasonal trends.
    </p>

    <h3>🚀 Key Features</h3>
    <ul>
        <li>Real-time price updates</li>
        <li>Interactive dashboard</li>
        <li>Profit analysis</li>
        <li>Smart recommendations</li>
    </ul>

    <h3>📈 How It Works</h3>
    <ul>
        <li>Dataset loaded</li>
        <li>Demand & stock simulated</li>
        <li>Pricing algorithm applied</li>
        <li>Charts generated</li>
    </ul>

    <h3>🎯 Objective</h3>
    <p>To demonstrate real-world data-driven pricing strategies.</p>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- DASHBOARD ----------
elif menu == "Dashboard":
    set_bg("https://images.unsplash.com/photo-1551288049-bebda4e38f71")

    if not st.session_state.logged_in:
        st.warning("Login first")
        st.stop()

    st.title("📊 Dashboard")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st_autorefresh(interval=5000, key="refresh")

    file = st.sidebar.file_uploader("Upload CSV")

    @st.cache_data
    def load():
        return pd.read_csv("default_dataset.csv")

    df = pd.read_csv(file) if file else load()

    df['Demand'] += [random.randint(-5,5) for _ in range(len(df))]
    df['Stock'] += [random.randint(-10,10) for _ in range(len(df))]
    df['Last_Updated'] = datetime.datetime.now()

    def calc(r):
        price = r['Base_Price']
        if r['Demand'] > 80: price *= 1.2
        elif r['Demand'] < 50: price *= 0.9
        return round(price,2)

    df['Dynamic_Price'] = df.apply(calc, axis=1)
    df['Profit'] = df['Dynamic_Price'] - df['Base_Price']

    df['Recommendation'] = df['Demand'].apply(
        lambda x: "Increase" if x>80 else "Decrease" if x<40 else "Stable"
    )

    # Filters
    search = st.sidebar.text_input("Search")
    season = st.sidebar.selectbox("Season", ["All"] + list(df['Season'].unique()))
    top_n = st.sidebar.slider("Top N", 5, 50, 10)

    if search:
        df = df[df['Product_Name'].str.contains(search, case=False)]
    if season != "All":
        df = df[df['Season']==season]

    # KPI
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Products", len(df))
    c2.metric("Avg Base", int(df['Base_Price'].mean()))
    c3.metric("Avg Dynamic", int(df['Dynamic_Price'].mean()))
    c4.metric("Profit", int(df['Profit'].mean()))
    st.markdown('</div>', unsafe_allow_html=True)

    # Charts
    st.markdown('<div class="card">', unsafe_allow_html=True)

    colA, colB = st.columns(2)

    with colA:
        top_products = df.sort_values(by="Dynamic_Price", ascending=False).head(top_n)
        fig, ax = plt.subplots()
        ax.bar(top_products['Product_Name'], top_products['Dynamic_Price'])
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with colB:
        fig, ax = plt.subplots()
        ax.pie(df['Season'].value_counts(), labels=df['Season'].value_counts().index, autopct='%1.1f%%')
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

    st.markdown('</div>', unsafe_allow_html=True)

    # Recommendations
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📌 Recommendations")
    st.dataframe(df[['Product_Name','Dynamic_Price','Recommendation']])
    st.markdown('</div>', unsafe_allow_html=True)

    # FULL TABLE
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Complete Dataset View")
    st.dataframe(df)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- ABOUT ----------
elif menu == "About":
    set_bg("https://images.unsplash.com/photo-1498050108023-c5249f4df085")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("""
    <h1>ℹ️ About This Project</h1>

    <p>
    This Dynamic Pricing System is designed to simulate modern retail pricing strategies.
    It dynamically adjusts product prices in real-time based on factors such as demand,
    stock availability, customer ratings, and seasonal trends.
    </p>

    <h3>🎯 Objective</h3>
    <p>
    The main objective of this project is to demonstrate how businesses can use data analytics
    and automation to optimize pricing decisions and maximize profitability.
    </p>

    <h3>🛠️ Technologies Used</h3>
    <ul>
        <li>Python</li>
        <li>Pandas</li>
        <li>Matplotlib & Seaborn</li>
        <li>Streamlit</li>
    </ul>

    <h3>📊 Key Features</h3>
    <ul>
        <li>Real-time data simulation</li>
        <li>Dynamic price calculation</li>
        <li>Interactive dashboard with multiple charts</li>
        <li>Filtering and analytics tools</li>
        <li>Recommendation system</li>
        <li>Multi-user login system</li>
    </ul>

    <hr>

    <h2>👨‍💻 About the Developer</h2>

    <p>
    <b>Name:</b> Jaskeerat Singh<br>
    <b>Course:</b> Bachelor of Computer Applications (BCA)<br>
    <b>University:</b> Graphic Era Deemed to be University
    </p>

    <p>
    This project was developed as part of academic coursework to explore practical
    applications of data analytics, dynamic pricing strategies, and interactive dashboards.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
