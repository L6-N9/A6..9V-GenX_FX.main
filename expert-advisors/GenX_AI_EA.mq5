//+------------------------------------------------------------------+
//|                                                     GenX_AI_EA.mq5 |
//|                          Copyright 2024, GenX Trading Platform    |
//|                                   https://github.com/genx-trading |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, GenX Trading Platform"
#property link      "https://github.com/genx-trading"
#property version   "2.00"

//--- Socket communication
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>

//--- Input parameters
input string   AI_Server_Host = "127.0.0.1";        // AI Server IP Address
input int      AI_Server_Port = 9090;               // AI Server Port
input int      Magic_Number = 12345;                // Magic Number for orders
input double   Default_Lot_Size = 0.1;              // Default lot size
input double   Max_Lot_Size = 1.0;                  // Maximum lot size
input int      Max_Open_Positions = 10;             // Maximum open positions
input double   Max_Risk_Per_Trade = 0.02;           // Maximum risk per trade (2%)
input bool     Enable_Auto_Trading = true;          // Enable automatic trading
input int      MaxSpread = 50;                     // Max spread in points
input string   TradingHours = "00:00-23:59";       // Trading hours (server time)
input int      Heartbeat_Interval = 30;             // Heartbeat interval in seconds
input bool     Log_Debug_Info = true;               // Enable debug logging

//--- Global variables
CTrade         trade;
CPositionInfo  position;
COrderInfo     order;

int            socket_handle = INVALID_HANDLE;
bool           is_connected = false;
datetime       last_heartbeat;
datetime       last_signal_time;

//--- Signal structure
struct TradingSignal {
    string signal_id;
    string instrument;
    string action;          // "BUY", "SELL", "CLOSE", "CLOSE_ALL"
    double volume;
    double stop_loss;
    double take_profit;
    int    magic_number;
    string comment;
    datetime timestamp;
    double confidence;
};

//--- Trade result structure
struct TradeResult {
    string signal_id;
    int    ticket;
    bool   success;
    int    error_code;
    string error_message;
    double execution_price;
    datetime execution_time;
    double slippage;
};

//--- Account status structure
struct AccountStatus {
    double balance;
    double equity;
    double margin;
    double free_margin;
    double margin_level;
    double profit;
    int    open_positions;
    datetime timestamp;
};

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    Print("GenX AI EA v2.00 Initializing...");
    
    // Initialize trade class
    trade.SetExpertMagicNumber(Magic_Number);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(Symbol());
    
    // Connect to AI server
    if (!ConnectToAIServer()) {
        Print("Failed to connect to AI server. EA will retry connection.");
        // Don't return error - allow EA to retry connection
    }
    
    last_heartbeat = TimeCurrent();
    last_signal_time = 0;
    
    Print("GenX AI EA initialized successfully");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("GenX AI EA shutting down. Reason: ", reason);
    
    // Close socket connection
    if (socket_handle != INVALID_HANDLE) {
        SocketClose(socket_handle);
        socket_handle = INVALID_HANDLE;
    }
    
    is_connected = false;
    Print("GenX AI EA deinitialized");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Check connection status
    if (!is_connected) {
        // Try to reconnect every 30 seconds
        if (TimeCurrent() - last_heartbeat > 30) {
            ConnectToAIServer();
            last_heartbeat = TimeCurrent();
        }
        return;
    }
    
    // Process incoming messages from AI server
    ProcessIncomingMessages();
    
    // Send heartbeat periodically
    if (TimeCurrent() - last_heartbeat >= Heartbeat_Interval) {
        SendHeartbeat();
        SendAccountStatus();
        last_heartbeat = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Connect to AI server                                            |
//+------------------------------------------------------------------+
bool ConnectToAIServer() {
    if (is_connected) return true;
    
    // Create socket
    socket_handle = SocketCreate();
    if (socket_handle == INVALID_HANDLE) {
        Print("Failed to create socket. Error: ", GetLastError());
        return false;
    }
    
    // Connect to server
    if (!SocketConnect(socket_handle, AI_Server_Host, AI_Server_Port, 5000)) {
        Print("Failed to connect to AI server at ", AI_Server_Host, ":", AI_Server_Port, 
              ". Error: ", GetLastError());
        SocketClose(socket_handle);
        socket_handle = INVALID_HANDLE;
        return false;
    }
    
    is_connected = true;
    Print("Successfully connected to AI server at ", AI_Server_Host, ":", AI_Server_Port);
    
    // Send EA information
    SendEAInfo();
    
    return true;
}

//+------------------------------------------------------------------+
//| Send EA information to server                                    |
//+------------------------------------------------------------------+
void SendEAInfo() {
    string ea_info = StringFormat(
        "{\"type\":\"EA_INFO\",\"data\":{\"name\":\"GenX AI EA\",\"version\":\"2.00\","
        "\"account\":\"%d\",\"broker\":\"%s\",\"symbol\":\"%s\",\"timeframe\":\"%s\","
        "\"magic_number\":%d},\"timestamp\":\"%s\"}",
        AccountInfoInteger(ACCOUNT_LOGIN),
        AccountInfoString(ACCOUNT_COMPANY),
        Symbol(),
        PeriodToString(Period()),
        Magic_Number,
        TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS)
    );
    
    SendMessage(ea_info);
}

//+------------------------------------------------------------------+
//| Send heartbeat message                                           |
//+------------------------------------------------------------------+
void SendHeartbeat() {
    string heartbeat = StringFormat(
        "{\"type\":\"HEARTBEAT\",\"data\":{\"status\":\"active\",\"positions\":%d,"
        "\"pending_orders\":%d,\"last_signal\":\"%s\"},\"timestamp\":\"%s\"}",
        PositionsTotal(),
        OrdersTotal(),
        TimeToString(last_signal_time, TIME_DATE | TIME_SECONDS),
        TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS)
    );
    
    SendMessage(heartbeat);
}

//+------------------------------------------------------------------+
//| Send account status                                              |
//+------------------------------------------------------------------+
void SendAccountStatus() {
    AccountStatus status;
    status.balance = AccountInfoDouble(ACCOUNT_BALANCE);
    status.equity = AccountInfoDouble(ACCOUNT_EQUITY);
    status.margin = AccountInfoDouble(ACCOUNT_MARGIN);
    status.free_margin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
    status.margin_level = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
    status.profit = AccountInfoDouble(ACCOUNT_PROFIT);
    status.open_positions = PositionsTotal();
    status.timestamp = TimeCurrent();
    
    string status_msg = StringFormat(
        "{\"type\":\"ACCOUNT_STATUS\",\"data\":{\"balance\":%.2f,\"equity\":%.2f,"
        "\"margin\":%.2f,\"free_margin\":%.2f,\"margin_level\":%.2f,\"profit\":%.2f,"
        "\"open_positions\":%d},\"timestamp\":\"%s\"}",
        status.balance, status.equity, status.margin, status.free_margin,
        status.margin_level, status.profit, status.open_positions,
        TimeToString(status.timestamp, TIME_DATE | TIME_SECONDS)
    );
    
    SendMessage(status_msg);
}

//+------------------------------------------------------------------+
//| Process incoming messages from AI server                        |
//+------------------------------------------------------------------+
void ProcessIncomingMessages() {
    if (!is_connected || socket_handle == INVALID_HANDLE) return;
    
    uint available = SocketIsReadable(socket_handle);
    if (available == 0) return;
    
    // Read available data
    string received = "";
    char buffer[];
    
    if (available > 0) {
        ArrayResize(buffer, available);
        int received_bytes = SocketRead(socket_handle, buffer, available, 1000);
        
        if (received_bytes > 0) {
            received = CharArrayToString(buffer, 0, received_bytes);
            
            if (Log_Debug_Info) {
                Print("Received message: ", received);
            }
            
            // Process the message
            ProcessMessage(received);
        }
    }
}

//+------------------------------------------------------------------+
//| Process individual message                                       |
//+------------------------------------------------------------------+
void ProcessMessage(string message) {
    // Simple JSON parsing for message type
    if (StringFind(message, "\"type\":\"SIGNAL\"") >= 0) {
        TradingSignal signal;
        if (ParseTradingSignal(message, signal)) {
            ExecuteTradingSignal(signal);
        }
    }
    else if (StringFind(message, "\"type\":\"COMMAND\"") >= 0) {
        ProcessCommand(message);
    }
    else {
        if (Log_Debug_Info) {
            Print("Unknown message type received: ", message);
        }
    }
}

//+------------------------------------------------------------------+
//| Parse trading signal from JSON message                          |
//+------------------------------------------------------------------+
bool ParseTradingSignal(string message, TradingSignal &signal) {
    // Simple JSON parsing - in production, use a proper JSON library
    int start, end;
    
    // Extract signal_id
    start = StringFind(message, "\"signal_id\":\"") + 13;
    end = StringFind(message, "\"", start);
    if (start >= 13 && end > start) {
        signal.signal_id = StringSubstr(message, start, end - start);
    }
    
    // Extract instrument
    start = StringFind(message, "\"instrument\":\"") + 14;
    end = StringFind(message, "\"", start);
    if (start >= 14 && end > start) {
        signal.instrument = StringSubstr(message, start, end - start);
    }
    
    // Extract action
    start = StringFind(message, "\"action\":\"") + 10;
    end = StringFind(message, "\"", start);
    if (start >= 10 && end > start) {
        signal.action = StringSubstr(message, start, end - start);
    }
    
    // Extract volume
    start = StringFind(message, "\"volume\":") + 9;
    end = StringFind(message, ",", start);
    if (end < 0) end = StringFind(message, "}", start);
    if (start >= 9 && end > start) {
        string vol_str = StringSubstr(message, start, end - start);
        signal.volume = StringToDouble(vol_str);
    }
    
    // Extract stop_loss (optional)
    start = StringFind(message, "\"stop_loss\":") + 12;
    if (start >= 12) {
        end = StringFind(message, ",", start);
        if (end < 0) end = StringFind(message, "}", start);
        if (end > start) {
            string sl_str = StringSubstr(message, start, end - start);
            if (sl_str != "null") {
                signal.stop_loss = StringToDouble(sl_str);
            }
        }
    }
    
    // Extract take_profit (optional)
    start = StringFind(message, "\"take_profit\":") + 15;
    if (start >= 15) {
        end = StringFind(message, ",", start);
        if (end < 0) end = StringFind(message, "}", start);
        if (end > start) {
            string tp_str = StringSubstr(message, start, end - start);
            if (tp_str != "null") {
                signal.take_profit = StringToDouble(tp_str);
            }
        }
    }
    
    // Set defaults
    signal.magic_number = Magic_Number;
    signal.comment = "GenX AI Signal";
    signal.timestamp = TimeCurrent();
    
    // Validate signal
    if (signal.signal_id == "" || signal.instrument == "" || signal.action == "") {
        Print("Invalid signal received - missing required fields");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Execute trading signal                                           |
//+------------------------------------------------------------------+
void ExecuteTradingSignal(TradingSignal &signal) {
    Print("Executing signal: ", signal.action, " ", signal.instrument, " ", signal.volume);
    
    last_signal_time = TimeCurrent();
    TradeResult result;
    result.signal_id = signal.signal_id;
    result.success = false;
    result.execution_time = TimeCurrent();
    
    // Validate signal before execution
    if (!ValidateSignal(signal)) {
        result.error_message = "Signal validation failed";
        SendTradeResult(result);
        return;
    }
    
    // Execute based on action
    if (signal.action == "BUY") {
        result.success = ExecuteBuyOrder(signal, result);
    }
    else if (signal.action == "SELL") {
        result.success = ExecuteSellOrder(signal, result);
    }
    else if (signal.action == "CLOSE") {
        result.success = ClosePosition(signal.instrument, result);
    }
    else if (signal.action == "CLOSE_ALL") {
        result.success = CloseAllPositions(result);
    }
    else {
        result.error_message = "Unknown action: " + signal.action;
    }
    
    // Send result back to AI server
    SendTradeResult(result);
}

//+------------------------------------------------------------------+
//| Validate trading signal                                          |
//+------------------------------------------------------------------+
bool ValidateSignal(TradingSignal &signal) {
    // Check if auto trading is enabled
    if (!Enable_Auto_Trading) {
        Print("Auto trading is disabled");
        return false;
    }

    // Check spread
    if (SymbolInfoInteger(Symbol(), SYMBOL_SPREAD) > MaxSpread) {
        Print("Spread too high: ", SymbolInfoInteger(Symbol(), SYMBOL_SPREAD));
        return false;
    }

    // Check trading hours
    if (!IsTradingTime()) {
        Print("Outside trading hours");
        return false;
    }
    
    // Check symbol
    if (signal.instrument != Symbol()) {
        Print("Signal for different symbol: ", signal.instrument, " (current: ", Symbol(), ")");
        return false;
    }
    
    // Check volume limits
    if (signal.volume <= 0 || signal.volume > Max_Lot_Size) {
        Print("Invalid volume: ", signal.volume, " (max: ", Max_Lot_Size, ")");
        return false;
    }
    
    // Check maximum positions
    if (PositionsTotal() >= Max_Open_Positions && 
        (signal.action == "BUY" || signal.action == "SELL")) {
        Print("Maximum positions reached: ", PositionsTotal());
        return false;
    }
    
    // Check account equity for risk management
    double account_equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double position_value = signal.volume * SymbolInfoDouble(Symbol(), SYMBOL_TRADE_CONTRACT_SIZE) * 
                           SymbolInfoDouble(Symbol(), SYMBOL_ASK);
    
    if (position_value > account_equity * Max_Risk_Per_Trade) {
        Print("Position size exceeds risk limit");
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
        return true;
    }

    return false;
}

//+------------------------------------------------------------------+
//| Execute buy order                                                |
//+------------------------------------------------------------------+
bool ExecuteBuyOrder(TradingSignal &signal, TradeResult &result) {
    double ask = SymbolInfoDouble(signal.instrument, SYMBOL_ASK);
    
    if (!trade.Buy(signal.volume, signal.instrument, ask, signal.stop_loss, 
                   signal.take_profit, signal.comment)) {
        result.error_code = trade.ResultRetcode();
        result.error_message = "Buy order failed: " + IntegerToString(result.error_code);
        Print(result.error_message);
        return false;
    }
    
    result.ticket = (int)trade.ResultOrder();
    result.execution_price = trade.ResultPrice();
    result.slippage = MathAbs(result.execution_price - ask);
    
    Print("Buy order executed successfully. Ticket: ", result.ticket, 
          " Price: ", result.execution_price);
    
    return true;
}

//+------------------------------------------------------------------+
//| Execute sell order                                               |
//+------------------------------------------------------------------+
bool ExecuteSellOrder(TradingSignal &signal, TradeResult &result) {
    double bid = SymbolInfoDouble(signal.instrument, SYMBOL_BID);
    
    if (!trade.Sell(signal.volume, signal.instrument, bid, signal.stop_loss, 
                    signal.take_profit, signal.comment)) {
        result.error_code = trade.ResultRetcode();
        result.error_message = "Sell order failed: " + IntegerToString(result.error_code);
        Print(result.error_message);
        return false;
    }
    
    result.ticket = (int)trade.ResultOrder();
    result.execution_price = trade.ResultPrice();
    result.slippage = MathAbs(result.execution_price - bid);
    
    Print("Sell order executed successfully. Ticket: ", result.ticket, 
          " Price: ", result.execution_price);
    
    return true;
}

//+------------------------------------------------------------------+
//| Close position for specific symbol                              |
//+------------------------------------------------------------------+
bool ClosePosition(string symbol, TradeResult &result) {
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (position.SelectByIndex(i)) {
            if (position.Symbol() == symbol && position.Magic() == Magic_Number) {
                if (trade.PositionClose(position.Ticket())) {
                    result.ticket = (int)position.Ticket();
                    result.execution_price = trade.ResultPrice();
                    Print("Position closed successfully. Ticket: ", result.ticket);
                    return true;
                } else {
                    result.error_code = trade.ResultRetcode();
                    result.error_message = "Failed to close position: " + IntegerToString(result.error_code);
                    Print(result.error_message);
                    return false;
                }
            }
        }
    }
    
    result.error_message = "No position found for symbol: " + symbol;
    Print(result.error_message);
    return false;
}

//+------------------------------------------------------------------+
//| Close all positions                                              |
//+------------------------------------------------------------------+
bool CloseAllPositions(TradeResult &result) {
    int closed_count = 0;
    
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (position.SelectByIndex(i)) {
            if (position.Magic() == Magic_Number) {
                if (trade.PositionClose(position.Ticket())) {
                    closed_count++;
                    Print("Position closed. Ticket: ", position.Ticket());
                }
            }
        }
    }
    
    if (closed_count > 0) {
        result.execution_price = 0; // Multiple positions
        Print("Closed ", closed_count, " positions");
        return true;
    } else {
        result.error_message = "No positions to close";
        return false;
    }
}

//+------------------------------------------------------------------+
//| Process command from AI server                                  |
//+------------------------------------------------------------------+
void ProcessCommand(string message) {
    if (StringFind(message, "\"command\":\"GET_STATUS\"") >= 0) {
        SendAccountStatus();
    }
    else if (StringFind(message, "\"command\":\"CLOSE_ALL\"") >= 0) {
        TradeResult result;
        result.signal_id = "COMMAND_CLOSE_ALL";
        result.success = CloseAllPositions(result);
        SendTradeResult(result);
    }
    else if (StringFind(message, "\"command\":\"PING\"") >= 0) {
        SendHeartbeat();
    }
    else {
        Print("Unknown command received: ", message);
    }
}

//+------------------------------------------------------------------+
//| Send trade result to AI server                                  |
//+------------------------------------------------------------------+
void SendTradeResult(TradeResult &result) {
    string result_msg = StringFormat(
        "{\"type\":\"TRADE_RESULT\",\"data\":{\"signal_id\":\"%s\",\"ticket\":%d,"
        "\"success\":%s,\"error_code\":%d,\"error_message\":\"%s\","
        "\"execution_price\":%.5f,\"slippage\":%.5f},\"timestamp\":\"%s\"}",
        result.signal_id,
        result.ticket,
        result.success ? "true" : "false",
        result.error_code,
        result.error_message,
        result.execution_price,
        result.slippage,
        TimeToString(result.execution_time, TIME_DATE | TIME_SECONDS)
    );
    
    SendMessage(result_msg);
}

//+------------------------------------------------------------------+
//| Send message to AI server                                       |
//+------------------------------------------------------------------+
void SendMessage(string message) {
    if (!is_connected || socket_handle == INVALID_HANDLE) {
        Print("Cannot send message - not connected to AI server");
        return;
    }
    
    // Add message length prefix (4 bytes)
    int message_length = StringLen(message);
    char length_bytes[4];
    length_bytes[0] = (char)((message_length >> 24) & 0xFF);
    length_bytes[1] = (char)((message_length >> 16) & 0xFF);
    length_bytes[2] = (char)((message_length >> 8) & 0xFF);
    length_bytes[3] = (char)(message_length & 0xFF);
    
    // Send length prefix
    if (SocketSend(socket_handle, length_bytes, 4) != 4) {
        Print("Failed to send message length");
        is_connected = false;
        return;
    }
    
    // Send message
    char message_bytes[];
    StringToCharArray(message, message_bytes, 0, WHOLE_ARRAY, CP_UTF8);
    
    if (SocketSend(socket_handle, message_bytes, ArraySize(message_bytes) - 1) != ArraySize(message_bytes) - 1) {
        Print("Failed to send message");
        is_connected = false;
        return;
    }
    
    if (Log_Debug_Info) {
        Print("Message sent: ", message);
    }
}

//+------------------------------------------------------------------+
//| Convert period to string                                         |
//+------------------------------------------------------------------+
string PeriodToString(ENUM_TIMEFRAMES period) {
    switch(period) {
        case PERIOD_M1:  return "M1";
        case PERIOD_M5:  return "M5";
        case PERIOD_M15: return "M15";
        case PERIOD_M30: return "M30";
        case PERIOD_H1:  return "H1";
        case PERIOD_H4:  return "H4";
        case PERIOD_D1:  return "D1";
        case PERIOD_W1:  return "W1";
        case PERIOD_MN1: return "MN1";
        default:         return "UNKNOWN";
    }
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer() {
    // Additional periodic tasks if needed
}
