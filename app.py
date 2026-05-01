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

    .block-container {{
        animation: fadeIn 0.8s ease-in-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .card {{
        background: rgba(0,0,0,0.6);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }}

    h1,h2,h3,p,label,div {{
        color:white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------- USERS ----------
users = {"admin": "admin123"}

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- SIDEBAR ----------
menu = st.sidebar.radio("Navigation", ["Login", "Home", "Dashboard", "About"])

# ---------- LOGIN ----------
if menu == "Login":
    set_bg("https://images.unsplash.com/photo-1521791136064-7986c2920216")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user in users and users[user] == pwd:
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# ---------- HOME ----------
elif menu == "Home":
    set_bg("https://images.unsplash.com/photo-1556740749-887f6717d7e4")

    st.markdown("""
    <div class="card">
    <h1>📊 Dynamic Pricing System</h1>
    <p>This project simulates real-time pricing strategies used in modern businesses.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- DASHBOARD ----------
elif menu == "Dashboard":
    set_bg("https://images.unsplash.com/photo-1551288049-bebda4e38f71")

    if not st.session_state.logged_in:
        st.warning("Login first")
        st.stop()

    file = st.file_uploader("Upload CSV")

    df = pd.read_csv(file) if file else pd.read_csv("default_dataset.csv")

    df['Demand'] += [random.randint(-5,5) for _ in range(len(df))]
    df['Stock'] += [random.randint(-10,10) for _ in range(len(df))]
    df['Last_Updated'] = datetime.datetime.now()

    df['Dynamic_Price'] = df['Base_Price'] * (1 + df['Demand']/100)
    df['Recommendation'] = df['Demand'].apply(
        lambda x: "Increase" if x>80 else "Decrease" if x<40 else "Stable"
    )

    # ---------- KPI ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("Total Products:", len(df))
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- CHARTS ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        ax.bar(df['Product_Name'], df['Dynamic_Price'])
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.hist(df['Dynamic_Price'])
        st.pyplot(fig)

    col3, col4 = st.columns(2)

    with col3:
        fig, ax = plt.subplots()
        ax.scatter(df['Demand'], df['Dynamic_Price'])
        st.pyplot(fig)

    with col4:
        fig, ax = plt.subplots()
        sns.heatmap(df[['Base_Price','Demand','Dynamic_Price']].corr(), annot=True)
        st.pyplot(fig)

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- RECOMMENDATIONS ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Recommendations")
    st.dataframe(df[['Product_Name','Dynamic_Price','Recommendation']])
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- FULL DATA ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Complete Dataset")
    st.dataframe(df)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- ABOUT ----------
elif menu == "About":
    set_bg("https://images.unsplash.com/photo-1498050108023-c5249f4df085")

    st.markdown("""
    <div class="card">
    <h1>About</h1>
    <p>Developed by Jaskeerat Singh</p>
    </div>
    """, unsafe_allow_html=True)
