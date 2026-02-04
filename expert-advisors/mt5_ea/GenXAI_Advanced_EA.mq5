//+------------------------------------------------------------------+
//|                                           GenXAI_Advanced_EA.mq5 |
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
input string API_URL = "http://localhost:8000/api/v1";
input string API_KEY = "";
input int API_TIMEOUT = 5000;

input group "=== Trading Parameters ==="
input double LotSize = 0.1;
input double MaxRisk = 0.02;
input double StopLossPercent = 0.02;
input double TakeProfitPercent = 0.04;
input int MaxPositions = 3;
input int MagicNumber = 123456;
input int MaxSpread = 50;
input string TradingHours = "00:00-23:59";
input bool UseTrailingStop = true;
input double TrailingDistance = 50;

input group "=== AI Parameters ==="
input bool UseEnsembleModel = true;
input double MinConfidence = 0.7;
input int PredictionInterval = 300; // 5 minutes
input bool UseRealTimeTraining = true;

input group "=== Risk Management ==="
input double MaxDrawdown = 0.15;
input double DailyLossLimit = 0.05;
input bool UsePositionSizing = true;
input double VolatilityMultiplier = 1.5;

//--- Global variables
CTrade trade;
CiMA ma_fast, ma_slow;
CiRSI rsi;
CiMACD macd;
CiATR atr;

datetime lastPrediction = 0;
double currentBalance = 0;
double startBalance = 0;
double dailyPnL = 0;
datetime lastDayCheck = 0;

struct AISignal {
    string symbol;
    int signal; // 1 = buy, -1 = sell, 0 = hold
    double confidence;
    double entry_price;
    double stop_loss;
    double take_profit;
    datetime timestamp;
};

AISignal lastSignal;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    Print("GenXAI Advanced EA v2.0 - Initializing...");
    
    // Initialize trading
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints(10);
    trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    // Initialize indicators
    ma_fast.Create(_Symbol, PERIOD_CURRENT, 10, 0, MODE_EMA, PRICE_CLOSE);
    ma_slow.Create(_Symbol, PERIOD_CURRENT, 20, 0, MODE_EMA, PRICE_CLOSE);
    rsi.Create(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
    macd.Create(_Symbol, PERIOD_CURRENT, 12, 26, 9, PRICE_CLOSE);
    atr.Create(_Symbol, PERIOD_CURRENT, 14);
    
    // Initialize balance tracking
    startBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    currentBalance = startBalance;
    
    Print("GenXAI Advanced EA initialized successfully");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("GenXAI Advanced EA deinitialized. Reason: ", reason);
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
    if (SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > MaxSpread) {
        return;
    }

    // Check trading hours
    if (!IsTradingTime()) {
        return;
    }
    
    // Get AI prediction
    if (TimeCurrent() - lastPrediction > PredictionInterval) {
        GetAIPrediction();
        lastPrediction = TimeCurrent();
    }
    
    // Process trading signals
    ProcessTradingSignals();
    
    // Manage existing positions
    ManagePositions();
    
    // Update trailing stops
    if (UseTrailingStop) {
        UpdateTrailingStops();
    }
}

//+------------------------------------------------------------------+
//| Get AI prediction from API                                       |
//+------------------------------------------------------------------+
void GetAIPrediction() {
    string url = API_URL + "/predictions";
    string headers = "Content-Type: application/json\r\nAuthorization: Bearer " + API_KEY;
    
    string request_body = StringFormat(
        "{\"symbol\":\"%s\",\"timeframe\":\"%s\",\"use_ensemble\":%s}",
        _Symbol,
        PeriodToString(PERIOD_CURRENT),
        UseEnsembleModel ? "true" : "false"
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
        Print("AI API Error: ", res);
    }
}

//+------------------------------------------------------------------+
//| Parse AI response                                                |
//+------------------------------------------------------------------+
void ParseAIResponse(string response) {
    // Simple JSON parsing (in production, use proper JSON library)
    lastSignal.symbol = _Symbol;
    lastSignal.timestamp = TimeCurrent();
    
    // Extract signal type
    if (StringFind(response, "\"prediction\":\"long\"") >= 0) {
        lastSignal.signal = 1;
    } else if (StringFind(response, "\"prediction\":\"short\"") >= 0) {
        lastSignal.signal = -1;
    } else {
        lastSignal.signal = 0;
    }
    
    // Extract confidence (simplified)
    int conf_start = StringFind(response, "\"confidence\":");
    if (conf_start >= 0) {
        string conf_str = StringSubstr(response, conf_start + 13, 4);
        lastSignal.confidence = StringToDouble(conf_str);
    }
    
    // Calculate entry, stop loss, and take profit
    double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double atr_value = atr.Main(0);
    
    lastSignal.entry_price = current_price;
    
    if (lastSignal.signal == 1) { // Buy signal
        lastSignal.stop_loss = current_price - (atr_value * 2);
        lastSignal.take_profit = current_price + (atr_value * 3);
    } else if (lastSignal.signal == -1) { // Sell signal
        lastSignal.stop_loss = current_price + (atr_value * 2);
        lastSignal.take_profit = current_price - (atr_value * 3);
    }
    
    Print("AI Signal: ", lastSignal.signal, " Confidence: ", lastSignal.confidence);
}

//+------------------------------------------------------------------+
//| Process trading signals                                          |
//+------------------------------------------------------------------+
void ProcessTradingSignals() {
    if (lastSignal.confidence < MinConfidence) {
        return;
    }
    
    // Check if we have conflicting positions
    if (CountPositions() >= MaxPositions) {
        return;
    }
    
    // Confirm signal with technical indicators
    if (!ConfirmSignalWithTechnicals(lastSignal.signal)) {
        return;
    }
    
    // Calculate position size
    double lot_size = CalculatePositionSize();
    
    // Execute trade
    if (lastSignal.signal == 1 && CountPositions(POSITION_TYPE_BUY) == 0) {
        ExecuteBuyOrder(lot_size);
    } else if (lastSignal.signal == -1 && CountPositions(POSITION_TYPE_SELL) == 0) {
        ExecuteSellOrder(lot_size);
    }
}

//+------------------------------------------------------------------+
//| Confirm signal with technical indicators                        |
//+------------------------------------------------------------------+
bool ConfirmSignalWithTechnicals(int signal) {
    double ma_fast_val = ma_fast.Main(0);
    double ma_slow_val = ma_slow.Main(0);
    double rsi_val = rsi.Main(0);
    double macd_val = macd.Main(0);
    
    if (signal == 1) { // Buy confirmation
        return (ma_fast_val > ma_slow_val && rsi_val < 70 && macd_val > 0);
    } else if (signal == -1) { // Sell confirmation
        return (ma_fast_val < ma_slow_val && rsi_val > 30 && macd_val < 0);
    }
    
    return false;
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
    
    double stop_distance = MathAbs(lastSignal.entry_price - lastSignal.stop_loss);
    double point_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    
    double lot_size = risk_amount / (stop_distance / tick_size * point_value);
    
    // Apply volatility adjustment
    double atr_value = atr.Main(0);
    double avg_atr = 0;
    for (int i = 0; i < 20; i++) {
        avg_atr += atr.Main(i);
    }
    avg_atr /= 20;
    
    double volatility_ratio = atr_value / avg_atr;
    lot_size /= (volatility_ratio * VolatilityMultiplier);
    
    // Normalize lot size
    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    lot_size = NormalizeDouble(lot_size, 2);
    lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
    
    return lot_size;
}

//+------------------------------------------------------------------+
//| Execute buy order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder(double lot_size) {
    double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    
    if (trade.Buy(lot_size, _Symbol, price, lastSignal.stop_loss, lastSignal.take_profit)) {
        Print("Buy order executed: ", lot_size, " lots at ", price);
        
        // Send trade notification to API
        SendTradeNotification("BUY", lot_size, price);
    } else {
        Print("Buy order failed: ", trade.ResultRetcode());
    }
}

//+------------------------------------------------------------------+
//| Execute sell order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder(double lot_size) {
    double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    if (trade.Sell(lot_size, _Symbol, price, lastSignal.stop_loss, lastSignal.take_profit)) {
        Print("Sell order executed: ", lot_size, " lots at ", price);
        
        // Send trade notification to API
        SendTradeNotification("SELL", lot_size, price);
    } else {
        Print("Sell order failed: ", trade.ResultRetcode());
    }
}

//+------------------------------------------------------------------+
//| Check risk management                                            |
//+------------------------------------------------------------------+
bool CheckRiskManagement() {
    currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // Check maximum drawdown
    double drawdown = (startBalance - equity) / startBalance;
    if (drawdown > MaxDrawdown) {
        Print("Maximum drawdown reached: ", drawdown * 100, "%");
        CloseAllPositions();
        return false;
    }
    
    // Check daily loss limit
    datetime current_day = TimeCurrent() / 86400 * 86400;
    if (current_day != lastDayCheck) {
        dailyPnL = 0;
        lastDayCheck = current_day;
    }
    
    double current_pnl = equity - currentBalance;
    dailyPnL += current_pnl;
    
    if (dailyPnL < -startBalance * DailyLossLimit) {
        Print("Daily loss limit reached: ", dailyPnL);
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
                    if (new_sl < current_sl) {
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
