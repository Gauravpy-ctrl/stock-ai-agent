from streamlit_autorefresh import st_autorefresh
# Auto refresh every 60 sec
st_autorefresh(interval=60000, key="refresh")
import streamlit as st
import plotly.graph_objs as go
from backend import *

# ---------- PAGE ----------
st.set_page_config(
    page_title="Stock AI Agent",
    page_icon="📈",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #0f172a, #020617);
    color: white;
}

.big-title {
    font-size: 52px;
    font-weight: 800;
    color: white;
}

.subtitle {
    color: #94a3b8;
    font-size: 18px;
    margin-bottom: 30px;
}

.glass {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
}

.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
}

.buy-box {
    background: rgba(34,197,94,0.15);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #22c55e;
}

.hold-box {
    background: rgba(234,179,8,0.15);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #eab308;
}

.avoid-box {
    background: rgba(239,68,68,0.15);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #ef4444;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("<div class='big-title'>📈 Stock AI Agent</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered stock analysis with technical + news intelligence</div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Controls")

symbol = st.sidebar.text_input("Stock Symbol", "TCS.NS")

risk = st.sidebar.selectbox(
    "Risk Level",
    ["low", "medium", "high"]
)

analyze = st.sidebar.button("🚀 Analyze Stock")

# ---------- TABS ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analysis",
    "📈 Chart",
    "🧠 Memory",
    "💼 Portfolio",
    "🤖 AI Chat"
])

if analyze:

    memory["risk_level"] = risk
    save_memory()

    with st.spinner("Analyzing stock with AI agents..."):

        tech = technical_agent(symbol)
        news = news_agent(symbol)
        decision, reason = decision_agent(tech, news)

    # ---------- TAB 1 ----------
    with tab1:

        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💰 Price</h3>
                <h2>{round(tech['price'],2)}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📊 RSI</h3>
                <h2>{round(tech['rsi'],2)}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🧠 Sentiment</h3>
                <h2>{news['sentiment']}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # ---------- DECISION ----------
        if decision == "BUY":
            st.markdown(f"""
            <div class='buy-box'>
                <h2>✅ BUY</h2>
                <p>{reason}</p>
            </div>
            """, unsafe_allow_html=True)

        elif decision == "HOLD":
            st.markdown(f"""
            <div class='hold-box'>
                <h2>⚠️ HOLD</h2>
                <p>{reason}</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class='avoid-box'>
                <h2>❌ AVOID</h2>
                <p>{reason}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
        
        # ---------- ALERTS ----------
        alerts = alert_agent(tech)

        st.subheader("🔔 Trading Alerts")

        for alert in alerts:
            st.info(alert)

    # ---------- TAB 2 ----------
with tab2:

    # 🔥 FIX
    data = get_stock_data(symbol)

    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    )])

    # Moving Average
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'].rolling(50).mean(),
        mode='lines',
        name='MA50'
    ))

    fig.update_layout(
        title=f"{symbol} Candlestick Chart",
        template="plotly_dark",
        height=650,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------- TAB 3 ----------
    with tab3:

        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        st.subheader("🧠 User Preferences")

        st.write(memory)

        st.markdown("</div>", unsafe_allow_html=True)
        
        

    # ---------- TAB 4 ----------
    with tab4:

        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        st.subheader("💼 AI Portfolio Dashboard")

        budget = st.slider(
            "Select Investment Budget",
            1000,
            100000,
            10000,
            step=1000
        )

        portfolio = portfolio_agent(budget)

        if portfolio:

            import pandas as pd

            df = pd.DataFrame(portfolio)

            st.dataframe(df, use_container_width=True)

            # ---------- PIE CHART ----------
            fig = go.Figure(data=[go.Pie(
                labels=df["Stock"],
                values=df["Investment"],
                hole=.4
            )])

            fig.update_layout(
                title="📊 Investment Allocation",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)

            total = df["Investment"].sum()

            st.success(f"💰 Total Investment: ₹{round(total,2)}")

        else:
            st.warning("No suitable portfolio found")

        st.markdown("</div>", unsafe_allow_html=True)
        
# ---------- TAB 5 ----------
with tab5:

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    st.subheader("🤖 AI Financial Chatbot")

    user_question = st.text_input(
        "Ask anything about the stock market"
    )

    if st.button("Ask AI"):

        with st.spinner("AI thinking..."):

            # 🔥 FIX
            tech_data = technical_agent(symbol)

            ai_response = chatbot_agent(
                user_question,
                tech_data
            )

        st.success(ai_response)

    st.markdown("</div>", unsafe_allow_html=True)