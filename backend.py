import yfinance as yf
import pandas as pd
import requests
import json
import os
from openai import OpenAI
from datetime import date, timedelta



import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# -------- CHATBOT AGENT --------
def chatbot_agent(user_message, stock_data=None):

    context = ""

    if stock_data:
        context = f"""
        Stock Price: {stock_data['price']}
        RSI: {stock_data['rsi']}
        Moving Average: {stock_data['ma']}
        """

    prompt = f"""
    You are an AI stock market assistant.

    {context}

    User Question:
    {user_message}

    Give concise financial insight.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are a smart AI stock assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
# -------- MEMORY --------
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"risk_level": "medium", "preferred_stocks": []}

memory = load_memory()

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# -------- STOCK DATA --------
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="6mo")

# -------- RSI --------
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# -------- TECH AGENT --------
def technical_agent(symbol):
    data = get_stock_data(symbol)
    data['RSI'] = calculate_rsi(data)
    data['MA50'] = data['Close'].rolling(50).mean()

    return {
        "price": data['Close'].iloc[-1],
        "rsi": data['RSI'].iloc[-1],
        "ma": data['MA50'].iloc[-1]
    }

# -------- NEWS --------
API_KEY = "YOUR_API_KEY"

def get_stock_news(symbol):
    today = date.today()
    past = today - timedelta(days=7)

    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={past}&to={today}&token={API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    if isinstance(data, list):
        return data[:5]
    return []

def analyze_news_sentiment(news):
    score = 0
    for article in news:
        text = article['headline'].lower()
        if "gain" in text or "profit" in text:
            score += 1
        if "loss" in text or "drop" in text:
            score -= 1

    return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"

def news_agent(symbol):
    news = get_stock_news(symbol.replace(".NS", ""))
    sentiment = analyze_news_sentiment(news)
    return {"sentiment": sentiment}

# -------- DECISION --------
def decision_agent(tech, news):
    price, rsi, ma = tech["price"], tech["rsi"], tech["ma"]
    sentiment = news["sentiment"]

    if price > ma and rsi < 70 and sentiment == "Positive":
        return "BUY", "Strong trend + positive news"
    elif rsi > 70:
        return "HOLD", "Overbought"
    elif sentiment == "Negative":
        return "AVOID", "Negative sentiment"
    elif price < ma:
        return "AVOID", "Downtrend"
    return "HOLD", "Mixed signals"


# -------- PORTFOLIO AGENT --------
def portfolio_agent(budget):

    stocks = ["TCS.NS", "INFY.NS", "WIPRO.NS", "HDFCBANK.NS"]

    portfolio = []

    allocation = budget / len(stocks)

    for symbol in stocks:

        tech = technical_agent(symbol)
        news = news_agent(symbol)
        decision, reason = decision_agent(tech, news)

        # Only include BUY/HOLD
        if decision != "AVOID":

            qty = int(allocation // tech["price"])

            portfolio.append({
                "Stock": symbol,
                "Price": round(tech["price"], 2),
                "Decision": decision,
                "Quantity": qty,
                "Investment": round(qty * tech["price"], 2)
            })

    return portfolio


# -------- ALERT AGENT --------
def alert_agent(tech):

    alerts = []

    if tech["rsi"] > 70:
        alerts.append("⚠️ RSI above 70 (Overbought)")

    elif tech["rsi"] < 30:
        alerts.append("🟢 RSI below 30 (Oversold Opportunity)")

    if tech["price"] > tech["ma"]:
        alerts.append("📈 Price above MA50 (Bullish Trend)")
    else:
        alerts.append("📉 Price below MA50 (Bearish Trend)")

    return alerts