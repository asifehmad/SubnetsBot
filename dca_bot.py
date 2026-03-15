#!/usr/bin/env python3
"""
Simple Subnet Alpha DCA Bot

A straightforward Dollar Cost Averaging bot that:
- Buys a fixed TAO amount in a single subnet at regular intervals
- Logs all transactions clearly
- Tracks average price and total investments
- Stops when wallet balance hits minimum threshold
- Provides detailed session summary when stopped
"""

import asyncio
import os
import time
import argparse
import bittensor as bt
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import signal
import sys

console = Console()
bt.trace()

class DCABot:
    def __init__(self, config):
        self.config = config
        self.wallet = None
        self.sub = None
        self.session_trades = []
        self.running = True
        self.start_time = time.time()
        
        # Session tracking
        self.total_tao_invested = 0.0
        self.total_alpha_bought = 0.0
        self.trades_count = 0
        
    async def initialize(self):
        """Initialize wallet and subtensor connection."""
        console.print(Panel("🚀 Initializing DCA Bot...", title="Startup", style="bold green"))
        
        # Set up wallet
        try:
            self.wallet = bt.wallet(name=self.config.wallet)
            password = os.environ.get("WALLET_PASSWORD")
            if not password:
                # Prompt for password if not in environment (safer)
                import getpass
                console.print(f"Using Wallet '{self.config.wallet}' ")
                password = getpass.getpass("🔐 Enter wallet password: ")
            if password:
                self.wallet.coldkey_file.save_password_to_env(password)
                # Clear password from memory
                del password
            self.wallet.unlock_coldkey()
            console.print(f"✅ Wallet '{self.config.wallet}' loaded successfully")
        except Exception as e:
            console.print(Panel(f"❌ Error loading wallet: {e}", title="Error", style="bold red"))
            return False
        
        # Set up subtensor connection
        try:
            self.sub = bt.async_subtensor()
            await self.sub.initialize()
            current_block = await self.sub.get_current_block()
            console.print(f"✅ Connected to Bittensor network (Block: {current_block})")
        except Exception as e:
            console.print(Panel(f"❌ Error connecting to network: {e}", title="Error", style="bold red"))
            return False
        
        return True
    
    async def get_wallet_balance(self):
        """Get current wallet balance with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return float(await self.sub.get_balance(self.wallet.coldkey.ss58_address))
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"⚠️ Error getting wallet balance (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise e
    
    async def get_subnet_info(self):
        """Get information about the target subnet with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                subnets = await self.sub.all_subnets()
                for subnet in subnets:
                    if subnet.netuid == self.config.target_netuid:
                        return subnet
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"⚠️ Error getting subnet info (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise e
    
    async def buy_alpha(self, amount_tao):
        """Buy alpha in the target subnet with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await self.sub.add_stake(
                    wallet=self.wallet,
                    hotkey_ss58=self.config.validator,
                    netuid=self.config.target_netuid,
                    amount=bt.Balance.from_tao(amount_tao),
                    wait_for_inclusion=False,
                    wait_for_finalization=False
                )
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"⚠️ Error buying alpha (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(10)  # Longer wait for transaction retries
                    continue
                else:
                    console.print(f"❌ Failed to buy alpha after {max_retries} attempts: {e}")
                    return False
    
    async def get_current_holdings(self):
        """Get current alpha holdings in the target subnet with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                stake_info = await self.sub.get_stake_for_coldkey(coldkey_ss58=self.wallet.coldkeypub.ss58_address)
                for stake in stake_info:
                    if stake.netuid == self.config.target_netuid and stake.hotkey_ss58 == self.config.validator:
                        return float(stake.stake)
                return 0.0
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"⚠️ Error getting holdings (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(5)
                    continue
                else:
                    console.print(f"❌ Failed to get holdings after {max_retries} attempts: {e}")
                    return 0.0
    
    def log_trade(self, amount_tao, alpha_price, alpha_amount, wallet_balance, total_holdings):
        """Log a trade transaction."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trade_record = {
            'timestamp': timestamp,
            'amount_tao': amount_tao,
            'alpha_price': alpha_price,
            'alpha_amount': alpha_amount,
            'wallet_balance_after': wallet_balance,
            'trade_number': self.trades_count + 1
        }
        
        self.session_trades.append(trade_record)
        self.total_tao_invested += amount_tao
        self.total_alpha_bought += alpha_amount
        self.trades_count += 1
        
        # Calculate running averages
        avg_price = self.calculate_average_price()
        
        # Console log with enhanced information
        console.print(f"🟢 TRADE #{self.trades_count} | {timestamp}")
        console.print(f"   💰 Bought: {alpha_amount:.6f} alpha for {amount_tao:.4f} TAO")
        console.print(f"   📊 Price: {alpha_price:.6f} TAO per alpha")
        console.print(f"   📈 Avg Price: {avg_price:.6f} TAO per alpha")
        console.print(f"   💎 Total Invested: {self.total_tao_invested:.6f} TAO")
        console.print(f"   🪙 Total Holdings: {total_holdings:.6f} alpha")
        console.print(f"   💳 Wallet Balance: {wallet_balance:.4f} TAO")
        console.print("─" * 60)
    
    def calculate_average_price(self):
        """Calculate average price paid for alpha."""
        if self.total_alpha_bought > 0:
            return self.total_tao_invested / self.total_alpha_bought
        return 0.0
    
    def print_session_summary(self):
        """Print detailed session summary."""
        session_duration = time.time() - self.start_time
        hours = int(session_duration // 3600)
        minutes = int((session_duration % 3600) // 60)
        seconds = int(session_duration % 60)
        
        avg_price = self.calculate_average_price()
        
        # Create summary table
        table = Table(title="📊 DCA Session Summary", box=box.ROUNDED, header_style="bold white on blue")
        table.add_column("Metric", style="cyan", justify="left")
        table.add_column("Value", style="white", justify="right")
        
        table.add_row("🎯 Target Subnet", str(self.config.target_netuid))
        table.add_row("⏱️ Session Duration", f"{hours}h {minutes}m {seconds}s")
        table.add_row("🔢 Total Trades", str(self.trades_count))
        table.add_row("💰 Total TAO Invested", f"{self.total_tao_invested:.6f} TAO")
        table.add_row("🪙 Total Alpha Bought", f"{self.total_alpha_bought:.6f} alpha")
        table.add_row("📈 Average Price Paid", f"{avg_price:.6f} TAO per alpha")
        
        if self.trades_count > 0:
            first_trade = self.session_trades[0]
            last_trade = self.session_trades[-1]
            price_change = ((last_trade['alpha_price'] - first_trade['alpha_price']) / first_trade['alpha_price']) * 100
            table.add_row("📊 Price Change", f"{price_change:+.2f}%")
        
        console.print()
        console.print(table)
        
        # Print detailed trade history
        if self.session_trades:
            console.print()
            console.print(Panel("📋 Trade History", style="bold blue"))
            for trade in self.session_trades:
                console.print(
                    f"#{trade['trade_number']:2d} | {trade['timestamp']} | "
                    f"{trade['alpha_amount']:8.6f} alpha @ {trade['alpha_price']:8.6f} TAO | "
                    f"Spent: {trade['amount_tao']:.4f} TAO"
                )
    
    async def dca_cycle(self):
        """Execute one DCA cycle."""
        try:
            # Check wallet balance
            wallet_balance = await self.get_wallet_balance()
            
            # Check if we should stop due to low balance
            if wallet_balance < self.config.min_balance:
                console.print(f"🛑 Stopping: Wallet balance ({wallet_balance:.4f} TAO) below minimum ({self.config.min_balance:.4f} TAO)")
                return False
            
            # Check if we have enough for this purchase
            if wallet_balance < self.config.purchase_amount:
                console.print(f"🛑 Stopping: Insufficient balance for purchase ({wallet_balance:.4f} < {self.config.purchase_amount:.4f} TAO)")
                return False
            
            # Get subnet information
            subnet_info = await self.get_subnet_info()
            if not subnet_info:
                console.print(f"❌ Error: Could not find subnet {self.config.target_netuid}")
                return False
            
            alpha_price = float(subnet_info.price)
            alpha_amount = self.config.purchase_amount / alpha_price
            
            # Check price threshold if configured
            if hasattr(self.config, 'max_price_threshold') and self.config.max_price_threshold > 0:
                if alpha_price > self.config.max_price_threshold:
                    console.print(f"Bot is running for subnet {str(self.config.target_netuid)}")
                    console.print(f"⏸️  Price too high: {alpha_price:.6f} TAO > {self.config.max_price_threshold:.6f} TAO threshold")
                    console.print(f"   💡 Waiting for better price. Current: {alpha_price:.6f} TAO, Target: ≤{self.config.max_price_threshold:.6f} TAO")
                    return True  # Continue running, just skip this purchase
            
            console.print(f"🔄 Attempting purchase: {self.config.purchase_amount:.4f} TAO → {alpha_amount:.6f} alpha @ {alpha_price:.6f} TAO/alpha")
            
            # Execute the purchase
            success = await self.buy_alpha(self.config.purchase_amount)
            
            if success:
                # Update balance and holdings after purchase
                wallet_balance = await self.get_wallet_balance()
                total_holdings = await self.get_current_holdings()
                self.log_trade(self.config.purchase_amount, alpha_price, alpha_amount, wallet_balance, total_holdings)
            else:
                console.print("❌ Purchase failed")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error in DCA cycle: {e}")
            console.print("🔄 Attempting to reconnect to network...")
            
            # Try to reconnect to the network
            try:
                if self.sub:
                    await self.sub.close()
                await asyncio.sleep(10)  # Wait before reconnecting
                self.sub = bt.async_subtensor()
                await self.sub.initialize()
                current_block = await self.sub.get_current_block()
                console.print(f"✅ Reconnected to network (Block: {current_block})")
                return True  # Continue running after successful reconnection
            except Exception as reconnect_error:
                console.print(f"❌ Failed to reconnect: {reconnect_error}")
                console.print("⏳ Will retry in next cycle...")
                return True  # Continue running, will retry in next cycle
    
    async def run(self):
        """Main bot loop."""
        if not await self.initialize():
            return
        
                # Print initial configuration
        price_filter_text = ""
        if hasattr(self.config, 'max_price_threshold') and self.config.max_price_threshold > 0:
            price_filter_text = f"💲 Max Price: {self.config.max_price_threshold:.6f} TAO per alpha\n"
        else:
            price_filter_text = f"💲 Max Price: No limit (buy at any price)\n"
            
        console.print(Panel(
            f"🎯 Target Subnet: {self.config.target_netuid}\n"
            f"💰 Purchase Amount: {self.config.purchase_amount:.4f} TAO per trade\n"
            f"⏰ Interval: {self.config.interval_seconds} seconds\n"
            f"🛑 Stop Balance: {self.config.min_balance:.4f} TAO\n"
            f"{price_filter_text}"
            f"🔑 Validator: {self.config.validator}",
            title="DCA Bot Configuration",
            style="bold cyan"
        ))
        
        # Initial status
        wallet_balance = await self.get_wallet_balance()
        holdings = await self.get_current_holdings()
        console.print(f"💳 Starting Wallet Balance: {wallet_balance:.4f} TAO")
        console.print(f"🪙 Current Alpha Holdings: {holdings:.6f} alpha")
        console.print("─" * 60)
        
        try:
            while self.running:
                # Execute DCA cycle
                should_continue = await self.dca_cycle()
                if not should_continue:
                    break
                
                # Wait for next interval
                console.print(f"⏳ Waiting {self.config.interval_seconds} seconds until next purchase...")
                for i in range(self.config.interval_seconds):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            console.print("\n🛑 Bot stopped by user")
        
        finally:
            console.print()
            console.print(Panel("📊 Generating Session Summary...", style="bold yellow"))
            self.print_session_summary()
            
            if self.sub:
                await self.sub.close()
    
    def stop(self):
        """Stop the bot gracefully."""
        self.running = False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Subnet Alpha DCA Bot")
    parser.add_argument("--wallet", type=str, default="default", help="Bittensor wallet name")
    parser.add_argument("--validator", type=str, required=True, help="Validator hotkey SS58 address")
    parser.add_argument("--target_netuid", type=int, required=True, help="The subnet you want to DCA into (e.g. 1)")
    parser.add_argument("--purchase_amount", type=float, required=True, help="Fixed TAO amount to buy each interval")
    parser.add_argument("--interval_seconds", type=int, default=5, help="How often to buy (in seconds)")
    parser.add_argument("--min_balance", type=float, default=0.5, help="Stop buying when wallet balance hits this threshold (in TAO)")
    parser.add_argument("--max_price_threshold", type=float, default=0.0, help="Only buy if alpha price is at or below this value (in TAO). 0.0 to disable")
    return parser.parse_args()

def signal_handler(bot):
    """Handle interrupt signals gracefully."""
    def handler(signum, frame):
        console.print("\n🛑 Received stop signal...")
        bot.stop()
    return handler

async def main():
    """Main entry point."""
    console.print(Panel("🤖 Subnet Alpha DCA Bot Starting...", title="Welcome", style="bold green"))
    
    # Load configuration
    config = parse_args()
    
    # Create and run bot
    bot = DCABot(config)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler(bot))
    signal.signal(signal.SIGTERM, signal_handler(bot))
    
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 
