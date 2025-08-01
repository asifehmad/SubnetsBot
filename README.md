# 🎯 Simple Subnet Alpha DCA Bot

A straightforward Dollar Cost Averaging (DCA) bot for Bittensor subnet alpha tokens. This bot focuses on one thing: buying a fixed amount of alpha in a specific subnet at regular intervals.

## 🚀 What It Does

- **DCA Strategy**: Buys a fixed TAO amount (e.g., 0.01 TAO) at regular intervals (e.g., every 5 minutes)
- **Single Subnet Focus**: Concentrates on one subnet you choose
- **Smart Stopping**: Automatically stops when wallet balance hits your minimum threshold
- **Enhanced Logging**: Shows every purchase with real-time session statistics
- **Session Analytics**: Average price, total invested, and current holdings after each trade
- **Network Resilience**: Auto-reconnects and retries on connection issues
- **Session Summary**: Provides complete analytics when stopped

## 📋 Quick Setup

1. **Install dependencies**:
   ```bash
   cd SubnetsBot
   pip install -r simple_requirements.txt
   ```

2. **Configure the bot**:
   Edit `dca_config.yaml`:
   ```yaml
   validator: "your_validator_hotkey_ss58_here"  # ← REPLACE THIS
   target_netuid: 1          # Choose your subnet
   purchase_amount: 0.01     # TAO amount per purchase
   interval_minutes: 5       # How often to buy
   min_balance: 0.5         # Stop when wallet hits this balance
   ```

3. **Run the bot**:
   ```bash
   python dca_bot.py
   ```
   
   The bot will prompt you to enter your wallet password securely:
   ```bash
   🔐 Enter wallet password: [type your password here]
   ```
   
   **Alternative (Less Secure)**: You can optionally set an environment variable:
   ```bash
   export WALLET_PASSWORD="your_wallet_password"
   python dca_bot.py
   ```
   ⚠️ **Not recommended on shared/rented servers** due to security risks.

## 📊 Example Output

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
🔑 Validator: 5HYjn...

💳 Starting Wallet Balance: 5.2500 TAO
🪙 Current Alpha Holdings: 0.125000 alpha
────────────────────────────────────────────────────────────

🔄 Attempting purchase: 0.0100 TAO → 0.018182 alpha @ 0.550000 TAO/alpha
🟢 TRADE #1 | 2024-01-15 14:30:25
   💰 Bought: 0.018182 alpha for 0.0100 TAO
   📊 Price: 0.550000 TAO per alpha
   📈 Avg Price: 0.550000 TAO per alpha
   💎 Total Invested: 0.010000 TAO
   🪙 Total Holdings: 0.143182 alpha
   💳 Wallet Balance: 5.2400 TAO
────────────────────────────────────────────────────────────
⏳ Waiting 5 minutes until next purchase...
```

## 🛑 When Bot Stops

The bot automatically stops and shows a summary when:
- Wallet balance drops below `min_balance`
- You press Ctrl+C
- Insufficient funds for next purchase

### Example Summary:
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

Session-Only Calculations:
📈 Average Price: Based only on trades made in this session
💎 Total Invested: TAO spent in current session only
🪙 Total Holdings: Your complete subnet position (includes previous holdings)
```

## ⚙️ Configuration Options

### Basic Settings
```yaml
target_netuid: 1        # Which subnet to buy alpha in
purchase_amount: 0.01   # TAO amount per purchase
interval_minutes: 5     # Minutes between purchases
min_balance: 0.5       # Stop when wallet balance hits this
```

### Popular Subnets
- `1`: Text Prompting subnet
- `3`: Conversational AI subnet
- `5`: Open Kaito subnet
- `7`: Mining subnet
- `9`: Pretraining subnet
- `11`: Writing subnet

### Strategy Examples

**Conservative (Long-term)**:
```yaml
purchase_amount: 0.01
interval_minutes: 15
min_balance: 1.0
```

**Aggressive (Short-term)**:
```yaml
purchase_amount: 0.1
interval_minutes: 3
min_balance: 0.5
```

**Hourly DCA**:
```yaml
purchase_amount: 0.05
interval_minutes: 60
min_balance: 2.0
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

1. **Start Small**: Begin with 0.01 TAO purchases to test
2. **Monitor First**: Watch the first few trades to ensure it's working
3. **Secure Setup**: Use manual password entry, especially on shared servers
4. **Adjust Intervals**: 5-15 minutes is usually good for most subnets
5. **Keep Reserves**: Set `min_balance` to keep some TAO for fees
6. **Track Performance**: Review the session summary to analyze your DCA strategy

## ⚠️ Important Notes

- **This bot only buys alpha** - it doesn't sell
- **DCA reduces timing risk** by averaging out price fluctuations
- **Always test with small amounts first**
- **Monitor your wallet balance** to ensure sufficient funds
- **The bot will stop automatically** when funds run low

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