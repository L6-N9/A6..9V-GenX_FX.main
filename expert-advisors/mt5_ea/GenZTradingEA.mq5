
//+------------------------------------------------------------------+
//|                                               GenZTradingEA.mq5 |
//|                                    GenZ Trading Platform Client |
//|                                               Signal Receiver EA |
//+------------------------------------------------------------------+
#property copyright "GenZ Trading Platform"
#property link      "https://genztradingbot.com"
#property version   "1.00"

#include <Trade\Trade.mqh>
#include <JSON.mqh>

//--- Input parameters
input string ServerURL = "http://localhost:3000"; // Server URL
input string EAName = "GenZ_Scalping_Bot_MT5"; // EA identification name
input double LotSize = 0.01; // Trade lot size
input int MagicNumber = 12345; // Magic number for trades
input int MaxSpread = 30; // Maximum spread in points
input string TradingHours = "00:00-23:59"; // Trading hours (server time)
input bool EnableAutoTrading = true; // Enable automatic trading
input int HeartbeatInterval = 30; // Heartbeat interval in seconds
input int SignalCheckInterval = 5; // Check for signals every X seconds

//--- Global variables
datetime lastHeartbeat = 0;
datetime lastSignalCheck = 0;
string connectionId = "";
bool isConnected = false;
CTrade trade;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("GenZ Trading EA MT5 starting...");
    
    // Set trade parameters
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints(10);
    trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    // Generate unique connection ID
    connectionId = EAName + "_" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "_" + TimeToString(TimeCurrent(), TIME_SECONDS);
    
    // Register with server
    if(RegisterWithServer())
    {
        isConnected = true;
        Print("Successfully connected to GenZ Trading Platform");
        Print("Connection ID: ", connectionId);
    }
    else
    {
        Print("Failed to connect to GenZ Trading Platform");
        return(INIT_FAILED);
    }
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                               |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("GenZ Trading EA MT5 shutting down. Reason: ", reason);
    
    // Unregister from server
    if(isConnected)
    {
        UnregisterFromServer();
    }
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Send heartbeat
    if(TimeCurrent() - lastHeartbeat >= HeartbeatInterval)
    {
        SendHeartbeat();
        lastHeartbeat = TimeCurrent();
    }
    
    // Check for new signals
    if(TimeCurrent() - lastSignalCheck >= SignalCheckInterval)
    {
        CheckForSignals();
        lastSignalCheck = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Register EA with the server                                      |
//+------------------------------------------------------------------+
bool RegisterWithServer()
{
    string url = ServerURL + "/api/mt45/register";
    string headers = "Content-Type: application/json\r\n";
    
    // Create JSON data
    CJAVal json;
    json["eaName"] = EAName;
    json["connectionId"] = connectionId;
    json["accountNumber"] = (long)AccountInfoInteger(ACCOUNT_LOGIN);
    json["symbol"] = Symbol();
    json["timeframe"] = (int)Period();
    json["platform"] = "MT5";
    
    string data = json.Serialize();
    
    char post[], result[];
    string resultHeaders;
    
    // Convert strings to char arrays
    StringToCharArray(data, post, 0, WHOLE_ARRAY, CP_UTF8);
    
    int timeout = 5000;
    int res = WebRequest("POST", url, headers, timeout, post, result, resultHeaders);
    
    if(res == 200)
    {
        string response = CharArrayToString(result, 0, WHOLE_ARRAY, CP_UTF8);
        if(StringFind(response, "\"success\":true") >= 0)
        {
            return true;
        }
    }
    
    Print("Registration failed. HTTP code: ", res);
    return false;
}

//+------------------------------------------------------------------+
//| Unregister EA from the server                                   |
//+------------------------------------------------------------------+
void UnregisterFromServer()
{
    string url = ServerURL + "/api/mt45/unregister";
    string headers = "Content-Type: application/json\r\n";
    
    CJAVal json;
    json["connectionId"] = connectionId;
    string data = json.Serialize();
    
    char post[], result[];
    string resultHeaders;
    
    StringToCharArray(data, post, 0, WHOLE_ARRAY, CP_UTF8);
    
    int timeout = 5000;
    WebRequest("POST", url, headers, timeout, post, result, resultHeaders);
}

//+------------------------------------------------------------------+
//| Send heartbeat to maintain connection                            |
//+------------------------------------------------------------------+
void SendHeartbeat()
{
    string url = ServerURL + "/api/mt45/heartbeat";
    string headers = "Content-Type: application/json\r\n";
    
    CJAVal json;
    json["connectionId"] = connectionId;
    json["status"] = "active";
    json["balance"] = AccountInfoDouble(ACCOUNT_BALANCE);
    json["equity"] = AccountInfoDouble(ACCOUNT_EQUITY);
    json["freeMargin"] = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
    
    string data = json.Serialize();
    
    char post[], result[];
    string resultHeaders;
    
    StringToCharArray(data, post, 0, WHOLE_ARRAY, CP_UTF8);
    
    int timeout = 5000;
    WebRequest("POST", url, headers, timeout, post, result, resultHeaders);
}

//+------------------------------------------------------------------+
//| Check for new trading signals                                   |
//+------------------------------------------------------------------+
void CheckForSignals()
{
    string url = ServerURL + "/api/mt45/signals/" + connectionId;
    
    char result[];
    string resultHeaders;
    
    int timeout = 5000;
    int res = WebRequest("GET", url, NULL, timeout, NULL, result, resultHeaders);
    
    if(res == 200)
    {
        string response = CharArrayToString(result, 0, WHOLE_ARRAY, CP_UTF8);
        if(StringFind(response, "\"signals\"") >= 0)
        {
            ProcessSignals(response);
        }
    }
}

//+------------------------------------------------------------------+
//| Process received signals                                         |
//+------------------------------------------------------------------+
void ProcessSignals(string jsonResponse)
{
    CJAVal json;
    
    if(json.Deserialize(jsonResponse))
    {
        CJAVal signals = json["signals"];
        
        for(int i = 0; i < signals.Size(); i++)
        {
            ProcessSingleSignal(signals[i]);
        }
    }
}

//+------------------------------------------------------------------+
//| Process a single trading signal                                 |
//+------------------------------------------------------------------+
void ProcessSingleSignal(CJAVal &signal)
{
    // Extract signal data
    string signalType = signal["signal"].ToStr();
    string symbol = signal["symbol"].ToStr();
    double entryPrice = signal["entryPrice"].ToDbl();
    double stopLoss = signal["stopLoss"].ToDbl();
    double takeProfit = signal["targetPrice"].ToDbl();
    double confidence = signal["confidence"].ToDbl();
    
    // Validate signal
    if(symbol != Symbol()) return; // Only trade current symbol
    if(confidence < 0.7) return; // Minimum confidence threshold
    if(!EnableAutoTrading) return;

    // Check trading hours
    if(!IsTradingTime())
    {
        Print("Outside trading hours. Signal ignored.");
        return;
    }
    
    // Check spread
    double spread = SymbolInfoInteger(Symbol(), SYMBOL_SPREAD);
    if(spread > MaxSpread) 
    {
        Print("Spread too high: ", spread, " points. Signal ignored.");
        return;
    }
    
    // Execute trade based on signal
    if(signalType == "BUY")
    {
        ExecuteBuyOrder(entryPrice, stopLoss, takeProfit);
    }
    else if(signalType == "SELL")
    {
        ExecuteSellOrder(entryPrice, stopLoss, takeProfit);
    }
    
    // Send confirmation back to server
    SendTradeConfirmation(signal, "executed");
}

//+------------------------------------------------------------------+
//| Check trading hours                                              |
//+------------------------------------------------------------------+
bool IsTradingTime()
{
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
//| Execute buy order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder(double entryPrice, double stopLoss, double takeProfit)
{
    double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
    double sl = (stopLoss > 0) ? stopLoss : 0;
    double tp = (takeProfit > 0) ? takeProfit : 0;
    
    if(trade.Buy(LotSize, Symbol(), ask, sl, tp, "GenZ Signal Buy"))
    {
        Print("BUY order executed. Ticket: ", trade.ResultOrder(), " Price: ", ask);
    }
    else
    {
        Print("BUY order failed. Error: ", trade.ResultRetcode());
    }
}

//+------------------------------------------------------------------+
//| Execute sell order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder(double entryPrice, double stopLoss, double takeProfit)
{
    double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
    double sl = (stopLoss > 0) ? stopLoss : 0;
    double tp = (takeProfit > 0) ? takeProfit : 0;
    
    if(trade.Sell(LotSize, Symbol(), bid, sl, tp, "GenZ Signal Sell"))
    {
        Print("SELL order executed. Ticket: ", trade.ResultOrder(), " Price: ", bid);
    }
    else
    {
        Print("SELL order failed. Error: ", trade.ResultRetcode());
    }
}

//+------------------------------------------------------------------+
//| Send trade confirmation to server                               |
//+------------------------------------------------------------------+
void SendTradeConfirmation(CJAVal &originalSignal, string status)
{
    string url = ServerURL + "/api/mt45/trade-confirmation";
    string headers = "Content-Type: application/json\r\n";
    
    CJAVal json;
    json["connectionId"] = connectionId;
    json["originalSignal"] = originalSignal;
    json["status"] = status;
    json["timestamp"] = TimeToString(TimeCurrent());
    json["ticket"] = (long)trade.ResultOrder();
    json["price"] = trade.ResultPrice();
    
    string data = json.Serialize();
    
    char post[], result[];
    string resultHeaders;
    
    StringToCharArray(data, post, 0, WHOLE_ARRAY, CP_UTF8);
    
    int timeout = 5000;
    WebRequest("POST", url, headers, timeout, post, result, resultHeaders);
}
