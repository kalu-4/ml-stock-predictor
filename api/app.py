"""
api/app.py
==========

REST API for stock price predictions.

Day 3 - Part 1
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_database import StockTable
from simple_predictor import get_prediction, train_and_predict

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def home():
    """API home/info endpoint"""
    return jsonify({
        'name': 'Stock Price Predictor API',
        'version': '1.0',
        'endpoints': {
            '/api/stocks': 'GET - List available stocks',
            '/api/predict/<symbol>': 'GET - Get prediction for a stock',
            '/api/history/<symbol>': 'GET - Get price history',
            '/api/train': 'POST - Train/retrain models'
        },
        'status': 'running'
    })


@app.route('/api/stocks')
def get_stocks():
    """
    Get list of available stocks.
    
    Returns:
        JSON list of stock symbols
    """
    try:
        # Get unique symbols from database
        db = StockTable("../stocks.db")
        all_rows = list(db.select_all())
        db.close()
        
        # Extract unique symbols
        symbols = list(set(row.symbol for row in all_rows))
        symbols.sort()
        
        return jsonify({
            'stocks': symbols,
            'count': len(symbols)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict/<symbol>')
def predict(symbol):
    """
    Get price prediction for a stock.
    
    Args:
        symbol: Stock ticker (e.g., AAPL)
    
    Returns:
        JSON with prediction data
    """
    try:
        print(f"\n[API] Prediction request for {symbol}")
        
        # Get prediction
        result = get_prediction(symbol)
        
        current = result['current_price']
        predicted = result['predicted_price']
        change = result['change_percent']
        
        response = {
            'symbol': symbol.upper(),
            'current_price': round(current, 2),
            'predicted_price': round(predicted, 2),
            'change_percent': round(change, 2),
            'direction': 'up' if change > 0 else 'down',
            'confidence': 'medium',  # Could calculate this from R² score
            'timestamp': None  # Could add timestamp
        }
        
        print(f"[API] ✓ Prediction: ${current:.2f} → ${predicted:.2f} ({change:+.2f}%)")
        
        return jsonify(response)
    
    except ValueError as e:
        print(f"[API] ✗ Error: {str(e)}")
        return jsonify({'error': f'Stock {symbol} not found in database'}), 404
    
    except Exception as e:
        print(f"[API] ✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/<symbol>')
def history(symbol):
    """
    Get price history for a stock.
    
    Args:
        symbol: Stock ticker
    
    Query params:
        days: Number of days (default: 30, max: 100)
    
    Returns:
        JSON with historical price data
    """
    try:
        # Get days parameter
        days = request.args.get('days', default=30, type=int)
        days = min(days, 100)  # Cap at 100 days
        
        print(f"\n[API] History request for {symbol} ({days} days)")
        
        # Get data from database
        db = StockTable("../stocks.db")
        all_rows = list(db.select_by_symbol(symbol))
        rows = all_rows[-days:] if len(all_rows) > days else all_rows
        db.close()
        
        if not rows:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        # Format data
        data = [{
            'date': row.date,
            'open': round(row.open, 2),
            'high': round(row.high, 2),
            'low': round(row.low, 2),
            'close': round(row.close, 2),
            'volume': row.volume
        } for row in rows]
        
        # Calculate statistics
        closes = [row.close for row in rows]
        avg_price = sum(closes) / len(closes)
        high_price = max(closes)
        low_price = min(closes)
        
        response = {
            'symbol': symbol.upper(),
            'data': data,
            'count': len(data),
            'statistics': {
                'average': round(avg_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'current': round(closes[-1], 2)
            }
        }
        
        print(f"[API] ✓ Returned {len(data)} data points")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"[API] ✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/train', methods=['POST'])
def train_models():
    """
    Train/retrain ML models for all stocks.
    
    Returns:
        JSON with training results
    """
    try:
        print("\n[API] Training request received")
        
        # Get list of stocks
        db = StockTable("../stocks.db")
        all_rows = list(db.select_all())
        db.close()
        
        symbols = list(set(row.symbol for row in all_rows))
        
        # Train each model
        results = []
        for symbol in symbols:
            print(f"[API] Training {symbol}...")
            result = train_and_predict(symbol)
            results.append({
                'symbol': result['symbol'],
                'r2_score': round(result['r2_score'], 4),
                'mse': round(result['mse'], 2)
            })
        
        print(f"[API] ✓ Trained {len(results)} models")
        
        return jsonify({
            'message': 'Models trained successfully',
            'models': results,
            'count': len(results)
        })
    
    except Exception as e:
        print(f"[API] ✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare')
def compare():
    """
    Compare multiple stocks.
    
    Query params:
        symbols: Comma-separated list of symbols (e.g., AAPL,GOOGL,MSFT)
    
    Returns:
        JSON with comparison data
    """
    try:
        # Get symbols parameter
        symbols_param = request.args.get('symbols', 'AAPL,GOOGL,MSFT')
        symbols = [s.strip().upper() for s in symbols_param.split(',')]
        
        print(f"\n[API] Comparison request for {symbols}")
        
        # Get predictions for each
        comparisons = []
        for symbol in symbols:
            try:
                result = get_prediction(symbol)
                comparisons.append({
                    'symbol': symbol,
                    'current': round(result['current_price'], 2),
                    'predicted': round(result['predicted_price'], 2),
                    'change': round(result['change_percent'], 2)
                })
            except:
                continue
        
        print(f"[API] ✓ Compared {len(comparisons)} stocks")
        
        return jsonify({
            'comparisons': comparisons,
            'count': len(comparisons)
        })
    
    except Exception as e:
        print(f"[API] ✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 STOCK PREDICTOR API")
    print("="*70)
    print("\n📡 Server starting on http://localhost:5000")
    print("\n📚 Available endpoints:")
    print("   GET  /                      - API info")
    print("   GET  /api/stocks            - List stocks")
    print("   GET  /api/predict/<symbol>  - Get prediction")
    print("   GET  /api/history/<symbol>  - Get history")
    print("   GET  /api/compare           - Compare stocks")
    print("   POST /api/train             - Train models")
    print("\n💡 Test in browser:")
    print("   http://localhost:5000/api/predict/AAPL")
    print("   http://localhost:5000/api/stocks")
    print("   http://localhost:5000/api/history/AAPL")
    print("\n⏹️  Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000)