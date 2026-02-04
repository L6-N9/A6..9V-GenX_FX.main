//+------------------------------------------------------------------+
//|                                                   GenX_VPS_EA.mq4 |
//|                                    GenX FX Trading System VPS EA |
//|                                   Optimized for VPS + AWS Signals |
//|                                   Version 1.10 - Improved TP/SL   |
//+------------------------------------------------------------------+
#property copyright "GenX FX"
#property version   "1.10"
#property strict

// Input Parameters
input group "=== Connection Settings ==="
input string SignalURL = "http://YOUR_AWS_IP:8000/MT4_Signals.csv";
input int SignalCheckInterval = 300; // 5 minutes

input group "=== Risk Management ==="
input double LotSize = 0.01;
input int MagicNumber = 12345;
input double MaxRisk = 2.0; // Max risk per trade %
input int DefaultStopLossPips = 500;
input int DefaultTakeProfitPips = 1000;
input int StopLevelBuffer = 20; // Extra points for stop level safety

input group "=== Trailing Stop ==="
input bool UseTrailingStop = true;
input int TrailingStopPips = 300;

// Global Variables
datetime lastSignalCheck = 0;
string signalData = "";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    Print("GenX VPS EA v1.10 Started - Connecting to AWS Signals");
    
    // Enable WebRequest for the signal URL
    if(!TerminalInfoInteger(TERMINAL_DLLS_ALLOWED)) {
        Alert("Please enable DLL imports in EA settings");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Check for new signals
    if(TimeCurrent() - lastSignalCheck >= SignalCheckInterval) {
        CheckForNewSignals();
        lastSignalCheck = TimeCurrent();
    }

    // Apply Trailing Stop logic
    if(UseTrailingStop) {
        ApplyTrailingStop();
    }
}

//+------------------------------------------------------------------+
//| Download and process signals from AWS                           |
//+------------------------------------------------------------------+
void CheckForNewSignals() {
    string url = SignalURL;
    
    // Download signals
    char data[];
    char headers[];
    string result_headers;
    int timeout = 5000;
    
    int res = WebRequest("GET", url, "", "", timeout, data, ArraySize(data), result_headers);
    
    if(res == 200) {
        signalData = CharArrayToString(data);
        ProcessSignals(signalData);
        Print("Signals updated from AWS");
    } else {
        Print("Failed to download signals. Error: ", res);
    }
}

//+------------------------------------------------------------------+
//| Process CSV signals and execute trades                          |
//+------------------------------------------------------------------+
void ProcessSignals(string csvData) {
    string lines[];
    int lineCount = StringSplit(csvData, '\n', lines);
    
    for(int i = 1; i < lineCount; i++) { // Skip header
        string fields[];
        int fieldCount = StringSplit(lines[i], ',', fields);
        
        // Support standardized 9-field format: Magic,Symbol,Signal,EntryPrice,StopLoss,TakeProfit,LotSize,Confidence,Timestamp
        if(fieldCount >= 8) {
            string symbol = fields[1];
            string action = fields[2];
            double entry = StringToDouble(fields[3]);
            double sl = StringToDouble(fields[4]);
            double tp = StringToDouble(fields[5]);
            double confidence = StringToDouble(fields[7]);

            if(confidence > 1.0) confidence /= 100.0; // Convert 85.0 to 0.85
            
            // Only trade current symbol with high confidence
            if(symbol == Symbol() && confidence >= 0.7) {
                ExecuteSignal(action, entry, sl, tp, confidence);
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Execute trading signal                                           |
//+------------------------------------------------------------------+
void ExecuteSignal(string action, double entry, double sl, double tp, double confidence) {
    // Check if we already have a position
    if(PositionsTotal() > 0) return;
    
    int orderType = -1;
    if(action == "BUY") orderType = OP_BUY;
    else if(action == "SELL") orderType = OP_SELL;
    
    if(orderType == -1) return;

    double price = (orderType == OP_BUY) ? Ask : Bid;

    // Use defaults if TP/SL are 0
    if(sl == 0) {
        if(orderType == OP_BUY) sl = price - DefaultStopLossPips * Point;
        else sl = price + DefaultStopLossPips * Point;
    }

    if(tp == 0) {
        if(orderType == OP_BUY) tp = price + DefaultTakeProfitPips * Point;
        else tp = price - DefaultTakeProfitPips * Point;
    }

    // Safety check: Ensure TP/SL are not too close to current price
    double minStopLevel = (MarketInfo(Symbol(), MODE_STOPLEVEL) + StopLevelBuffer) * Point;

    if(orderType == OP_BUY) {
        if(price - sl < minStopLevel) sl = price - minStopLevel;
        if(tp - price < minStopLevel) tp = price + minStopLevel;
    } else {
        if(sl - price < minStopLevel) sl = price + minStopLevel;
        if(price - tp < minStopLevel) tp = price - minStopLevel;
    }

    // Calculate lot size based on confidence and risk
    double lots = CalculateLotSize(sl, confidence);

    int ticket = OrderSend(Symbol(), orderType, lots, price, 3, sl, tp,
                          "GenX VPS EA", MagicNumber, 0, clrGreen);

    if(ticket > 0) {
        Print("Order executed: ", action, " ", lots, " lots at ", price, " SL: ", sl, " TP: ", tp);
    } else {
        Print("Order failed. Error: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk and confidence                 |
//+------------------------------------------------------------------+
double CalculateLotSize(double stopLoss, double confidence) {
    double balance = AccountBalance();
    double riskAmount = balance * (MaxRisk / 100.0);
    
    // Adjust risk based on confidence
    riskAmount = riskAmount * (confidence / 1.0); // confidence is 0.7 to 1.0
    
    double pipValue = MarketInfo(Symbol(), MODE_TICKVALUE);
    double stopLossDistance = MathAbs(Ask - stopLoss);

    if(stopLossDistance == 0) stopLossDistance = DefaultStopLossPips * Point;

    double stopLossPips = stopLossDistance / Point;
    
    double lots = riskAmount / (stopLossPips * pipValue);
    
    // Normalize lot size
    double minLot = MarketInfo(Symbol(), MODE_MINLOT);
    double maxLot = MarketInfo(Symbol(), MODE_MAXLOT);
    double lotStep = MarketInfo(Symbol(), MODE_LOTSTEP);
    
    lots = MathMax(minLot, MathMin(maxLot, lots));
    lots = NormalizeDouble(lots / lotStep, 0) * lotStep;
    
    return lots;
}

//+------------------------------------------------------------------+
//| Apply Trailing Stop to open positions                           |
//+------------------------------------------------------------------+
void ApplyTrailingStop() {
    for(int i = 0; i < OrdersTotal(); i++) {
        if(OrderSelect(i, SELECT_BY_POS) &&
           OrderSymbol() == Symbol() &&
           OrderMagicNumber() == MagicNumber) {

            if(OrderType() == OP_BUY) {
                if(Bid - OrderOpenPrice() > TrailingStopPips * Point) {
                    if(OrderStopLoss() < Bid - TrailingStopPips * Point) {
                        bool res = OrderModify(OrderTicket(), OrderOpenPrice(),
                                              Bid - TrailingStopPips * Point,
                                              OrderTakeProfit(), 0, clrBlue);
                        if(!res) Print("Trailing Stop modification failed. Error: ", GetLastError());
                    }
                }
            } else if(OrderType() == OP_SELL) {
                if(OrderOpenPrice() - Ask > TrailingStopPips * Point) {
                    if(OrderStopLoss() > Ask + TrailingStopPips * Point || OrderStopLoss() == 0) {
                        bool res = OrderModify(OrderTicket(), OrderOpenPrice(),
                                              Ask + TrailingStopPips * Point,
                                              OrderTakeProfit(), 0, clrRed);
                        if(!res) Print("Trailing Stop modification failed. Error: ", GetLastError());
                    }
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Get total positions                                              |
//+------------------------------------------------------------------+
int PositionsTotal() {
    int count = 0;
    for(int i = 0; i < OrdersTotal(); i++) {
        if(OrderSelect(i, SELECT_BY_POS) && 
           OrderSymbol() == Symbol() && 
           OrderMagicNumber() == MagicNumber) {
            count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("GenX VPS EA Stopped");
}