#!/usr/bin/env python3
"""
Subnet Alpha Unstaking Bot

A smart unstaking bot that sells alpha for TAO when prices hit target levels.
Complements the DCA bot by providing the "sell high" part of the strategy.

Features:
- Sells fixed alpha amounts when price reaches target thresholds
- Comprehensive session tracking and analytics
- Network resilience with auto-reconnection
- Real-time profit calculations and statistics
- Detailed session summaries when stopped
"""

import asyncio
import os
import time
import yaml
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

class UnstakingBot:
    def __init__(self, config):
        self.config = config
        self.wallet = None
        self.sub = None
        self.session_trades = []
        self.running = True
        self.start_time = time.time()
        
        # Session tracking
        self.total_tao_earned = 0.0
        self.total_alpha_sold = 0.0
        self.trades_count = 0
        
    async def initialize(self):
        """Initialize wallet and subtensor connection."""
        console.print(Panel("🚀 Initializing Unstaking Bot...", title="Startup", style="bold green"))
        
        # Set up wallet
        try:
            self.wallet = bt.wallet(name=self.config.wallet)
            password = os.environ.get("WALLET_PASSWORD")
            if not password:
                # Prompt for password if not in environment (safer)
                import getpass
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
    
    async def unstake_alpha(self, amount_alpha):
        """Unstake/sell alpha from the target subnet with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await self.sub.unstake(
                    wallet=self.wallet,
                    hotkey_ss58=self.config.validator,
                    netuid=self.config.target_netuid,
                    amount=bt.Balance.from_tao(amount_alpha),
                    wait_for_inclusion=False,
                    wait_for_finalization=False
                )
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"⚠️ Error unstaking alpha (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(10)  # Longer wait for transaction retries
                    continue
                else:
                    console.print(f"❌ Failed to unstake alpha after {max_retries} attempts: {e}")
                    return False
    
    def log_trade(self, alpha_amount, alpha_price, tao_earned, wallet_balance, remaining_holdings):
        """Log an unstaking transaction."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trade_record = {
            'timestamp': timestamp,
            'alpha_amount': alpha_amount,
            'alpha_price': alpha_price,
            'tao_earned': tao_earned,
            'wallet_balance_after': wallet_balance,
            'trade_number': self.trades_count + 1
        }
        
        self.session_trades.append(trade_record)
        self.total_tao_earned += tao_earned
        self.total_alpha_sold += alpha_amount
        self.trades_count += 1
        
        # Calculate running averages
        avg_price = self.calculate_average_price()
        
        # Console log with enhanced information
        console.print(f"🔴 SALE #{self.trades_count} | {timestamp}")
        console.print(f"   💰 Sold: {alpha_amount:.6f} alpha for {tao_earned:.6f} TAO")
        console.print(f"   📊 Price: {alpha_price:.6f} TAO per alpha")
        console.print(f"   📈 Avg Price: {avg_price:.6f} TAO per alpha")
        console.print(f"   💎 Total Earned: {self.total_tao_earned:.6f} TAO")
        console.print(f"   🪙 Remaining Holdings: {remaining_holdings:.6f} alpha")
        console.print(f"   💳 Wallet Balance: {wallet_balance:.4f} TAO")
        console.print("─" * 60)
    
    def calculate_average_price(self):
        """Calculate average price received for alpha sales."""
        if self.total_alpha_sold > 0:
            return self.total_tao_earned / self.total_alpha_sold
        return 0.0
    
    def print_session_summary(self):
        """Print detailed session summary."""
        session_duration = time.time() - self.start_time
        hours = int(session_duration // 3600)
        minutes = int((session_duration % 3600) // 60)
        seconds = int(session_duration % 60)
        
        avg_price = self.calculate_average_price()
        
        # Create summary table
        table = Table(title="📊 Unstaking Session Summary", box=box.ROUNDED, header_style="bold white on red")
        table.add_column("Metric", style="cyan", justify="left")
        table.add_column("Value", style="white", justify="right")
        
        table.add_row("🎯 Target Subnet", str(self.config.target_netuid))
        table.add_row("⏱️ Session Duration", f"{hours}h {minutes}m {seconds}s")
        table.add_row("🔢 Total Sales", str(self.trades_count))
        table.add_row("🪙 Total Alpha Sold", f"{self.total_alpha_sold:.6f} alpha")
        table.add_row("💰 Total TAO Earned", f"{self.total_tao_earned:.6f} TAO")
        table.add_row("📈 Average Price Received", f"{avg_price:.6f} TAO per alpha")
        
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
            console.print(Panel("📋 Sales History", style="bold red"))
            for trade in self.session_trades:
                console.print(
                    f"#{trade['trade_number']:2d} | {trade['timestamp']} | "
                    f"{trade['alpha_amount']:8.6f} alpha @ {trade['alpha_price']:8.6f} TAO | "
                    f"Earned: {trade['tao_earned']:.6f} TAO"
                )
    
    async def unstaking_cycle(self):
        """Execute one unstaking cycle."""
        try:
            # Get subnet information
            subnet_info = await self.get_subnet_info()
            if not subnet_info:
                console.print(f"❌ Error: Could not find subnet {self.config.target_netuid}")
                return False
            
            alpha_price = float(subnet_info.price)
            
            # Check if we should sell based on price threshold
            if hasattr(self.config, 'min_price_threshold') and self.config.min_price_threshold > 0:
                if alpha_price < self.config.min_price_threshold:
                    console.print(f"Bot is running for subnet {str(self.config.target_netuid)}")
                    console.print(f"⏸️  Price too low: {alpha_price:.6f} TAO < {self.config.min_price_threshold:.6f} TAO threshold")
                    console.print(f"   💡 Waiting for higher price. Current: {alpha_price:.6f} TAO, Target: ≥{self.config.min_price_threshold:.6f} TAO")
                    return True  # Continue running, just skip this sale
            
            # Check current holdings
            current_holdings = await self.get_current_holdings()
            if current_holdings < self.config.unstake_amount:
                console.print(f"🛑 Insufficient holdings: {current_holdings:.6f} < {self.config.unstake_amount:.6f} alpha needed")
                # console.print(f"   💡 Need at least {self.config.unstake_amount:.6f} alpha to unstake")
                
                console.print(f"Selling all the remaining {current_holdings:.6f}")
                    
                success = await self.unstake_alpha(current_holdings)
                    
                if success:
                    console.print(f" ✅ Sold all the remaining Alpha below the {self.config.unstake_amount}")
                else:
                    console.print("❌ Sale failed")
                return True  # Continue running, maybe more alpha will be available later
            
            # Check minimum holdings threshold
            if hasattr(self.config, 'min_holdings_threshold'):
                remaining_after_sale = current_holdings - self.config.unstake_amount
                if remaining_after_sale < self.config.min_holdings_threshold:
                    console.print(f"🛑 Would leave holdings below threshold: {remaining_after_sale:.6f} < {self.config.min_holdings_threshold:.6f} alpha")
                    return True  # Skip this sale to maintain minimum holdings
            
            tao_to_earn = self.config.unstake_amount * alpha_price
            
            console.print(f"🔄 Attempting sale: {self.config.unstake_amount:.6f} alpha → {tao_to_earn:.6f} TAO @ {alpha_price:.6f} TAO/alpha")
            
            # Execute the sale
            success = await self.unstake_alpha(self.config.unstake_amount)
            
            if success:
                # Update balance and holdings after sale
                wallet_balance = await self.get_wallet_balance()
                remaining_holdings = await self.get_current_holdings()
                self.log_trade(self.config.unstake_amount, alpha_price, tao_to_earn, wallet_balance, remaining_holdings)
            else:
                console.print("❌ Sale failed")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error in unstaking cycle: {e}")
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
        if hasattr(self.config, 'min_price_threshold') and self.config.min_price_threshold > 0:
            price_filter_text = f"💲 Min Price: {self.config.min_price_threshold:.6f} TAO per alpha\n"
        else:
            price_filter_text = f"💲 Min Price: No limit (sell at any price)\n"
            
        min_holdings_text = ""
        if hasattr(self.config, 'min_holdings_threshold'):
            min_holdings_text = f"🪙 Min Holdings: {self.config.min_holdings_threshold:.6f} alpha\n"
            
        console.print(Panel(
            f"🎯 Target Subnet: {self.config.target_netuid}\n"
            f"🪙 Unstake Amount: {self.config.unstake_amount:.6f} alpha per trade\n"
            f"⏰ Interval: {self.config.interval_minutes} minutes\n"
            f"{price_filter_text}"
            f"{min_holdings_text}"
            f"🔑 Validator: {self.config.validator}",
            title="Unstaking Bot Configuration",
            style="bold red"
        ))
        
        # Initial status
        wallet_balance = await self.get_wallet_balance()
        holdings = await self.get_current_holdings()
        console.print(f"💳 Starting Wallet Balance: {wallet_balance:.4f} TAO")
        console.print(f"🪙 Current Alpha Holdings: {holdings:.6f} alpha")
        console.print("─" * 60)
        
        try:
            while self.running:
                # Execute unstaking cycle
                should_continue = await self.unstaking_cycle()
                if not should_continue:
                    break
                
                # Wait for next interval
                console.print(f"⏳ Waiting {self.config.interval_minutes} minutes until next check...")
                for i in range(self.config.interval_minutes * 60):
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

def load_config(config_file="unstaking_config.yaml"):
    """Load configuration from YAML file."""
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return type('Config', (), config)()
    except FileNotFoundError:
        console.print(Panel(f"❌ Config file '{config_file}' not found!", title="Error", style="bold red"))
        return None
    except Exception as e:
        console.print(Panel(f"❌ Error loading config: {e}", title="Error", style="bold red"))
        return None

def signal_handler(bot):
    """Handle interrupt signals gracefully."""
    def handler(signum, frame):
        console.print("\n🛑 Received stop signal...")
        bot.stop()
    return handler

async def main():
    """Main entry point."""
    console.print(Panel("🤖 Subnet Alpha Unstaking Bot Starting...", title="Welcome", style="bold red"))
    
    # Load configuration
    config = load_config("unstaking_config.yaml")
    if not config:
        return
    
    # Create and run bot
    bot = UnstakingBot(config)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler(bot))
    signal.signal(signal.SIGTERM, signal_handler(bot))
    
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 
