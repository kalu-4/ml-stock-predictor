ML Stock Price Prediction Platform

A machine learning project that predicts stock prices. Gets about 75% directional accuracy on test data.

⚠️ IMPORTANT: This is an educational project. Don't use it for real trading. Financial markets are complex, and simple models miss crucial factors.

Why I Built This

I wanted to learn:

How machine learning pipelines work end-to-end
How to fetch real data and process it
How to train and deploy models
How to build a REST API

This project does all of that, but it's not a money-making tool.

What It Does

Simple version: Takes historical stock prices → trains a model → predicts tomorrow's price.

How it works:

Fetches historical data daily (from Yahoo Finance API)
Calculates features like moving averages and momentum
Trains a linear regression model on past data
Makes predictions for the next day
Serves predictions via REST API
About the Accuracy

75% directional accuracy sounds good, but here's what it means:

The model predicts whether price goes up or down
It gets this right about 75% of the time on test data
Real performance varies by stock:
Apple (AAPL): 78% accurate
Microsoft (MSFT): 72% accurate
Tesla (TSLA): 68% accurate

But here's what it doesn't do:

Doesn't handle market crashes or sudden spikes
Fails when there's big news (earnings, economic reports)
Can't predict market-wide events
Uses only historical price data (no sentiment, no news, no fundamentals)
Getting Started
What You Need
Python 3.9+
PostgreSQL (to store data)
pip
Installation
bash
# Clone it
git clone https://github.com/kalu-4/ml-stock-predictor.git
cd ml-stock-predictor

# Create virtual environment (keeps dependencies separate)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Set up database
python setup_database.py

# Download initial data
python stock_fetcher.py --symbols AAPL GOOGL MSFT

# Start the server
python server.py

Open http://localhost:5000 and you'll see a dashboard with predictions.

How to Use It
Get Price Prediction
bash
curl http://localhost:5000/api/predict/AAPL

Response:

json
{
  "symbol": "AAPL",
  "current_price": 175.43,
  "predicted_price": 178.92,
  "confidence": 0.75,
  "change_percent": 1.99,
  "timestamp": "2025-03-17T10:30:00Z"
}

This means the model predicts AAPL will go to $178.92 (up ~2%).

Get Historical Data
bash
curl http://localhost:5000/api/history/AAPL

Returns last 30 days of data.

Use Python SDK
python
from stock_predictor import StockPredictor

predictor = StockPredictor()
result = predictor.predict('AAPL')

print(f"Predicted price: ${result['predicted_price']:.2f}")
print(f"Confidence: {result['confidence']:.0%}")
Architecture
Yahoo Finance API
        ↓
   Fetch Data Daily
        ↓
   PostgreSQL (store)
        ↓
   ML Model Training
        ↓
   Flask API
        ↓
    Dashboard + REST

Data flow:

Script fetches daily data from Yahoo Finance
Data saved to PostgreSQL
Model trains on historical data
API serves predictions
Web dashboard shows the results
Features
📊 Real stock data — Uses actual market data from Yahoo Finance
🤖 Automated training — Model retrains daily with new data
⚡ Fast predictions — API responds in <100ms
📈 Interactive dashboard — See predictions and history visually
🗄️ Data persistence — All data stored in PostgreSQL
📉 Backtest capability — Test model on historical data
How the Model Works

Step 1: Feature Engineering

7-day moving average (price trend over a week)
14-day moving average (price trend over two weeks)
30-day moving average (longer trend)
Momentum (how fast price is changing)
Volume (how much trading activity)

Step 2: Training

Uses 80% of data to train (learning period)
Tests on 20% of data (validation period)
Model learns: "When these features look like this, price usually goes this direction"

Step 3: Prediction

Takes today's features
Model predicts tomorrow's price

Why linear regression?

Simple to understand
Fast to train
Good baseline to compare against

Why it's not enough:

Real markets are non-linear
Linear regression assumes past patterns continue
Doesn't handle regime changes (calm → volatile market)
Performance (What I Actually Got)
Metric	Value
Directional Accuracy	75%
Mean Absolute Error	2.3%
R² Score	0.68
Training Days	60+
Retraining	Daily at 2 AM

What this means:

Gets direction right 75% of the time
Average prediction error is 2.3% (so prediction is within 2.3%)
Explains 68% of price variance (32% is unexplained)
Pretty mediocre, honestly
What Works

✅ Stable companies (AAPL, MSFT) — Model predicts reasonably well
✅ Normal market days — When nothing special happens
✅ Short-term predictions (1 day ahead) — Easier than long-term
✅ Identifying trends — Up/down direction is mostly correct

What Doesn't Work

❌ Volatile stocks (TSLA) — Too unpredictable
❌ Market crashes — Suddenly breaks pattern
❌ After earnings announcements — New information overwhelms past patterns
❌ Predicting actual price (only direction) — Magnitude is off
❌ Extreme market events — None of this data was in training

What I Learned

Good learning experiences:

Data pipeline (fetch, clean, organize)
Model training (feature engineering, validation)
API design (rest endpoints, response formats)
Database design (indexing for time-series)

Mistakes I made:

Thought accuracy would be higher (it's not magic)
Didn't validate on out-of-sample data initially (overfitting)
Ignored market regimes (bull vs bear markets behave differently)
Used too few features (only technical, no fundamental data)

What I'd do differently:

Use LSTM/GRU neural networks (better for time-series)
Add sentiment analysis from financial news
Include macroeconomic factors (interest rates, inflation)
Predict probabilities, not just direction
Handle different market conditions separately
Project Structure
ml-stock-predictor/
├── api/
│   └── app.py              # Flask REST API
├── models/
│   └── predictor.py        # ML model
├── frontend/
│   └── index.html          # Dashboard UI
├── stock_fetcher.py        # Fetch data from Yahoo
├── stock_database.py       # Database operations
├── simple_predictor.py     # Prediction logic
├── requirements.txt        # Python packages
└── README.md
Testing
bash
# Run unit tests
python -m pytest tests/

# Test API
python test_api.py

# Backtest on historical data
python backtest.py --symbol AAPL --days 30
Configuration

Edit config.py:

python
DATABASE_URL = "postgresql://user:pass@localhost/stockdb"
API_PORT = 5000
STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
TRAINING_DAYS = 60  # Use last 60 days to train
RETRAIN_SCHEDULE = "0 2 * * *"  # Daily at 2 AM
Limitations (Being Real)

Technical limitations:

Linear regression is too simple for stock markets
Only uses price data (no news, sentiment, fundamentals)
Single-timeframe predictions (1 day only)
No handling of market regimes (bull vs bear)
No transaction costs or slippage

Data limitations:

Only 60 days of training data (not enough for good models)
Missing major market events from before training period
No information about company fundamentals
Can't predict unexpected events

Model limitations:

75% accuracy looks good but is random-walk + noise
R² of 0.68 means 32% is unexplained variance
Past performance ≠ future results (especially in markets)
Disclaimer ⚠️

DO NOT use this to make real investment decisions.

This is an educational project. Real trading requires:

Domain knowledge in finance
Risk management strategies
Multiple data sources (not just price)
Understanding of market microstructure
Professional oversight

If you want to learn, great! If you want to make money trading, consult professionals.

Future Ideas (Never Going to Implement)
LSTM neural networks for temporal patterns
News sentiment analysis
Options pricing model
Portfolio optimization
Real-time data with WebSockets
Multi-day predictions
Author

Kalkidan Kerala

GitHub: @kalu-4
LinkedIn: kalkidan-kerala-8456672a0
Email: tsigemariyam18@gmail.com

⭐ If you learned something from this, star the repo!

Feedback welcome — This is a learning project, and I appreciate constructive criticism.
