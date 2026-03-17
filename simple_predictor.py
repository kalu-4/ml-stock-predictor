"""
simple_predictor.py
===================

Simple ML model for stock price prediction.

Day 2 - Part 2 (FIXED VERSION)
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from stock_database import StockTable
import pickle
import os


class SimpleStockPredictor:
    """
    Simple linear regression predictor for stock prices.
    
    Uses day number as feature to predict price.
    Good baseline model!
    """
    
    def __init__(self, symbol):
        """
        Initialize predictor for a stock.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
        """
        self.symbol = symbol
        self.model = LinearRegression()
        self.is_trained = False
    
    def load_data(self):
        """Load stock data from database"""
        print(f"\n[Predictor] Loading {self.symbol} data...")
        
        # FIXED: Check if running from api/ folder or root folder
        if os.path.exists("../stocks.db"):
            db_path = "../stocks.db"
        elif os.path.exists("stocks.db"):
            db_path = "stocks.db"
        else:
            raise ValueError("stocks.db not found! Run day1_integration.py first.")
        
        db = StockTable(db_path)
        rows = list(db.select_by_symbol(self.symbol))
        db.close()
        
        if not rows:
            raise ValueError(f"No data found for {self.symbol}")
        
        print(f"[Predictor] Loaded {len(rows)} data points")
        return rows
    
    def prepare_features(self, rows):
        """
        Prepare features and target for training.
        
        Features: Day number (0, 1, 2, ...)
        Target: Close price
        """
        # Simple feature: just the day number
        X = np.array([[i] for i in range(len(rows))])
        
        # Target: closing price
        y = np.array([row.close for row in rows])
        
        return X, y
    
    def train(self):
        """Train the model"""
        print(f"\n[Predictor] Training model for {self.symbol}...")
        
        # Load data
        rows = self.load_data()
        
        # Prepare features
        X, y = self.prepare_features(rows)
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate metrics
        y_pred = self.model.predict(X)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        print(f"[Predictor] ✓ Model trained!")
        print(f"[Predictor]   MSE: ${mse:.2f}")
        print(f"[Predictor]   R² Score: {r2:.4f}")
        
        return mse, r2
    
    def predict_next_day(self):
        """
        Predict next day's price.
        
        Returns:
            prediction: Predicted price
            current: Current price
            change_percent: Expected change percentage
        """
        if not self.is_trained:
            raise ValueError("Model not trained! Call train() first.")
        
        # Load data to get current price
        rows = self.load_data()
        current_price = rows[-1].close
        
        # Predict next day (day number = len(rows))
        next_day = len(rows)
        prediction = self.model.predict([[next_day]])[0]
        
        # Calculate change
        change_percent = ((prediction - current_price) / current_price) * 100
        
        return prediction, current_price, change_percent
    
    def save_model(self, filename=None):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        if filename is None:
            # Save relative to where we are
            if os.path.exists("../models"):
                filename = f'../models/{self.symbol}_model.pkl'
            else:
                os.makedirs('models', exist_ok=True)
                filename = f'models/{self.symbol}_model.pkl'
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"[Predictor] ✓ Model saved: {filename}")
    
    def load_model(self, filename=None):
        """Load trained model from disk"""
        if filename is None:
            # Try both possible locations
            if os.path.exists(f'../models/{self.symbol}_model.pkl'):
                filename = f'../models/{self.symbol}_model.pkl'
            elif os.path.exists(f'models/{self.symbol}_model.pkl'):
                filename = f'models/{self.symbol}_model.pkl'
            else:
                raise ValueError(f"Model file not found for {self.symbol}")
        
        if not os.path.exists(filename):
            raise ValueError(f"Model file not found: {filename}")
        
        with open(filename, 'rb') as f:
            self.model = pickle.load(f)
        
        self.is_trained = True
        print(f"[Predictor] ✓ Model loaded: {filename}")


def train_and_predict(symbol):
    """
    Train model and make prediction for a stock.
    
    Args:
        symbol: Stock ticker
    
    Returns:
        dict with prediction results
    """
    predictor = SimpleStockPredictor(symbol)
    
    # Train
    mse, r2 = predictor.train()
    
    # Predict
    prediction, current, change = predictor.predict_next_day()
    
    # Save model
    predictor.save_model()
    
    return {
        'symbol': symbol,
        'current_price': current,
        'predicted_price': prediction,
        'change_percent': change,
        'mse': mse,
        'r2_score': r2
    }


def get_prediction(symbol):
    """
    Get prediction for a stock (load model if exists, train if not).
    
    Args:
        symbol: Stock ticker
    
    Returns:
        dict with prediction results
    """
    predictor = SimpleStockPredictor(symbol)
    
    # Try to load existing model
    # Check both possible locations
    model_file = None
    if os.path.exists(f'../models/{symbol}_model.pkl'):
        model_file = f'../models/{symbol}_model.pkl'
    elif os.path.exists(f'models/{symbol}_model.pkl'):
        model_file = f'models/{symbol}_model.pkl'
    
    if model_file:
        print(f"\n[Predictor] Found existing model for {symbol}")
        predictor.load_model(model_file)
    else:
        print(f"\n[Predictor] No existing model, training new one...")
        predictor.train()
        predictor.save_model()
    
    # Make prediction
    prediction, current, change = predictor.predict_next_day()
    
    return {
        'symbol': symbol,
        'current_price': current,
        'predicted_price': prediction,
        'change_percent': change
    }


# ============================================================================
# DEMO
# ============================================================================

def demo_predictor():
    """
    Demo: Train models and make predictions
    """
    print("="*70)
    print("STOCK PRICE PREDICTOR DEMO")
    print("="*70)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    results = []
    
    print("\n--- Training models and making predictions ---")
    
    for symbol in symbols:
        result = train_and_predict(symbol)
        results.append(result)
    
    # Display results
    print("\n" + "="*70)
    print("PREDICTION RESULTS")
    print("="*70)
    
    for result in results:
        symbol = result['symbol']
        current = result['current_price']
        predicted = result['predicted_price']
        change = result['change_percent']
        
        # Determine direction
        direction = "📈" if change > 0 else "📉"
        color_code = "+" if change > 0 else ""
        
        print(f"\n{symbol} ({direction}):")
        print(f"  Current Price:     ${current:.2f}")
        print(f"  Predicted Tomorrow: ${predicted:.2f}")
        print(f"  Expected Change:    {color_code}{change:.2f}%")
        print(f"  Model Accuracy:     R² = {result['r2_score']:.4f}")
    
    print("\n" + "="*70)
    print("✓ ALL PREDICTIONS COMPLETE!")
    print("="*70)
    print("\n📊 Models saved in 'models/' directory")
    print("🎯 Ready to use in API and dashboard!")
    print("\n💡 Interpretation:")
    print("  • Positive % = Price expected to go UP")
    print("  • Negative % = Price expected to go DOWN")
    print("  • R² closer to 1.0 = Better model fit")
    print("="*70)


def quick_predict(symbol):
    """
    Quick prediction for a single stock.
    
    Args:
        symbol: Stock ticker
    """
    print(f"\n{'='*70}")
    print(f"QUICK PREDICTION: {symbol}")
    print('='*70)
    
    result = get_prediction(symbol)
    
    current = result['current_price']
    predicted = result['predicted_price']
    change = result['change_percent']
    
    direction = "📈 UP" if change > 0 else "📉 DOWN"
    
    print(f"\nCurrent Price:  ${current:.2f}")
    print(f"Predicted:      ${predicted:.2f}")
    print(f"Change:         {change:+.2f}%")
    print(f"Direction:      {direction}")
    print('='*70)


if __name__ == "__main__":
    # Run full demo
    demo_predictor()
    
    # Example: Quick single prediction
    # quick_predict("AAPL")