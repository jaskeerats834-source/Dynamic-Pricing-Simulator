import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import datetime
from streamlit_autorefresh import st_autorefresh

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dynamic Pricing System", layout="wide")

# ------------------ BACKGROUND FUNCTION ------------------
def set_bg(image_url):
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
                    url("{image_url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    h1, h2, h3, h4, h5, h6, p, label, div {{
        color: white !important;
    }}
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
    set_bg("https://images.unsplash.com/photo-1521791136064-7986c2920216")

    st.markdown("<h1 style='text-align:center;'>🔐 Welcome Back</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="background: rgba(0,0,0,0.6); padding:20px; border-radius:10px;">
        """, unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username} ✅")
            else:
                st.error("Invalid credentials ❌")

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------ HOME PAGE ------------------
elif menu == "Home":
    set_bg("https://images.unsplash.com/photo-1556740749-887f6717d7e4")

    st.markdown("<h1>📊 Dynamic Pricing System</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(0,0,0,0.6); padding:20px; border-radius:10px;">
    <p style="font-size:18px;">
    A real-time retail pricing system that adjusts product prices based on demand,
    stock levels, ratings, and seasonal trends.
    </p>

    <h3>🚀 Features:</h3>
    <ul>
    <li>Real-time pricing updates</li>
    <li>Interactive analytics dashboard</li>
    <li>Profit insights</li>
    <li>Smart recommendations</li>
    </ul>

    <h3>🎯 Objective:</h3>
    <p>To simulate real-world pricing strategies used by e-commerce platforms.</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------ DASHBOARD ------------------
elif menu == "Dashboard":
    set_bg("https://images.unsplash.com/photo-1551288049-bebda4e38f71")

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

    df['Demand'] = df['Demand'].apply(lambda x: max(0, x + random.randint(-5, 5)))
    df['Stock'] = df['Stock'].apply(lambda x: max(0, x + random.randint(-10, 10)))
    df['Last_Updated'] = datetime.datetime.now()

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

    st.markdown('<div style="background: rgba(0,0,0,0.6); padding:15px; border-radius:10px;">', unsafe_allow_html=True)

    st.subheader("📊 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", len(df))
    c2.metric("Avg Base", f"₹{df['Base_Price'].mean():.0f}")
    c3.metric("Avg Dynamic", f"₹{df['Dynamic_Price'].mean():.0f}")
    c4.metric("Avg Profit", f"₹{df['Profit'].mean():.0f}")

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        fig, ax = plt.subplots()
        ax.hist(df['Dynamic_Price'], bins=20)
        st.pyplot(fig)

    with colB:
        fig, ax = plt.subplots()
        ax.scatter(df['Demand'], df['Dynamic_Price'])
        st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ ABOUT ------------------
elif menu == "About":
    set_bg("https://images.unsplash.com/photo-1498050108023-c5249f4df085")

    st.markdown("""
    <div style="background: rgba(0,0,0,0.6); padding:20px; border-radius:10px;">
    <h1>ℹ️ About Project</h1>

    <p>This Dynamic Pricing System simulates real-world retail pricing strategies.</p>

    <h3>Technologies:</h3>
    <ul>
    <li>Python</li>
    <li>Pandas</li>
    <li>Matplotlib & Seaborn</li>
    <li>Streamlit</li>
    </ul>

    <p>Includes real-time simulation, analytics, and recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
