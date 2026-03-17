"""
visualizer.py
=============

Creates beautiful stock price charts.

Day 2 - Part 1
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from stock_database import StockTable


class StockVisualizer:
    """
    Create visualizations for stock data.
    """
    
    def __init__(self):
        """Initialize visualizer"""
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_price_history(self, symbol, days=30, save=True):
        """
        Plot stock price history.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            days: Number of days to show
            save: Whether to save chart as PNG
        """
        print(f"\n[Visualizer] Creating chart for {symbol}...")
        
        # Get data from database
        db = StockTable("stocks.db")
        all_rows = list(db.select_by_symbol(symbol))
        rows = all_rows[-days:] if len(all_rows) > days else all_rows
        db.close()
        
        if not rows:
            print(f"[Visualizer] ERROR: No data found for {symbol}")
            return
        
        # Extract data
        dates = [row.date for row in rows]
        closes = [row.close for row in rows]
        highs = [row.high for row in rows]
        lows = [row.low for row in rows]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Plot price line
        ax.plot(dates, closes, 
                color='#2E86AB', 
                linewidth=2.5, 
                marker='o', 
                markersize=4,
                label='Close Price')
        
        # Add high/low range
        ax.fill_between(dates, lows, highs, 
                        alpha=0.2, 
                        color='#A23B72',
                        label='Daily Range (High-Low)')
        
        # Formatting
        ax.set_title(f'{symbol} Stock Price - Last {len(rows)} Days', 
                    fontsize=18, 
                    fontweight='bold',
                    pad=20)
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        
        # Rotate date labels
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc='best', fontsize=10)
        
        # Add current price annotation
        current_price = closes[-1]
        ax.annotate(f'${current_price:.2f}', 
                   xy=(dates[-1], current_price),
                   xytext=(10, 10), 
                   textcoords='offset points',
                   fontsize=12,
                   fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', 
                            facecolor='yellow', 
                            alpha=0.7))
        
        # Tight layout
        plt.tight_layout()
        
        # Save or show
        if save:
            filename = f'{symbol}_price_chart.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"[Visualizer] ✓ Chart saved: {filename}")
        else:
            plt.show()
        
        plt.close()
        
        return filename if save else None
    
    def plot_multiple_stocks(self, symbols, days=30):
        """
        Compare multiple stocks on one chart.
        
        Args:
            symbols: List of stock tickers
            days: Number of days to show
        """
        print(f"\n[Visualizer] Creating comparison chart for {len(symbols)} stocks...")
        
        # Get data for all stocks
        db = StockTable("stocks.db")
        stock_data = {}
        
        for symbol in symbols:
            all_rows = list(db.select_by_symbol(symbol))
            rows = all_rows[-days:] if len(all_rows) > days else all_rows
            
            if rows:
                dates = [row.date for row in rows]
                closes = [row.close for row in rows]
                
                # Normalize to percentage change from first day
                first_price = closes[0]
                normalized = [(price / first_price - 1) * 100 for price in closes]
                
                stock_data[symbol] = {
                    'dates': dates,
                    'normalized': normalized
                }
        
        db.close()
        
        if not stock_data:
            print("[Visualizer] ERROR: No data found")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Plot each stock
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        
        for i, (symbol, data) in enumerate(stock_data.items()):
            ax.plot(data['dates'], 
                   data['normalized'], 
                   color=colors[i % len(colors)],
                   linewidth=2.5,
                   marker='o',
                   markersize=4,
                   label=symbol)
        
        # Formatting
        ax.set_title('Stock Performance Comparison (% Change)', 
                    fontsize=18, 
                    fontweight='bold',
                    pad=20)
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Change (%)', fontsize=12, fontweight='bold')
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Rotate date labels
        plt.xticks(rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Legend
        ax.legend(loc='best', fontsize=12)
        
        plt.tight_layout()
        
        # Save
        filename = 'comparison_chart.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"[Visualizer] ✓ Comparison chart saved: {filename}")
        
        plt.close()
        
        return filename
    
    def create_summary_stats(self, symbol):
        """
        Create summary statistics visualization.
        
        Args:
            symbol: Stock ticker
        """
        print(f"\n[Visualizer] Creating summary stats for {symbol}...")
        
        # Get data
        db = StockTable("stocks.db")
        rows = list(db.select_by_symbol(symbol))
        db.close()
        
        if not rows:
            print(f"[Visualizer] ERROR: No data found for {symbol}")
            return
        
        # Calculate stats
        closes = [row.close for row in rows]
        volumes = [row.volume for row in rows]
        
        current = closes[-1]
        avg = sum(closes) / len(closes)
        highest = max(closes)
        lowest = min(closes)
        volatility = (max(closes) - min(closes)) / avg * 100
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Left: Price statistics
        stats = {
            'Current': current,
            'Average': avg,
            'Highest': highest,
            'Lowest': lowest
        }
        
        colors = ['#2E86AB', '#A23B72', '#10b981', '#ef4444']
        bars = ax1.bar(stats.keys(), stats.values(), color=colors, alpha=0.7)
        
        ax1.set_title(f'{symbol} Price Statistics', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.2f}',
                    ha='center', va='bottom', fontweight='bold')
        
        # Right: Volume over time
        dates = [row.date for row in rows[-20:]]  # Last 20 days
        recent_volumes = volumes[-20:]
        
        ax2.bar(range(len(recent_volumes)), recent_volumes, 
               color='#6A994E', alpha=0.7)
        ax2.set_title('Trading Volume (Last 20 Days)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Days Ago', fontsize=12)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add volatility text
        fig.text(0.5, 0.02, 
                f'Volatility: {volatility:.2f}% | Total Data Points: {len(rows)}',
                ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        filename = f'{symbol}_summary_stats.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"[Visualizer] ✓ Summary stats saved: {filename}")
        
        plt.close()
        
        return filename


# ============================================================================
# DEMO
# ============================================================================

def demo_visualizer():
    """
    Demo: Create all visualizations
    """
    print("="*70)
    print("STOCK VISUALIZER DEMO")
    print("="*70)
    
    viz = StockVisualizer()
    
    # Individual stock charts
    print("\n--- Creating individual stock charts ---")
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    for symbol in symbols:
        viz.plot_price_history(symbol, days=30)
    
    # Comparison chart
    print("\n--- Creating comparison chart ---")
    viz.plot_multiple_stocks(symbols, days=30)
    
    # Summary stats
    print("\n--- Creating summary statistics ---")
    for symbol in symbols:
        viz.create_summary_stats(symbol)
    
    print("\n" + "="*70)
    print("✓ ALL VISUALIZATIONS CREATED!")
    print("="*70)
    print("\nGenerated files:")
    print("  📊 AAPL_price_chart.png")
    print("  📊 GOOGL_price_chart.png")
    print("  📊 MSFT_price_chart.png")
    print("  📊 comparison_chart.png")
    print("  📊 AAPL_summary_stats.png")
    print("  📊 GOOGL_summary_stats.png")
    print("  📊 MSFT_summary_stats.png")
    print("\n✓ Check your project folder for beautiful charts!")
    print("="*70)


if __name__ == "__main__":
    demo_visualizer()