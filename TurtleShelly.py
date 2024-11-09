import requests
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# API keys
alpha_vantage_api_key = 'WY68QLSPCFD9VZFB'
news_api_key = '416412eab78248ecbde0eec9ef07bfaf'


# Function to fetch stock data from Alpha Vantage
def get_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data['Time Series (Daily)'] if 'Time Series (Daily)' in data else {}


# Function to fetch company overview from Alpha Vantage
def get_company_overview(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}


# Function to fetch news data from NewsAPI
def get_news_data(company_name, api_key):
    url = f'https://newsapi.org/v2/everything?q={company_name}&apiKey={api_key}'
    response = requests.get(url)
    return response.json()['articles'] if 'articles' in response.json() else []


# Function to process stock data and plot it
def plot_stock_data(stock_data):
    dates = list(stock_data.keys())
    prices = [float(stock_data[date]['4. close']) for date in dates]

    # Create Plotly chart
    fig = go.Figure(data=go.Scatter(x=dates, y=prices))
    fig.update_layout(
        title="Stock Price Over Time",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis=dict(tickformat='%Y-%m-%d'),
        template="plotly_dark"
    )
    return fig


# Streamlit App
def main():
    st.title("Company Financial Performance Forecast")

    company_symbol = st.text_input("Enter Company Symbol (e.g., AAPL for Apple)", "AAPL")
    company_name = company_symbol  # Use symbol as the name for simplicity

    # Get financial data and news
    stock_data = get_stock_data(company_symbol, alpha_vantage_api_key)
    company_overview = get_company_overview(company_symbol, alpha_vantage_api_key)
    news_data = get_news_data(company_name, news_api_key)

    # Display Financial Data
    if company_overview:
        st.subheader(f"{company_name} - Financial Overview")
        st.write(f"**Market Capitalization**: {company_overview.get('MarketCapitalization', 'N/A')}")
        st.write(f"**PE Ratio**: {company_overview.get('PERatio', 'N/A')}")
        st.write(f"**EPS (Earnings Per Share)**: {company_overview.get('EPS', 'N/A')}")
        st.write(f"**EBITDA**: {company_overview.get('EBITDA', 'N/A')}")
        st.write(f"**52 Week High**: {company_overview.get('52WeekHigh', 'N/A')}")
        st.write(f"**52 Week Low**: {company_overview.get('52WeekLow', 'N/A')}")

    else:
        st.write("Unable to fetch financial data for the selected company.")

    # Display Stock Graph at the bottom
    if stock_data:
        st.subheader(f"{company_name} - Stock Price Over Time")
        stock_fig = plot_stock_data(stock_data)
        st.plotly_chart(stock_fig)

    else:
        st.write("Failed to retrieve stock data.")

    # Display News Data (Optional)
    if news_data:
        st.subheader(f"Latest News on {company_name}")
        for article in news_data[:5]:  # Show top 5 articles
            st.write(f"- {article['title']}")
            st.write(f"  Source: {article['source']['name']}")
            st.write(f"  Link: {article['url']}")
            st.write(f"  Sentiment: {get_sentiment(article['title'])}")
    else:
        st.write("No news data available.")


# Function to analyze sentiment of a text
def get_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] >= 0.05:
        return "Positive"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"


# Run the app
if __name__ == "__main__":
    main()
