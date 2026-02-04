//+------------------------------------------------------------------+
//| GenX Signal Reader EA for MT4                                   |
//| Reads signals from GenX CSV file and executes trades            |
//+------------------------------------------------------------------+
#property copyright "GenX FX Trading System"
#property link      "https://github.com/Mouy-leng/GenX_FX"
#property version   "1.00"
#property strict

//--- Input parameters
input string    CSVFileName = "MT4_Signals.csv";  // CSV file name in MQL4/Files folder
input double    RiskPercent = 2.0;                // Risk per trade in %
input int       MagicNumber = 123450;             // Base magic number
input bool      EnableTrading = true;             // Enable/disable trading
input int       MaxTrades = 5;                    // Maximum concurrent trades
input int       CheckInterval = 30;               // Check for new signals every X seconds

//--- Global variables
datetime lastCheck = 0;
string processedSignals[];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("GenX Signal Reader EA initialized");
    Print("CSV File: ", CSVFileName);
    Print("Risk per trade: ", RiskPercent, "%");
    Print("Magic number: ", MagicNumber);
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("GenX Signal Reader EA stopped");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check for new signals every X seconds
    if(TimeCurrent() - lastCheck < CheckInterval)
        return;
        
    lastCheck = TimeCurrent();
    
    if(EnableTrading)
    {
        ReadAndProcessSignals();
    }
}

//+------------------------------------------------------------------+
//| Read signals from CSV file                                      |
//+------------------------------------------------------------------+
void ReadAndProcessSignals()
{
    int fileHandle = FileOpen(CSVFileName, FILE_READ|FILE_CSV);
    
    if(fileHandle == INVALID_HANDLE)
    {
        Print("Error opening file: ", CSVFileName, " Error: ", GetLastError());
        return;
    }
    
    string headers = FileReadString(fileHandle); // Skip header row
    
    while(!FileIsEnding(fileHandle))
    {
        string magic = FileReadString(fileHandle);
        string symbol = FileReadString(fileHandle);
        string signal = FileReadString(fileHandle);
        string entryPriceStr = FileReadString(fileHandle);
        string stopLossStr = FileReadString(fileHandle);
        string takeProfitStr = FileReadString(fileHandle);
        string lotSizeStr = FileReadString(fileHandle);
        string confidenceStr = FileReadString(fileHandle); // 8th field (index 7)
        string timestamp = FileReadString(fileHandle);    // 9th field (index 8)
        
        // Skip empty lines
        if(magic == "" || symbol == "")
            continue;
            
        // Convert strings to numbers
        int magicNum = (int)StringToInteger(magic);
        double entryPrice = StringToDouble(entryPriceStr);
        double stopLoss = StringToDouble(stopLossStr);
        double takeProfit = StringToDouble(takeProfitStr);
        double lotSize = StringToDouble(lotSizeStr);
        
        // Check if signal is for current symbol
        if(symbol != Symbol())
            continue;
            
        // Check if we already processed this signal
        if(IsSignalProcessed(magic))
            continue;
            
        // Check if we have too many trades
        if(CountOpenTrades() >= MaxTrades)
        {
            Print("Maximum trades reached: ", MaxTrades);
            continue;
        }
        
        // Process the signal
        ProcessSignal(magicNum, signal, entryPrice, stopLoss, takeProfit, lotSize);
        
        // Mark signal as processed
        AddProcessedSignal(magic);
    }
    
    FileClose(fileHandle);
}

//+------------------------------------------------------------------+
//| Process individual signal                                       |
//+------------------------------------------------------------------+
void ProcessSignal(int magic, string signal, double entry, double sl, double tp, double lots)
{
    double price;
    int orderType;
    color orderColor;
    
    // Determine order type and price
    if(signal == "BUY")
    {
        orderType = OP_BUY;
        price = Ask;
        orderColor = clrGreen;
    }
    else if(signal == "SELL")
    {
        orderType = OP_SELL;
        price = Bid;
        orderColor = clrRed;
    }
    else
    {
        Print("Unknown signal type: ", signal);
        return;
    }
    
    // Calculate lot size based on risk
    double calcLots = CalculateLotSize(sl, price, orderType);
    if(calcLots > 0)
        lots = calcLots;
    
    // Normalize lot size
    lots = NormalizeLots(lots);
    
    // Check minimum distance for stops
    double minDistance = MarketInfo(Symbol(), MODE_STOPLEVEL) * Point;
    
    if(orderType == OP_BUY)
    {
        if(sl > 0 && price - sl < minDistance)
        {
            Print("Stop loss too close for BUY order. Adjusting...");
            sl = price - minDistance;
        }
        if(tp > 0 && tp - price < minDistance)
        {
            Print("Take profit too close for BUY order. Adjusting...");
            tp = price + minDistance;
        }
    }
    else if(orderType == OP_SELL)
    {
        if(sl > 0 && sl - price < minDistance)
        {
            Print("Stop loss too close for SELL order. Adjusting...");
            sl = price + minDistance;
        }
        if(tp > 0 && price - tp < minDistance)
        {
            Print("Take profit too close for SELL order. Adjusting...");
            tp = price - minDistance;
        }
    }
    
    // Place the order
    int ticket = OrderSend(Symbol(), orderType, lots, price, 3, sl, tp, 
                          "GenX Signal #" + IntegerToString(magic), magic, 0, orderColor);
    
    if(ticket > 0)
    {
        Print("Order placed successfully: Ticket=", ticket, " Type=", signal, 
              " Lots=", lots, " Price=", price, " SL=", sl, " TP=", tp);
    }
    else
    {
        Print("Error placing order: ", GetLastError(), " Type=", signal, 
              " Price=", price, " SL=", sl, " TP=", tp);
    }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk percentage                     |
//+------------------------------------------------------------------+
double CalculateLotSize(double stopLoss, double entryPrice, int orderType)
{
    if(stopLoss <= 0 || RiskPercent <= 0)
        return 0;
    
    double balance = AccountBalance();
    double riskAmount = balance * RiskPercent / 100.0;
    
    double pipValue = MarketInfo(Symbol(), MODE_TICKVALUE);
    if(MarketInfo(Symbol(), MODE_DIGITS) == 5 || MarketInfo(Symbol(), MODE_DIGITS) == 3)
        pipValue *= 10;
    
    double stopPips;
    if(orderType == OP_BUY)
        stopPips = (entryPrice - stopLoss) / Point;
    else
        stopPips = (stopLoss - entryPrice) / Point;
    
    if(stopPips <= 0)
        return 0;
    
    double lots = riskAmount / (stopPips * pipValue);
    
    return lots;
}

//+------------------------------------------------------------------+
//| Normalize lot size according to broker requirements             |
//+------------------------------------------------------------------+
double NormalizeLots(double lots)
{
    double minLot = MarketInfo(Symbol(), MODE_MINLOT);
    double maxLot = MarketInfo(Symbol(), MODE_MAXLOT);
    double lotStep = MarketInfo(Symbol(), MODE_LOTSTEP);
    
    if(lots < minLot)
        return minLot;
    if(lots > maxLot)
        return maxLot;
    
    return NormalizeDouble(lots / lotStep, 0) * lotStep;
}

//+------------------------------------------------------------------+
//| Check if signal was already processed                           |
//+------------------------------------------------------------------+
bool IsSignalProcessed(string magic)
{
    for(int i = 0; i < ArraySize(processedSignals); i++)
    {
        if(processedSignals[i] == magic)
            return true;
    }
    return false;
}

//+------------------------------------------------------------------+
//| Add signal to processed list                                    |
//+------------------------------------------------------------------+
void AddProcessedSignal(string magic)
{
    int size = ArraySize(processedSignals);
    ArrayResize(processedSignals, size + 1);
    processedSignals[size] = magic;
}

//+------------------------------------------------------------------+
//| Count open trades for this EA                                   |
//+------------------------------------------------------------------+
int CountOpenTrades()
{
    int count = 0;
    for(int i = 0; i < OrdersTotal(); i++)
    {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
        {
            if(OrderSymbol() == Symbol() && OrderMagicNumber() >= MagicNumber && 
               OrderMagicNumber() < MagicNumber + 1000)
            {
                count++;
            }
        }
    }
    return count;
}