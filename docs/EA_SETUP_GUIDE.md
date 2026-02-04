# 🤖 EA Setup Guide - Simple Steps for Humans

## 🎯 **What We're Doing Here**

Think of this like connecting your phone to WiFi, but instead we're connecting your trading robot (EA) to:
1. **Your signals** (the trading decisions)
2. **Your Exness account** (where the money is)

It's really that simple! Let me walk you through it.

---

## 📁 **Step 1: Find Your EA Files**

Go to your project folder and look for the `expert-advisors/` directory. You'll see these files:
- `MT4_GenX_EA_Example.mq4` - For MetaTrader 4
- `GenX_AI_EA.mq5` - For MetaTrader 5

**Choose the one that matches your MetaTrader version.** Most people use MT4, so we'll focus on that.

---

## 📂 **Step 2: Copy the EA to MetaTrader**

### For MT4:
1. **Open your MetaTrader 4**
2. **Press `Ctrl + Shift + D`** (this opens the data folder)
3. **Go to**: `MQL4` → `Experts`
4. **Copy** your `MT4_GenX_EA_Example.mq4` file here
5. **Close and restart MetaTrader 4**

### For MT5:
1. **Open your MetaTrader 5**
2. **Press `Ctrl + Shift + D`** (this opens the data folder)
3. **Go to**: `MQL5` → `Experts`
4. **Copy** your `GenX_AI_EA.mq5` file here
5. **Close and restart MetaTrader 5**

---

## ⚙️ **Step 3: Configure the EA Settings**

When you drag the EA onto a chart, a settings window will pop up. Here's what each setting means **in human terms**:

### 🔧 **Basic Settings (The Important Ones)**

```
📁 CSVFileName = "MT4_Signals.csv"
```
**What this means**: This tells the EA where to find your trading signals.
**What you do**: Leave this as is, unless you renamed the file.

```
💰 RiskPercent = 2.0
```
**What this means**: How much of your account to risk per trade (2% = if you have $1000, risk $20 per trade).
**What you do**: Start with 1.0 or 2.0. Don't go crazy here!

```
🎯 MagicNumber = 123450
```
**What this means**: A unique ID for your EA's trades (so it doesn't mess with manual trades).
**What you do**: Change this to any number you like, like your birthday (20240315 for March 15, 2024).

```
📊 MaxTrades = 5
```
**What this means**: Maximum number of trades the EA can have open at once.
**What you do**: Start with 3-5. Don't let it open 20 trades at once!

```
⏰ CheckInterval = 30
```
**What this means**: How often (in seconds) the EA checks for new signals.
**What you do**: 30 seconds is good. Don't make it too fast (like 1 second) or too slow (like 300 seconds).

### 🛡️ **Safety Settings**

```
🔒 EnableTrading = true
```
**What this means**: Actually place trades (true) or just show what it would do (false).
**What you do**: Start with `false` to test, then change to `true` when ready.

---

## 📊 **Step 4: Set Up Your Signal Generation**

### **Option A: Generate Signals Automatically**
```bash
# Run this on your Google VM every few minutes
source genx_env/bin/activate
python3 demo_excel_generator.py
```

This creates the CSV file with trading signals that your EA reads.

### **Option B: Use AMP for Full Automation**
```bash
# Let AMP handle everything automatically
python3 amp_cli.py run
```

This runs continuously and keeps generating fresh signals.

---

## 📂 **Step 5: Make Sure Files Are in the Right Place**

Your EA needs to find the signal file. Here's where it should be:

### **If you're running everything on the same computer:**
Put the CSV file in: `MetaTrader/MQL4/Files/MT4_Signals.csv`

### **If signals are generated on Google VM:**
You need to copy the file from your VM to your local computer:
1. **Download** `signal_output/MT4_Signals.csv` from your Google VM
2. **Put it** in your MetaTrader's `MQL4/Files/` folder
3. **Update it** regularly (or automate this with a script)

---

## 🚀 **Step 6: Start Trading**

1. **Open MetaTrader 4/5**
2. **Login to your Exness account**
3. **Open a chart** (EURUSD is good for testing)
4. **Drag your EA** from the Navigator onto the chart
5. **Configure the settings** (as explained above)
6. **Click OK**

### **What You Should See:**
- 😊 **Smiley face** in the top-right corner = EA is running
- 📝 **Messages in the "Experts" tab** = EA is working
- 📊 **"GenX Signal Reader" in the chart** = Everything connected

---

## 🔍 **Step 7: Monitor and Test**

### **First Hour - Watch Closely:**
- Check if EA finds the CSV file
- See if it reads signals correctly  
- Watch for any error messages
- Make sure it's not opening crazy trades

### **First Day - Check Regularly:**
- Monitor trade performance
- Adjust risk settings if needed
- Make sure signal file stays updated

### **After That - Relax:**
- Check once or twice a day
- Let the system do its work
- Enjoy your automated trading!

---

## 🚨 **Common Problems & Solutions**

### **Problem**: "File not found" error
**Solution**: Make sure `MT4_Signals.csv` is in the `MQL4/Files/` folder

### **Problem**: EA not making any trades
**Solution**: 
1. Check `EnableTrading = true`
2. Make sure your broker allows automated trading
3. Verify the CSV file has recent signals

### **Problem**: Too many trades opening
**Solution**: Lower the `MaxTrades` setting to 2-3

### **Problem**: Losing money fast
**Solution**: 
1. Lower `RiskPercent` to 0.5% or 1%
2. Check if signals are good quality
3. Maybe run in demo mode first

---

## 💡 **Pro Tips for Success**

### **Start Small & Test:**
- Use demo account first
- Start with 0.5% risk per trade
- Watch for a few days before increasing

### **Keep Signals Fresh:**
- Update CSV file at least daily
- Better yet, automate with AMP
- Old signals = bad trades

### **Monitor Your Account:**
- Check daily, not hourly
- Don't panic on small losses
- Trust the system but stay aware

### **Backup Plan:**
- Know how to turn off the EA quickly
- Have manual trading skills as backup
- Don't put all your money in automation

---

## 🎯 **Your 15-Minute Setup Checklist**

□ **Copy EA file to MetaTrader**  
□ **Restart MetaTrader**  
□ **Generate signal file** (`python3 demo_excel_generator.py`)  
□ **Copy CSV to MQL4/Files folder**  
□ **Drag EA onto chart**  
□ **Set RiskPercent = 1.0**  
□ **Set EnableTrading = false** (for testing)  
□ **Click OK and watch for 30 minutes**  
□ **If working well, set EnableTrading = true**  
□ **Enjoy automated trading!** 🎉

---

## 🤝 **Need Help?**

If something's not working:
1. **Check the MetaTrader "Experts" tab** for error messages
2. **Make sure your Exness account allows automated trading**
3. **Verify the CSV file exists and has recent data**
4. **Try with a demo account first**

**Remember**: This is like learning to drive - start slow, be careful, and you'll get the hang of it! 🚗💨