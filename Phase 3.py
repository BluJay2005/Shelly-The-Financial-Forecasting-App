import requests
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.linear_model import LinearRegression
import numpy as np

# API keys
alpha_vantage_api_key = '1UDQXIUV6X6G8P5C'
news_api_key = 'c82f8dfe888a443e93ae468a52f6cda2'


# Function to fetch stock data from Alpha Vantage
def get_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    print(f"Stock Data Response: {response.json()}")  # Debugging API response
    data = response.json()
    return data['Time Series (Daily)'] if 'Time Series (Daily)' in data else {}


# Function to fetch company overview from Alpha Vantage
def get_company_overview(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    print(f"Company Overview Response: {response.json()}")  # Debugging API response
    return response.json() if response.status_code == 200 else {}


# Function to fetch news data from NewsAPI
def get_news_data(company_name, api_key):
    url = f'https://newsapi.org/v2/everything?q={company_name}&apiKey={api_key}'
    response = requests.get(url)
    return response.json()['articles'] if 'articles' in response.json() else []


# Function to analyze sentiment of a text
def get_sentiment(text):
    if not text:
        return "N/A"

    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] >= 0.05:
        return "Positive"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"


# Function to plot stock data
def plot_stock_data(stock_data):
    dates = list(stock_data.keys())
    prices = [float(stock_data[date]['4. close']) for date in dates]

    fig = go.Figure(data=go.Scatter(x=dates, y=prices))
    fig.update_layout(
        title="Stock Price Over Time",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis=dict(tickformat='%Y-%m-%d'),
        template="plotly_dark"
    )
    return fig


# Function to forecast future stock price using linear regression
def forecast_stock_data(stock_data):
    # Convert date to numerical format for regression
    dates = list(stock_data.keys())[-30:]  # Get the last 30 days of stock data for forecasting
    prices = [float(stock_data[date]['4. close']) for date in dates]

    # Prepare data for linear regression
    X = np.array(range(len(prices))).reshape(-1, 1)  # Days as numbers
    y = np.array(prices)

    model = LinearRegression()
    model.fit(X, y)

    # Predict future price (for the next day)
    future_day = np.array([[len(prices)]])
    predicted_price = model.predict(future_day)[0]

    return predicted_price


# AI-generated financial report
def generate_financial_report(company_overview):
    market_cap = company_overview.get('MarketCapitalization', 'N/A')
    pe_ratio = company_overview.get('PERatio', 'N/A')
    eps = company_overview.get('EPS', 'N/A')
    ebitda = company_overview.get('EBITDA', 'N/A')
    high_52week = company_overview.get('52WeekHigh', 'N/A')
    low_52week = company_overview.get('52WeekLow', 'N/A')

    # Basic assessment based on some values
    if market_cap == 'N/A' or pe_ratio == 'N/A' or eps == 'N/A':
        financial_health = "The financial data for this company could not be retrieved, so it is difficult to assess its current financial health."
    else:
        pe_assessment = "good" if float(pe_ratio) < 20 else "bad"
        eps_assessment = "good" if float(eps) > 0 else "bad"

        # Construct a report based on this information
        financial_health = f"The company has a market capitalization of {market_cap}, which is a solid indicator of its size in the market. The P/E ratio is {pe_ratio}, which is considered {pe_assessment}, and the EPS is {eps}, which is considered {eps_assessment}."

        if high_52week != 'N/A' and low_52week != 'N/A':
            financial_health += f" The company’s stock has a 52-week range from {low_52week} to {high_52week}, which can provide insights into the stock's volatility."

        financial_health += " Based on these metrics, the company seems to be in " + (
            "good" if eps_assessment == "good" and pe_assessment == "good" else "poor") + " financial standing."

    return financial_health


# Streamlit App
def main():
    st.title("Company Financial Performance Forecast")

    company_symbol = st.text_input("Enter Company Symbol (e.g., AAPL for Apple)", "AAPL")

    # Get financial data and news
    stock_data = get_stock_data(company_symbol, alpha_vantage_api_key)
    company_overview = get_company_overview(company_symbol, alpha_vantage_api_key)

    # Get the company name from the overview (or fallback to the symbol if not available)
    company_name = company_overview.get('Name', company_symbol)  # Use the company name if available, else fallback to symbol

    news_data = get_news_data(company_name, news_api_key)

    # Display General Company Overview
    if company_overview:
        st.subheader(f"{company_name} - General Overview")
        st.write(f"**Market Cap**: {company_overview.get('MarketCapitalization', 'N/A')}")
        st.write(f"**P/E Ratio**: {company_overview.get('PERatio', 'N/A')}")
        st.write(f"**EPS**: {company_overview.get('EPS', 'N/A')}")
        st.write(f"**EBITDA**: {company_overview.get('EBITDA', 'N/A')}")
        st.write(f"**52 Week High**: {company_overview.get('52WeekHigh', 'N/A')}")
        st.write(f"**52 Week Low**: {company_overview.get('52WeekLow', 'N/A')}")
    else:
        st.write("Unable to retrieve company overview data.")

    # Display AI-generated Financial Report
    if company_overview:
        st.subheader(f"{company_name} - Financial Report")
        report = generate_financial_report(company_overview)
        st.write(report)
    else:
        st.write("Unable to generate a financial report for the selected company.")

    # Display Stock Graph
    if stock_data:
        st.subheader(f"{company_name} - Stock Price Over Time")
        stock_fig = plot_stock_data(stock_data)
        st.plotly_chart(stock_fig)

        # Display Forecast for Next Day
        predicted_price = forecast_stock_data(stock_data)
        st.write(f"**Forecasted Price for Next Day**: ${predicted_price:.2f}")

    else:
        st.write("Failed to retrieve stock data.")

    # Display News Data (only 2 articles initially)
    if news_data:
        st.subheader(f"Latest News on {company_name}")

        # Show top 2 articles by default
        for article in news_data[:2]:
            st.write(f"- {article['title']}")
            st.write(f"  Source: {article['source']['name']}")
            st.write(f"  Link: {article['url']}")
            sentiment = get_sentiment(article['title'])
            st.write(f"  Sentiment: {sentiment}")

        # Add dropdown to show more articles
        if len(news_data) > 2:
            with st.expander("View More Articles"):
                forimport requests
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.linear_model import LinearRegression
import numpy as np

# API keys
alpha_vantage_api_key = '1UDQXIUV6X6G8P5C'
news_api_key = 'c82f8dfe888a443e93ae468a52f6cda2'


# Function to fetch stock data from Alpha Vantage
def get_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    print(f"Stock Data Response: {response.json()}")  # Debugging API response
    data = response.json()
    return data['Time Series (Daily)'] if 'Time Series (Daily)' in data else {}


# Function to fetch company overview from Alpha Vantage
def get_company_overview(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    print(f"Company Overview Response: {response.json()}")  # Debugging API response
    return response.json() if response.status_code == 200 else {}


# Function to fetch news data from NewsAPI
def get_news_data(company_name, api_key):
    url = f'https://newsapi.org/v2/everything?q={company_name}&apiKey={api_key}'
    response = requests.get(url)
    return response.json()['articles'] if 'articles' in response.json() else []


# Function to analyze sentiment of a text
def get_sentiment(text):
    if not text:
        return "N/A"

    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] >= 0.05:
        return "Positive"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"


# Function to plot stock data
def plot_stock_data(stock_data):
    dates = list(stock_data.keys())
    prices = [float(stock_data[date]['4. close']) for date in dates]

    fig = go.Figure(data=go.Scatter(x=dates, y=prices))
    fig.update_layout(
        title="Stock Price Over Time",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis=dict(tickformat='%Y-%m-%d'),
        template="plotly_dark"
    )
    return fig


# Function to forecast future stock price using linear regression
def forecast_stock_data(stock_data):
    # Convert date to numerical format for regression
    dates = list(stock_data.keys())[-30:]  # Get the last 30 days of stock data for forecasting
    prices = [float(stock_data[date]['4. close']) for date in dates]

    # Prepare data for linear regression
    X = np.array(range(len(prices))).reshape(-1, 1)  # Days as numbers
    y = np.array(prices)

    model = LinearRegression()
    model.fit(X, y)

    # Predict future price (for the next day)
    future_day = np.array([[len(prices)]])
    predicted_price = model.predict(future_day)[0]

    return predicted_price


# AI-generated financial report
def generate_financial_report(company_overview):
    market_cap = company_overview.get('MarketCapitalization', 'N/A')
    pe_ratio = company_overview.get('PERatio', 'N/A')
    eps = company_overview.get('EPS', 'N/A')
    ebitda = company_overview.get('EBITDA', 'N/A')
    high_52week = company_overview.get('52WeekHigh', 'N/A')
    low_52week = company_overview.get('52WeekLow', 'N/A')

    # Basic assessment based on some values
    if market_cap == 'N/A' or pe_ratio == 'N/A' or eps == 'N/A':
        financial_health = "The financial data for this company could not be retrieved, so it is difficult to assess its current financial health."
    else:
        pe_assessment = "good" if float(pe_ratio) < 20 else "bad"
        eps_assessment = "good" if float(eps) > 0 else "bad"

        # Construct a report based on this information
        financial_health = f"The company has a market capitalization of {market_cap}, which is a solid indicator of its size in the market. The P/E ratio is {pe_ratio}, which is considered {pe_assessment}, and the EPS is {eps}, which is considered {eps_assessment}."

        if high_52week != 'N/A' and low_52week != 'N/A':
            financial_health += f" The company’s stock has a 52-week range from {low_52week} to {high_52week}, which can provide insights into the stock's volatility."

        financial_health += " Based on these metrics, the company seems to be in " + (
            "good" if eps_assessment == "good" and pe_assessment == "good" else "poor") + " financial standing."

    return financial_health


# Streamlit App
def main():
    st.title("Company Financial Performance Forecast")

    company_symbol = st.text_input("Enter Company Symbol (e.g., AAPL for Apple)", "AAPL")

    # Get financial data and news
    stock_data = get_stock_data(company_symbol, alpha_vantage_api_key)
    company_overview = get_company_overview(company_symbol, alpha_vantage_api_key)

    # Get the company name from the overview (or fallback to the symbol if not available)
    company_name = company_overview.get('Name', company_symbol)  # Use the company name if available, else fallback to symbol

    news_data = get_news_data(company_name, news_api_key)

    # Display General Company Overview
    if company_overview:
        st.subheader(f"{company_name} - General Overview")
        st.write(f"**Market Cap**: {company_overview.get('MarketCapitalization', 'N/A')}")
        st.write(f"**P/E Ratio**: {company_overview.get('PERatio', 'N/A')}")
        st.write(f"**EPS**: {company_overview.get('EPS', 'N/A')}")
        st.write(f"**EBITDA**: {company_overview.get('EBITDA', 'N/A')}")
        st.write(f"**52 Week High**: {company_overview.get('52WeekHigh', 'N/A')}")
        st.write(f"**52 Week Low**: {company_overview.get('52WeekLow', 'N/A')}")
    else:
        st.write("Unable to retrieve company overview data.")

    # Display AI-generated Financial Report
    if company_overview:
        st.subheader(f"{company_name} - Financial Report")
        report = generate_financial_report(company_overview)
        st.write(report)
    else:
        st.write("Unable to generate a financial report for the selected company.")

    # Display Stock Graph
    if stock_data:
        st.subheader(f"{company_name} - Stock Price Over Time")
        stock_fig = plot_stock_data(stock_data)
        st.plotly_chart(stock_fig)

        # Display Forecast for Next Day
        predicted_price = forecast_stock_data(stock_data)
        st.write(f"**Forecasted Price for Next Day**: ${predicted_price:.2f}")

    else:
        st.write("Failed to retrieve stock data.")

    # Display News Data (only 2 articles initially)
    if news_data:
        st.subheader(f"Latest News on {company_name}")

        # Show top 2 articles by default
        for article in news_data[:2]:
            st.write(f"- {article['title']}")
            st.write(f"  Source: {article['source']['name']}")
            st.write(f"  Link: {article['url']}")
            sentiment = get_sentiment(article['title'])
            st.write(f"  Sentiment: {sentiment}")

        # Add dropdown to show more articles
        if len(news_data) > 2:
            with st.expander("View More Articles"):
                for article in news_data[2:]:
                    st.write(f"- {article['title']}")
                    st.write(f"  Source: {article['source']['name']}")
                    st.write(f"  Link: {article['url']}")
                    sentiment = get_sentiment(article['title'])
                    st.write(f"  Sentiment: {sentiment}")

    else:
        st.write("No news data available.")


# Run the app
if __name__ == "__main__":
    main()
 article in news_data[2:]:
                    st.write(f"- {article['title']}")
                    st.write(f"  Source: {article['source']['name']}")
                    st.write(f"  Link: {article['url']}")
                    sentiment = get_sentiment(article['title'])
                    st.write(f"  Sentiment: {sentiment}")

    else:
        st.write("No news data available.")


# Run the app
if __name__ == "__main__":
    main()
