# 🎯 Subnet Alpha Trading Bots

A complete trading system for Bittensor subnet alpha tokens with two complementary bots:

## 🤖 **DCA Bot** - Buy Low
Dollar Cost Averaging bot that buys alpha when prices are favorable.

## 🔴 **Unstaking Bot** - Sell High  
Smart selling bot that unstakes alpha when prices reach profit targets.

## 🚀 What The System Does

### **DCA Bot Features:**
- **Smart DCA Strategy**: Buys a fixed TAO amount (e.g., 0.01 TAO) at regular intervals (e.g., every 5 minutes)
- **Price-Based Filtering**: Only buys when alpha price is at or below your threshold (e.g., ≤0.05 TAO)
- **Accumulation Focus**: Builds alpha positions during favorable market conditions

### **Unstaking Bot Features:**
- **Smart Profit-Taking**: Sells fixed alpha amounts (e.g., 0.1 alpha) when price reaches targets (e.g., ≥0.08 TAO)
- **Position Management**: Maintains minimum holdings while taking profits
- **High-Price Alerts**: Only sells when profitable price thresholds are met

### **Shared Features:**
- **Single Subnet Focus**: Both bots concentrate on one subnet you choose
- **Enhanced Logging**: Shows every trade with real-time session statistics
- **Session Analytics**: Tracks performance, averages, and totals for each bot
- **Network Resilience**: Auto-reconnects and retries on connection issues
- **Session Summaries**: Provides complete analytics when stopped
- **Secure Password Handling**: Manual entry with memory cleanup

## 📋 Quick Setup

1. **Install dependencies**:
   ```bash
   cd SubnetsBot
   pip install -r requirements.txt
   ```

2. **Configure both bots**:
   
   **DCA Bot** - Edit `dca_config.yaml`:
   ```yaml
   validator: "your_validator_hotkey_ss58_here"  # ← REPLACE THIS
   target_netuid: 1          # Choose your subnet
   purchase_amount: 0.01     # TAO amount per purchase
   interval_minutes: 5       # How often to buy
   min_balance: 0.5         # Stop when wallet hits this balance
   max_price_threshold: 0.05 # Only buy if price ≤ 0.05 TAO per alpha
   ```
   
   **Unstaking Bot** - Edit `unstaking_config.yaml`:
   ```yaml
   validator: "your_validator_hotkey_ss58_here"  # ← SAME AS ABOVE
   target_netuid: 1          # Same subnet as DCA bot
   unstake_amount: 0.1       # Alpha amount per sale
   interval_minutes: 10      # How often to check for selling
   min_price_threshold: 0.08 # Only sell if price ≥ 0.08 TAO per alpha
   min_holdings_threshold: 0.5 # Never sell below this amount
   ```

3. **Run the bots**:
   
   **DCA Bot** (in one terminal):
   ```bash
   python dca_bot.py
   ```
   
   **Unstaking Bot** (in another terminal):
   ```bash
   python unstaking_bot.py
   ```
   
   Both bots will prompt you to enter your wallet password securely:
   ```bash
   🔐 Enter wallet password: [type your password here]
   ```
   
   **Alternative (Less Secure)**: You can optionally set an environment variable:
   ```bash
   export WALLET_PASSWORD="your_wallet_password"
   python dca_bot.py  # or unstaking_bot.py
   ```
   ⚠️ **Not recommended on shared/rented servers** due to security risks.

## 💰 Complete Trading Strategy

### **Example Profitable Setup:**
```yaml
# DCA Bot - Buy Low
max_price_threshold: 0.05    # Buy below 0.05 TAO
purchase_amount: 0.01        # Spend 0.01 TAO per purchase

# Unstaking Bot - Sell High  
min_price_threshold: 0.08    # Sell above 0.08 TAO
unstake_amount: 0.1          # Sell 0.1 alpha per sale
```

**Profit Margin**: 60% (0.08/0.05 = 1.6x)

This setup automatically:
- 📈 **Accumulates** alpha when price ≤ 0.05 TAO
- 📉 **Takes profits** when price ≥ 0.08 TAO  
- 🔄 **Compounds** gains through both price appreciation and position building

## 📊 Example Output

### **DCA Bot Output:**

```
🚀 Initializing DCA Bot...
🔐 Enter wallet password: [hidden input]
✅ Wallet 'default' loaded successfully
✅ Connected to Bittensor network (Block: 1234567)

DCA Bot Configuration
🎯 Target Subnet: 1
💰 Purchase Amount: 0.0100 TAO per trade
⏰ Interval: 5 minutes
🛑 Stop Balance: 0.5000 TAO
💲 Max Price: 0.050000 TAO per alpha
🔑 Validator: 5HYjn...

💳 Starting Wallet Balance: 5.2500 TAO
🪙 Current Alpha Holdings: 0.125000 alpha
────────────────────────────────────────────────────────────

⏸️  Price too high: 0.550000 TAO > 0.050000 TAO threshold
   💡 Waiting for better price. Current: 0.550000 TAO, Target: ≤0.050000 TAO
⏳ Waiting 5 minutes until next purchase...

🔄 Attempting purchase: 0.0100 TAO → 0.200000 alpha @ 0.050000 TAO/alpha
🟢 TRADE #1 | 2024-01-15 14:30:25
   💰 Bought: 0.018182 alpha for 0.0100 TAO
   📊 Price: 0.550000 TAO per alpha
   📈 Avg Price: 0.550000 TAO per alpha
   💎 Total Invested: 0.010000 TAO
   🪙 Total Holdings: 0.143182 alpha
   💳 Wallet Balance: 5.2400 TAO
────────────────────────────────────────────────────────────
⏳ Waiting 5 minutes until next purchase...

### **Unstaking Bot Output:**
```
🚀 Initializing Unstaking Bot...
🔐 Enter wallet password: [hidden input]
✅ Wallet 'default' loaded successfully
✅ Connected to Bittensor network (Block: 1234567)

Unstaking Bot Configuration
🎯 Target Subnet: 1
🪙 Unstake Amount: 0.100000 alpha per trade
⏰ Interval: 10 minutes
💲 Min Price: 0.080000 TAO per alpha
🪙 Min Holdings: 0.500000 alpha
🔑 Validator: 5HYjn...

💳 Starting Wallet Balance: 2.1500 TAO
🪙 Current Alpha Holdings: 1.425000 alpha
────────────────────────────────────────────────────────────

⏸️  Price too low: 0.065000 TAO < 0.080000 TAO threshold
   💡 Waiting for higher price. Current: 0.065000 TAO, Target: ≥0.080000 TAO
⏳ Waiting 10 minutes until next check...

🔄 Attempting sale: 0.100000 alpha → 0.008000 TAO @ 0.080000 TAO/alpha
🔴 SALE #1 | 2024-01-15 15:45:25
   💰 Sold: 0.100000 alpha for 0.008000 TAO
   📊 Price: 0.080000 TAO per alpha
   📈 Avg Price: 0.080000 TAO per alpha
   💎 Total Earned: 0.008000 TAO
   🪙 Remaining Holdings: 1.325000 alpha
   💳 Wallet Balance: 2.1580 TAO
────────────────────────────────────────────────────────────
⏳ Waiting 10 minutes until next check...
```
```

## 🛑 When Bots Stop

### **DCA Bot** stops when:
- Wallet balance drops below `min_balance`
- You press Ctrl+C
- Insufficient funds for next purchase

### **Unstaking Bot** stops when:
- You press Ctrl+C
- Network connection issues (with auto-retry)
- No alpha holdings to sell

### Example DCA Summary:
```
📊 DCA Session Summary
┌─────────────────────┬─────────────────────┐
│ 🎯 Target Subnet    │                   1 │
│ ⏱️ Session Duration  │          2h 15m 30s │
│ 🔢 Total Trades      │                  27 │
│ 💰 Total TAO Invested│            0.270000 │
│ 🪙 Total Alpha Bought│            0.491818 │
│ 📈 Average Price Paid│            0.549130 │
│ 📊 Price Change      │              +2.45% │
└─────────────────────┴─────────────────────┘

📋 Trade History
# 1 | 2024-01-15 14:30:25 | 0.018182 alpha @ 0.550000 TAO | Spent: 0.0100 TAO
# 2 | 2024-01-15 14:35:25 | 0.018519 alpha @ 0.540000 TAO | Spent: 0.0100 TAO
# 3 | 2024-01-15 14:40:25 | 0.018182 alpha @ 0.550000 TAO | Spent: 0.0100 TAO
...

### Example Unstaking Summary:
```
📊 Unstaking Session Summary
┌─────────────────────┬─────────────────────┐
│ 🎯 Target Subnet    │                   1 │
│ ⏱️ Session Duration  │          4h 20m 15s │
│ 🔢 Total Sales      │                   8 │
│ 🪙 Total Alpha Sold │            0.800000 │
│ 💰 Total TAO Earned │            0.068000 │
│ 📈 Average Price    │            0.085000 │
│ 📊 Price Change     │              +6.25% │
└─────────────────────┴─────────────────────┘

📋 Sales History
# 1 | 2024-01-15 15:45:25 | 0.100000 alpha @ 0.080000 TAO | Earned: 0.008000 TAO
# 2 | 2024-01-15 16:15:25 | 0.100000 alpha @ 0.085000 TAO | Earned: 0.008500 TAO
...
```

Session-Only Calculations:
📈 **DCA Bot**: Average price and total invested based only on current session
📉 **Unstaking Bot**: Average sale price and total earned based only on current session  
🪙 **Total Holdings**: Your complete subnet position (includes all previous activity)
```

## ⚙️ Configuration Options

### **DCA Bot Settings** (`dca_config.yaml`)
```yaml
target_netuid: 1        # Which subnet to buy alpha in
purchase_amount: 0.01   # TAO amount per purchase
interval_minutes: 5     # Minutes between purchases
min_balance: 0.5       # Stop when wallet balance hits this
max_price_threshold: 0.05  # Only buy if price is ≤ this value (0.0 = no limit)
```

### **Unstaking Bot Settings** (`unstaking_config.yaml`)
```yaml
target_netuid: 1        # Which subnet to sell alpha from (match DCA bot)
unstake_amount: 0.1     # Alpha amount per sale
interval_minutes: 10    # Minutes between price checks
min_price_threshold: 0.08  # Only sell if price is ≥ this value (0.0 = no limit)
min_holdings_threshold: 0.5  # Never sell below this alpha amount
```

### Complete Trading Strategies

**Conservative Long-Term Growth**:
```yaml
# DCA Bot
purchase_amount: 0.01
interval_minutes: 15
max_price_threshold: 0.03  # Buy below 0.03 TAO
min_balance: 1.0

# Unstaking Bot  
unstake_amount: 0.05
interval_minutes: 30
min_price_threshold: 0.07  # Sell above 0.07 TAO
min_holdings_threshold: 1.0  # Keep substantial position
```

**Aggressive High-Frequency Trading**:
```yaml
# DCA Bot
purchase_amount: 0.1
interval_minutes: 3
max_price_threshold: 0.08  # Buy up to 0.08 TAO
min_balance: 0.5

# Unstaking Bot
unstake_amount: 0.2
interval_minutes: 5  
min_price_threshold: 0.10  # Sell above 0.10 TAO
min_holdings_threshold: 0.2
```

**Value Hunter (Wide Margins)**:
```yaml
# DCA Bot
purchase_amount: 0.05
interval_minutes: 30
max_price_threshold: 0.025  # Only buy very cheap
min_balance: 2.0

# Unstaking Bot
unstake_amount: 0.15
interval_minutes: 15
min_price_threshold: 0.08   # Sell for good profits
min_holdings_threshold: 0.5
```

**Emergency Mode (No Filters)**:
```yaml
# DCA Bot - Buy at any price
max_price_threshold: 0.0

# Unstaking Bot - Sell everything
min_price_threshold: 0.0
min_holdings_threshold: 0.0
```

## 🔧 Troubleshooting

**Bot won't start:**
- Check wallet name in config
- Verify validator hotkey is correct
- Enter correct wallet password when prompted
- Ensure wallet file exists and isn't corrupted

**"Subnet not found" error:**
- Verify `target_netuid` exists and is active
- Check Bittensor network status

**"Insufficient balance" immediately:**
- Check your actual wallet balance
- Lower `purchase_amount` or `min_balance`

**Connection errors:**
- Check internet connection
- Wait for Bittensor network issues to resolve

## 📈 Tips for Success

1. **Start Small**: Begin with 0.01 TAO purchases and 0.05 alpha sales to test
2. **Research Prices**: Check historical alpha prices to set smart buy/sell thresholds
3. **Set Profit Margins**: Ensure sell threshold > buy threshold for profitability
4. **Monitor First**: Watch the first few cycles of both bots to ensure they work
5. **Secure Setup**: Use manual password entry, especially on shared servers
6. **Coordinate Bots**: Use same subnet for both bots, different intervals for balance
7. **Position Management**: Set appropriate `min_holdings_threshold` to maintain base position
8. **Keep Reserves**: Set `min_balance` to keep some TAO for fees and opportunities
9. **Track Performance**: Review session summaries to analyze your complete trading strategy

## ⚠️ Important Notes

- **Complete Trading System**: DCA bot buys, unstaking bot sells
- **Smart Automation**: Both bots use time-based AND price-based strategies  
- **Price Coordination**: Set buy threshold < sell threshold for profitability
- **Position Management**: Unstaking bot preserves minimum holdings
- **Always test with small amounts first**
- **Research price history** to set appropriate thresholds
- **Monitor both wallet balance and alpha holdings**
- **Bots can run independently** or together for complete automation

## 🔐 Security Features

### **Secure Password Handling**
- 🔐 **Manual password entry**: Prompts for password at startup (recommended)
- 🧹 **Memory cleanup**: Password cleared from memory after use
- ⚠️ **Environment variable support**: Optional but less secure on shared servers
- 🔒 **One-time entry**: Password only needed once per session, not per trade

### **When Password is Required**
- ✅ **Bot startup** - Enter once when starting
- ✅ **After restart** - Need to re-enter if bot is restarted
- ❌ **Not during trades** - All purchases happen automatically after unlock
- ❌ **Not during waits** - No interruption during interval periods

### **Best Practices for Servers**
- 🏠 **Local development**: Safest option for testing
- 🔒 **Dedicated servers**: Better than shared hosting
- ⚠️ **Shared servers**: Use manual password entry only
- 🚫 **Avoid env vars**: On rented/shared infrastructure like DATA Crunch

## 🛡️ Safety & Reliability Features

### **Network Resilience**
- 🔄 **Auto-reconnection**: Reconnects automatically if connection drops
- 🔁 **Retry Logic**: 3 attempts for all network operations with smart delays
- 💪 **Continuous Operation**: Bot keeps running through network hiccups
- ⚡ **Smart Recovery**: Graceful error handling without stopping the process

### **Enhanced Monitoring**
- 📊 **Real-time Stats**: Session average price and total invested after each trade
- 🪙 **Live Holdings**: Shows your current total alpha position in the subnet
- 📈 **Session Analytics**: Running calculations based only on current session trades
- 💳 **Balance Tracking**: Continuous wallet balance monitoring

### **General Safety**
- ✅ Automatic stopping when balance is low
- ✅ Graceful shutdown with Ctrl+C
- ✅ Comprehensive trade logging with session statistics
- ✅ Session summaries with all transaction details
- ✅ Error handling and recovery
- ✅ Secure password handling with memory cleanup

---

**💡 Pro Tip**: DCA works best over longer periods. Set it up and let it run for hours or days to smooth out price volatility!

**⚠️ Risk Warning**: Only invest what you can afford to lose. Cryptocurrency trading involves risk. 