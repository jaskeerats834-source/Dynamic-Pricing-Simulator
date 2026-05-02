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

    /* 🔥 Sidebar Button Styling */
    [data-testid="stSidebar"] .stButton>button {{
        width: 100%;
        margin-bottom: 10px;
        padding: 12px;
        border-radius: 8px;
        background: linear-gradient(90deg, #2563eb, #06b6d4);
        font-weight: 600;
        color: white;
        border: none;
        transition: 0.3s;
    }}

    [data-testid="stSidebar"] .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0px 0px 12px rgba(37,99,235,0.7);
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
if "menu" not in st.session_state:
    st.session_state.menu = "Login"

# ---------- SIDEBAR (UPDATED) ----------
st.sidebar.markdown("## 🚀 Dynamic Pricing System")

menu = None

if st.sidebar.button("🔐 Login"):
    menu = "Login"
if st.sidebar.button("🏠 Home"):
    menu = "Home"
if st.sidebar.button("📊 Dashboard"):
    menu = "Dashboard"
if st.sidebar.button("ℹ️ About"):
    menu = "About"

if menu:
    st.session_state.menu = menu

menu = st.session_state.menu

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

    # 🏆 BEST PRODUCT
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏆 Best Product")

    if not df.empty:
        best_product = df.loc[df['Dynamic_Price'].idxmax()]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Product", best_product['Product_Name'])
        col2.metric("Price", f"₹{best_product['Dynamic_Price']}")
        col3.metric("Demand", int(best_product['Demand']))
        col4.metric("Status", best_product['Recommendation'])

    st.markdown('</div>', unsafe_allow_html=True)

    # 💰 PROFIT LEADERBOARD
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💰 Top Profitable Products")

    top_profit = df.sort_values(by="Profit", ascending=False).head(5)
    st.table(top_profit[['Product_Name', 'Dynamic_Price', 'Profit']])

    st.markdown('</div>', unsafe_allow_html=True)

    # 🛍️ PRODUCT CARDS
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🛍️ Product Showcase")

    top_display = df.sort_values(by="Dynamic_Price", ascending=False).head(6)
    cols = st.columns(3)

    for i, (_, row) in enumerate(top_display.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05);
                        padding:15px;
                        border-radius:10px;
                        margin-bottom:15px;
                        text-align:center;">
                <h4>{row['Product_Name']}</h4>
                <p>💰 ₹{row['Dynamic_Price']}</p>
                <p>📦 Stock: {row['Stock']}</p>
                <p>🔥 Demand: {row['Demand']}</p>
                <p>📊 {row['Recommendation']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 📊 CHARTS (FIXED DARK MODE)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    colA, colB = st.columns(2)

    with colA:
        top_products = df.sort_values(by="Dynamic_Price", ascending=False).head(top_n)
        fig, ax = plt.subplots()
        ax.bar(top_products['Product_Name'], top_products['Dynamic_Price'])
        ax.set_facecolor('#111111')
        fig.patch.set_facecolor('#111111')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with colB:
        fig, ax = plt.subplots()
        ax.pie(df['Season'].value_counts(),
               labels=df['Season'].value_counts().index,
               autopct='%1.1f%%')
        ax.set_facecolor('#111111')
        fig.patch.set_facecolor('#111111')
        st.pyplot(fig)

    colC, colD = st.columns(2)

    with colC:
        fig, ax = plt.subplots()
        ax.hist(df['Dynamic_Price'])
        ax.set_facecolor('#111111')
        fig.patch.set_facecolor('#111111')
        ax.tick_params(colors='white')
        st.pyplot(fig)

    with colD:
        fig, ax = plt.subplots()
        ax.scatter(df['Demand'], df['Dynamic_Price'])
        ax.set_facecolor('#111111')
        fig.patch.set_facecolor('#111111')
        ax.tick_params(colors='white')
        st.pyplot(fig)

    st.markdown('</div>', unsafe_allow_html=True)

    # 📈 PROFIT TREND
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Profit Trend")

    if "profit_history" not in st.session_state:
        st.session_state.profit_history = []

    current_profit = df['Profit'].sum()
    st.session_state.profit_history.append(current_profit)

    fig, ax = plt.subplots()
    ax.plot(st.session_state.profit_history)
    ax.set_facecolor('#111111')
    fig.patch.set_facecolor('#111111')
    ax.tick_params(colors='white')

    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    # 🎯 RECOMMENDATIONS (STYLED)
       # 🎯 RECOMMENDATIONS (STYLED)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📌 Recommendations")

    def get_badge(val):
        if val == "Increase":
            return f"<span style='color:#22c55e;font-weight:bold;'>▲ {val}</span>"
        elif val == "Decrease":
            return f"<span style='color:#ef4444;font-weight:bold;'>▼ {val}</span>"
        else:
            return f"<span style='color:#eab308;font-weight:bold;'>● {val}</span>"

    # Base dataframe
    rec_df = df[['Product_Name','Dynamic_Price','Recommendation']].copy()

    # 🔍 SEARCH BAR
    search_term = st.text_input("🔍 Search Product in Recommendations")

    if search_term:
        rec_df = rec_df[rec_df['Product_Name'].str.contains(search_term, case=False)]

    # Apply badges AFTER filtering
    rec_df['Recommendation'] = rec_df['Recommendation'].apply(get_badge)

    # 📥 DOWNLOAD BUTTON
    download_df = df[['Product_Name','Dynamic_Price','Recommendation']].copy()

    st.download_button(
        label="📥 Download Recommendations CSV",
        data=download_df.to_csv(index=False),
        file_name="recommendations.csv",
        mime="text/csv"
    )

    # 📜 SCROLLABLE TABLE
    table_html = rec_df.to_html(escape=False)

    st.markdown(f"""
    <div style="
        max-height: 300px;
        overflow-y: auto;
        border-radius: 10px;
    ">
        {table_html}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
     # 📂 FULL DATASET
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
