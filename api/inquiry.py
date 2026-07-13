import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime

# ==========================================
# 📊 MULTI-YEAR DATA FETCHER (WITH LOOP)
# ==========================================
def fetch_historical_data_extended(symbol, total_candles=11000):
    """Binance se chunks mein data download karta hai bina limit error ke"""
    url = "https://data-api.binance.vision/api/v3/klines"
    all_candles = []
    end_time = None
    
    limit_per_request = 1000
    candles_needed = total_candles
    
    print(f"[*] Fetching historical data for {symbol}...")
    
    while candles_needed > 0:
        fetch_limit = min(candles_needed, limit_per_request)
        params = {
            'symbol': symbol, 
            'interval': '4h', 
            'limit': fetch_limit
        }
        if end_time:
            params['endTime'] = end_time
            
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if not data or isinstance(data, dict) or len(data) == 0:
                break
                
            batch = []
            for c in data:
                batch.append({
                    'Time': pd.to_datetime(c[0], unit='ms'),
                    'Open': float(c[1]), 'High': float(c[2]), 'Low': float(c[3]),
                    'Close': float(c[4]), 'Volume': float(c[5])
                })
                
            all_candles = batch + all_candles
            end_time = int(data[0][0]) - 1
            candles_needed -= len(data)
            
            time.sleep(0.2) # API Ban avoidance pause
            
        except Exception as e:
            print(f"[-] Error in loop for {symbol}: {e}")
            break
            
    df = pd.DataFrame(all_candles)
    if not df.empty:
        df.drop_duplicates(subset=['Time'], inplace=True)
        df.set_index('Time', inplace=True)
        print(f"[+] Loaded {len(df)} candles for {symbol}")
        return df
    return None

# ==========================================
# 🧠 THE MEGA STRESS TEST ENGINE
# ==========================================
def run_backtest():
    print("=" * 60)
    print("👁️ GOD'S EYE OFFLINE LAB: 5-YEAR MEGA STRESS TEST (8 COINS)")
    print("=" * 60)
    
    # ⏱️ 5 YEARS CONFIGURATION SWITCH (11000 Candles)
    CANDLE_LIMIT = 2200
    
    # 👑 Fetch Master BTC Data
    print(f"[*] Fetching Master BTC Data for {CANDLE_LIMIT} candles...")
    df_btc = fetch_historical_data_extended('BTCUSDT', total_candles=CANDLE_LIMIT)
    if df_btc is None:
        print("[-] Could not fetch BTC data. Exiting.")
        return
        
    df_btc['BTC_EMA_50'] = df_btc['Close'].ewm(span=50, adjust=False).mean()
    
    # 🌟 EXPANDED TO FULL 8-COIN MASTER LIST
        # ⏱️ 1 YEAR CONFIGURATION SWITCH
    CANDLE_LIMIT = 2200
    
    # 🌟 EXPANDED TO 15-COIN MASTER LIST
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 
        'LINKUSDT', 'AVAXUSDT', 'NEARUSDT', 'DOGEUSDT',
        'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'MATICUSDT',
        'SUIUSDT', 'FETUSDT', 'SHIBUSDT'
    ]

    
    total_trades = 0
    total_wins = 0
    total_losses = 0

    for symbol in symbols:
        print(f"\n[*] Simulating {symbol}...")
        df = fetch_historical_data_extended(symbol, total_candles=CANDLE_LIMIT)
        if df is None: continue
        
        # Merge BTC Trend Data
        df = df.join(df_btc[['Close', 'BTC_EMA_50']], rsuffix='_btc')
        df.rename(columns={'Close_btc': 'BTC_Close'}, inplace=True)
        
        # Indicators
        df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['Vol_MA'] = df['Volume'].rolling(window=15).mean()
        
        df['tr0'] = abs(df['High'] - df['Low'])
        df['tr1'] = abs(df['High'] - df['Close'].shift(1))
        df['tr2'] = abs(df['Low'] - df['Close'].shift(1))
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
        df['ATR'] = df['tr'].rolling(window=14).mean()
        df['ATR_MA'] = df['ATR'].rolling(window=50).mean()
        
        df.dropna(inplace=True) 
        
        trades_won = 0
        trades_lost = 0
        
        # Time Machine Simulation Loop
        for i in range(200, len(df) - 1): 
            
            c1_high, c1_low = df['High'].iloc[i-2], df['Low'].iloc[i-2]
            c2_open, c2_close = df['Open'].iloc[i-1], df['Close'].iloc[i-1]
            c3_high, c3_low = df['High'].iloc[i], df['Low'].iloc[i]
            
            c2_volume, c2_vol_ma = df['Volume'].iloc[i-1], df['Vol_MA'].iloc[i-1]
            ema_200 = df['EMA_200'].iloc[i-1]
            atr, atr_ma = df['ATR'].iloc[i-1], df['ATR_MA'].iloc[i-1]
            
            btc_close = df['BTC_Close'].iloc[i-1]
            btc_ema = df['BTC_EMA_50'].iloc[i-1]
            
            btc_trend = "BULLISH" if btc_close > btc_ema else "BEARISH"
            
            if atr < atr_ma: continue
            
            fvg_gap_pct = (abs(c3_low - c1_high) / c2_close) * 100 if c1_high < c3_low else (abs(c1_low - c3_high) / c2_close) * 100
            if fvg_gap_pct < 0.70 or c2_volume < (c2_vol_ma * 1.4): continue
            
            entry, sl, tp, trade_type = None, None, None, None
            
            # 🟢 Bullish FVG Check
            if c1_high < c3_low and c2_close > c2_open and c2_close > ema_200:
                if btc_trend == "BEARISH": continue 
                
                entry = (c1_high + c3_low) / 2
                sl = df['Low'].iloc[i-1]
                if entry > sl:
                    risk = entry - sl
                    if ((risk / entry) * 100) >= 0.40:
                        tp = entry + (5.0 * risk)
                        trade_type = 'LONG'
                        
            # 🔴 Bearish FVG Check
            elif c1_low > c3_high and c2_close < c2_open and c2_close < ema_200:
                if btc_trend == "BULLISH": continue 
                
                entry = (c1_low + c3_high) / 2
                sl = df['High'].iloc[i-1]
                if entry < sl:
                    risk = sl - entry
                    if ((risk / entry) * 100) >= 0.40:
                        tp = entry - (5.0 * risk)
                        trade_type = 'SHORT'
            
            # Outcome Tracking
            if trade_type:
                total_trades += 1
                trade_active = True
                
                for j in range(i + 1, len(df)):
                    future_high = df['High'].iloc[j]
                    future_low = df['Low'].iloc[j]
                    
                    if trade_type == 'LONG':
                        if future_low <= sl:
                            trades_lost += 1
                            total_losses += 1
                            trade_active = False
                            break
                        elif future_high >= tp:
                            trades_won += 1
                            total_wins += 1
                            trade_active = False
                            break
                            
                    elif trade_type == 'SHORT':
                        if future_high >= sl:
                            trades_lost += 1
                            total_losses += 1
                            trade_active = False
                            break
                        elif future_low <= tp:
                            trades_won += 1
                            total_wins += 1
                            trade_active = False
                            break
                
        print(f"   -> {symbol} Finished | Trades: {trades_won + trades_lost} | Won: {trades_won} | Lost: {trades_lost}")

    # ==========================================
    # 🏆 FINAL STRESS TEST REPORT
    # ==========================================
    print("\n" + "=" * 60)
    print(f"📈 THE ULTIMATE 5-YEAR MASTER AUDIT REPORT")
    print("=" * 60)
    print(f"• Total Master Trades Taken : {total_trades}")
    print(f"• Total Wins (1:5 RR)       : {total_wins}")
    print(f"• Total Losses (1R)         : {total_losses}")
    
    if total_trades > 0:
        win_rate = (total_wins / total_trades) * 100
        print(f"• Audited Master Win Rate   : {win_rate:.2f}%")
        
        net_r = (total_wins * 5) - total_losses
        print(f"• Audited Net Profit (R)    : {net_r:+}R")
        
        if net_r > 0:
            print(f"\n🔥 FINAL VERDICT: BACKTEST SUCCESSFUL. System highly viable for live deployment.")
        else:
            print(f"\n⚠️ FINAL VERDICT: STRESS TEST FAILED. Do not deploy.")
    else:
        print("• Win Rate                  : N/A")

if __name__ == "__main__":
    run_backtest()
