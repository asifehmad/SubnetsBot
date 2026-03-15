# 🎯 Subnet Alpha Trading Bots

A complete trading system for Bittensor subnet alpha tokens with two complementary bots:

## 🤖 **DCA Bot** - Buy Low
Dollar Cost Averaging bot that buys alpha when prices are favorable.

## 🔴 **Unstaking Bot** - Sell High  
Smart selling bot that unstakes alpha when prices reach profit targets.

## 📋 Quick Setup

1. **Install dependencies**:
   ```bash
   cd SubnetsBot
   pip install -r requirements.txt
   ```

2. **Run the bots via CLI**:
   Both bots use command-line arguments instead of config files.

   **Run DCA Bot**:
   ```bash
   python dca_bot.py \
       --wallet your_wallet \
       --validator your_validator_hotkey \
       --target_netuid 1 \
       --purchase_amount 0.01 \
       --interval_seconds 5 \
       --max_tao_investment 5.0 \
       --max_price_threshold 0.05
   ```

   **Run Unstaking Bot**:
   ```bash
   python unstaking_bot.py \
       --wallet your_wallet \
       --validator your_validator_hotkey \
       --target_netuid 1 \
       --unstake_amount 0.1 \
       --interval_seconds 10 \
       --min_price_threshold 0.08 \
       --min_holdings_threshold 0.5
   ```

3. **Secure Password Entry**:
   When prompted, enter your wallet password securely. Wait for network connection and initialization.

## ⚙️ CLI Arguments Reference

You can view all available options by running:
```bash
python dca_bot.py --help
python unstaking_bot.py --help
```

### DCA Bot
- `--wallet`: Bittensor wallet name (default: "default")
- `--validator`: Validator hotkey SS58 address (required)
- `--target_netuid`: Target subnet UID (required)
- `--purchase_amount`: Fixed TAO amount to buy (required)
- `--interval_seconds`: Wait time between trades (default: 5)
- `--min_balance`: Stop buying if wallet TAO balance drops below this (default: 0.0 = disabled)
- `--max_price_threshold`: Maximum TAO price per alpha to buy (default: 0.0 = disabled)
- `--max_tao_investment`: Stop buying when this much total TAO has been invested in this session (default: 0.0 = disabled)

### Unstaking Bot
- `--wallet`: Bittensor wallet name (default: "default")
- `--validator`: Validator hotkey SS58 address (required)
- `--target_netuid`: Target subnet UID (required)
- `--unstake_amount`: Fixed alpha amount to sell (required)
- `--interval_seconds`: Wait time between sell checks (default: 10)
- `--min_price_threshold`: Minimum TAO price per alpha to sell (default: 0.08)
- `--min_holdings_threshold`: Minimum alpha holdings to retain (default: 0.5)

## 💰 Trading Strategy Example

**Buy Low:** DCA bot buys at `0.01 TAO` per trade when the price is `≤ 0.05 TAO`.
**Sell High:** Unstaking bot sells `0.1 alpha` per trade when the price is `≥ 0.08 TAO`.
**Profit Margin**: 60% (0.08 / 0.05 = 1.6x)

---
**💡 Pro Tip**: Both bots can run independently or continuously in parallel for complete automation. Use `tmux` or `screen` to keep them running on remote servers!

**⚠️ Risk Warning**: Only invest what you can afford to lose. Cryptocurrency trading involves risk.
