//+------------------------------------------------------------------+
//|                                           EXNESS_GenX_Trader.mq5 |
//|                                  Copyright 2024, GenX Trading    |
//|                                             https://genx.trade    |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, GenX Trading"
#property link      "https://genx.trade"
#property version   "2.00"
#property strict

#include <Trade\Trade.mqh>
#include <Indicators\Indicators.mqh>

//--- Input parameters
input group "=== API Configuration ==="
input bool   UseAI = true;                    // Use AI Server for signals
input string API_URL = "http://203.147.134.90";
input string API_KEY = "";
input int    API_TIMEOUT = 5000;

input group "=== Trading Parameters ==="
input double LotSize = 0.1;
input double MaxRisk = 0.01;
input double StopLossPercent = 0.02;
input double TakeProfitPercent = 0.04;
input int    MaxPositions = 3;
input int    MagicNumber = 123456;
input int    MaxSpread = 50;                  // Max spread in points
input int    MaxSlippage = 10;                // Max slippage in points
input string TradingHours = "00:00-23:59";    // Trading hours (server time)
input bool   UseTrailingStop = true;
input double TrailingDistance = 50;

input group "=== Strategy Parameters ==="
input int    MA_Fast_Period = 10;
input int    MA_Slow_Period = 30;
input int    RSI_Period = 14;
input int    RSI_Overbought = 70;
input int    RSI_Oversold = 30;

input group "=== Risk Management ==="
input double MaxDrawdown = 0.15;
input double DailyLossLimit = 0.05;
input bool   UsePositionSizing = true;
input double VolatilityMultiplier = 1.5;

//--- Global variables
CTrade trade;
CiMA ma_fast, ma_slow;
CiRSI rsi;
CiMACD macd;
CiATR atr;

datetime lastPrediction = 0;
double startBalance = 0;
datetime lastDayCheck = 0;

struct TradingSignal {
    int direction; // 1 = buy, -1 = sell, 0 = none
    double confidence;
    double entry_price;
    double stop_loss;
    double take_profit;
};

TradingSignal currentSignal;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    Print("EXNESS GenX Trader v2.0 Initializing...");
    Print("Symbol: ", _Symbol);
    Print("Strategy: MA(", MA_Fast_Period, "/", MA_Slow_Period, ") + RSI(", RSI_Period, ")");
    Print("Risk: ", MaxRisk * 100, "% per trade");
    Print("Trading: ENABLED");

    // Initialize trading
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints(MaxSlippage);
    trade.SetTypeFilling(ORDER_FILLING_FOK);

    // Initialize indicators
    if (!ma_fast.Create(_Symbol, PERIOD_CURRENT, MA_Fast_Period, 0, MODE_EMA, PRICE_CLOSE)) return INIT_FAILED;
    if (!ma_slow.Create(_Symbol, PERIOD_CURRENT, MA_Slow_Period, 0, MODE_EMA, PRICE_CLOSE)) return INIT_FAILED;
    if (!rsi.Create(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE)) return INIT_FAILED;
    if (!macd.Create(_Symbol, PERIOD_CURRENT, 12, 26, 9, PRICE_CLOSE)) return INIT_FAILED;
    if (!atr.Create(_Symbol, PERIOD_CURRENT, 14)) return INIT_FAILED;

    // Initialize balance tracking
    startBalance = AccountInfoDouble(ACCOUNT_BALANCE);

    Print("EXNESS GenX Trader v2.0 initialized successfully");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("EXNESS GenX Trader v2.0 deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Update indicators
    ma_fast.Refresh();
    ma_slow.Refresh();
    rsi.Refresh();
    macd.Refresh();
    atr.Refresh();

    // Check risk management
    if (!CheckRiskManagement()) {
        return;
    }

    // Check spread
    if (!CheckSpread()) {
        return;
    }

    // Check trading hours
    if (!IsTradingTime()) {
        return;
    }

    // Get Signal
    if (UseAI) {
        // AI Logic
        if (TimeCurrent() - lastPrediction > 300) { // Check every 5 mins
            GetAIPrediction();
            lastPrediction = TimeCurrent();
        }
    } else {
        // Local Strategy Logic
        GetTechnicalSignal();
    }

    // Process trading signals
    ProcessTradingSignals();

    // Update trailing stops
    if (UseTrailingStop) {
        UpdateTrailingStops();
    }
}

//+------------------------------------------------------------------+
//| Get Technical Signal (MA + RSI)                                 |
//+------------------------------------------------------------------+
void GetTechnicalSignal() {
    currentSignal.direction = 0;
    currentSignal.confidence = 0.0;

    double fastVal = ma_fast.Main(0);
    double slowVal = ma_slow.Main(0);
    double rsiVal = rsi.Main(0);

    // MA Crossover + RSI Filter
    // Buy: Fast > Slow AND RSI < Overbought
    if (fastVal > slowVal && rsiVal < RSI_Overbought) {
         // Check if crossover just happened for better entry?
         // For simplicity, just check condition.
         currentSignal.direction = 1;
         currentSignal.confidence = 0.8; // High confidence for technicals
    }
    // Sell: Fast < Slow AND RSI > Oversold
    else if (fastVal < slowVal && rsiVal > RSI_Oversold) {
         currentSignal.direction = -1;
         currentSignal.confidence = 0.8;
    }

    // Calculate SL/TP based on ATR
    double current_price = (currentSignal.direction == 1) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double atr_value = atr.Main(0);

    currentSignal.entry_price = current_price;
    if (currentSignal.direction == 1) {
        currentSignal.stop_loss = current_price - (atr_value * 2);
        currentSignal.take_profit = current_price + (atr_value * 3);
    } else if (currentSignal.direction == -1) {
        currentSignal.stop_loss = current_price + (atr_value * 2);
        currentSignal.take_profit = current_price - (atr_value * 3);
    }
}

//+------------------------------------------------------------------+
//| Get AI prediction from API                                       |
//+------------------------------------------------------------------+
void GetAIPrediction() {
    string url = API_URL + "/predictions";
    string headers = "Content-Type: application/json\r\nAuthorization: Bearer " + API_KEY;

    string request_body = StringFormat(
        "{\"symbol\":\"%s\",\"timeframe\":\"%s\",\"use_ensemble\":true}",
        _Symbol,
        PeriodToString(PERIOD_CURRENT)
    );

    char post_data[];
    char result[];
    string result_headers;

    ArrayResize(post_data, StringToCharArray(request_body, post_data) - 1);

    int res = WebRequest(
        "POST",
        url,
        headers,
        API_TIMEOUT,
        post_data,
        result,
        result_headers
    );

    if (res == 200) {
        ParseAIResponse(CharArrayToString(result));
    } else {
        // Print("AI API Error: ", res);
    }
}

//+------------------------------------------------------------------+
//| Parse AI response                                                |
//+------------------------------------------------------------------+
void ParseAIResponse(string response) {
    // Simple JSON parsing
    if (StringFind(response, "\"prediction\":\"long\"") >= 0) {
        currentSignal.direction = 1;
    } else if (StringFind(response, "\"prediction\":\"short\"") >= 0) {
        currentSignal.direction = -1;
    } else {
        currentSignal.direction = 0;
    }

    // Extract confidence... (simplified)
    currentSignal.confidence = 0.8; // Default if parsing fails

    // SL/TP from ATR
    double current_price = (currentSignal.direction == 1) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double atr_value = atr.Main(0);

    currentSignal.entry_price = current_price;
    if (currentSignal.direction == 1) {
        currentSignal.stop_loss = current_price - (atr_value * 2);
        currentSignal.take_profit = current_price + (atr_value * 3);
    } else if (currentSignal.direction == -1) {
        currentSignal.stop_loss = current_price + (atr_value * 2);
        currentSignal.take_profit = current_price - (atr_value * 3);
    }
}

//+------------------------------------------------------------------+
//| Process trading signals                                          |
//+------------------------------------------------------------------+
void ProcessTradingSignals() {
    if (currentSignal.direction == 0) return;

    // Check Max Positions
    if (CountPositions() >= MaxPositions) {
        return;
    }

    // Check for existing position in same direction
    if (currentSignal.direction == 1 && CountPositions(POSITION_TYPE_BUY) > 0) return;
    if (currentSignal.direction == -1 && CountPositions(POSITION_TYPE_SELL) > 0) return;

    // Calculate position size
    double lot_size = CalculatePositionSize();

    // Execute
    if (currentSignal.direction == 1) {
        ExecuteBuyOrder(lot_size);
    } else if (currentSignal.direction == -1) {
        ExecuteSellOrder(lot_size);
    }

    // Reset signal after processing
    currentSignal.direction = 0;
}

//+------------------------------------------------------------------+
//| Calculate position size based on risk                           |
//+------------------------------------------------------------------+
double CalculatePositionSize() {
    if (!UsePositionSizing) {
        return LotSize;
    }

    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = balance * MaxRisk;

    double stop_distance = MathAbs(currentSignal.entry_price - currentSignal.stop_loss);
    if (stop_distance == 0) stop_distance = 100 * _Point; // Safety fallback

    double point_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

    if (tick_size == 0) return LotSize; // Safety

    double lot_size = risk_amount / (stop_distance / tick_size * point_value);

    // Normalize lot size
    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

    // Normalize to steps
    lot_size = MathFloor(lot_size / lot_step) * lot_step;

    lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));

    return lot_size;
}

//+------------------------------------------------------------------+
//| Execute buy order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder(double lot_size) {
    double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

    if (trade.Buy(lot_size, _Symbol, price, currentSignal.stop_loss, currentSignal.take_profit)) {
        Print("Buy order executed: ", lot_size, " lots at ", price);
        if (UseAI) SendTradeNotification("BUY", lot_size, price);
    } else {
        Print("Buy order failed: ", trade.ResultRetcode());
    }
}

//+------------------------------------------------------------------+
//| Execute sell order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder(double lot_size) {
    double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

    if (trade.Sell(lot_size, _Symbol, price, currentSignal.stop_loss, currentSignal.take_profit)) {
        Print("Sell order executed: ", lot_size, " lots at ", price);
        if (UseAI) SendTradeNotification("SELL", lot_size, price);
    } else {
        Print("Sell order failed: ", trade.ResultRetcode());
    }
}

//+------------------------------------------------------------------+
//| Check risk management                                            |
//+------------------------------------------------------------------+
bool CheckRiskManagement() {
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);

    // Check maximum drawdown from start
    double drawdown = (startBalance - equity) / startBalance;
    if (drawdown > MaxDrawdown) {
        Print("Maximum drawdown reached: ", drawdown * 100, "%");
        CloseAllPositions();
        return false;
    }

    // Simple Daily Loss Limit Approximation
    // If equity is below (startBalance * (1 - DailyLossLimit)), stop trading.
    // NOTE: In a real production EA, this should reset daily.
    // Here we use startBalance as reference.
    if (equity < startBalance * (1 - DailyLossLimit)) {
         Print("Loss limit reached relative to start balance.");
         CloseAllPositions();
         return false;
    }

    return true;
}

//+------------------------------------------------------------------+
//| Count positions                                                  |
//+------------------------------------------------------------------+
int CountPositions(ENUM_POSITION_TYPE type = -1) {
    int count = 0;

    for (int i = 0; i < PositionsTotal(); i++) {
        if (PositionGetTicket(i) > 0) {
            if (PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                if (type == -1 || PositionGetInteger(POSITION_TYPE) == type) {
                    count++;
                }
            }
        }
    }

    return count;
}

//+------------------------------------------------------------------+
//| Update trailing stops                                            |
//+------------------------------------------------------------------+
void UpdateTrailingStops() {
    for (int i = 0; i < PositionsTotal(); i++) {
        if (PositionGetTicket(i) > 0) {
            if (PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                double current_sl = PositionGetDouble(POSITION_SL);
                double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                double new_sl = current_sl;

                if (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                    new_sl = current_price - TrailingDistance * _Point;
                    if (new_sl > current_sl) {
                        trade.PositionModify(PositionGetTicket(i), new_sl, PositionGetDouble(POSITION_TP));
                    }
                } else {
                    new_sl = current_price + TrailingDistance * _Point;
                    if (new_sl < current_sl || current_sl == 0) {
                        trade.PositionModify(PositionGetTicket(i), new_sl, PositionGetDouble(POSITION_TP));
                    }
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Send trade notification to API                                   |
//+------------------------------------------------------------------+
void SendTradeNotification(string action, double volume, double price) {
    string url = API_URL + "/trading/notifications";
    string headers = "Content-Type: application/json\r\nAuthorization: Bearer " + API_KEY;

    string request_body = StringFormat(
        "{\"symbol\":\"%s\",\"action\":\"%s\",\"volume\":%.2f,\"price\":%.5f,\"timestamp\":\"%s\"}",
        _Symbol,
        action,
        volume,
        price,
        TimeToString(TimeCurrent())
    );

    char post_data[];
    char result[];
    string result_headers;

    ArrayResize(post_data, StringToCharArray(request_body, post_data) - 1);

    WebRequest("POST", url, headers, API_TIMEOUT, post_data, result, result_headers);
}

//+------------------------------------------------------------------+
//| Close all positions                                              |
//+------------------------------------------------------------------+
void CloseAllPositions() {
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (PositionGetTicket(i) > 0) {
            if (PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                trade.PositionClose(PositionGetTicket(i));
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Check spread                                                     |
//+------------------------------------------------------------------+
bool CheckSpread() {
    long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
    if (spread > MaxSpread) {
        // Only print occasionally to avoid log spam? Or just return false.
        // Print("Spread too high: ", spread);
        return false;
    }
    return true;
}

//+------------------------------------------------------------------+
//| Check trading hours                                              |
//+------------------------------------------------------------------+
bool IsTradingTime() {
    datetime current_time = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(current_time, dt);

    string current_time_str = StringFormat("%02d:%02d", dt.hour, dt.min);

    // Parse TradingHours "HH:MM-HH:MM"
    string parts[];
    if (StringSplit(TradingHours, '-', parts) == 2) {
        string start_time = parts[0];
        string end_time = parts[1];

        if (current_time_str >= start_time && current_time_str <= end_time) {
            return true;
        }
    } else {
        // If format is wrong, default to true or log error?
        // We'll assume always trade if format is bad for safety, or better:
        return true;
    }

    return false;
}

//+------------------------------------------------------------------+
//| Helper function to convert period to string                     |
//+------------------------------------------------------------------+
string PeriodToString(ENUM_TIMEFRAMES period) {
    switch(period) {
        case PERIOD_M1: return "1m";
        case PERIOD_M5: return "5m";
        case PERIOD_M15: return "15m";
        case PERIOD_M30: return "30m";
        case PERIOD_H1: return "1h";
        case PERIOD_H4: return "4h";
        case PERIOD_D1: return "1d";
        default: return "1h";
    }
}
