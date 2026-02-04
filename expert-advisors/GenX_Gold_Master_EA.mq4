//+------------------------------------------------------------------+
//| GenX Gold Master EA - Advanced Gold Trading System              |
//| Reads signals from GenX VM + Advanced Gold-Specific Strategies  |
//+------------------------------------------------------------------+
#property copyright "GenX FX Trading System - Gold Master"
#property link      "https://github.com/Mouy-leng/GenX_FX"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Input Parameters                                                 |
//+------------------------------------------------------------------+
//--- VM Connection Settings
input string    VMSignalURL = "http://34.71.143.222:8080/MT4_Signals.csv";
input int       VMTimeoutSeconds = 30;
input int       CheckInterval = 30;

//--- Gold Pair Configuration
input bool      Trade_XAUUSD = true;
input bool      Trade_XAUEUR = true;
input bool      Trade_XAUGBP = true;
input bool      Trade_XAUAUD = true;
input bool      Trade_XAUCAD = false;
input bool      Trade_XAUCHF = false;

//--- Risk Management
input double    BaseRiskPercent = 1.0;
input double    MaxRiskPerTrade = 5.0;
input double    MaxTotalRisk = 15.0;
input int       MaxTradesPerPair = 2;
input int       MaxTotalTrades = 6;

//--- Confidence-Based Risk Scaling
input double    MinConfidenceToTrade = 75.0;
input double    HighConfidenceLevel = 85.0;
input double    VeryHighConfidenceLevel = 90.0;
input double    MaxConfidenceRiskMultiplier = 4.0;

//--- Advanced Strategy Settings
input bool      EnableBackupStrategy = true;
input bool      EnableVolatilityFilter = true;
input int       VolatilityPeriod = 14;
input double    HighVolatilityThreshold = 1.5;

//--- Trading Controls
input int       MagicNumber = 888888;
input bool      EnableTrading = false;  // Start in test mode
input int       Slippage = 3;

//+------------------------------------------------------------------+
//| Global Variables                                                 |
//+------------------------------------------------------------------+
datetime lastCheck = 0;
datetime lastSignalTime = 0;
string goldPairs[] = {"XAUUSD", "XAUEUR", "XAUGBP", "XAUAUD", "XAUCAD", "XAUCHF"};
bool pairEnabled[] = {true, true, true, true, false, false};
double currentVolatility[];

enum TradingMode {
    VM_MODE,
    BACKUP_MODE,
    HYBRID_MODE
};

TradingMode currentMode = VM_MODE;

struct GoldSignal {
    string symbol;
    string signal;
    double entryPrice;
    double stopLoss;
    double takeProfit;
    double confidence;
    datetime timestamp;
    double volatility;
};

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("=== GenX Gold Master EA Starting ===");
    Print("VM Signal URL: ", VMSignalURL);
    Print("Base Risk: ", BaseRiskPercent, "%");
    Print("Trading Mode: ", EnableTrading ? "LIVE" : "TEST");
    
    // Initialize pair settings
    pairEnabled[0] = Trade_XAUUSD;
    pairEnabled[1] = Trade_XAUEUR;
    pairEnabled[2] = Trade_XAUGBP;
    pairEnabled[3] = Trade_XAUAUD;
    pairEnabled[4] = Trade_XAUCAD;
    pairEnabled[5] = Trade_XAUCHF;
    
    ArrayResize(currentVolatility, ArraySize(goldPairs));
    
    // Display enabled pairs
    Print("=== Enabled Gold Pairs ===");
    for(int i = 0; i < ArraySize(goldPairs); i++) {
        if(pairEnabled[i]) {
            Print("✅ ", goldPairs[i], " - ENABLED");
        } else {
            Print("❌ ", goldPairs[i], " - DISABLED");
        }
    }
    
    Print("=== Gold Master EA Initialized Successfully ===");
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("=== GenX Gold Master EA Stopped ===");
    Print("Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check for new signals periodically
    if(TimeCurrent() - lastCheck < CheckInterval)
        return;
    
    lastCheck = TimeCurrent();
    
    // Update volatility for all pairs
    UpdateVolatilityData();
    
    // Try to get signals from VM
    if(currentMode == VM_MODE || currentMode == HYBRID_MODE) {
        if(ProcessVMSignals()) {
            return; // Successfully processed VM signals
        } else if(currentMode == HYBRID_MODE) {
            Print("⚠️ VM signals failed, switching to backup strategy");
            currentMode = BACKUP_MODE;
        }
    }
    
    // Use backup strategy if VM fails or backup mode active
    if(currentMode == BACKUP_MODE || (currentMode == HYBRID_MODE && EnableBackupStrategy)) {
        ProcessBackupStrategy();
    }
}

//+------------------------------------------------------------------+
//| Process VM Signals                                               |
//+------------------------------------------------------------------+
bool ProcessVMSignals()
{
    string csvData = DownloadCSVFromVM();
    if(csvData == "") {
        Print("❌ Failed to download signals from VM");
        return false;
    }
    
    GoldSignal signals[];
    int signalCount = ParseGoldSignals(csvData, signals);
    
    if(signalCount == 0) {
        Print("ℹ️ No gold signals found in VM data");
        return true; // Not an error, just no signals
    }
    
    Print("📊 Found ", signalCount, " gold signals from VM");
    
    // Process each gold signal
    for(int i = 0; i < signalCount; i++) {
        ProcessGoldSignal(signals[i]);
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Download CSV from VM                                             |
//+------------------------------------------------------------------+
string DownloadCSVFromVM()
{
    // Simulate downloading CSV data
    // In real implementation, use WinInet or shell commands
    string filename = "MT4_Signals.csv";
    
    if(!FileIsExist(filename)) {
        Print("❌ Signal file not found: ", filename);
        return "";
    }
    
    int fileHandle = FileOpen(filename, FILE_READ|FILE_CSV);
    if(fileHandle == INVALID_HANDLE) {
        Print("❌ Failed to open signal file");
        return "";
    }
    
    string csvData = "";
    while(!FileIsEnding(fileHandle)) {
        csvData += FileReadString(fileHandle) + "\n";
    }
    
    FileClose(fileHandle);
    return csvData;
}

//+------------------------------------------------------------------+
//| Parse Gold Signals from CSV                                      |
//+------------------------------------------------------------------+
int ParseGoldSignals(string csvData, GoldSignal &signals[])
{
    string lines[];
    int lineCount = StringSplit(csvData, '\n', lines);
    
    int signalCount = 0;
    ArrayResize(signals, 20); // Allocate space
    
    for(int i = 1; i < lineCount; i++) { // Skip header
        string fields[];
        int fieldCount = StringSplit(lines[i], ',', fields);
        if(fieldCount < 8) continue;
        
        string symbol = StringTrimLeft(StringTrimRight(fields[1]));
        
        // Check if it's a gold pair
        if(!IsGoldPair(symbol)) continue;
        
        // Check if pair is enabled
        if(!IsPairEnabled(symbol)) continue;
        
        // Parse signal data
        GoldSignal signal;
        signal.symbol = symbol;
        signal.signal = StringTrimLeft(StringTrimRight(fields[2]));
        signal.entryPrice = StringToDouble(fields[3]);
        signal.stopLoss = StringToDouble(fields[4]);
        signal.takeProfit = StringToDouble(fields[5]);

        // In the standardized 9-column format, confidence is at index 7.
        // If 8 columns, we might be using the simplified format where lot size is at 6.
        if(fieldCount >= 8) {
            signal.confidence = StringToDouble(fields[7]);
        } else {
            signal.confidence = 80.0; // Default
        }

        signal.timestamp = TimeCurrent();
        signal.volatility = GetPairVolatility(symbol);
        
        // Validate signal
        if(signal.confidence >= MinConfidenceToTrade) {
            signals[signalCount] = signal;
            signalCount++;
        }
    }
    
    ArrayResize(signals, signalCount);
    return signalCount;
}

//+------------------------------------------------------------------+
//| Process Individual Gold Signal                                   |
//+------------------------------------------------------------------+
void ProcessGoldSignal(GoldSignal &signal)
{
    Print("🥇 Processing signal: ", signal.symbol, " ", signal.signal, 
          " Confidence: ", signal.confidence, "%");
    
    // Calculate dynamic risk based on confidence
    double riskPercent = CalculateConfidenceBasedRisk(signal.confidence);
    
    // Apply volatility adjustment
    if(EnableVolatilityFilter) {
        riskPercent = AdjustRiskForVolatility(riskPercent, signal.volatility);
    }
    
    // Check if we can trade this pair
    if(!CanOpenNewTrade(signal.symbol)) {
        Print("⚠️ Cannot open new trade for ", signal.symbol, " (limits reached)");
        return;
    }
    
    // Execute the trade
    if(EnableTrading) {
        ExecuteGoldTrade(signal, riskPercent);
    } else {
        Print("📝 TEST MODE - Would trade: ", signal.symbol, " ", signal.signal, 
              " Risk: ", riskPercent, "%");
    }
}

//+------------------------------------------------------------------+
//| Calculate Confidence-Based Risk                                  |
//+------------------------------------------------------------------+
double CalculateConfidenceBasedRisk(double confidence)
{
    double riskMultiplier = 1.0;
    
    if(confidence >= VeryHighConfidenceLevel) {
        riskMultiplier = MaxConfidenceRiskMultiplier; // 90%+ = 4x risk
    } else if(confidence >= HighConfidenceLevel) {
        riskMultiplier = 2.5; // 85%+ = 2.5x risk
    } else if(confidence >= 80.0) {
        riskMultiplier = 1.5; // 80%+ = 1.5x risk
    } else {
        riskMultiplier = 1.0; // Default risk
    }
    
    double calculatedRisk = BaseRiskPercent * riskMultiplier;
    
    // Apply safety cap
    if(calculatedRisk > MaxRiskPerTrade) {
        calculatedRisk = MaxRiskPerTrade;
    }
    
    Print("💡 Confidence: ", confidence, "% → Risk: ", calculatedRisk, "% (Multiplier: ", riskMultiplier, ")");
    
    return calculatedRisk;
}

//+------------------------------------------------------------------+
//| Adjust Risk for Volatility                                       |
//+------------------------------------------------------------------+
double AdjustRiskForVolatility(double baseRisk, double volatility)
{
    // Higher volatility = slightly reduce risk for safety
    // Lower volatility = slightly increase risk for opportunity
    
    double volatilityAdjustment = 1.0;
    
    if(volatility > HighVolatilityThreshold) {
        volatilityAdjustment = 0.8; // Reduce risk in high volatility
    } else if(volatility < 0.5) {
        volatilityAdjustment = 1.2; // Increase risk in low volatility
    }
    
    return baseRisk * volatilityAdjustment;
}

//+------------------------------------------------------------------+
//| Execute Gold Trade                                               |
//+------------------------------------------------------------------+
void ExecuteGoldTrade(GoldSignal &signal, double riskPercent)
{
    double lotSize = CalculateLotSize(signal.symbol, signal.entryPrice, 
                                     signal.stopLoss, riskPercent);
    
    if(lotSize <= 0) {
        Print("❌ Invalid lot size calculated for ", signal.symbol);
        return;
    }
    
    // Normalize lot size
    lotSize = NormalizeLots(signal.symbol, lotSize);
    
    int orderType;
    double price;
    
    if(signal.signal == "BUY") {
        orderType = OP_BUY;
        price = MarketInfo(signal.symbol, MODE_ASK);
    } else if(signal.signal == "SELL") {
        orderType = OP_SELL;
        price = MarketInfo(signal.symbol, MODE_BID);
    } else {
        Print("❌ Invalid signal type: ", signal.signal);
        return;
    }
    
    // Place the order
    int ticket = OrderSend(signal.symbol, orderType, lotSize, price, Slippage,
                          signal.stopLoss, signal.takeProfit, 
                          "GenX Gold " + DoubleToStr(signal.confidence, 1) + "%",
                          MagicNumber, 0, clrNONE);
    
    if(ticket > 0) {
        Print("✅ Gold trade opened: ", signal.symbol, " ", signal.signal, 
              " Lot: ", lotSize, " Confidence: ", signal.confidence, "%");
    } else {
        Print("❌ Failed to open trade: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Calculate Lot Size Based on Risk                                 |
//+------------------------------------------------------------------+
double CalculateLotSize(string symbol, double entryPrice, double stopLoss, double riskPercent)
{
    double accountBalance = AccountBalance();
    double riskAmount = accountBalance * riskPercent / 100.0;
    
    double pipValue = MarketInfo(symbol, MODE_TICKVALUE);
    double stopLossPips = MathAbs(entryPrice - stopLoss) / MarketInfo(symbol, MODE_POINT);
    
    if(stopLossPips <= 0) return 0;
    
    double lotSize = riskAmount / (stopLossPips * pipValue);
    
    return lotSize;
}

//+------------------------------------------------------------------+
//| Normalize Lot Size                                               |
//+------------------------------------------------------------------+
double NormalizeLots(string symbol, double lotSize)
{
    double minLot = MarketInfo(symbol, MODE_MINLOT);
    double maxLot = MarketInfo(symbol, MODE_MAXLOT);
    double lotStep = MarketInfo(symbol, MODE_LOTSTEP);
    
    if(lotSize < minLot) return minLot;
    if(lotSize > maxLot) return maxLot;
    
    return NormalizeDouble(lotSize / lotStep, 0) * lotStep;
}

//+------------------------------------------------------------------+
//| Backup Strategy for Gold                                         |
//+------------------------------------------------------------------+
void ProcessBackupStrategy()
{
    Print("🔄 Running backup strategy for gold pairs");
    
    for(int i = 0; i < ArraySize(goldPairs); i++) {
        if(!pairEnabled[i]) continue;
        
        string symbol = goldPairs[i];
        
        if(!CanOpenNewTrade(symbol)) continue;
        
        // Advanced gold strategy
        int signal = AnalyzeGoldTechnicals(symbol);
        
        if(signal != 0 && EnableTrading) {
            ExecuteBackupTrade(symbol, signal);
        }
    }
}

//+------------------------------------------------------------------+
//| Advanced Gold Technical Analysis                                 |
//+------------------------------------------------------------------+
int AnalyzeGoldTechnicals(string symbol)
{
    // Multi-timeframe analysis
    double ma20_H1 = iMA(symbol, PERIOD_H1, 20, 0, MODE_SMA, PRICE_CLOSE, 0);
    double ma50_H1 = iMA(symbol, PERIOD_H1, 50, 0, MODE_SMA, PRICE_CLOSE, 0);
    double ma20_H4 = iMA(symbol, PERIOD_H4, 20, 0, MODE_SMA, PRICE_CLOSE, 0);
    double ma50_H4 = iMA(symbol, PERIOD_H4, 50, 0, MODE_SMA, PRICE_CLOSE, 0);
    
    double rsi = iRSI(symbol, PERIOD_H1, 14, PRICE_CLOSE, 0);
    double atr = iATR(symbol, PERIOD_H1, 14, 0);
    
    double currentPrice = MarketInfo(symbol, MODE_BID);
    
    // Trend analysis
    bool bullishH1 = ma20_H1 > ma50_H1;
    bool bullishH4 = ma20_H4 > ma50_H4;
    bool priceAboveMA = currentPrice > ma20_H1;
    
    // Volatility breakout
    bool highVolatility = atr > GetAverageATR(symbol, PERIOD_H1, 50);
    
    // Buy signal
    if(bullishH1 && bullishH4 && priceAboveMA && rsi < 70 && highVolatility) {
        return 1; // BUY
    }
    
    // Sell signal  
    if(!bullishH1 && !bullishH4 && !priceAboveMA && rsi > 30 && highVolatility) {
        return -1; // SELL
    }
    
    return 0; // No signal
}

//+------------------------------------------------------------------+
//| Execute Backup Trade                                             |
//+------------------------------------------------------------------+
void ExecuteBackupTrade(string symbol, int signal)
{
    double lotSize = CalculateBackupLotSize(symbol);
    double price, stopLoss, takeProfit;
    int orderType;
    
    if(signal == 1) { // BUY
        orderType = OP_BUY;
        price = MarketInfo(symbol, MODE_ASK);
        stopLoss = price - 500 * MarketInfo(symbol, MODE_POINT); // 50 pip SL
        takeProfit = price + 1000 * MarketInfo(symbol, MODE_POINT); // 100 pip TP
    } else { // SELL
        orderType = OP_SELL;
        price = MarketInfo(symbol, MODE_BID);
        stopLoss = price + 500 * MarketInfo(symbol, MODE_POINT);
        takeProfit = price - 1000 * MarketInfo(symbol, MODE_POINT);
    }
    
    int ticket = OrderSend(symbol, orderType, lotSize, price, Slippage,
                          stopLoss, takeProfit, "GenX Gold Backup",
                          MagicNumber + 1000, 0, clrBlue);
    
    if(ticket > 0) {
        Print("✅ Backup trade opened: ", symbol, " Type: ", signal);
    }
}

//+------------------------------------------------------------------+
//| Utility Functions                                                |
//+------------------------------------------------------------------+
bool IsGoldPair(string symbol)
{
    return StringFind(symbol, "XAU") == 0;
}

bool IsPairEnabled(string symbol)
{
    for(int i = 0; i < ArraySize(goldPairs); i++) {
        if(goldPairs[i] == symbol) {
            return pairEnabled[i];
        }
    }
    return false;
}

bool CanOpenNewTrade(string symbol)
{
    int tradesForPair = CountTradesForSymbol(symbol);
    int totalTrades = CountTotalTrades();
    
    return (tradesForPair < MaxTradesPerPair && totalTrades < MaxTotalTrades);
}

int CountTradesForSymbol(string symbol)
{
    int count = 0;
    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
            if(OrderSymbol() == symbol && OrderMagicNumber() == MagicNumber) {
                count++;
            }
        }
    }
    return count;
}

int CountTotalTrades()
{
    int count = 0;
    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
            if(OrderMagicNumber() == MagicNumber || OrderMagicNumber() == MagicNumber + 1000) {
                count++;
            }
        }
    }
    return count;
}

double GetPairVolatility(string symbol)
{
    double atr = iATR(symbol, PERIOD_H1, 14, 0);
    double price = MarketInfo(symbol, MODE_BID);
    return (atr / price) * 100;
}

double GetAverageATR(string symbol, int timeframe, int period)
{
    double sum = 0;
    for(int i = 0; i < period; i++) {
        sum += iATR(symbol, timeframe, 14, i);
    }
    return sum / period;
}

void UpdateVolatilityData()
{
    for(int i = 0; i < ArraySize(goldPairs); i++) {
        currentVolatility[i] = GetPairVolatility(goldPairs[i]);
    }
}

double CalculateBackupLotSize(string symbol)
{
    return NormalizeLots(symbol, BaseRiskPercent * AccountBalance() / 10000);
}